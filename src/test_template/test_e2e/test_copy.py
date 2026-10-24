"""Check representative complete projects through the Copier CLI."""

import subprocess
from pathlib import Path

import pytest

from ..support import TemplateCase


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            TemplateCase(
                answers={},
                expected={
                    '.copier-answers.yml': ('features:', "core_repository_url: ''"),
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
                answers={
                    'features': '[core, copier, python, sphinx, gitlab, codex, claude, devcontainer]',
                    'core_repository_name': 'Widget',
                    'core_repository_url': 'https://gitlab.com/example/widget.git',
                    'core_development_repository_url': 'https://gitlab.example.com/team/widget',
                    'python_package_name': 'acme_widget',
                    'sphinx_needs': 'true',
                },
                expected={
                    '.codex/maintenance.sh': ('glab auth status', "GITLAB_HOST='gitlab.example.com'"),
                    '.codex/setup.sh': ('glab auth login', 'python -m pip install --editable . --group dev', "GITLAB_HOST='gitlab.example.com'"),
                    '.copier-answers.yml': ('python_package_name: acme_widget', 'core_development_repository_url: https://gitlab.example.com/team/widget'),
                    '.devcontainer/devcontainer.json': ('openai.chatgpt', 'claude-code:1.0', '"setupCodex"', '"setupPython"', '"setupClaude"', 'CLAUDE_CONFIG_DIR'),
                    '.gitignore': ('CLAUDE.local.md', '.claude/settings.local.json'),
                    '.gitlab-ci.yml': (),
                    '.gitlab/ci/copier.yml': (),
                    '.gitlab/ci/demo.yml': (),
                    '.gitlab/ci/python.yml': (),
                    '.gitlab/ci/sphinx.yml': ('sphinx:pages:',),
                    '.gitlab/issue_templates/default.md': (),
                    '.gitlab/merge_request_templates/default.md': (),
                    'AGENTS.md': ('## GitLab development workflow', '[gitlab.example.com/team/widget](https://gitlab.example.com/team/widget)'),
                    'CLAUDE.md': ('@AGENTS.md',),
                    'LICENSE.md': (),
                    'README.md': ('# [Widget](https://gitlab.com/example/widget.git)', '[GitLab Pages](https://example.gitlab.io/widget/)', '[development repository](https://gitlab.example.com/team/widget)'),
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
