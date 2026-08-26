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
        rendered = case.render(
            "template/{% if core_include_readme %}README.md{% endif %}.jinja"
        )

    assert "# [Example Repository](https://example.com/repository)" in rendered
    assert (
        "* [Example Owner](mailto:owner@example.com) - @example-owner" in rendered
    )
    assert "Please see: [LICENSE.md](LICENSE.md)" in rendered


def test_readme_without_optional_owner_contact(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        core_owner_name="Example Owner",
        core_owner_email="",
        core_owner_user="",
        core_license="NOASSERTION",
    ) as case:
        rendered = case.render(
            "template/{% if core_include_readme %}README.md{% endif %}.jinja"
        )

    assert "* Example Owner" in rendered
    assert "mailto:" not in rendered
    assert " - @" not in rendered
    assert "_TODO: Add license information._" in rendered
