"""Smoke checks for Copier output and each of its templates."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, module_context


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'vars': {'enabled': True, 'version': '9.17.2', 'module_name': 'custom'},
                    'files': [
                        {'path': 'copier.yml', 'template': 'files/copier.yml.jinja'},
                        {'path': 'template/{% yield file from files %}{{ file.path }}{% endyield %}.jinja', 'template': 'files/yield.jinja'},
                        {'path': 'template/{{ _copier_conf.answers_file }}.jinja', 'template': 'files/answers.jinja'},
                        {'path': 'modules/custom/copier.yml', 'template': 'files/module.yml.jinja'},
                        {'path': 'modules/custom/exports.jinja', 'template': 'files/exports.jinja'},
                    ],
                    'contributions': [],
                },
            ),
            id='defaults',
        ),
        pytest.param(ModuleCase(inputs={'version': '9.18.0', 'module_name': 'example'}, expected={'vars': {'version': '9.18.0', 'module_name': 'example'}}), id='inputs'),
        pytest.param(
            ModuleCase(inputs={'module_name': 'example'}, answers={'copier_module_name': ''}, expected={'vars': {'module_name': ''}}),
            id='empty-answer-overrides-input',
        ),
        pytest.param(ModuleCase(inputs={'module_name': ''}, expected={'vars': {'module_name': ''}}), id='empty-input'),
        pytest.param(ModuleCase(inputs={'enabled': False}, expected={'vars': {'enabled': False}}), id='disabled'),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('copier', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=module_context('copier', version='9.17.2', module_name='example'),
                contains=(
                    '_min_copier_version: &min_copier_version "9.17.2"',
                    '_subdirectory: template',
                    '!include modules/example/copier.yml',
                    "enabled: {{ 'example' in features }}",
                    "{%- from module_path ~ '/exports.jinja' import output with context -%}",
                    '{{ result.contributions | to_json }}',
                ),
            ),
            id='named-module',
        ),
        pytest.param(
            RenderCase(
                context=module_context('copier', version='9.18.0', module_name=''),
                contains=('_min_copier_version: &min_copier_version "9.18.0"', 'choices: {}', 'default: []', '{{ result.files | to_json }}'),
            ),
            id='no-module',
        ),
    ],
)
def test_copier_config(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/copier.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=module_context('copier', module_name='example'),
                contains=('example_defaults:', 'example_inputs:', 'example:', '{%- set vars = dict(example_defaults, **example_inputs) -%}', 'vars: {{ vars | to_json }}'),
            ),
            id='named-module',
        ),
    ],
)
def test_module_config(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/module.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [pytest.param(RenderCase(context=module_context('copier', module_name='example'), contains=('{% set output = example %}',)), id='named-module')],
)
def test_exports(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/exports.jinja', case)


@pytest.mark.parametrize('case', [pytest.param(RenderCase(contains=('{% include file.template %}',)), id='inner-file')])
def test_yield(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/yield.jinja', case)


@pytest.mark.parametrize('case', [pytest.param(RenderCase(contains=('{{ _copier_answers|to_nice_yaml -}}',)), id='inner-answers')])
def test_answers(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/copier/files/answers.jinja', case)
