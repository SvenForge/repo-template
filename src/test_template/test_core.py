from collections.abc import Callable
from contextlib import AbstractContextManager

import pytest

from .conftest import CopierCase


@pytest.mark.parametrize(
    ("repository_url", "expected"),
    [
        ("", "gitlab.com"),
        ("https://gitlab.example.com/group/repository.git", "gitlab.example.com"),
        ("git@gitlab.example.com:group/repository.git", "gitlab.example.com"),
    ],
    ids=["default", "https", "ssh"],
)
def test_repository_host(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    repository_url: str,
    expected: str,
) -> None:
    with copier_case(core_repository_url=repository_url) as case:
        repository_host = case.context["core_repository_host"]

    assert repository_host == expected


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
        rendered = case.render("template/{% if core_include_readme %}README.md{% endif %}.jinja")
        assert case.context["core_include_license"] is True

    assert "# [Example Repository](https://example.com/repository)" in rendered
    assert "* [Example Owner](mailto:owner@example.com) - @example-owner" in rendered
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
        rendered = case.render("template/{% if core_include_readme %}README.md{% endif %}.jinja")
        assert case.context["core_include_license"] is False

    assert "* Example Owner" in rendered
    assert "mailto:" not in rendered
    assert " - @" not in rendered
    assert "_TODO: Add license information._" in rendered


@pytest.mark.parametrize(
    ("template_name", "expected"),
    [
        ("LICENSE_MIT.jinja", "MIT License"),
        ("LICENSE_NONE.jinja", "All rights reserved."),
    ],
)
def test_license(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    template_name: str,
    expected: str,
) -> None:
    with copier_case(core_owner_name="Example Owner") as case:
        rendered = case.render(f"template/_modules/core/{template_name}")
        year = case.context["core_year"]

    assert f"{year} Example Owner" in rendered
    assert expected in rendered


def test_gitignore(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case() as case:
        rendered = case.render("template/{% if core_include_gitignore %}.gitignore{% endif %}.jinja")

    assert "### Linux ###" in rendered
    assert "### macOS ###" in rendered
    assert "### VisualStudioCode ###" in rendered
    assert "### Windows ###" in rendered
    assert "### Python ###" in rendered
    assert "### Project Customization ###" in rendered
