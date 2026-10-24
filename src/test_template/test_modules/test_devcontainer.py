"""Smoke checks for Dev Container output and each of its templates."""

import json

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, json_items, module_context

CONTAINER_CONTEXT = module_context('devcontainer', image='example.com/development:1')
CONTAINER_CONTEXT['contributions'] = [{'target': 'devcontainer.extensions', 'template': 'modules/devcontainer/fragments/devcontainer.extensions.json.jinja'}]


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'vars': {'image': 'mcr.microsoft.com/devcontainers/base:2-bookworm'},
                    'files': [{'path': '.devcontainer/devcontainer.json', 'template': 'files/devcontainer.json.jinja'}],
                    'contributions': [{'target': 'devcontainer.extensions', 'template': 'fragments/devcontainer.extensions.json.jinja'}],
                },
            ),
            id='defaults',
        ),
        pytest.param(ModuleCase(inputs={'image': 'example.com/development:1'}, expected={'vars': {'image': 'example.com/development:1'}}), id='custom-image'),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('devcontainer', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context={
                    **CONTAINER_CONTEXT,
                    'contributions': [
                        *CONTAINER_CONTEXT['contributions'],
                        {'target': 'devcontainer.features', 'template': 'modules/codex/fragments/devcontainer.features.json.jinja'},
                        {'target': 'devcontainer.features', 'template': 'modules/claude/fragments/devcontainer.features.json.jinja'},
                        {'target': 'devcontainer.mounts', 'template': 'modules/claude/fragments/devcontainer.mounts.json.jinja'},
                        {'target': 'devcontainer.containerEnv', 'template': 'modules/claude/fragments/devcontainer.containerEnv.json.jinja'},
                    ],
                },
                parse=json.loads,
                expected={
                    'features': {
                        'ghcr.io/devcontainers/features/node:2': {},
                        'ghcr.io/dirien/devcontainer-feature-codex/codex:0': {},
                        'ghcr.io/anthropics/devcontainer-features/claude-code:1.0': {},
                    },
                    'mounts': ['source=claude-config-${devcontainerId},target=/home/vscode/.claude,type=volume'],
                    'containerEnv': {'CLAUDE_CONFIG_DIR': '/home/vscode/.claude'},
                },
            ),
            id='combined-agent-contributions',
        ),
        pytest.param(
            RenderCase(
                context=CONTAINER_CONTEXT,
                parse=json.loads,
                expected={
                    'image': 'example.com/development:1',
                    'remoteUser': 'vscode',
                    'customizations': {'vscode': {'extensions': ['mhutchie.git-graph', 'streetsidesoftware.code-spell-checker']}},
                },
            ),
            id='custom-image-and-extensions',
        ),
    ],
)
def test_devcontainer_config(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/devcontainer/files/devcontainer.json.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=json_items, expected=['mhutchie.git-graph', 'streetsidesoftware.code-spell-checker']), id='editor-extensions'),
    ],
)
def test_extensions(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/devcontainer/fragments/devcontainer.extensions.json.jinja', case)
