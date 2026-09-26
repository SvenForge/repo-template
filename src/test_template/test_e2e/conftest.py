"""Temporary source copies are confined to the CLI tests."""

import shutil
from pathlib import Path

import pytest

from ..support import TEMPLATE_ROOT


@pytest.fixture
def template_source(tmp_path: Path) -> Path:
    source = tmp_path / 'template-source'
    source.mkdir()
    shutil.copy2(TEMPLATE_ROOT / 'copier.yml', source / 'copier.yml')
    for name in ('modules', 'template'):
        shutil.copytree(TEMPLATE_ROOT / name, source / name)
    return source
