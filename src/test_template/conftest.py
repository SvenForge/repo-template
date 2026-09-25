"""Fixtures for testing module templates without Git side effects."""

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from copier._main import Worker

TEMPLATE_ROOT = Path(__file__).parents[2]


@dataclass
class CopierCase:
    worker: Worker

    @property
    def context(self) -> dict[str, Any]:
        return self.worker._render_context()

    def render(self, template_name: str) -> str:
        template = self.worker.jinja_env.get_template(template_name)
        return template.render(**self.context)


@pytest.fixture
def template_source(tmp_path: Path) -> Path:
    source = tmp_path / 'template-source'
    source.mkdir()
    shutil.copy2(TEMPLATE_ROOT / 'copier.yml', source / 'copier.yml')
    for name in ('modules', 'template'):
        shutil.copytree(TEMPLATE_ROOT / name, source / name)
    return source


@pytest.fixture
def copier_case(tmp_path: Path, template_source: Path):
    @contextmanager
    def create(**answers: Any) -> Iterator[CopierCase]:
        with Worker(
            src_path=str(template_source),
            dst_path=tmp_path / "unused",
            data=answers,
            defaults=True,
            skip_tasks=True,
            quiet=True,
        ) as worker:
            worker._ask()
            yield CopierCase(worker)

    return create
