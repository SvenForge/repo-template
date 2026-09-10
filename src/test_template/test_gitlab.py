from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
import yaml

from .conftest import CopierCase


PATH_ROOT_PIPELINE = "template/{% if gitlab_include_pipeline %}.gitlab-ci.yml{% endif %}"
PATH_COPIER_PIPELINE = "template/{% if gitlab_include_pipeline_copier %}.gitlab{% endif %}/ci/copier.yml.jinja"
PATH_DEMO_PIPELINE = "template/{% if gitlab_include_pipeline_demo %}.gitlab{% endif %}/ci/demo.yml"
PATH_PYTHON_PIPELINE = "template/{% if gitlab_include_pipeline_python %}.gitlab{% endif %}/ci/python.yml.jinja"
PATH_MR_TEMPLATE = "template/{% if gitlab_include_merge_request_template %}.gitlab{% endif %}/merge_request_templates/default.md"
PATH_ISSUE_TEMPLATE = "template/{% if gitlab_include_issue_template %}.gitlab{% endif %}/issue_templates/default.md"


def test_gitlab_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        root_pipeline = yaml.safe_load(case.render(PATH_ROOT_PIPELINE))
        copier_pipeline = yaml.safe_load(case.render(PATH_COPIER_PIPELINE))
        demo_pipeline = yaml.safe_load(case.render(PATH_DEMO_PIPELINE))

    assert root_pipeline["include"] == [{"local": ".gitlab/ci/*.yml"}]
    assert "copier:check" in copier_pipeline
    assert copier_pipeline[".copier:base"]["variables"]["COPIER_VERSION"] == "9.17.2"
    assert "demo:fortune" in demo_pipeline


def test_gitlab_python_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["gitlab", "python"],
        gitlab_pipeline=["python"],
        python_version="3.13",
    ) as case:
        rendered_root = case.render(PATH_ROOT_PIPELINE)
        rendered_python = case.render(PATH_PYTHON_PIPELINE)

    root_pipeline = yaml.safe_load(rendered_root)
    python_pipeline = yaml.safe_load(rendered_python)

    assert root_pipeline["include"] == [{"local": ".gitlab/ci/*.yml"}]

    base = python_pipeline[".python:base"]
    assert base["image"] == "python:3.13-bookworm"
    assert base["before_script"] == [
        "python -m pip install --upgrade pip",
        'python -m pip install --editable . --group "$PYTHON_DEPENDENCY_GROUP"',
    ]

    pytest_job = python_pipeline["python:pytest"]
    assert pytest_job["needs"] == []
    assert pytest_job["variables"]["PYTHON_DEPENDENCY_GROUP"] == "test"
    assert pytest_job["script"] == ["pytest"]
    assert pytest_job["artifacts"]["when"] == "always"
    assert pytest_job["artifacts"]["reports"] == {
        "junit": "pytest.xml",
        "coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"},
    }

    ruff_job = python_pipeline["python:ruff"]
    assert ruff_job["needs"] == []
    assert ruff_job["variables"]["PYTHON_DEPENDENCY_GROUP"] == "lint"
    assert ruff_job["script"] == [
        "ruff check src --output-format=gitlab"
        " --output-file=ruff-code-quality.json || true",
        "ruff format --check src || true",
    ]
    assert ruff_job["artifacts"] == {
        "when": "always",
        "reports": {"codequality": "ruff-code-quality.json"},
    }

    mypy_job = python_pipeline["python:mypy"]
    assert mypy_job["needs"] == []
    assert mypy_job["variables"]["PYTHON_DEPENDENCY_GROUP"] == "lint"
    assert mypy_job["script"] == [
        "mypy --no-error-summary > mypy-out.txt || true",
        "mypy-gitlab-code-quality < mypy-out.txt > mypy-code-quality.json",
    ]
    assert mypy_job["artifacts"] == {
        "when": "always",
        "reports": {"codequality": "mypy-code-quality.json"},
    }

    visible_jobs = {key for key in python_pipeline if not key.startswith(".")}
    assert visible_jobs == {"python:pytest", "python:ruff", "python:mypy"}
    for job_name in visible_jobs:
        assert python_pipeline[job_name]["extends"] == ".python:base"
        assert python_pipeline[job_name]["needs"] == []

    for rendered in (rendered_root, rendered_python):
        assert "{{" not in rendered
        assert "{%" not in rendered


def test_gitlab_contribution_templates(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        issue = case.render(PATH_ISSUE_TEMPLATE)
        merge_request = case.render(PATH_MR_TEMPLATE)
        agents_fragment = case.render("template/_modules/gitlab/AGENTS.md.jinja")

    assert "## Problem" in issue
    assert "## How are the changes verified?" in merge_request
    assert "## GitLab development workflow" in agents_fragment


def test_gitlab_python_pipeline_choice_requires_python_module(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with pytest.raises(ValueError, match="gitlab_pipeline"):
        with copier_case(features=["gitlab"], gitlab_pipeline=["python"]):
            pass


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        ({"features": []}, (False, False, False, False, False, False)),
        (
            {"features": ["gitlab"], "gitlab_pipeline": []},
            (True, True, False, False, False, False),
        ),
        (
            {"features": ["gitlab"], "gitlab_pipeline": ["copier"]},
            (True, True, True, False, False, True),
        ),
        (
            {"features": ["python"]},
            (False, False, False, False, False, False),
        ),
        (
            {"features": ["gitlab", "python"], "gitlab_pipeline": []},
            (True, True, False, False, False, False),
        ),
        (
            {"features": ["gitlab", "python"], "gitlab_pipeline": ["python"]},
            (True, True, False, False, True, True),
        ),
        (
            {"features": ["gitlab", "python"]},
            (True, True, True, True, True, True),
        ),
    ],
    ids=[
        "without-gitlab",
        "without-pipeline",
        "copier-only",
        "python-only",
        "python-with-empty-pipeline",
        "python-pipeline",
        "python-default-pipelines",
    ],
)
def test_gitlab_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    answers: dict[str, Any],
    expected: tuple[bool, bool, bool, bool, bool, bool],
) -> None:
    with copier_case(**answers) as case:
        selected = (
            case.context["gitlab_include_issue_template"],
            case.context["gitlab_include_merge_request_template"],
            case.context["gitlab_include_pipeline_copier"],
            case.context["gitlab_include_pipeline_demo"],
            case.context["gitlab_include_pipeline_python"],
            case.context["gitlab_include_pipeline"],
        )

    assert selected == expected
