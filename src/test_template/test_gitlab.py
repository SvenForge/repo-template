from collections.abc import Callable
from contextlib import AbstractContextManager

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


def test_gitlab_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        root_pipeline = yaml.safe_load(case.render(ROOT_PIPELINE))
        copier_pipeline = yaml.safe_load(case.render(COPIER_PIPELINE))
        demo_pipeline = yaml.safe_load(case.render(DEMO_PIPELINE))

    assert root_pipeline["include"] == [{"local": ".gitlab/ci/*.yml"}]
    assert copier_pipeline["copier:check"]["extends"] == ".copier:base"
    assert copier_pipeline["copier:check"]["needs"] == []
    assert copier_pipeline["copier:check"]["script"] == ["copier check-update"]
    assert copier_pipeline[".copier:base"]["before_script"] == [
        'python -m pip install "copier==9.17.2"'
    ]
    assert demo_pipeline["demo:fortune"]["extends"] == ".demo:base"
    assert demo_pipeline["demo:fortune"]["needs"] == []
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


def test_empty_pipeline_selection_omits_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["gitlab"],
        gitlab_pipeline=[],
    ) as case:
        assert case.context["gitlab_include_issue_template"] is True
        assert case.context["gitlab_include_merge_request_template"] is True
        assert case.context["gitlab_include_pipeline_copier"] is False
        assert case.context["gitlab_include_pipeline_demo"] is False
        assert case.context["gitlab_include_pipeline"] is False


def test_pipeline_job_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"], gitlab_pipeline=["copier"]) as case:
        copier_pipeline = yaml.safe_load(case.render(COPIER_PIPELINE))

        assert case.context["gitlab_include_pipeline_copier"] is True
        assert case.context["gitlab_include_pipeline_demo"] is False
        assert case.context["gitlab_include_pipeline"] is True

    assert "copier:check" in copier_pipeline


def test_gitlab_calculated_variables_without_feature(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=[]) as case:
        assert case.context["gitlab_include_issue_template"] is False
        assert case.context["gitlab_include_merge_request_template"] is False
        assert case.context["gitlab_include_pipeline_copier"] is False
        assert case.context["gitlab_include_pipeline_demo"] is False
        assert case.context["gitlab_include_pipeline"] is False
