from collections.abc import Callable
from contextlib import AbstractContextManager
import tomllib

import pytest

from .conftest import CopierCase


PATH_PROJECT = "template/{% if python_include_pyproject %}pyproject.toml{% endif %}.jinja"
PATH_PACKAGE = "template/{% if python_include_package %}src{% endif %}/{{ python_package_name }}/__init__.py.jinja"
PATH_IMPORT_TEST = "template/{% if python_include_testpackage %}src{% endif %}/{{ python_testpackage_name }}/{% if python_include_importtest %}test_import.py{% endif %}.jinja"
PATH_SETUP = "template/_modules/python/setup.sh.jinja"


def test_python_file_selection_and_defaults(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=[]) as case:
        context = case.context

    assert context["python_include_pyproject"] == False
    assert context["python_include_package"] == False
    assert context["python_include_distribution"] == False
    assert context["python_include_testpackage"] == False
    assert context["python_include_importtest"] == False
    assert context["python_include_devgroup"] == False
    assert context["python_include_setup"] == False

    with copier_case(features=["core", "python"]) as case:
        context = case.context

    assert context["python_include_pyproject"] == True
    assert context["python_include_package"] == False
    assert context["python_include_distribution"] == False
    assert context["python_include_testpackage"] == True
    assert context["python_include_importtest"] == False
    assert context["python_include_devgroup"] == True
    assert context["python_include_setup"] == True
    assert context["python_package_name"] == ""
    assert context["python_distribution_name"] == ""
    assert context["python_testpackage_name"] == "test_project"
    assert context["python_tools"] == ["pytest", "ruff", "mypy"]
    assert context["python_version"] == "3.12"


@pytest.mark.parametrize(
    ("answers", "question"),
    [
        (
            {
                "python_package_name": "example_package",
                "python_distribution_name": "Example-package",
            },
            "python_distribution_name",
        ),
        ({"python_package_name": "example-package"}, "python_package_name"),
        ({"python_version": "3"}, "python_version"),
    ],
)
def test_python_answer_validation(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    answers: dict[str, str],
    question: str,
) -> None:
    with pytest.raises(ValueError, match=question):
        with copier_case(features=["core", "python"], **answers):
            pass


def test_python_distribution_name_default(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core", "python"],
        python_package_name="_example__package_",
    ) as case:
        context = case.context

    assert context["python_distribution_name"] == "example-package"
    assert context["python_include_distribution"] is True


def test_python_project_configuration(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core", "python"],
        core_repository_name="Acme Widget",
        python_distribution_name="acme-widget-library",
        python_package_name="acme_widget_library",
        python_version="3.15",
    ) as case:
        project = tomllib.loads(case.render(PATH_PROJECT))
        package = case.render(PATH_PACKAGE)
        import_test = case.render(PATH_IMPORT_TEST)
        setup = case.render(PATH_SETUP)
        context = case.context

    assert project["project"]["name"] == "acme-widget-library"
    assert project["project"]["requires-python"] == ">=3.15"
    assert project["build-system"]["build-backend"] == "setuptools.build_meta"
    assert set(project["dependency-groups"]) == {"test", "lint", "dev"}
    assert project["tool"]["pytest"]["ini_options"]["testpaths"] == ["src/test_*"]
    assert project["tool"]["coverage"]["run"]["omit"] == ["test_*"]
    assert project["tool"]["ruff"]["src"] == ["src"]
    assert project["tool"]["mypy"]["files"] == ["src"]
    assert context["python_testpackage_name"] == "test_acme_widget_library"
    assert context["python_include_distribution"] is True
    assert '"""Acme Widget package."""' in package
    assert "import acme_widget_library" in import_test
    assert "python -m pip install --editable . --group dev" in setup


def test_python_package_without_distribution(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core", "python"],
        core_repository_name="Acme Widget",
        python_package_name="acme_widget",
        python_distribution_name="",
        python_tools=["pytest"],
    ) as case:
        project = tomllib.loads(case.render(PATH_PROJECT))
        import_test = case.render(PATH_IMPORT_TEST)
        setup = case.render(PATH_SETUP)
        context = case.context

    assert "build-system" not in project
    assert "project" not in project
    assert "setuptools" not in project["tool"]
    assert "setuptools_scm" not in project["tool"]
    assert project["tool"]["pytest"]["ini_options"]["pythonpath"] == ["src"]
    assert context["python_include_package"] is True
    assert context["python_include_distribution"] is False
    assert "import acme_widget" in import_test
    assert "python -m pip install --group dev" in setup
    assert "--editable" not in setup


@pytest.mark.parametrize(
    ("python_tools", "dependency_groups", "tool_sections"),
    [
        ([], set(), set()),
        (["pytest"], {"test", "dev"}, {"pytest", "coverage"}),
        (["ruff"], {"lint", "dev"}, {"ruff"}),
        (["mypy"], {"lint", "dev"}, {"mypy"}),
    ],
    ids=["none", "pytest", "ruff", "mypy"],
)
def test_python_tool_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    python_tools: list[str],
    dependency_groups: set[str],
    tool_sections: set[str],
) -> None:
    with copier_case(
        features=["core", "python"],
        python_tools=python_tools,
    ) as case:
        project = tomllib.loads(case.render(PATH_PROJECT))
        context = case.context

    assert set(project.get("dependency-groups", {})) == dependency_groups
    assert set(project.get("tool", {})) == tool_sections
    assert context["python_include_testpackage"] is ("pytest" in python_tools)
    assert context["python_include_devgroup"] is bool(python_tools)
    assert context["python_include_setup"] is bool(python_tools)
