"""Check Sphinx module files and their project integrations."""

import ast
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
import tomllib
import yaml

from .conftest import CopierCase

PATH_CONFIG = "modules/sphinx/files/conf.py.jinja"
PATH_INDEX = "modules/sphinx/files/index.md.jinja"
PATH_LICENSE = "modules/core/files/LICENSE_NONE.md.jinja"
PATH_README = "modules/core/files/README.md.jinja"
PATH_MAKEFILE = "modules/sphinx/files/Makefile.jinja"
PATH_MAKEBAT = "modules/sphinx/files/make.bat.jinja"
PATH_API = "modules/sphinx/files/api.md.jinja"
PATH_PIPELINE = "modules/gitlab/files/ci/sphinx.yml.jinja"
PATH_ROOT_PIPELINE = "modules/gitlab/files/gitlab-ci.yml.jinja"
PATH_NEEDS = {
    "requirements": "modules/sphinx/files/requirements.md.jinja",
    "architecture": "modules/sphinx/files/architecture.md.jinja",
    "implementation": "modules/sphinx/files/implementation.md.jinja",
    "verification": "modules/sphinx/files/verification.md.jinja",
}


def _literal_assignments(source: str, names: set[str]) -> dict[str, Any]:
    assignments: dict[str, Any] = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue

        if value is None:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id in names:
                assignments[target.id] = ast.literal_eval(value)

    return assignments


def test_sphinx_without_readme(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core", "sphinx", "python"],
        core_repository_name="Example Repository",
        core_include_readme=False,
        sphinx_needs=False,
        sphinx_api_packages=[],
    ) as case:
        features = case.context["features"]
        included = {file["path"] for file in case.context["sphinx"]["files"]}
        index = case.render(PATH_INDEX)
        makefile = case.render(PATH_MAKEFILE)
        makebat = case.render(PATH_MAKEBAT)

    assert "python" in features
    assert included == {"doc/sphinx/conf.py", "doc/sphinx/index.md", "doc/notes.md", "doc/sphinx/Makefile", "doc/sphinx/make.bat"}
    assert "# Example Repository" in index
    assert "Documentation for Example Repository." in index
    assert ":glob:" in index
    assert "../*" in index
    assert '-c "$(CONFDIR)"' in makefile
    assert "SOURCEDIR     = ../.." in makefile
    assert "BUILDDIR      = _build" in makefile
    assert "-c %CONFDIR%" in makebat
    assert r'SOURCEDIR="..\.."' in makebat
    assert "BUILDDIR=_build" in makebat


