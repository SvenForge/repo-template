"""Check representative complete projects through the Copier CLI."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True)
class CopyCase:
    answers: dict[str, str]
    expected_files: dict[str, tuple[str, ...]]
    answers_only: bool = False


COPY_CASES = {
    'defaults': CopyCase(
        answers={},
        expected_files={
            '.copier-answers.yml': ('features:',),
            'README.md': ('# My Repository',),
            '.devcontainer/devcontainer.json': ('python -m pip install --group dev',),
            '.gitlab/ci/python.yml': ('python:pytest:',),
            'pyproject.toml': ('[dependency-groups]',),
            'doc/sphinx/conf.py': ("project = 'My Repository'",),
            'doc/api.md': ('sphinx/_apidoc/test_my_repository/modules',),
        },
    ),
    'empty-repository': CopyCase(
        answers={'features': '[]'},
        expected_files={'.copier-answers.yml': ('features: []',)},
        answers_only=True,
    ),
    'all-modules': CopyCase(
        answers={
            'features': '[core, copier, python, sphinx, gitlab, codex, devcontainer]',
            'core_repository_name': 'Widget',
            'core_repository_url': 'https://gitlab.com/example/widget.git',
            'python_package_name': 'acme_widget',
            'sphinx_needs': 'true',
        },
        expected_files={
            '.copier-answers.yml': ('python_package_name: acme_widget',),
            'README.md': ('# [Widget](https://gitlab.com/example/widget.git)', '[GitLab Pages](https://example.gitlab.io/widget/)'),
            'copier.yml': ('!include template/_modules/core/copier.yml',),
            'template/_modules/core/copier.yml': (),
            'src/acme_widget/__init__.py': ('Widget package.',),
            'src/test_acme_widget/test_import.py': ('import acme_widget',),
            'pyproject.toml': ('name = "acme-widget"', 'sphinx-needs'),
            'doc/api.md': ('sphinx/_apidoc/acme_widget/modules',),
            'doc/requirements.md': ('{req}',),
            '.gitlab/ci/sphinx.yml': ('sphinx:pages:',),
            'AGENTS.md': ('## GitLab development workflow',),
            '.codex/setup.sh': ('glab auth login', 'python -m pip install --editable . --group dev'),
            '.codex/maintenance.sh': ('glab auth status',),
            '.devcontainer/devcontainer.json': ('openai.chatgpt', '"setupCodex"', '"setupPython"'),
        },
    ),
}


@pytest.mark.parametrize('case', COPY_CASES.values(), ids=COPY_CASES.keys())
def test_copy(tmp_path: Path, template_source: Path, case: CopyCase) -> None:
    destination = tmp_path / 'repository'
    command = ['copier', 'copy', '--defaults', '--quiet', str(template_source), str(destination)]
    for name, value in case.answers.items():
        command.extend(('--data', f'{name}={value}'))
    subprocess.run(command, check=True)

    for path, expected_content in case.expected_files.items():
        content = (destination / path).read_text()
        for expected in expected_content:
            assert expected in content
    if case.answers_only:
        # The empty selection promises an empty repository except for saved answers.
        assert {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()} == {'.copier-answers.yml'}
