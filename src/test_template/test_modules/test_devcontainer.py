"""Smoke checks for Dev Container output and each of its templates."""

import json

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, json_items, module_context

OUTPUT_CASES = {
    'defaults': ModuleCase(
        expected={
            'vars': {'image': 'mcr.microsoft.com/devcontainers/base:2-bookworm'},
            'files': [{'path': '.devcontainer/devcontainer.json', 'template': 'files/devcontainer.json.jinja'}],
            'contributions': [{'target': 'devcontainer.extensions', 'template': 'fragments/devcontainer.extensions.json.jinja'}],
        },
    ),
    'custom-image': ModuleCase(inputs={'image': 'example.com/development:1'}, expected={'vars': {'image': 'example.com/development:1'}}),
}
CONTAINER_CONTEXT = module_context('devcontainer', image='example.com/development:1')
CONTAINER_CONTEXT['contributions'] = [{'target': 'devcontainer.extensions', 'template': 'modules/devcontainer/fragments/devcontainer.extensions.json.jinja'}]


@pytest.mark.parametrize('case', OUTPUT_CASES.values(), ids=OUTPUT_CASES.keys())
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('devcontainer', case)


@pytest.mark.parametrize(
    'case',
    [
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
