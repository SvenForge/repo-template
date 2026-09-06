from collections.abc import Callable
from contextlib import AbstractContextManager
import os
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest

from .conftest import CopierCase, TEMPLATE_ROOT


PATH_PROJECT = "template/{% if python_include_pyproject %}pyproject.toml{% endif %}.jinja"
PATH_PACKAGE = "template/{% if python_include_package %}src{% endif %}/{{ python_package_name }}/__init__.py.jinja"
PATH_TEST_PACKAGE = "template/{% if python_include_testpackage %}src{% endif %}/test_{{ python_package_name }}/__init__.py"
PATH_IMPORT_TEST = "template/{% if python_include_testpackage %}src{% endif %}/test_{{ python_package_name }}/test_import.py.jinja"


def test_python_file_selection_and_name_defaults(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=[]) as case:
        assert (
            case.context["python_include_pyproject"],
            case.context["python_include_package"],
            case.context["python_include_testpackage"],
        ) == (False, False, False)

    with copier_case(
        features=["python"],
        core_repository_name="Example Repository",
    ) as case:
        assert (
            case.context["python_include_pyproject"],
            case.context["python_include_package"],
            case.context["python_include_testpackage"],
        ) == (True, True, True)
        assert case.context["python_distribution_name"] == "example-repository"
        assert case.context["python_package_name"] == "example_repository"
        assert case.context["python_version"] == "3.12"


