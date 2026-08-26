from collections.abc import Callable
from contextlib import AbstractContextManager

from .conftest import CopierCase


def test_readme_with_owner_contact(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        core_repository_name="Example Repository",
        core_repository_url="https://example.com/repository",
        core_owner_name="Example Owner",
        core_owner_email="owner@example.com",
        core_owner_user="example-owner",
    ) as case:
        rendered = case.render("template/README.md.jinja")
        year = case.context["core_year"]

    assert "# [Example Repository](https://example.com/repository)" in rendered
    assert (
        "* [Example Owner](mailto:owner@example.com) - @example-owner" in rendered
    )
    assert f"Copyright © {year} Example Owner." in rendered


def test_readme_without_optional_owner_contact(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        core_owner_name="Example Owner",
        core_owner_email="",
        core_owner_user="",
    ) as case:
        rendered = case.render("template/README.md.jinja")

    assert "* Example Owner" in rendered
    assert "mailto:" not in rendered
    assert " - @" not in rendered
