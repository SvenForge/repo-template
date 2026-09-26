"""Smoke checks for GitLab output and each of its templates."""

import pytest
import yaml  # type: ignore[import-untyped]

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, module_context

GITLAB_CONTEXT = module_context(
    'gitlab',
    repository_host='gitlab.example.com',
    copier_version='9.17.2',
    python_version='3.13',
    python_tools=['pytest', 'ruff', 'mypy'],
    has_python_distribution=True,
    pages_url='https://group.gitlab.io/widget/',
)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'vars': {'pipeline': ['copier', 'demo']},
                    'files': [
                        {'path': '.gitlab/issue_templates/default.md', 'template': 'files/issue.md.jinja'},
                        {'path': '.gitlab/merge_request_templates/default.md', 'template': 'files/merge_request.md.jinja'},
                        {'path': '.gitlab-ci.yml', 'template': 'files/gitlab-ci.yml.jinja'},
                        {'path': '.gitlab/ci/copier.yml', 'template': 'files/ci/copier.yml.jinja'},
                    ],
                    'contributions': [{'target': 'codex.agents', 'template': 'fragments/AGENTS.md.jinja'}],
                },
            ),
            id='defaults',
        ),
        pytest.param(
            ModuleCase(
                inputs={'python_enabled': True, 'python_tools': ['pytest'], 'sphinx_enabled': True, 'has_readme': True, 'repository_path': 'group/widget'},
                answers={'gitlab_pipeline': ['python', 'sphinx']},
                expected={
                    'vars': {'pipeline': ['python', 'sphinx'], 'pages_url': 'https://group.gitlab.io/widget/'},
                    'files': [
                        {'path': '.gitlab/ci/python.yml', 'template': 'files/ci/python.yml.jinja'},
                        {'path': '.gitlab/ci/sphinx.yml', 'template': 'files/ci/sphinx.yml.jinja'},
                    ],
                    'contributions': [{'target': 'core.readme.documentation', 'template': 'fragments/readme.documentation.md.jinja'}],
                },
            ),
            id='python-and-documentation',
        ),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('gitlab', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=yaml.safe_load, expected={'include': [{'local': '.gitlab/ci/*.yml'}], 'stages': ['test']}), id='included-jobs'),
    ],
)
def test_root_pipeline(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/gitlab-ci.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=GITLAB_CONTEXT,
                parse=yaml.safe_load,
                expected={
                    '.copier:base': {'variables': {'COPIER_VERSION': '9.17.2'}},
                    'copier:check': {'script': ['copier check-update']},
                },
            ),
            id='template-update-check',
        ),
    ],
)
def test_copier_pipeline(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/ci/copier.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(parse=yaml.safe_load, expected={'demo:fortune': {'script': ['fortune | cowsay']}}), id='demo-job'),
    ],
)
def test_demo_pipeline(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/ci/demo.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=GITLAB_CONTEXT,
                parse=yaml.safe_load,
                expected={
                    '.python:base': {'image': 'python:3.13-bookworm'},
                    'python:pytest': {'script': ['pytest'], 'variables': {'PYTHON_DEPENDENCY_GROUP': 'test'}},
                    'python:ruff': {'variables': {'PYTHON_DEPENDENCY_GROUP': 'lint'}},
                    'python:mypy': {'variables': {'PYTHON_DEPENDENCY_GROUP': 'lint'}},
                },
            ),
            id='python-tools',
        ),
    ],
)
def test_python_pipeline(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/ci/python.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=GITLAB_CONTEXT,
                parse=yaml.safe_load,
                expected={
                    'sphinx:build': {'script': ["make -C doc/sphinx html SPHINXOPTS='-W --keep-going'"]},
                    'sphinx:pages': {'pages': {'publish': 'doc/sphinx/_build/html'}, 'needs': [{'job': 'sphinx:build', 'artifacts': True}]},
                },
            ),
            id='documentation-build-and-pages',
        ),
    ],
)
def test_sphinx_pipeline(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/ci/sphinx.yml.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('## Problem', '## Solution', '## Acceptance')), id='issue-sections'),
    ],
)
def test_issue_template(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/issue.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('## What is changed?', '## How are the changes verified?', '## Issue references')), id='merge-request-sections'),
    ],
)
def test_merge_request_template(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/files/merge_request.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('## GitLab development workflow', 'plan', 'create', 'verify', 'deploy')), id='workflow-guidance'),
    ],
)
def test_agents_fragment(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/fragments/AGENTS.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(context=GITLAB_CONTEXT, contains=('GITLAB_TOKEN must be provided', 'readonly GITLAB_HOST="gitlab.example.com"', 'glab auth login', 'sha256sum --check')),
            id='persisted-authentication',
        ),
    ],
)
def test_setup_fragment(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/fragments/setup.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=GITLAB_CONTEXT, contains=('readonly GITLAB_HOST="gitlab.example.com"', 'glab auth status')), id='authentication-check'),
    ],
)
def test_maintenance_fragment(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/fragments/maintenance.sh.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=GITLAB_CONTEXT, contains=('[GitLab Pages](https://group.gitlab.io/widget/)',)), id='published-documentation'),
    ],
)
def test_documentation_fragment(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/gitlab/fragments/readme.documentation.md.jinja', case)
