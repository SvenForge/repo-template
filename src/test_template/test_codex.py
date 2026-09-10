from collections.abc import Callable
from contextlib import AbstractContextManager
import json
from typing import Any

import pytest

from .conftest import CopierCase


PATH_AGENTS = "template/{% if codex_include_agents %}AGENTS.md{% endif %}.jinja"
PATH_SETUP = "template/{% if codex_include_setup %}.codex{% endif %}/setup.sh.jinja"
PATH_MAINTENANCE = "template/{% if codex_include_maintenance %}.codex{% endif %}/maintenance.sh.jinja"
PATH_DEVCONTAINER_CONFIG = "template/{% if devcontainer_include_config %}.devcontainer{% endif %}/devcontainer.json.jinja"


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        (
            {"features": []},
            (False, False, False, False, False),
        ),
        (
            {"features": ["codex"], "codex_cloud": False},
            (False, False, True, False, False),
        ),
        (
            {"features": ["codex", "devcontainer"]},
            (True, True, True, True, True),
        ),
    ],
    ids=["without-codex", "agents-only", "with-devcontainer"],
)
def test_codex_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    answers: dict[str, Any],
    expected: tuple[bool, bool, bool, bool, bool],
) -> None:
    with copier_case(**answers) as case:
        selected = (
            case.context["codex_cloud"],
            case.context["codex_devcontainer"],
            case.context["codex_include_agents"],
            case.context["codex_include_setup"],
            case.context["codex_include_maintenance"],
        )

    assert selected == expected


def test_codex_cloud_scripts(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["codex", "gitlab", "python"],
        core_repository_url="https://gitlab.example.com/group/repository.git",
    ) as case:
        setup = case.render(PATH_SETUP)
        maintenance = case.render(PATH_MAINTENANCE)

    for script in (setup, maintenance):
        assert script.startswith("#!/usr/bin/env bash\n")
        assert "set -euo pipefail" in script
        assert 'readonly GITLAB_HOST="gitlab.example.com"' in script
        assert "python -m pip install --editable . --group dev" in script
        assert "{{" not in script
        assert "{%" not in script

    assert "GITLAB_TOKEN" in setup
    assert "glab auth login" in setup
    assert "glab auth status" in maintenance


def test_codex_agent_instructions(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["codex"]) as case:
        codex_only = case.render(PATH_AGENTS)
    with copier_case(features=["codex", "gitlab"]) as case:
        with_gitlab = case.render(PATH_AGENTS)

    assert "## General guidelines" in codex_only
    assert "## GitLab development workflow" not in codex_only
    assert "## GitLab development workflow" in with_gitlab
    assert "## Safety and boundaries" in with_gitlab


def test_codex_devcontainer_integration(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["codex", "devcontainer", "python"]) as case:
        rendered = case.render(PATH_DEVCONTAINER_CONFIG)

    config = json.loads(rendered)

    assert "ghcr.io/dirien/devcontainer-feature-codex/codex:0" in config["features"]
    assert config["mounts"] == [
        "source=codex-config-${devcontainerId},target=/home/vscode/.codex,type=volume"
    ]
    assert "setupCodex" in config["postCreateCommand"]
    assert "setupPython" in config["postCreateCommand"]
    assert "openai.chatgpt" in config["customizations"]["vscode"]["extensions"]
