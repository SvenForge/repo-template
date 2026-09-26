"""Smoke checks for Core output and each of its templates."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck, module_context

OUTPUT_CASES = {
    'defaults': ModuleCase(
        expected={
            'vars': {'repository_name': 'My Repository', 'license': 'NONE'},
            'files': [
                {'path': 'README.md', 'template': 'files/README.md.jinja'},
                {'path': 'LICENSE.md', 'template': 'files/LICENSE_NONE.md.jinja'},
                {'path': '.gitignore', 'template': 'files/gitignore.jinja'},
            ],
            'contributions': [{'target': 'core.gitignore', 'template': 'fragments/gitignore.jinja'}],
        },
    ),
    'hosted-repository': ModuleCase(
        inputs={'repository_name': 'Input Name', 'repository_url': 'git@gitlab.example.com:group/widget.git', 'year': 2026},
        answers={'core_repository_name': 'Widget', 'core_owner_name': 'Example Owner', 'core_license': 'MIT'},
        expected={
            'vars': {'repository_name': 'Widget', 'repository_host': 'gitlab.example.com', 'repository_path': 'group/widget', 'owner_name': 'Example Owner', 'year': 2026},
            'files': [{'path': 'LICENSE.md', 'template': 'files/LICENSE_MIT.md.jinja'}],
            'contributions': [{'target': 'core.gitignore', 'template': 'fragments/gitignore.jinja'}],
        },
    ),
}
README_CONTEXT = module_context(
    'core',
    repository_name='Widget',
    repository_url='https://example.com/widget',
    owner_name='Example Owner',
    owner_email='owner@example.com',
    owner_user='example-owner',
)
README_CONTEXT['core']['files'] = [{'path': 'LICENSE.md'}]
LICENSE_CONTEXT = module_context('core', year=2026, owner_name='Example Owner')
GITIGNORE_CONTEXT = module_context('core')
GITIGNORE_CONTEXT['contributions'] = [{'target': 'core.gitignore', 'template': 'modules/core/fragments/gitignore.jinja'}]


@pytest.mark.parametrize('case', OUTPUT_CASES.values(), ids=OUTPUT_CASES.keys())
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('core', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=README_CONTEXT, contains=('# [Widget](https://example.com/widget)', 'mailto:owner@example.com', '[LICENSE.md](./LICENSE.md)')), id='owner-and-license'),
    ],
)
def test_readme(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/core/files/README.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=LICENSE_CONTEXT, contains=('MIT License', '2026 Example Owner', 'Permission is hereby granted')), id='mit'),
    ],
)
def test_license_mit(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/core/files/LICENSE_MIT.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=LICENSE_CONTEXT, contains=('2026 Example Owner', 'All rights reserved.')), id='proprietary'),
    ],
)
def test_license_none(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/core/files/LICENSE_NONE.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(context=GITIGNORE_CONTEXT, contains=('### Linux ###', '### Project Customization ###')), id='core-contribution'),
    ],
)
def test_gitignore_file(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/core/files/gitignore.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('### Linux ###', '### macOS ###', '### Windows ###', '### VisualStudioCode ###')), id='desktop-environments'),
    ],
)
def test_gitignore_fragment(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/core/fragments/gitignore.jinja', case)
