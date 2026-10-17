"""Smoke checks for the shared Python project file and installation support."""

import tomllib

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, json_members, module_context

DEVELOPMENT_CONTEXT = module_context('pyproject', has_distribution=False, has_dev_dependencies=True)
DISTRIBUTION_CONTEXT = module_context('pyproject', has_distribution=True, has_dev_dependencies=True)
SPHINX_CONTEXT = {
    **DEVELOPMENT_CONTEXT,
    'sphinx': {'vars': {'needs': False}},
    'contributions': [{'target': 'pyproject.dev_dependencies', 'template': 'modules/sphinx/fragments/dev_dependencies.toml.jinja'}],
}


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(expected={'files': [{'path': 'pyproject.toml', 'template': 'files/pyproject.toml.jinja'}], 'contributions': []}),
            id='file-only',
        ),
        pytest.param(
            ModuleCase(
                inputs={'has_dev_dependencies': True},
                expected={
                    'vars': {'has_dev_dependencies': True, 'has_distribution': False, 'python_version': '3.12'},
                    'contributions': [
                        {'target': 'codex.setup', 'template': 'fragments/setup.sh.jinja'},
                        {'target': 'codex.maintenance', 'template': 'fragments/maintenance.sh.jinja'},
                        {'target': 'devcontainer.postCreateCommand', 'template': 'fragments/devcontainer.postCreateCommand.json.jinja'},
                    ],
                },
            ),
            id='dependencies-and-installation',
        ),
        pytest.param(
            ModuleCase(inputs={'enabled': False, 'has_dev_dependencies': True, 'has_distribution': True}, expected={'files': [], 'contributions': []}),
            id='disabled',
        ),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('pyproject', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(context=SPHINX_CONTEXT, parse=tomllib.loads, expected={'dependency-groups': {'dev': ['furo', 'myst-parser', 'sphinx>=8.2']}}),
            id='sphinx-without-python',
        ),
        pytest.param(
            RenderCase(
                context={
                    **SPHINX_CONTEXT,
                    'sphinx': {'vars': {'needs': True}},
                    'python': {'vars': {'has_distribution': False, 'tools': ['ruff']}},
                    'contributions': [
                        {'target': 'pyproject.sections', 'template': 'modules/python/fragments/pyproject.toml.jinja'},
                        {'target': 'pyproject.dev_dependencies', 'template': 'modules/python/fragments/dev_dependencies.toml.jinja'},
                        *SPHINX_CONTEXT['contributions'],
                    ],
                },
                parse=tomllib.loads,
                expected={
                    'tool': {'ruff': {'src': ['src']}},
                    'dependency-groups': {'dev': ['ruff', 'furo', 'myst-parser', 'sphinx>=8.2', 'sphinx-needs']},
                },
            ),
            id='python-and-sphinx-contributions',
        ),
    ],
)
def test_pyproject(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/files/pyproject.toml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(context=DISTRIBUTION_CONTEXT, macro='install_commands', contains=('python -m pip install --upgrade pip', 'python -m pip install --editable . --group dev')),
            id='distribution-and-tools',
        ),
        pytest.param(RenderCase(context=DEVELOPMENT_CONTEXT, macro='install_commands', contains=('python -m pip install --group dev',)), id='dependencies-only'),
        pytest.param(
            RenderCase(context=module_context('pyproject', has_distribution=True, has_dev_dependencies=False), macro='install_commands', contains=('python -m pip install --editable .',)),
            id='distribution-only',
        ),
    ],
)
def test_install_helper(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/fragments/install.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=DISTRIBUTION_CONTEXT, contains=('python -m pip install --editable . --group dev',)), id='distribution-and-tools'),
        pytest.param(RenderCase(context=DEVELOPMENT_CONTEXT, contains=('python -m pip install --group dev',)), id='dependencies-only'),
    ],
)
def test_setup(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/fragments/setup.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=DEVELOPMENT_CONTEXT, contains=('python -m pip install --group dev',)), id='dependencies-only'),
    ],
)
def test_maintenance(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/fragments/maintenance.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=DEVELOPMENT_CONTEXT, parse=json_members, contains=('"setupPython"', 'python -m pip install --group dev')), id='dependencies-only'),
    ],
)
def test_post_create_command(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/fragments/devcontainer.postCreateCommand.json.jinja', case)
