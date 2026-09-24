"""Check the Copier module and its generated starter template."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from copier._main import Worker

from .conftest import CopierCase

PATH_COPIER_CONFIG = "modules/copier/files/copier.yml.jinja"
PATH_CORE_CONFIG = "modules/copier/files/core.yml.jinja"


@pytest.mark.parametrize(
    ("features", "expected"),
    [([], False), (["copier"], True)],
    ids=["without-copier", "with-copier"],
)
def test_copier_file_selection(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    features: list[str],
    expected: bool,
) -> None:
    with copier_case(features=features) as case:
        assert case.context["copier"]["vars"]["enabled"] is expected
        assert bool(case.context["copier"]["files"]) is expected


def test_copier_configuration(
    tmp_path: Path,
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["copier"]) as case:
        root_config = case.render(PATH_COPIER_CONFIG)
        core_config = case.render(PATH_CORE_CONFIG)
        case.worker.run_copy()
        source = case.worker.dst_path

    assert "_subdirectory: template" in root_config
    assert "features:" in root_config
    assert "!include modules/core/copier.yml" in root_config
    assert "{% raw %}" not in root_config
    assert "core_inputs:" in core_config
    assert "files: []" in core_config
    with Worker(
        src_path=str(source),
        dst_path=tmp_path / "generated-project",
        defaults=True,
        skip_tasks=True,
        quiet=True,
    ) as worker:
        worker.run_copy()
        context = worker._render_context()
        assert context["core"]["vars"]["enabled"] is True
        assert context["files"] == []
        assert context["contributions"] == []
