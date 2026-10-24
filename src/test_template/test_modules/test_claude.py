"""Smoke checks for Claude output and its integration fragments."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, json_items, json_members


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'vars': {'devcontainer_integration': False},
                    'files': [{'path': 'CLAUDE.md', 'template': 'files/CLAUDE.md.jinja'}],
                    'contributions': [{'target': 'core.gitignore', 'template': 'fragments/gitignore.jinja'}],
                },
            ),
            id='instructions',
        ),
        pytest.param(
            ModuleCase(
                inputs={'devcontainer_available': True},
                expected={
                    'vars': {'devcontainer_integration': True},
                    'contributions': [
                        {'target': 'devcontainer.features', 'template': 'fragments/devcontainer.features.json.jinja'},
                        {'target': 'devcontainer.mounts', 'template': 'fragments/devcontainer.mounts.json.jinja'},
                        {'target': 'devcontainer.containerEnv', 'template': 'fragments/devcontainer.containerEnv.json.jinja'},
                        {'target': 'devcontainer.postCreateCommand', 'template': 'fragments/devcontainer.postCreateCommand.json.jinja'},
                    ],
                },
            ),
            id='devcontainer',
        ),
        pytest.param(
            ModuleCase(inputs={'devcontainer_available': True}, answers={'claude_devcontainer': False}, expected={'vars': {'devcontainer_integration': False}}),
            id='devcontainer-disabled',
        ),
        pytest.param(ModuleCase(inputs={'enabled': False}, expected={'files': [], 'contributions': []}), id='disabled'),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('claude', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(expected='@AGENTS.md\n'), id='shared-instructions-import'),
    ],
)
def test_claude(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/claude/files/CLAUDE.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_members, expected={'ghcr.io/anthropics/devcontainer-features/claude-code:1.0': {}}), id='official-feature'),
    ],
)
def test_features(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/claude/fragments/devcontainer.features.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_items, contains=('source=claude-config-${devcontainerId}', 'target=/home/vscode/.claude', 'type=volume')), id='persistent-configuration'),
    ],
)
def test_mounts(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/claude/fragments/devcontainer.mounts.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_members, expected={'CLAUDE_CONFIG_DIR': '/home/vscode/.claude'}), id='configuration-directory'),
    ],
)
def test_container_environment(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/claude/fragments/devcontainer.containerEnv.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_members, contains=('"setupClaude"', '$CLAUDE_CONFIG_DIR', 'chmod 700')), id='configuration-permissions'),
    ],
)
def test_post_create_command(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/claude/fragments/devcontainer.postCreateCommand.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('CLAUDE.local.md', '.claude/settings.local.json')), id='local-configuration'),
    ],
)
def test_gitignore(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/claude/fragments/gitignore.jinja', case)
