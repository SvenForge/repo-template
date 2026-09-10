from collections.abc import Callable
from contextlib import AbstractContextManager
import tomllib

import pytest

from .conftest import CopierCase


PATH_PROJECT = "template/{% if python_include_pyproject %}pyproject.toml{% endif %}.jinja"
PATH_PACKAGE = "template/{% if python_include_package %}src{% endif %}/{{ python_package_name }}/__init__.py.jinja"
PATH_IMPORT_TEST = "template/{% if python_include_testpackage %}src{% endif %}/test_{{ python_package_name }}/test_import.py.jinja"


def test_python_file_selection_and_defaults(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=[]) as case:
        context = case.context

    assert context["python_include_pyproject"] == False
    assert context["python_include_package"] == False
    assert context["python_include_testpackage"] == False

    with copier_case(
        features=["python"],
        core_repository_name="Example Repository",
    ) as case:
        context = case.context

    assert context["python_include_pyproject"] == True
    assert context["python_include_package"] == True
    assert context["python_include_testpackage"] == True
    assert context["python_distribution_name"] == "example-repository"
    assert context["python_package_name"] == "example_repository"
    assert context["python_version"] == "3.12"


@pytest.mark.parametrize(
    ("answers", "question"),
    [
        (
            {"python_distribution_name": "Example-package"},
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
        with copier_case(features=["python"], **answers):
            pass


def test_python_project_configuration(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["python"],
        core_repository_name="Acme Widget",
        python_distribution_name="acme-widget-library",
        python_package_name="acme_widget_library",
        python_version="3.15",
    ) as case:
        project = tomllib.loads(case.render(PATH_PROJECT))
        package = case.render(PATH_PACKAGE)
        import_test = case.render(PATH_IMPORT_TEST)

    assert project["project"]["name"] == "acme-widget-library"
    assert project["project"]["requires-python"] == ">=3.15"
    assert project["build-system"]["build-backend"] == "setuptools.build_meta"
    assert set(project["dependency-groups"]) == {"test", "lint", "dev"}
    assert project["tool"]["pytest"]["ini_options"]["testpaths"] == ["src/test_*"]
    assert project["tool"]["coverage"]["run"]["omit"] == ["test_*"]
    assert project["tool"]["ruff"]["src"] == ["src"]
    assert project["tool"]["mypy"]["files"] == ["src"]
    assert "import acme_widget_library" in import_test
