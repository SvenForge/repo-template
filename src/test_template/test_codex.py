from collections.abc import Callable
from contextlib import AbstractContextManager
import json
import subprocess
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
        features=["codex", "gitlab"],
        core_repository_url="https://gitlab.example.com/group/repository.git",
    ) as case:
        setup = case.render(PATH_SETUP)
        maintenance = case.render(PATH_MAINTENANCE)

    for script in (setup, maintenance):
        subprocess.run(["bash", "-n"], input=script, text=True, check=True)
        assert script.startswith("#!/usr/bin/env bash\n")
        assert "set -euo pipefail" in script
        assert 'readonly GITLAB_HOST="gitlab.example.com"' in script
        assert "env/dev/constraints.txt" not in script
        assert "{{" not in script
        assert "{%" not in script

    assert "GITLAB_TOKEN" in setup
    assert "glab auth login" in setup
    assert "glab auth status" in maintenance


def test_python_codex_cloud_scripts(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["codex", "python"]) as case:
        without_gitlab = (case.render(PATH_SETUP), case.render(PATH_MAINTENANCE))
    with copier_case(features=["codex", "gitlab", "python"]) as case:
        with_gitlab = (case.render(PATH_SETUP), case.render(PATH_MAINTENANCE))

    install_commands = [
        "python -m pip install --constraint env/dev/constraints.txt --upgrade pip",
        "python -m pip install --constraint env/dev/constraints.txt --editable . --group dev",
    ]
    for script in (*without_gitlab, *with_gitlab):
        subprocess.run(["bash", "-n"], input=script, text=True, check=True)
        for command in install_commands:
            assert script.count(command) == 1
        assert script.index(install_commands[0]) < script.index(install_commands[1])
        assert "{{" not in script
        assert "{%" not in script

    for script in without_gitlab:
        assert "GITLAB_HOST" not in script
    for script in with_gitlab:
        assert script.index(install_commands[1]) < script.index("GITLAB_HOST")


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
    with copier_case(
        features=["codex", "devcontainer", "python"],
        python_version="3.13",
    ) as case:
        rendered = case.render(PATH_DEVCONTAINER_CONFIG)

    config = json.loads(rendered)

    assert "ghcr.io/dirien/devcontainer-feature-codex/codex:0" in config["features"]
    assert config["mounts"] == [
        "source=codex-config-${devcontainerId},target=/home/vscode/.codex,type=volume"
    ]
    assert set(config["postCreateCommand"]) == {"setupCodex", "setupPython"}
    assert config["image"] == "mcr.microsoft.com/devcontainers/python:3-3.13-bookworm"
    assert "openai.chatgpt" in config["customizations"]["vscode"]["extensions"]
    assert "{{" not in rendered
    assert "{%" not in rendered
