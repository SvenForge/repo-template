"""Check representative complete projects through the Copier CLI."""

import subprocess
from pathlib import Path

import pytest

from ..support import TemplateCase

COPY_CASES = {
    'defaults': TemplateCase(
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
    'empty-repository': TemplateCase(
        answers={'features': '[]'},
        expected={'.copier-answers.yml': ('features: []',)},
    ),
    'all-modules': TemplateCase(
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
            'copier.yml': ('!include template/_modules/core/copier.yml',),
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
            'pyproject.toml': ('name = "acme-widget"', 'sphinx-needs'),
            'src/acme_widget/__init__.py': ('Widget package.',),
            'src/test_acme_widget/__init__.py': (),
            'src/test_acme_widget/test_import.py': ('import acme_widget',),
            'src/test_acme_widget/test_self.py': (),
            'template/_modules/core/copier.yml': (),
        },
    ),
}


@pytest.mark.parametrize('case', COPY_CASES.values(), ids=COPY_CASES.keys())
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
