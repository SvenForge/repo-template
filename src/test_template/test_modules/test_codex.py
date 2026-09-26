"""Smoke checks for Codex output and each of its templates."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, json_items, json_members, module_context

OUTPUT_CASES = {
    'cloud': ModuleCase(
        expected={
            'vars': {'cloud_integration': True},
            'files': [
                {'path': 'AGENTS.md', 'template': 'files/AGENTS.md.jinja'},
                {'path': '.codex/setup.sh', 'template': 'files/setup.sh.jinja'},
                {'path': '.codex/maintenance.sh', 'template': 'files/maintenance.sh.jinja'},
            ],
            'contributions': [],
        },
    ),
    'devcontainer': ModuleCase(
        inputs={'devcontainer_available': True},
        answers={'codex_cloud': False},
        expected={
            'vars': {'cloud_integration': False, 'devcontainer_integration': True},
            'files': [{'path': 'AGENTS.md', 'template': 'files/AGENTS.md.jinja'}],
            'contributions': [
                {'target': 'devcontainer.features', 'template': 'fragments/devcontainer.features.json.jinja'},
                {'target': 'devcontainer.mounts', 'template': 'fragments/devcontainer.mounts.json.jinja'},
                {'target': 'devcontainer.extensions', 'template': 'fragments/devcontainer.extensions.json.jinja'},
                {'target': 'devcontainer.postCreateCommand', 'template': 'fragments/devcontainer.postCreateCommand.json.jinja'},
            ],
        },
    ),
}
CODEX_CONTEXT = module_context('codex')


@pytest.mark.parametrize('case', OUTPUT_CASES.values(), ids=OUTPUT_CASES.keys())
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('codex', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=CODEX_CONTEXT, contains=('## General guidelines', '## Safety and boundaries', 'Do not edit or publish any secrets')), id='agent-instructions'),
    ],
)
def test_agents(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/files/AGENTS.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=CODEX_CONTEXT, contains=('#!/usr/bin/env bash', 'set -euo pipefail', 'bash .codex/setup.sh')), id='cloud-setup'),
    ],
)
def test_setup(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/files/setup.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=CODEX_CONTEXT, contains=('#!/usr/bin/env bash', 'set -euo pipefail', 'bash .codex/maintenance.sh')), id='cloud-maintenance'),
    ],
)
def test_maintenance(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/files/maintenance.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_members, expected={'ghcr.io/dirien/devcontainer-feature-codex/codex:0': {}}), id='codex-cli'),
    ],
)
def test_features(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/fragments/devcontainer.features.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_items, expected=['openai.chatgpt']), id='codex-extension'),
    ],
)
def test_extensions(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/fragments/devcontainer.extensions.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_items, contains=('target=/home/vscode/.codex', 'type=volume')), id='persistent-configuration'),
    ],
)
def test_mounts(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/fragments/devcontainer.mounts.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_members, contains=('"setupCodex"', 'chmod 700')), id='configuration-permissions'),
    ],
)
def test_post_create_command(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/codex/fragments/devcontainer.postCreateCommand.json.jinja', case)
