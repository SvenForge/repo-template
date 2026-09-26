"""Read-only Copier evaluation and Jinja rendering shared by the smoke tests."""

from collections.abc import Generator, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from copier._main import Worker
from jinja2 import Environment, StrictUndefined

from .support import TEMPLATE_ROOT, ModuleCase, ModuleCheck, RenderCase, TemplateCheck, VariableCase, VariablesCheck, assert_expected


@contextmanager
def _worker(source: Path, answers: dict[str, Any]) -> Generator[Worker, None, None]:
    """Use pinned Copier internals without cloning, copying, or writing answers."""
    with Worker(src_path=str(source), dst_path=TEMPLATE_ROOT, data=answers, defaults=True, skip_tasks=True, quiet=True) as worker:
        # Cached properties let the questionnaire read this checkout directly.
        # Never call run_copy/run_update here; only CLI tests exercise VCS and disk output.
        worker.template.__dict__['vcs'] = None
        worker.subproject.__dict__['last_answers'] = {}
        yield worker


@pytest.fixture
def check_module() -> ModuleCheck:
    def check(module: str, case: ModuleCase) -> None:
        answers = {f'{module}_inputs': case.inputs, **case.answers}
        with _worker(TEMPLATE_ROOT / 'modules' / module, answers) as worker:
            worker._ask()
            output = worker._render_context()[module]
        assert_expected(output, case.expected)

    return check


@pytest.fixture
def check_variables() -> VariablesCheck:
    def check(case: VariableCase) -> None:
        with _worker(TEMPLATE_ROOT, case.answers) as worker:
            worker._ask()
            context = worker._render_context()
        assert_expected(context, case.expected)

    return check


@pytest.fixture(scope='session')
def render_environment() -> Iterator[Environment]:
    with _worker(TEMPLATE_ROOT, {}) as worker:
        environment = worker.jinja_env
        environment.undefined = StrictUndefined
        yield environment


@pytest.fixture
def check_template(render_environment: Environment) -> TemplateCheck:
    def check(template_name: str, case: RenderCase) -> None:
        template = render_environment.get_template(template_name)
        if case.macro:
            rendered = str(getattr(template.make_module(case.context), case.macro)())
        else:
            rendered = template.render(**case.context)
        for text in case.contains:
            assert text in rendered
        parsed = case.parse(rendered) if case.parse else rendered
        if case.expected is not None:
            assert_expected(parsed, case.expected)

    return check
