from collections.abc import Callable
from contextlib import AbstractContextManager

import yaml

from .conftest import CopierCase


ROOT_PIPELINE = "template/{% if 'gitlab' in modules %}.gitlab-ci.yml{% endif %}"
GITLAB_PIPELINE = (
    "template/{% if 'gitlab' in modules %}.gitlab{% endif %}/ci/gitlab.yml"
)


def test_gitlab_pipeline(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        root_pipeline = yaml.safe_load(case.render(ROOT_PIPELINE))
        gitlab_pipeline = yaml.safe_load(case.render(GITLAB_PIPELINE))

    assert root_pipeline == {"include": [{"local": ".gitlab/ci/*.yml"}]}
    assert gitlab_pipeline["gitlab:copier-update"]["extends"] == ".gitlab:base"
    assert gitlab_pipeline["gitlab:copier-update"]["needs"] == []
    assert "workflow" in gitlab_pipeline
    assert "stages" in gitlab_pipeline


def test_gitlab_contribution_templates(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["gitlab"]) as case:
        issue = case.render(
            "template/{% if 'gitlab' in modules %}.gitlab{% endif %}/"
            "issue_templates/default.md"
        )
        merge_request = case.render(
            "template/{% if 'gitlab' in modules %}.gitlab{% endif %}/"
            "merge_request_templates/default.md"
        )
        agents_fragment = case.render("template/_modules/gitlab/AGENTS.md.jinja")

    assert "## Problem" in issue
    assert "/label ~workflow::plan" in issue
    assert "## Verification" in merge_request
    assert "/label ~workflow::create" in merge_request
    assert "## GitLab development workflow" in agents_fragment
    assert "workflow::deploy" in agents_fragment
