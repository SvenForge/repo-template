from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
import subprocess

import pytest

from .conftest import CopierCase, TEMPLATE_ROOT


PATH_COPIER_CONFIG = (
    "template/{% if copier_include_template %}copier.yml{% endif %}.jinja"
)
PATH_CORE_CONFIG = (
    "template/{% if copier_include_template %}template{% endif %}/_modules/core/copier.yml"
)


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
        assert case.context["copier_include_template"] is expected


def test_copier_configuration(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["copier"]) as case:
        root_config = case.render(PATH_COPIER_CONFIG)
        core_config = case.render(PATH_CORE_CONFIG)
        copier_version = case.context["copier_version"]

    assert root_config == f"""---
_min_copier_version: "{copier_version}"
_subdirectory: template
_exclude:
  - /_modules
---
!include template/_modules/core/copier.yml
"""
    assert "{{" not in root_config
    assert core_config == "---\n{}\n"


def test_generated_copier_configuration(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    subprocess.run(
        [
            "copier",
            "copy",
            "--defaults",
            "--quiet",
            "--vcs-ref=HEAD",
            "--data",
            "features=[copier]",
            "--data",
            "core_include_readme=false",
            "--data",
            "core_license=NOASSERTION",
            "--data",
            "core_include_gitignore=false",
            str(TEMPLATE_ROOT),
            str(repository),
        ],
        check=True,
    )

    destination = tmp_path / "rendered"
    destination.mkdir()
    subprocess.run(
        [
            "copier",
            "copy",
            "--defaults",
            "--quiet",
            str(repository),
            str(destination),
        ],
        check=True,
    )
    assert not any(destination.iterdir())
