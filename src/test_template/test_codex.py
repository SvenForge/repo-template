from collections.abc import Callable
from contextlib import AbstractContextManager
import json
import os
from pathlib import Path
import subprocess

import pytest

from .conftest import CopierCase


PATH_AGENTS = "template/{% if codex_include_config %}AGENTS.md{% endif %}.jinja"
PATH_SETUP = "template/{% if codex_include_config %}.codex{% endif %}/setup.sh.jinja"
PATH_MAINTENANCE = "template/{% if codex_include_config %}.codex{% endif %}/maintenance.sh.jinja"
PATH_DEVCONTAINER_CONFIG = "template/{% if devcontainer_include_config %}.devcontainer{% endif %}/devcontainer.json.jinja"
PATH_DEVCONTAINER_LOCK = "template/{% if codex_include_devcontainer %}.devcontainer{% endif %}/devcontainer-lock.json"


@pytest.mark.parametrize(
    ("features", "expected"),
    [
        ([], (False, False)),
        (["codex"], (True, False)),
        (["codex", "devcontainer"], (True, True)),
    ],
    ids=["without-codex", "codex-only", "with-devcontainer"],
)
def test_codex_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    features: list[str],
    expected: tuple[bool, bool],
) -> None:
    with copier_case(features=features) as case:
        selected = (
            case.context["codex_include_config"],
            case.context["codex_include_devcontainer"],
        )

    assert selected == expected


def test_codex_script_composition(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    rendered: dict[str, tuple[str, str]] = {}
    combinations = {
        "codex": ["codex"],
        "copier": ["codex", "copier"],
        "gitlab": ["codex", "gitlab"],
        "combined": ["codex", "copier", "gitlab"],
    }
    for name, features in combinations.items():
        with copier_case(features=features) as case:
            rendered[name] = (
                case.render(PATH_SETUP),
                case.render(PATH_MAINTENANCE),
            )

    codex_setup, codex_maintenance = rendered["codex"]
    copier_setup, copier_maintenance = rendered["copier"]
    gitlab_setup, gitlab_maintenance = rendered["gitlab"]
    combined_setup, combined_maintenance = rendered["combined"]

    for setup, maintenance in rendered.values():
        assert setup.startswith("#!/usr/bin/env bash\n")
        assert maintenance.startswith("#!/usr/bin/env bash\n")
        assert "set -euo pipefail" in setup
        assert "set -euo pipefail" in maintenance
        assert "env/dev/requirements.txt" not in setup
        assert "env/dev/requirements.txt" not in maintenance
        assert "{{" not in setup
        assert "{%" not in setup
        assert "{{" not in maintenance
        assert "{%" not in maintenance

    assert "copier==" not in codex_setup
    assert "copier==" not in codex_maintenance
    assert "GITLAB_TOKEN" not in codex_setup
    assert "glab auth status" not in codex_maintenance

    assert 'python -m pip install "copier==9.17.2"' in copier_setup
    assert 'python -m pip install "copier==9.17.2"' in copier_maintenance
    assert "GITLAB_TOKEN" not in copier_setup
    assert "glab auth status" not in copier_maintenance

    assert "copier==" not in gitlab_setup
    assert "copier==" not in gitlab_maintenance
    assert 'readonly GLAB_VERSION="1.113.0"' in gitlab_setup
    assert "glab auth login" in gitlab_setup
    assert "GITLAB_TOKEN" in gitlab_setup
    assert "GITLAB_TOKEN" not in gitlab_maintenance
    assert "glab auth status" in gitlab_maintenance

    token_guard = ': "${GITLAB_TOKEN:?GITLAB_TOKEN must be provided as a Codex Cloud Environment Secret.}"'
    assert combined_setup.index("copier==9.17.2") < combined_setup.index(token_guard)
    assert combined_maintenance.index("copier==9.17.2") < combined_maintenance.index("glab auth status")


@pytest.mark.parametrize(
    "features",
    [
        ["codex"],
        ["codex", "copier"],
        ["codex", "gitlab"],
        ["codex", "copier", "gitlab"],
    ],
    ids=["codex", "copier", "gitlab", "combined"],
)
def test_codex_scripts_are_valid_bash(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    tmp_path: Path,
    features: list[str],
) -> None:
    with copier_case(features=features) as case:
        scripts = {
            "setup.sh": case.render(PATH_SETUP),
            "maintenance.sh": case.render(PATH_MAINTENANCE),
        }

    for name, content in scripts.items():
        path = tmp_path / name
        path.write_text(content)
        subprocess.run(["bash", "-n", path], check=True)


def test_codex_setup_requires_gitlab_secret(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    tmp_path: Path,
) -> None:
    with copier_case(features=["codex", "gitlab"]) as case:
        setup = case.render(PATH_SETUP)

    path = tmp_path / "setup.sh"
    path.write_text(setup)
    environment = os.environ.copy()
    for name in ("GITLAB_TOKEN", "GITLAB_ACCESS_TOKEN", "OAUTH_TOKEN"):
        environment.pop(name, None)

    result = subprocess.run(
        ["bash", path],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )

    assert result.returncode != 0
    assert "GITLAB_TOKEN must be provided as a Codex Cloud Environment Secret." in result.stderr


def test_codex_agent_instructions(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["codex"]) as case:
        codex_only = case.render(PATH_AGENTS)
    with copier_case(features=["codex", "gitlab"]) as case:
        with_gitlab = case.render(PATH_AGENTS)

    for agents in (codex_only, with_gitlab):
        assert agents.startswith("# AGENTS.md\n")
        assert "## General guidelines" in agents
        assert "## Safety and boundaries" in agents
        assert "{{" not in agents
        assert "{%" not in agents

    assert "## GitLab development workflow" not in codex_only
    assert "## GitLab development workflow" in with_gitlab


def test_codex_devcontainer_integration(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["codex", "devcontainer"]) as case:
        rendered_config = case.render(PATH_DEVCONTAINER_CONFIG)
        rendered_lock = case.render(PATH_DEVCONTAINER_LOCK)

    config = json.loads(rendered_config)
    lock = json.loads(rendered_lock)

    assert config["features"] == {
        "ghcr.io/devcontainers/features/node:2": {},
        "ghcr.io/dirien/devcontainer-feature-codex/codex:0": {},
    }
    assert config["mounts"] == [
        "source=codex-config-${devcontainerId},target=/home/vscode/.codex,type=volume"
    ]
    setup_codex = config["postCreateCommand"]["setupCodex"]
    assert 'sudo chown -R "$(id -u):$(id -g)" "$config_dir"' in setup_codex
    assert 'chmod 700 "$config_dir"' in setup_codex
    assert "analytics" not in setup_codex

    extensions = config["customizations"]["vscode"]["extensions"]
    assert extensions == [
        "openai.chatgpt",
        "mhutchie.git-graph",
        "Gruntfuggly.todo-tree",
        "mutantdino.resourcemonitor",
        "streetsidesoftware.code-spell-checker",
    ]

    assert set(lock["features"]) == set(config["features"])
    assert lock["features"]["ghcr.io/devcontainers/features/node:2"]["version"] == "2.1.0"
    assert lock["features"]["ghcr.io/dirien/devcontainer-feature-codex/codex:0"]["version"] == "0.0.1"
    for feature in lock["features"].values():
        assert feature["resolved"].endswith(feature["integrity"])

    assert "{{" not in rendered_config
    assert "{%" not in rendered_config
