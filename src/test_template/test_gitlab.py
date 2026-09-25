"""Check GitLab module files, pipelines, and contributions."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
import yaml

from .conftest import CopierCase

PATH_ROOT_PIPELINE = "modules/gitlab/files/gitlab-ci.yml.jinja"
PATH_COPIER_PIPELINE = "modules/gitlab/files/ci/copier.yml.jinja"
PATH_DEMO_PIPELINE = "modules/gitlab/files/ci/demo.yml.jinja"
PATH_PYTHON_PIPELINE = "modules/gitlab/files/ci/python.yml.jinja"
PATH_MR_TEMPLATE = "modules/gitlab/files/merge_request.md.jinja"
PATH_ISSUE_TEMPLATE = "modules/gitlab/files/issue.md.jinja"


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
    assert copier_pipeline["copier:check"]["allow_failure"] is True
    assert "demo:fortune" in demo_pipeline


def test_gitlab_python_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core", "gitlab", "python"],
        gitlab_pipeline=["python"],
        python_tools=["pytest", "mypy"],
        python_version="3.13",
    ) as case:
        rendered_python = case.render(PATH_PYTHON_PIPELINE)

    python_pipeline = yaml.safe_load(rendered_python)

    visible_jobs = {key for key in python_pipeline if not key.startswith(".")}
    assert visible_jobs == {"python:pytest", "python:mypy"}
    assert python_pipeline[".python:base"]["image"] == "python:3.13-bookworm"
    install = python_pipeline[".python:base"]["before_script"][1]
    assert "python -m pip install --group" in install
    assert "coverage_report" in python_pipeline["python:pytest"]["artifacts"]["reports"]
    assert python_pipeline["python:mypy"]["allow_failure"] is True
    assert "codequality" in python_pipeline["python:mypy"]["artifacts"]["reports"]


def test_gitlab_contribution_templates(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        issue = case.render(PATH_ISSUE_TEMPLATE)
        merge_request = case.render(PATH_MR_TEMPLATE)
        agents_fragment = case.render("modules/gitlab/fragments/AGENTS.md.jinja")

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
            {"features": ["core", "gitlab", "python"]},
            (True, True, True, True, True, True),
        ),
        (
            {
                "features": ["core", "gitlab", "python"],
                "python_tools": [],
            },
            (True, True, True, True, False, True),
        ),
    ],
    ids=[
        "without-gitlab",
        "without-pipeline",
        "copier-only",
        "python-default-pipelines",
        "python-without-tools",
    ],
)
def test_gitlab_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    answers: dict[str, Any],
    expected: tuple[bool, bool, bool, bool, bool, bool],
) -> None:
    with copier_case(**answers) as case:
        files = {file["path"] for file in case.context["gitlab"]["files"]}
        selected = tuple(
            path in files
            for path in (
                ".gitlab/issue_templates/default.md",
                ".gitlab/merge_request_templates/default.md",
                ".gitlab/ci/copier.yml",
                ".gitlab/ci/demo.yml",
                ".gitlab/ci/python.yml",
                ".gitlab-ci.yml",
            )
        )

    assert selected == expected
