from collections.abc import Callable
from contextlib import AbstractContextManager
import json

import pytest

from .conftest import CopierCase


PATH_DEVCONTAINER_CONFIG = "template/{% if devcontainer_include_config %}.devcontainer{% endif %}/devcontainer.json.jinja"


@pytest.mark.parametrize(
    ("features", "expected"),
    [([], False), (["devcontainer"], True)],
    ids=["without-devcontainer", "with-devcontainer"],
)
def test_devcontainer_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    features: list[str],
    expected: bool,
) -> None:
    with copier_case(features=features) as case:
        assert case.context["devcontainer_include_config"] is expected


def test_devcontainer_configuration(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["devcontainer"]) as case:
        rendered = case.render(PATH_DEVCONTAINER_CONFIG)

    config = json.loads(rendered)

    assert config["image"] == "mcr.microsoft.com/devcontainers/base:2-bookworm"
    assert config["features"] == {}
    assert config["remoteUser"] == "vscode"
    assert config["mounts"] == []
    assert config["postCreateCommand"] == {}

    vscode = config["customizations"]["vscode"]
    assert vscode["extensions"] == [
        "mhutchie.git-graph",
        "Gruntfuggly.todo-tree",
        "mutantdino.resourcemonitor",
        "streetsidesoftware.code-spell-checker",
    ]
    assert vscode["settings"] == {
        "telemetry.telemetryLevel": "off",
        "workbench.enableExperiments": False,
        "telemetry.feedback.enabled": False,
        "terminal.integrated.defaultProfile.linux": "bash",
    }

    assert "openai.chatgpt" not in rendered
    assert "env/dev/requirements.txt" not in rendered
    assert "setupCodex" not in rendered
    assert "setupPython" not in rendered
    assert "{{" not in rendered
    assert "{%" not in rendered
