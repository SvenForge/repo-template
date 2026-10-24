"""Smoke checks for shared agent guidance and contributed sections."""

import pytest

from ..support import ModuleCase, ModuleCheck, RenderCase, TemplateCheck

AGENTS_CONTEXT = {
    'contributions': [
        {'target': 'agents.sections', 'template': 'modules/agents/fragments/guidelines.md.jinja'},
        {'target': 'agents.sections', 'template': 'modules/agents/fragments/safety.md.jinja'},
        {'target': 'agents.sections', 'template': 'modules/gitlab/fragments/AGENTS.md.jinja'},
    ],
}


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            ModuleCase(
                expected={
                    'files': [{'path': 'AGENTS.md', 'template': 'files/AGENTS.md.jinja'}],
                    'contributions': [
                        {'target': 'agents.sections', 'template': 'fragments/guidelines.md.jinja'},
                        {'target': 'agents.sections', 'template': 'fragments/safety.md.jinja'},
                    ],
                },
            ),
            id='shared-guidance',
        ),
        pytest.param(ModuleCase(inputs={'enabled': False}, expected={'files': [], 'contributions': []}), id='disabled'),
    ],
)
def test_output(check_module: ModuleCheck, case: ModuleCase) -> None:
    check_module('agents', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            RenderCase(
                context=AGENTS_CONTEXT,
                contains=('# AGENTS.md', '## General guidelines', '## Safety and boundaries', '## GitLab development workflow'),
            ),
            id='shared-and-gitlab-guidance',
        ),
    ],
)
def test_agents(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/agents/files/AGENTS.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('## General guidelines', 'Use American English')), id='general-guidelines'),
    ],
)
def test_guidelines(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/agents/fragments/guidelines.md.jinja', case)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(RenderCase(contains=('## Safety and boundaries', 'Do not edit or publish any secrets')), id='safety-boundaries'),
    ],
)
def test_safety(check_template: TemplateCheck, case: RenderCase) -> None:
    check_template('modules/agents/fragments/safety.md.jinja', case)
