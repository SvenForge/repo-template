import ast
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import yaml

from .conftest import CopierCase


PATH_CONFIG = "template/{% if sphinx_include_config %}conf.py{% endif %}.jinja"
PATH_INDEX = "template/{% if sphinx_include_index %}index.md{% endif %}.jinja"
PATH_MAKEFILE = "template/{% if sphinx_include_makefile %}doc{% endif %}/sphinx/Makefile"
PATH_MAKEBAT = "template/{% if sphinx_include_makebat %}doc{% endif %}/sphinx/make.bat"
PATH_API = "template/{% if sphinx_include_api %}doc{% endif %}/api.md.jinja"
PATH_PIPELINE = "template/{% if gitlab_include_pipeline_sphinx %}.gitlab{% endif %}/ci/sphinx.yml.jinja"
PATH_ROOT_PIPELINE = "template/{% if gitlab_include_pipeline %}.gitlab-ci.yml{% endif %}"
PATH_NEEDS = {
    "requirements": "template/{% if sphinx_include_requirements %}doc{% endif %}/requirements.md.jinja",
    "architecture": "template/{% if sphinx_include_architecture %}doc{% endif %}/architecture.md.jinja",
    "implementation": "template/{% if sphinx_include_implementation %}doc{% endif %}/implementation.md.jinja",
    "verification": "template/{% if sphinx_include_verification %}doc{% endif %}/verification.md.jinja",
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


def test_sphinx_standalone_without_readme(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["sphinx"],
        core_repository_name="Example Repository",
        core_include_readme=False,
        sphinx_needs=False,
    ) as case:
        modules = case.context["modules"]
        included = tuple(
            case.context[name]
            for name in (
                "sphinx_include_config",
                "sphinx_include_index",
                "sphinx_include_makefile",
                "sphinx_include_makebat",
                "sphinx_include_api",
                "sphinx_include_requirements",
                "sphinx_include_architecture",
                "sphinx_include_implementation",
                "sphinx_include_verification",
            )
        )
        index = case.render(PATH_INDEX)
        makefile = case.render(PATH_MAKEFILE)
        makebat = case.render(PATH_MAKEBAT)

    assert "python" in modules
    assert included == (True, True, True, True, True, False, False, False, False)
    assert "# Example Repository" in index
    assert "Documentation for Example Repository." in index
    assert "{include} README.md" not in index
    assert "doc/api" in index
    assert "sphinx-build" in makefile
    assert "SOURCEDIR = ../.." in makefile
    assert "BUILDDIR = _build" in makefile
    assert "sphinx-build" in makebat
    assert r"SOURCEDIR=..\.." in makebat
    assert "BUILDDIR=_build" in makebat


def test_sphinx_integrations(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["sphinx", "gitlab"],
        core_repository_name="Example Library",
        core_owner_name="Example Owner",
        sphinx_needs=True,
        sphinx_needs_pages=list(PATH_NEEDS),
        gitlab_pipeline=["sphinx"],
    ) as case:
        context = case.context
        config = case.render(PATH_CONFIG)
        index = case.render(PATH_INDEX)
        api = case.render(PATH_API)
        needs_pages = {
            name: case.render(path)
            for name, path in PATH_NEEDS.items()
        }
        pipeline = yaml.safe_load(case.render(PATH_PIPELINE))
        root_pipeline = yaml.safe_load(case.render(PATH_ROOT_PIPELINE))

    assert {"sphinx", "python", "gitlab"}.issubset(context["modules"])
    assert context["gitlab_include_pipeline_sphinx"] is True
    assert all(
        context[f"sphinx_include_{page}"]
        for page in PATH_NEEDS
    )

    assignments = _literal_assignments(
        config,
        {
            "project",
            "author",
            "extensions",
            "html_theme",
            "intersphinx_mapping",
            "exclude_patterns",
            "needs_types",
        },
    )
    assert assignments["project"] == "Example Library"
    assert assignments["author"] == "Example Owner"
    assert {
        "myst_parser",
        "sphinx.ext.intersphinx",
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.napoleon",
        "sphinx_needs",
    }.issubset(assignments["extensions"])
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
    assert "LICENSE.md" not in assignments["exclude_patterns"]
    assert {need_type["directive"] for need_type in assignments["needs_types"]} >= {
        "req",
        "spec",
        "impl",
        "test",
    }

    assert "{include} README.md" in index
    for entry in (
        "doc/api",
        *(f"doc/{page}" for page in PATH_NEEDS),
        "LICENSE",
    ):
        assert entry in index
    assert "{eval-rst}" in api
    assert ".. autosummary::" in api
    assert ":toctree: sphinx/_autosummary" in api
    assert "example_library" in api

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
        "make -C doc/sphinx html SPHINXOPTS='-W --keep-going'"
    ]
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
    assert root_pipeline["stages"] == ["test", "deploy"]
