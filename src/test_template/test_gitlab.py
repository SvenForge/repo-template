from collections.abc import Callable
from contextlib import AbstractContextManager

import yaml

from .conftest import CopierCase


ROOT_PIPELINE = "template/{% if gitlab_include_pipeline %}.gitlab-ci.yml{% endif %}"
GITLAB_PIPELINE = (
    "template/{% if gitlab_include_pipeline %}.gitlab{% endif %}/ci/gitlab.yml"
)


def test_gitlab_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        root_pipeline = yaml.safe_load(case.render(ROOT_PIPELINE))
        gitlab_pipeline = yaml.safe_load(case.render(GITLAB_PIPELINE))

    assert root_pipeline["include"] == [{"local": ".gitlab/ci/*.yml"}]
    assert gitlab_pipeline["gitlab:copier-update"]["extends"] == ".gitlab:base"
    assert gitlab_pipeline["gitlab:copier-update"]["needs"] == []
    assert gitlab_pipeline["gitlab:copier-update"]["script"] == ["copier check-update"]
    assert gitlab_pipeline["gitlab:demo"]["needs"] == []
    assert "workflow" in root_pipeline
    assert "stages" in root_pipeline


def test_gitlab_contribution_templates(
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
    assert "/label ~workflow::plan" in issue
    assert "## How are the changes verified?" in merge_request
    assert "## GitLab development workflow" in agents_fragment
    assert "workflow::deploy" in agents_fragment


def test_optional_gitlab_files(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["gitlab"],
        gitlab_include_issue_template=False,
        gitlab_include_merge_request_template=False,
        gitlab_include_pipeline=False,
    ) as case:
        assert case.context["gitlab_include_issue_template"] is False
        assert case.context["gitlab_include_merge_request_template"] is False
        assert case.context["gitlab_include_pipeline"] is False