@pytest.mark.parametrize(
    ("answers", "question"),
    [
        ({"python_distribution_name": "Example-package"}, "python_distribution_name"),
        ({"python_distribution_name": "example_package"}, "python_distribution_name"),
        ({"python_package_name": "example-package"}, "python_package_name"),
        ({"python_package_name": "class"}, "python_package_name"),
        ({"python_version": "3"}, "python_version"),
        ({"python_version": "3.11"}, "python_version"),
        ({"python_version": "3.13.1"}, "python_version"),
        ({"python_version": "4.0"}, "python_version"),
        ({"python_version": "3.15"}, "python_version"),
    ],
    ids=[
        "uppercase-distribution",
        "underscored-distribution",
        "hyphenated-package",
        "keyword-package",
        "missing-minor",
        "below-supported-range",
        "patch-version",
        "wrong-major",
        "above-supported-range",
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
        core_owner_name="Example Owner",
        core_owner_email="owner@example.com",
        core_license="MIT",
        python_distribution_name="acme-widget-library",
        python_package_name="acme_widget_library",
        python_version="3.14",
    ) as case:
        project = tomllib.loads(case.render(PATH_PROJECT))
        package = case.render(PATH_PACKAGE)
        test_package = case.render(PATH_TEST_PACKAGE)
        import_test = case.render(PATH_IMPORT_TEST)

    assert project["project"]["name"] == "acme-widget-library"
    assert project["project"]["requires-python"] == ">=3.14"
    assert project["project"]["dynamic"] == ["version"]
    assert project["project"]["dependencies"] == []
    assert project["project"]["readme"] == "README.md"
    assert project["project"]["authors"] == [
        {"name": "Example Owner", "email": "owner@example.com"}
    ]
    assert project["project"]["license"] == "MIT"
    assert project["project"]["license-files"] == ["LICENSE.md"]

    assert project["build-system"]["build-backend"] == "setuptools.build_meta"
    assert any(
        requirement.startswith("setuptools-scm")
        for requirement in project["build-system"]["requires"]
    )
    assert project["tool"]["setuptools"]["package-dir"] == {"": "src"}
    assert project["tool"]["setuptools"]["packages"]["find"]["where"] == ["src"]
    assert project["tool"]["setuptools_scm"]["fallback_version"]

    groups = project["dependency-groups"]
    assert groups["test"] == ["pytest", "pytest-cov"]
    assert groups["lint"] == ["mypy", "ruff"]
    assert groups["dev"] == [
        {"include-group": "test"},
        {"include-group": "lint"},
    ]

    assert project["tool"]["pytest"]["ini_options"]["testpaths"] == [
        "src/test_acme_widget_library"
    ]
    assert project["tool"]["coverage"]["run"]["source"] == ["acme_widget_library"]
    assert project["tool"]["ruff"] == {
        "src": ["src"],
        "target-version": "py314",
    }
    assert project["tool"]["mypy"]["files"] == [
        "src/acme_widget_library",
        "src/test_acme_widget_library",
    ]
    assert project["tool"]["mypy"]["python_version"] == "3.14"
    assert project["tool"]["pytest"]["ini_options"]["addopts"] == [
        "--cov=acme_widget_library",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage.xml",
        "--junitxml=pytest.xml",
    ]

    assert "Acme Widget" in package
    assert test_package == ""
    assert "import acme_widget_library" in import_test

    for rendered in (package, test_package, import_test):
        assert "{{" not in rendered
        assert "{%" not in rendered


def test_python_project_omits_absent_core_metadata(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["python"],
        core_include_readme=False,
        core_owner_name="",
        core_license="NOASSERTION",
    ) as case:
        rendered = case.render(PATH_PROJECT)
        project = tomllib.loads(rendered)["project"]
    assert "dependencies = []\n\n[dependency-groups]" in rendered
    assert "\n\n\n" not in rendered

    assert "readme" not in project
    assert "authors" not in project
    assert "license" not in project
    assert "license-files" not in project


def test_python_project_proprietary_license_metadata(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["python"], core_license="NONE") as case:
        project = tomllib.loads(case.render(PATH_PROJECT))["project"]

    assert project["license"] == "LicenseRef-Proprietary"
    assert project["license-files"] == ["LICENSE.md"]


def _copy_python_project(destination: Path) -> None:
    subprocess.run(
        [
            "copier",
            "copy",
            "--defaults",
            "--quiet",
            "--vcs-ref=HEAD",
            "--data",
            "features=[python]",
            "--data",
            "core_include_readme=false",
            "--data",
            "core_license=NOASSERTION",
            "--data",
            "core_include_gitignore=false",
            str(TEMPLATE_ROOT),
            str(destination),
        ],
        check=True,
    )


def test_generated_python_project_smoke(tmp_path: Path) -> None:
    destination = tmp_path / "python-project"
    _copy_python_project(destination)

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(destination / "src")
    subprocess.run(
        [sys.executable, "-m", "pytest", "-o", "addopts="],
        cwd=destination,
        env=environment,
        check=True,
    )


def test_generated_python_project_editable_install(tmp_path: Path) -> None:
    """Exercise the complete generated toolchain when network tests are enabled."""
    if os.environ.get("RUN_PYTHON_PROJECT_SMOKE") != "1":
        pytest.skip("set RUN_PYTHON_PROJECT_SMOKE=1 to install the generated toolchain")

    destination = tmp_path / "python-project"
    _copy_python_project(destination)

    environment = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(environment)],
        check=True,
    )
    python = environment / "bin/python"
    subprocess.run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ],
        cwd=destination,
        check=True,
    )
    subprocess.run(
        [
            python,
            "-m",
            "pip",
            "install",
            "--editable",
            ".",
            "--group",
            "dev",
        ],
        cwd=destination,
        check=True,
    )
    subprocess.run(
        [python, "-m", "pytest"],
        cwd=destination,
        check=True,
    )
    subprocess.run(
        [python, "-m", "ruff", "check", "src"],
        cwd=destination,
        check=True,
    )
    subprocess.run(
        [python, "-m", "ruff", "format", "--check", "src"],
        cwd=destination,
        check=True,
    )
    subprocess.run([python, "-m", "mypy"], cwd=destination, check=True)
    subprocess.run(
        [
            python,
            "-c",
            (
                "from importlib.metadata import version; "
                "assert version('my-repository') == '0.0.0'"
            ),
        ],
        cwd=destination,
        check=True,
    )
