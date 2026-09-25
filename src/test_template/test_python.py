"""Check Python module outputs and generated project configuration."""

from collections.abc import Callable
from contextlib import AbstractContextManager

import pytest
import tomllib

from .conftest import CopierCase

PATH_PROJECT = "modules/python/files/pyproject.toml.jinja"
PATH_PACKAGE = "modules/python/files/package/__init__.py.jinja"
PATH_IMPORT_TEST = "modules/python/files/testpackage/test_import.py.jinja"
PATH_SETUP = "modules/python/fragments/setup.sh.jinja"


def test_python_file_selection_and_defaults(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=[]) as case:
        context = case.context

    assert context["python"]["files"] == []
    assert context["python"]["vars"]["has_distribution"] is False
    assert context["python"]["vars"]["has_dev_dependencies"] is False
    assert context["python"]["contributions"] == []

    with copier_case(features=["core", "python"]) as case:
        context = case.context

    assert {file["path"] for file in context["python"]["files"]} == {
        "pyproject.toml", "src/test_project/__init__.py", "src/test_project/test_self.py",
    }
    assert context["python"]["vars"]["has_distribution"] is False
    assert context["python"]["vars"]["has_dev_dependencies"] is True
    assert any(item["target"] == "codex.setup" for item in context["python"]["contributions"])
    assert context["python"]["vars"]["package_name"] == ""
    assert context["python"]["vars"]["distribution_name"] == ""
    assert context["python"]["vars"]["testpackage_name"] == "test_project"
    assert context["python"]["vars"]["tools"] == ["pytest", "ruff", "mypy"]
    assert context["python"]["vars"]["version"] == "3.12"


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
    with pytest.raises(ValueError, match=question), copier_case(features=["core", "python"], **answers):
        pass


def test_python_distribution_name_default(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core", "python"],
        python_package_name="_example__package_",
    ) as case:
        context = case.context

    assert context["python"]["vars"]["distribution_name"] == "example-package"
    assert context["python"]["vars"]["has_distribution"] is True


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
    assert context["python"]["vars"]["testpackage_name"] == "test_acme_widget_library"
    assert context["python"]["vars"]["has_distribution"] is True
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

    assert project["tool"]["pytest"]["ini_options"]["pythonpath"] == ["src"]
    assert "src/acme_widget/__init__.py" in {file["path"] for file in context["python"]["files"]}
    assert context["python"]["vars"]["has_distribution"] is False
    assert "import acme_widget" in import_test
    assert "python -m pip install --group dev" in setup


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
    assert ("src/test_project/test_self.py" in {file["path"] for file in context["python"]["files"]}) is ("pytest" in python_tools)
    assert context["python"]["vars"]["has_dev_dependencies"] is bool(python_tools)
    assert any(item["target"] == "codex.setup" for item in context["python"]["contributions"]) is bool(python_tools)