def test_sphinx_integrations(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    pages_url = "https://example.gitlab.io/example-library/"
    with copier_case(
        features=["core", "sphinx", "gitlab", "python"],
        core_repository_name="Example Library",
        core_repository_url="git@gitlab.com:example/example-library.git",
        core_owner_name="Example Owner",
        python_package_name="example_library",
        sphinx_needs=True,
        sphinx_needs_pages=list(PATH_NEEDS),
        gitlab_pipeline=["sphinx"],
    ) as case:
        context = case.context
        config = case.render(PATH_CONFIG)
        index = case.render(PATH_INDEX)
        readme = case.render(PATH_README)
        api = case.render(PATH_API)
        license_text = case.render(PATH_LICENSE)
        needs_pages = {
            name: case.render(path)
            for name, path in PATH_NEEDS.items()
        }
        pipeline = yaml.safe_load(case.render(PATH_PIPELINE))
        root_pipeline = yaml.safe_load(case.render(PATH_ROOT_PIPELINE))

    assert {"sphinx", "python", "gitlab"}.issubset(context["features"])
    assert ".gitlab/ci/sphinx.yml" in {file["path"] for file in context["gitlab"]["files"]}
    assert {f"doc/{page}.md" for page in PATH_NEEDS}.issubset(
        file["path"] for file in context["sphinx"]["files"]
    )

    assignments = _literal_assignments(
        config,
        {
            "project",
            "author",
            "extensions",
            "needs_sphinx",
            "html_theme",
            "intersphinx_mapping",
            "exclude_patterns",
            "apidoc_modules",
            "needs_types",
        },
    )
    assert assignments["project"] == "Example Library"
    assert assignments["author"] == "Example Owner"
    assert {
        "myst_parser",
        "sphinx.ext.intersphinx",
        "sphinx.ext.apidoc",
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx_needs",
    }.issubset(assignments["extensions"])
    assert assignments["needs_sphinx"] == "8.2"
    assert assignments["apidoc_modules"] == [
        {
            "path": f"../../src/{package}",
            "destination": f"doc/sphinx/_apidoc/{package}",
        }
        for package in ["example_library", "test_example_library"]
    ]
    assert assignments["html_theme"] == "furo"
    assert {
        "python",
        "sphinx",
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
    }.issubset(assignments["intersphinx_mapping"])
    assert "doc/sphinx/_build" in assignments["exclude_patterns"]
    assert {need_type["directive"] for need_type in assignments["needs_types"]} >= {
        "req",
        "spec",
        "impl",
        "test",
    }

    assert "{include} ../../README.md" in index
    assert ":end-before: <!-- toctree-start -->" in index
    assert ":start-after: <!-- toctree-end -->" in index
    assert "{toctree}" in index
    assert ":glob:" in index
    assert "../*" in index
    assert f"[GitLab Pages]({pages_url})" in readme
    assert "<!-- toctree-start -->" in readme
    assert "<!-- toctree-end -->" in readme
    assert "License <../../LICENSE>" in index
    assert license_text.startswith("# License & Copyright Information\n")
    assert "{toctree}" in api
    assert "sphinx/_apidoc/example_library/modules" in api
    assert "sphinx/_apidoc/test_example_library/modules" in api

    needs_contracts = {
        "requirements": ("req", "REQ_001"),
        "architecture": ("spec", "SPEC_001"),
        "implementation": ("impl", "IMPL_001"),
        "verification": ("test", "TEST_001"),
    }
    for page, (directive, need_id) in needs_contracts.items():
        assert f"{{{directive}}}" in needs_pages[page]
        assert need_id in needs_pages[page]

    visible_jobs = {key for key in pipeline if not key.startswith(".")}
    assert visible_jobs == {"sphinx:build", "sphinx:pages"}
    assert pipeline[".sphinx:base"]["image"] == "python:3.12-bookworm"
    assert "python -m pip install --editable . --group doc" in pipeline[".sphinx:base"]["before_script"]

    build = pipeline["sphinx:build"]
    assert build["needs"] == []
    assert build["script"] == [
        "make -C doc/sphinx html SPHINXOPTS='-W --keep-going'",
    ]
    assert build["rules"][-1] == {
        "when": "manual",
        "allow_failure": True,
    }
    merge_request_rule = next(
        rule
        for rule in build["rules"]
        if rule.get("if") == '$CI_PIPELINE_SOURCE == "merge_request_event"'
    )
    assert {"**/*.py", "**/*.md", "doc/**/*", "src/**/*"}.issubset(
        merge_request_rule["changes"],
    )
    assert {
        path.rstrip("/")
        for path in build["artifacts"]["paths"]
    } == {"doc/sphinx/_build/html"}

    pages = pipeline["sphinx:pages"]
    assert any(
        isinstance(need, dict)
        and need.get("job") == "sphinx:build"
        and need.get("artifacts") is True
        for need in pages["needs"]
    )
    assert pages["pages"]["publish"].rstrip("/") == "doc/sphinx/_build/html"
    assert root_pipeline["stages"] == ["test"]


@pytest.mark.parametrize("packages", [["example_library"], ["test_contracts"], []])
def test_sphinx_api_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    packages: list[str],
) -> None:
    with copier_case(
        features=["core", "python", "sphinx"],
        python_package_name="example_library",
        python_testpackage_name="test_contracts",
        sphinx_api_packages=packages,
    ) as case:
        context = case.context
        config = _literal_assignments(case.render(PATH_CONFIG), {"extensions", "apidoc_modules"})
        project = tomllib.loads(case.render("modules/python/files/pyproject.toml.jinja"))

    assert context["_copier_answers"]["sphinx_api_packages"] == packages
    assert context["sphinx"]["vars"]["api_packages"] == packages
    assert ("doc/api.md" in {file["path"] for file in context["sphinx"]["files"]}) is bool(packages)
    assert ("sphinx.ext.apidoc" in config["extensions"]) is bool(packages)
    assert ({"include-group": "test"} in project["dependency-groups"]["doc"]) is ("test_contracts" in packages)
    if packages:
        assert [entry["path"] for entry in config["apidoc_modules"]] == [f"../../src/{package}" for package in packages]


def test_sphinx_host_packages(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["sphinx"],
        sphinx_inputs={
            "python_packages": ["alpha", "beta", "gamma"],
            "package_dependency_groups": {"beta": ["test"], "gamma": ["test"]},
        },
    ) as case:
        config = _literal_assignments(case.render(PATH_CONFIG), {"apidoc_modules"})
        assert case.context["sphinx"]["vars"]["api_packages"] == ["alpha", "beta", "gamma"]
        assert case.context["sphinx"]["vars"]["api_dependency_groups"] == ["test"]
        assert len({entry["destination"] for entry in config["apidoc_modules"]}) == 3
