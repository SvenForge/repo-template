"""Check representative complete projects through the Copier CLI."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ..support import TEMPLATE_ROOT, TemplateCase


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            TemplateCase(
                answers={},
                expected={
                    '.copier-answers.yml': ('features:',),
                    '.devcontainer/devcontainer.json': ('python -m pip install --group dev',),
                    '.gitignore': (),
                    '.gitlab-ci.yml': (),
                    '.gitlab/ci/copier.yml': (),
                    '.gitlab/ci/demo.yml': (),
                    '.gitlab/ci/python.yml': ('python:pytest:',),
                    '.gitlab/ci/sphinx.yml': (),
                    '.gitlab/issue_templates/default.md': (),
                    '.gitlab/merge_request_templates/default.md': (),
                    'LICENSE.md': (),
                    'README.md': ('# My Repository',),
                    'doc/api.md': ('sphinx/_apidoc/test_my_repository/modules',),
                    'doc/notes.md': (),
                    'doc/sphinx/Makefile': (),
                    'doc/sphinx/conf.py': ("project = 'My Repository'",),
                    'doc/sphinx/index.md': (),
                    'doc/sphinx/make.bat': (),
                    'pyproject.toml': ('[dependency-groups]',),
                    'src/test_my_repository/__init__.py': (),
                    'src/test_my_repository/test_self.py': (),
                },
            ),
            id='defaults',
        ),
        pytest.param(
            TemplateCase(
                answers={'features': '[]'},
                expected={'.copier-answers.yml': ('features: []',)},
            ),
            id='empty-repository',
        ),
        pytest.param(
            TemplateCase(
                answers={'features': '[copier]', 'copier_module_name': ''},
                expected={
                    '.copier-answers.yml': (),
                    'copier.yml': ('module_paths:', 'choices: {}'),
                    'template/{% yield file from files %}{{ file.path }}{% endyield %}.jinja': ('{% include file.template %}',),
                    'template/{{ _copier_conf.answers_file }}.jinja': ('{{ _copier_answers|to_nice_yaml -}}',),
                },
            ),
            id='empty-starter',
        ),
        pytest.param(
            TemplateCase(
                answers={
                    'features': '[core, copier, python, sphinx, gitlab, codex, devcontainer]',
                    'core_repository_name': 'Widget',
                    'core_repository_url': 'https://gitlab.com/example/widget.git',
                    'python_package_name': 'acme_widget',
                    'sphinx_needs': 'true',
                },
                expected={
                    '.codex/maintenance.sh': ('glab auth status',),
                    '.codex/setup.sh': ('glab auth login', 'python -m pip install --editable . --group dev'),
                    '.copier-answers.yml': ('python_package_name: acme_widget',),
                    '.devcontainer/devcontainer.json': ('openai.chatgpt', '"setupCodex"', '"setupPython"'),
                    '.gitignore': (),
                    '.gitlab-ci.yml': (),
                    '.gitlab/ci/copier.yml': (),
                    '.gitlab/ci/demo.yml': (),
                    '.gitlab/ci/python.yml': (),
                    '.gitlab/ci/sphinx.yml': ('sphinx:pages:',),
                    '.gitlab/issue_templates/default.md': (),
                    '.gitlab/merge_request_templates/default.md': (),
                    'AGENTS.md': ('## GitLab development workflow',),
                    'LICENSE.md': (),
                    'README.md': ('# [Widget](https://gitlab.com/example/widget.git)', '[GitLab Pages](https://example.gitlab.io/widget/)'),
                    'copier.yml': ('_subdirectory: template', '!include modules/custom/copier.yml'),
                    'doc/api.md': ('sphinx/_apidoc/acme_widget/modules',),
                    'doc/architecture.md': (),
                    'doc/implementation.md': (),
                    'doc/notes.md': (),
                    'doc/requirements.md': ('{req}',),
                    'doc/sphinx/Makefile': (),
                    'doc/sphinx/conf.py': (),
                    'doc/sphinx/index.md': (),
                    'doc/sphinx/make.bat': (),
                    'doc/verification.md': (),
                    'modules/custom/copier.yml': ('custom_defaults:', 'custom_inputs:', 'files: []', 'contributions: []'),
                    'modules/custom/exports.jinja': ('{% set output = custom %}',),
                    'pyproject.toml': ('name = "acme-widget"', 'sphinx-needs'),
                    'src/acme_widget/__init__.py': ('Widget package.',),
                    'src/test_acme_widget/__init__.py': (),
                    'src/test_acme_widget/test_import.py': ('import acme_widget',),
                    'src/test_acme_widget/test_self.py': (),
                    'template/{% yield file from files %}{{ file.path }}{% endyield %}.jinja': ('{% include file.template %}',),
                    'template/{{ _copier_conf.answers_file }}.jinja': ('{{ _copier_answers|to_nice_yaml -}}',),
                },
            ),
            id='all-modules',
        ),
    ],
)
def test_copy(tmp_path: Path, template_source: Path, case: TemplateCase) -> None:
    destination = tmp_path / 'repository'
    command = ['copier', 'copy', '--defaults', '--quiet', str(template_source), str(destination)]
    for name, value in case.answers.items():
        command.extend(('--data', f'{name}={value}'))
    subprocess.run(command, check=True)

    files = {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()}
    assert files == set(case.expected)

    for path, expected_content in case.expected.items():
        content = (destination / path).read_text()
        for expected in expected_content:
            assert expected in content

    if 'copier.yml' in case.expected:
        inner_destination = tmp_path / 'inner-repository'
        subprocess.run(['copier', 'copy', '--defaults', '--quiet', str(destination), str(inner_destination)], check=True)
        assert {path.relative_to(inner_destination).as_posix() for path in inner_destination.rglob('*') if path.is_file()} == {'.copier-answers.yml'}


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(TemplateCase(answers={'features': '[]'}, expected={'.copier-answers.yml': ('features: []',)}), id='disabled'),
        pytest.param(TemplateCase(answers={'features': '[guidance]'}, expected={'.copier-answers.yml': ('features:\n- guidance\n',), 'AGENTS.md': ()}), id='guidance'),
        pytest.param(
            TemplateCase(
                answers={'features': '[workspace]'},
                expected={
                    '.copier-answers.yml': ('features:\n- workspace\n',),
                    'AGENTS.md': (),
                    '.codex/setup.sh': (),
                    '.codex/maintenance.sh': (),
                    '.devcontainer/devcontainer.json': (),
                },
            ),
            id='workspace',
        ),
        pytest.param(
            TemplateCase(
                answers={'features': '[guidance, workspace]'},
                expected={
                    '.copier-answers.yml': ('features:\n- guidance\n- workspace\n',),
                    'AGENTS.md': (),
                    '.codex/setup.sh': (),
                    '.codex/maintenance.sh': (),
                    '.devcontainer/devcontainer.json': (),
                },
            ),
            id='shared-provider',
        ),
    ],
)
def test_consumer_example(tmp_path: Path, template_source: Path, case: TemplateCase) -> None:
    source = tmp_path / 'consumer'
    shutil.copytree(template_source, source / 'vendor' / 'repo-template')
    shutil.copytree(template_source / 'template', source / 'template')
    guide = (TEMPLATE_ROOT / 'doc' / 'module-guide.md').read_text()
    configuration = guide.split('### Minimal consumer example', 1)[1].split('```yaml\n', 1)[1].split('```', 1)[0]
    (source / 'copier.yml').write_text(configuration)

    destination = tmp_path / 'repository'
    subprocess.run(['copier', 'copy', '--defaults', '--quiet', '--data', f'features={case.answers["features"]}', str(source), str(destination)], check=True)
    assert {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()} == set(case.expected)
    for path, expected_content in case.expected.items():
        content = (destination / path).read_text()
        for expected in expected_content:
            assert expected in content
    assert '\nmodule_paths:' not in (destination / '.copier-answers.yml').read_text()

    if '.devcontainer/devcontainer.json' in case.expected:
        container = json.loads((destination / '.devcontainer' / 'devcontainer.json').read_text())
        extensions = container['customizations']['vscode']['extensions']
        assert extensions.count('openai.chatgpt') == 1
        assert extensions.index('openai.chatgpt') < extensions.index('mhutchie.git-graph')
