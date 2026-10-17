"""Smoke checks for Python output and each of its templates."""

import ast
import tomllib

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, module_context, toml_items

PYTHON_VARIABLES = {
    'repository_name': 'Widget',
    'package_name': 'acme_widget',
    'distribution_name': 'acme-widget',
    'testpackage_name': 'test_acme_widget',
    'version': '3.13',
    'tools': ['pytest', 'ruff', 'mypy'],
    'has_distribution': True,
    'has_readme': True,
    'has_license': True,
    'license': 'MIT',
    'owner_name': 'Example Owner',
    'owner_email': 'owner@example.com',
}
PYTHON_CONTEXT = module_context('python', **PYTHON_VARIABLES)
DEVELOPMENT_CONTEXT = module_context('python', **{**PYTHON_VARIABLES, 'has_distribution': False, 'package_name': ''})


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'vars': {'testpackage_name': 'test_my_repository'},
                    'files': [
                        {'path': 'src/test_my_repository/test_self.py', 'template': 'files/testpackage/test_self.py.jinja'},
                    ],
                    'contributions': [
                        {'target': 'core.gitignore', 'template': 'fragments/gitignore.jinja'},
                        {'target': 'pyproject.dev_dependencies', 'template': 'fragments/dev_dependencies.toml.jinja'},
                    ],
                },
            ),
            id='development-tools',
        ),
        pytest.param(
            ModuleCase(
                inputs={'repository_name': 'Widget'},
                answers={'python_package_name': 'acme_widget', 'python_version': '3.13'},
                expected={
                    'vars': {'distribution_name': 'acme-widget', 'has_distribution': True, 'version': '3.13', 'testpackage_name': 'test_acme_widget'},
                    'files': [
                        {'path': 'src/acme_widget/__init__.py', 'template': 'files/package/__init__.py.jinja'},
                        {'path': 'src/test_acme_widget/test_import.py', 'template': 'files/testpackage/test_import.py.jinja'},
                    ],
                    'contributions': [{'target': 'pyproject.sections', 'template': 'fragments/pyproject.toml.jinja'}],
                },
            ),
            id='distribution',
        ),
        pytest.param(
            ModuleCase(
                inputs={'enabled': False},
                answers={'python_package_name': 'previous_package', 'python_tools': ['pytest', 'ruff', 'mypy']},
                expected={'files': [], 'contributions': []},
            ),
            id='disabled-with-previous-answers',
        ),
        pytest.param(
            ModuleCase(
                inputs={'testpackage_name': 'qa_default'},
                answers={'python_testpackage_name': 'qa_widget', 'python_tools': ['pytest']},
                expected={
                    'vars': {'testpackage_name': 'qa_widget', 'tools': ['pytest']},
                    'files': [{'path': 'src/qa_widget/test_self.py', 'template': 'files/testpackage/test_self.py.jinja'}],
                },
            ),
            id='custom-test-package',
        ),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('python', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=PYTHON_CONTEXT,
                parse=tomllib.loads,
                expected={
                    'project': {'name': 'acme-widget', 'requires-python': '>=3.13', 'readme': 'README.md'},
                    'build-system': {'build-backend': 'setuptools.build_meta'},
                },
            ),
            id='distribution',
        ),
        pytest.param(
            RenderCase(
                context=DEVELOPMENT_CONTEXT,
                parse=tomllib.loads,
                expected={
                    'tool': {'pytest': {'ini_options': {'testpaths': ['src/test_*']}}},
                },
            ),
            id='development-only',
        ),
    ],
)
def test_pyproject_sections(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/fragments/pyproject.toml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=PYTHON_CONTEXT, parse=ast.parse, contains=('Widget package.',)), id='package-description'),
    ],
)
def test_package_init(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/files/package/__init__.py.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=ast.parse, contains=('Test package.',)), id='test-package'),
    ],
)
def test_testpackage_init(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/files/testpackage/__init__.py.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=PYTHON_CONTEXT, parse=ast.parse, contains=('import acme_widget', "assert acme_widget.__name__ == 'acme_widget'")), id='package-import'),
    ],
)
def test_import_test(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/files/testpackage/test_import.py.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=ast.parse, contains=('def test_pass()', 'assert True')), id='pytest-starter'),
    ],
)
def test_self_test(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/files/testpackage/test_self.py.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(context=PYTHON_CONTEXT, parse=toml_items, expected=['pytest', 'pytest-cov', 'mypy', 'mypy-gitlab-code-quality', 'ruff']),
            id='development-tools',
        ),
    ],
)
def test_dev_dependencies(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/fragments/dev_dependencies.toml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('__pycache__/', '.venv', '.pytest_cache/')), id='python-artifacts'),
    ],
)
def test_gitignore(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/python/fragments/gitignore.jinja', case)
