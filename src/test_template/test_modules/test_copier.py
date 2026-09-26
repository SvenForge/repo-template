"""Smoke checks for Copier output and each of its templates."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, module_context

OUTPUT_CASES = {
    'defaults': ModuleCase(
        expected={
            'vars': {'enabled': True, 'version': '9.17.2'},
            'files': [
                {'path': 'copier.yml', 'template': 'files/copier.yml.jinja'},
                {'path': 'template/_modules/core/copier.yml', 'template': 'files/core.yml.jinja'},
            ],
            'contributions': [],
        },
    ),
    'custom-version': ModuleCase(inputs={'version': '9.18.0'}, expected={'vars': {'version': '9.18.0'}}),
}


@pytest.mark.parametrize('case', OUTPUT_CASES.values(), ids=OUTPUT_CASES.keys())
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('copier', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=module_context('copier', version='9.17.2'),
                contains=('_min_copier_version: &min_copier_version "9.17.2"', '_subdirectory: template', '!include template/_modules/core/copier.yml'),
            ),
            id='starter-template',
        ),
    ],
)
def test_copier_config(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/copier.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        # This starter file intentionally leaves the consumer's Core configuration empty.
        pytest.param(RenderCase(expected=''), id='empty-starter-module'),
    ],
)
def test_core_config(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/core.yml.jinja', case)
