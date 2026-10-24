"""Smoke checks for Sphinx output and each of its templates."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, module_context, python_assignments, toml_items

SPHINX_VARIABLES = {
    'repository_name': 'Widget',
    'owner_name': 'Example Owner',
    'year': 2026,
    'has_readme': True,
    'has_license': True,
    'api_packages': ['widget', 'test_widget'],
    'needs': True,
}
SPHINX_CONTEXT = module_context('sphinx', **SPHINX_VARIABLES)
MINIMAL_CONTEXT = module_context('sphinx', **{**SPHINX_VARIABLES, 'has_readme': False, 'has_license': False, 'api_packages': [], 'needs': False})


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'vars': {'repository_name': 'My Repository', 'needs': False},
                    'files': [
                        {'path': 'doc/sphinx/conf.py', 'template': 'files/conf.py.jinja'},
                        {'path': 'doc/sphinx/index.md', 'template': 'files/index.md.jinja'},
                        {'path': 'doc/notes.md', 'template': 'files/notes.md.jinja'},
                    ],
                    'contributions': [
                        {'target': 'pyproject.dev_dependencies', 'template': 'fragments/dev_dependencies.toml.jinja'},
                        {'target': 'core.gitignore', 'template': 'fragments/gitignore.jinja'},
                    ],
                },
            ),
            id='defaults',
        ),
        pytest.param(
            ModuleCase(
                inputs={'python_packages': ['widget', 'test_widget'], 'year': 2026},
                answers={'sphinx_api_packages': ['test_widget'], 'sphinx_needs': True},
                expected={
                    'vars': {'api_packages': ['test_widget'], 'needs': True},
                    'files': [
                        {'path': 'doc/api.md', 'template': 'files/api.md.jinja'},
                        {'path': 'doc/requirements.md', 'template': 'files/requirements.md.jinja'},
                        {'path': 'doc/architecture.md', 'template': 'files/architecture.md.jinja'},
                        {'path': 'doc/implementation.md', 'template': 'files/implementation.md.jinja'},
                        {'path': 'doc/verification.md', 'template': 'files/verification.md.jinja'},
                    ],
                },
            ),
            id='test-api-and-needs',
        ),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('sphinx', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=SPHINX_CONTEXT,
                parse=python_assignments,
                expected={
                    'project': 'Widget',
                    'author': 'Example Owner',
                    'extensions': ['myst_parser', 'sphinx.ext.apidoc', 'sphinx_needs'],
                    'apidoc_modules': [
                        {'path': '../../src/widget', 'destination': 'doc/sphinx/_apidoc/widget'},
                        {'path': '../../src/test_widget', 'destination': 'doc/sphinx/_apidoc/test_widget'},
                    ],
                },
            ),
            id='api-and-needs',
        ),
        pytest.param(RenderCase(context=MINIMAL_CONTEXT, parse=python_assignments, expected={'project': 'Widget', 'extensions': ['myst_parser']}), id='minimal'),
    ],
)
def test_conf(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/conf.py.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=SPHINX_CONTEXT, contains=('{include} ../../README.md', 'License <../../LICENSE>', '{toctree}')), id='readme-and-license'),
        pytest.param(RenderCase(context=MINIMAL_CONTEXT, contains=('# Widget', 'Documentation for Widget.', '../*')), id='standalone-index'),
    ],
)
def test_index(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/index.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=SPHINX_CONTEXT, contains=('sphinx/_apidoc/widget/modules', 'sphinx/_apidoc/test_widget/modules')), id='package-api-links'),
    ],
)
def test_api(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/api.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('SOURCEDIR     = ../..', '-c "$(CONFDIR)"', '$(SPHINXBUILD) -M')), id='sphinx-command'),
    ],
)
def test_makefile(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/Makefile.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=(r'SOURCEDIR="..\.."', '-c %CONFDIR%', '%SPHINXBUILD% -M')), id='windows-sphinx-command'),
    ],
)
def test_make_bat(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/make.bat.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('# Notes', 'Add notes or other documentation')), id='starter-notes'),
    ],
)
def test_notes(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/notes.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('{req}', ':id: REQ_001')), id='requirement-starter'),
    ],
)
def test_requirements(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/requirements.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('{spec}', ':id: SPEC_001')), id='specification-starter'),
    ],
)
def test_architecture(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/architecture.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('{impl}', ':id: IMPL_001')), id='implementation-starter'),
    ],
)
def test_implementation(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/implementation.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('{test}', ':id: TEST_001')), id='verification-starter'),
    ],
)
def test_verification(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/files/verification.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=SPHINX_CONTEXT, parse=toml_items, expected=['furo', 'myst-parser', 'sphinx>=8.2', 'sphinx-needs']), id='api-dependencies-and-needs'),
        pytest.param(RenderCase(context=MINIMAL_CONTEXT, parse=toml_items, expected=['furo', 'myst-parser', 'sphinx>=8.2']), id='minimal'),
    ],
)
def test_dev_dependencies(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/fragments/dev_dependencies.toml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('doc/sphinx/_apidoc/', 'doc/sphinx/_build/')), id='generated-documentation'),
    ],
)
def test_gitignore(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/sphinx/fragments/gitignore.jinja', case)
