from collections.abc import Callable
from contextlib import AbstractContextManager

import pytest

from .conftest import CopierCase


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
        modules = case.context["modules"]

    assert root_config == f"""---
_min_copier_version: &min_copier_version "{copier_version}"
_subdirectory: template
_exclude:
  - /_modules

features:
  type: str
  help: Which template features shall be used?
  multiselect: true
  choices: []
  default: []

modules:
  type: yaml
  help: Which template modules shall be used?
  default: "{modules}"
  when: false

copier_version:
  type: str
  help: Which Copier version does this template require?
  default: *min_copier_version
  when: false

---
!include template/_modules/core/copier.yml
"""
    assert "{{" not in root_config
    assert core_config == ""
