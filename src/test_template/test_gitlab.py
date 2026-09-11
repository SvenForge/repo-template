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
    assert "CI_JOB_TOKEN" in copier_pipeline[".copier:base"]["before_script"][0]
    assert "demo:fortune" in demo_pipeline


def test_gitlab_python_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["gitlab", "python"],
        gitlab_pipeline=["python"],
        python_version="3.13",
    ) as case:
        rendered_python = case.render(PATH_PYTHON_PIPELINE)

    python_pipeline = yaml.safe_load(rendered_python)

    visible_jobs = {key for key in python_pipeline if not key.startswith(".")}
    assert visible_jobs == {"python:pytest", "python:ruff", "python:mypy"}
    assert python_pipeline[".python:base"]["image"] == "python:3.13-bookworm"
    assert "coverage_report" in python_pipeline["python:pytest"]["artifacts"]["reports"]
    for job_name in ("python:ruff", "python:mypy"):
        assert python_pipeline[job_name]["allow_failure"] is True
        assert "codequality" in python_pipeline[job_name]["artifacts"]["reports"]


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
            {"features": ["gitlab", "python"]},
            (True, True, True, True, True, True),
        ),
    ],
    ids=[
        "without-gitlab",
        "without-pipeline",
        "copier-only",
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
