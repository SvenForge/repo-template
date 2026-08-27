from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
import yaml

from .conftest import CopierCase


ROOT_PIPELINE = "template/{% if gitlab_include_pipeline %}.gitlab-ci.yml{% endif %}"
COPIER_PIPELINE = (
    "template/{% if gitlab_include_pipeline_copier %}.gitlab{% endif %}/"
    "ci/copier.yml.jinja"
)
DEMO_PIPELINE = (
    "template/{% if gitlab_include_pipeline_demo %}.gitlab{% endif %}/ci/demo.yml"
)


def test_gitlab_pipeline_smoke(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        root_pipeline = yaml.safe_load(case.render(ROOT_PIPELINE))
        copier_pipeline = yaml.safe_load(case.render(COPIER_PIPELINE))
        demo_pipeline = yaml.safe_load(case.render(DEMO_PIPELINE))

    assert root_pipeline["include"] == [{"local": ".gitlab/ci/*.yml"}]
    assert "copier:check" in copier_pipeline
    assert copier_pipeline[".copier:base"]["variables"]["COPIER_VERSION"] == "9.17.2"
    assert "demo:fortune" in demo_pipeline


def test_gitlab_contribution_templates_smoke(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        issue = case.render(
            "template/{% if gitlab_include_issue_template %}.gitlab{% endif %}/"
            "issue_templates/default.md"
        )
        merge_request = case.render(
            "template/{% if gitlab_include_merge_request_template %}.gitlab{% endif %}/"
            "merge_request_templates/default.md"
        )
        agents_fragment = case.render("template/_modules/gitlab/AGENTS_gitlab.jinja")

    assert "## Problem" in issue
    assert "## How are the changes verified?" in merge_request
    assert "## GitLab development workflow" in agents_fragment


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        ({"features": []}, (False, False, False, False, False)),
        (
            {"features": ["gitlab"], "gitlab_pipeline": []},
            (True, True, False, False, False),
        ),
        (
            {"features": ["gitlab"], "gitlab_pipeline": ["copier"]},
            (True, True, True, False, True),
        ),
    ],
    ids=["without-gitlab", "without-pipeline", "copier-only"],
)
def test_gitlab_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    answers: dict[str, Any],
    expected: tuple[bool, bool, bool, bool, bool],
) -> None:
    with copier_case(**answers) as case:
        selected = (
            case.context["gitlab_include_issue_template"],
            case.context["gitlab_include_merge_request_template"],
            case.context["gitlab_include_pipeline_copier"],
            case.context["gitlab_include_pipeline_demo"],
            case.context["gitlab_include_pipeline"],
        )

    assert selected == expected
