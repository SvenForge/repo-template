"""Smoke checks for the shared Python project file and installation support."""

import tomllib

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, json_members, module_context

PYPROJECT_VARIABLES = {
    'name': 'widget',
    'version': '0.0.0',
    'python_version': '3.13',
    'readme': 'README.md',
    'license': 'MIT',
    'license_files': ['LICENSE.md'],
    'owner_name': 'Example Owner',
    'owner_email': 'owner@example.com',
}
PROJECT_CONTEXT = module_context('pyproject', **PYPROJECT_VARIABLES)
DEVELOPMENT_CONTEXT = {
    **PROJECT_CONTEXT,
    'contributions': [{'target': 'pyproject.dev_dependencies', 'template': 'modules/sphinx/fragments/dev_dependencies.toml.jinja'}],
}
DISTRIBUTION_CONTEXT = {
    **DEVELOPMENT_CONTEXT,
    'contributions': [
        {'target': 'pyproject.build_system', 'template': 'modules/python/fragments/setuptools.toml.jinja'},
        *DEVELOPMENT_CONTEXT['contributions'],
    ],
}
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
                inputs={'install': True},
                answers={'python_version': '3.13'},
                expected={
                    'vars': {'install': True, 'python_version': '3.13'},
                    'contributions': [
                        {'target': 'codex.setup', 'template': 'fragments/setup.sh.jinja'},
                        {'target': 'codex.maintenance', 'template': 'fragments/setup.sh.jinja'},
                        {'target': 'devcontainer.postCreateCommand', 'template': 'fragments/devcontainer.postCreateCommand.json.jinja'},
                    ],
                },
            ),
            id='dependencies-and-installation',
        ),
        pytest.param(
            ModuleCase(inputs={'enabled': False, 'install': True}, expected={'files': [], 'contributions': []}),
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
            RenderCase(context=PROJECT_CONTEXT, parse=tomllib.loads, expected={'project': {'name': 'widget', 'version': '0.0.0', 'requires-python': '>=3.13', 'readme': 'README.md', 'license': 'MIT', 'license-files': ['LICENSE.md'], 'authors': [{'name': 'Example Owner', 'email': 'owner@example.com'}]}}),
            id='project-metadata-without-contributions',
        ),
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
                        {'target': 'pyproject.sections', 'template': 'modules/python/fragments/ruff.toml.jinja'},
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
        pytest.param(RenderCase(context=DISTRIBUTION_CONTEXT, contains=('python -m pip install --editable . --group dev',)), id='distribution-and-tools'),
        pytest.param(RenderCase(context=DEVELOPMENT_CONTEXT, contains=('python -m pip install --group dev',)), id='dependencies-only'),
        pytest.param(
            RenderCase(context={**PROJECT_CONTEXT, 'contributions': [DISTRIBUTION_CONTEXT['contributions'][0]]}, contains=('python -m pip install --editable .',)),
            id='distribution-only',
        ),
    ],
)
def test_setup(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/fragments/setup.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=DEVELOPMENT_CONTEXT, parse=json_members, contains=('"setupPython"', 'python -m pip install --group dev')), id='dependencies-only'),
    ],
)
def test_post_create_command(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/pyproject/fragments/devcontainer.postCreateCommand.json.jinja', case)
