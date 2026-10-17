"""Smoke checks for host wiring and aggregated template output variables."""

import pytest

from ..support import VariableCase, VariablesCheck


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            VariableCase(
                expected={
                    'files': [
                        {'path': 'README.md', 'template': 'modules/core/files/README.md.jinja'},
                        {'path': '.devcontainer/devcontainer.json', 'template': 'modules/devcontainer/files/devcontainer.json.jinja'},
                        {'path': 'pyproject.toml', 'template': 'modules/pyproject/files/pyproject.toml.jinja'},
                        {'path': 'doc/api.md', 'template': 'modules/sphinx/files/api.md.jinja'},
                    ],
                    'contributions': [
                        {'target': 'core.gitignore', 'template': 'modules/python/fragments/gitignore.jinja'},
                        {'target': 'pyproject.dev_dependencies', 'template': 'modules/sphinx/fragments/dev_dependencies.toml.jinja'},
                        {'target': 'devcontainer.postCreateCommand', 'template': 'modules/pyproject/fragments/devcontainer.postCreateCommand.json.jinja'},
                    ],
                    'devcontainer': {'vars': {'image': 'mcr.microsoft.com/devcontainers/python:3-3.12-bookworm'}},
                    'sphinx': {'vars': {'api_packages': ['test_my_repository']}},
                    'gitlab': {'vars': {'pipeline': ['python', 'sphinx']}},
                },
            ),
            id='defaults',
        ),
        pytest.param(
            VariableCase(
                answers={'features': ['core', 'sphinx', 'gitlab']},
                expected={
                    'python': {'vars': {'enabled': False}, 'files': [], 'contributions': []},
                    'pyproject': {'vars': {'enabled': True, 'install': 'dependencies', 'name': 'my-repository'}},
                    'files': [{'path': 'pyproject.toml', 'template': 'modules/pyproject/files/pyproject.toml.jinja'}],
                    'gitlab': {'vars': {'python_enabled': False, 'has_python_distribution': False, 'pipeline': ['sphinx']}},
                },
            ),
            id='sphinx-without-python',
        ),
        pytest.param(
            VariableCase(
                answers={
                    'features': ['core', 'sphinx', 'gitlab', 'codex', 'devcontainer'],
                    'sphinx_needs': True,
                    'python_package_name': 'previous_package',
                    'python_tools': ['pytest', 'ruff', 'mypy'],
                    'python_version': '3.13',
                },
                expected={
                    'python': {'vars': {'enabled': False}, 'files': [], 'contributions': []},
                    'pyproject': {'vars': {'install': 'dependencies', 'python_version': '3.13'}},
                    'sphinx': {'vars': {'needs': True, 'api_packages': []}},
                    'devcontainer': {'vars': {'image': 'mcr.microsoft.com/devcontainers/python:3-3.13-bookworm'}},
                    'contributions': [
                        {'target': 'codex.setup', 'template': 'modules/pyproject/fragments/setup.sh.jinja'},
                        {'target': 'codex.maintenance', 'template': 'modules/pyproject/fragments/setup.sh.jinja'},
                        {'target': 'devcontainer.postCreateCommand', 'template': 'modules/pyproject/fragments/devcontainer.postCreateCommand.json.jinja'},
                    ],
                    'gitlab': {'vars': {'python_enabled': False, 'has_python_distribution': False}},
                },
            ),
            id='sphinx-integrations-with-previous-python-answers',
        ),
        pytest.param(
            VariableCase(
                answers={'features': ['python'], 'python_package_name': 'widget', 'python_tools': []},
                expected={
                    'pyproject': {'vars': {'name': 'widget', 'version': '', 'install': 'editable'}},
                    'sphinx': {'files': [], 'contributions': []},
                    'files': [{'path': 'pyproject.toml', 'template': 'modules/pyproject/files/pyproject.toml.jinja'}],
                },
            ),
            id='python-distribution-without-sphinx-or-tools',
        ),
        pytest.param(
            VariableCase(
                answers={'features': ['core']},
                expected={
                    'files': [
                        {'path': 'README.md', 'template': 'modules/core/files/README.md.jinja'},
                        {'path': '.gitignore', 'template': 'modules/core/files/gitignore.jinja'},
                    ],
                    'contributions': [{'target': 'core.gitignore', 'template': 'modules/core/fragments/gitignore.jinja'}],
                },
            ),
            id='core-only',
        ),
        pytest.param(
            VariableCase(
                answers={'features': []},
                expected={'files': [], 'contributions': [], 'pyproject': {'vars': {'enabled': False}, 'files': [], 'contributions': []}},
            ),
            id='disabled-modules',
        ),
        pytest.param(
            VariableCase(
                answers={
                    'features': ['gitlab', 'devcontainer'],
                    'codex_inputs': {'enabled': True, 'cloud_integration': False, 'devcontainer_available': True},
                },
                expected={
                    'files': [{'path': 'AGENTS.md', 'template': 'modules/codex/files/AGENTS.md.jinja'}],
                    'contributions': [{'target': 'devcontainer.features', 'template': 'modules/codex/fragments/devcontainer.features.json.jinja'}],
                    'codex': {'vars': {'enabled': True, 'cloud_integration': False, 'devcontainer_integration': True}},
                },
            ),
            id='unselected-provider',
        ),
        pytest.param(
            VariableCase(
                answers={
                    'features': ['core', 'copier', 'python', 'sphinx', 'gitlab', 'codex', 'devcontainer'],
                    'core_repository_name': 'Widget',
                    'core_repository_url': 'https://gitlab.com/example/widget.git',
                    'python_package_name': 'acme_widget',
                    'python_version': '3.13',
                    'sphinx_needs': True,
                },
                expected={
                    'files': [
                        {'path': 'copier.yml', 'template': 'modules/copier/files/copier.yml.jinja'},
                        {'path': 'src/acme_widget/__init__.py', 'template': 'modules/python/files/package/__init__.py.jinja'},
                        {'path': 'doc/requirements.md', 'template': 'modules/sphinx/files/requirements.md.jinja'},
                        {'path': '.gitlab/ci/sphinx.yml', 'template': 'modules/gitlab/files/ci/sphinx.yml.jinja'},
                        {'path': 'AGENTS.md', 'template': 'modules/codex/files/AGENTS.md.jinja'},
                    ],
                    'contributions': [
                        {'target': 'core.readme.documentation', 'template': 'modules/gitlab/fragments/readme.documentation.md.jinja'},
                        {'target': 'devcontainer.features', 'template': 'modules/codex/fragments/devcontainer.features.json.jinja'},
                        {'target': 'codex.setup', 'template': 'modules/pyproject/fragments/setup.sh.jinja'},
                    ],
                    'python': {'vars': {'distribution_name': 'acme-widget', 'has_distribution': True}},
                    'devcontainer': {'vars': {'image': 'mcr.microsoft.com/devcontainers/python:3-3.13-bookworm'}},
                    'gitlab': {'vars': {'pages_url': 'https://example.gitlab.io/widget/', 'has_python_distribution': True}},
                    'sphinx': {'vars': {'repository_name': 'Widget', 'api_packages': ['acme_widget', 'test_acme_widget']}},
                    'codex': {'vars': {'devcontainer_integration': True}},
                },
            ),
            id='all-modules',
        ),
    ],
)
def test_variables(check_variables: VariablesCheck, case: VariableCase) -> None:
    check_variables(case)
