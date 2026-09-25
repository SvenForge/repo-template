"""Check Core module settings and generated files."""

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
    with copier_case(features=["core"], core_repository_url=repository_url) as case:
        repository_host = case.context["core"]["vars"]["repository_host"]

    assert repository_host == expected


def test_readme_with_owner_contact(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core"],
        core_repository_name="Example Repository",
        core_repository_url="https://example.com/repository",
        core_owner_name="Example Owner",
        core_owner_email="owner@example.com",
        core_owner_user="example-owner",
    ) as case:
        rendered = case.render("modules/core/files/README.md.jinja")
        assert "LICENSE.md" in {file["path"] for file in case.context["core"]["files"]}

    assert "# [Example Repository](https://example.com/repository)" in rendered
    assert "* [Example Owner](mailto:owner@example.com) - @example-owner" in rendered
    assert "Please see: [LICENSE.md](./LICENSE.md)" in rendered


def test_readme_without_optional_owner_contact(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(
        features=["core"],
        core_owner_name="Example Owner",
        core_owner_email="",
        core_owner_user="",
        core_license="NOASSERTION",
    ) as case:
        rendered = case.render("modules/core/files/README.md.jinja")
        assert "LICENSE.md" not in {file["path"] for file in case.context["core"]["files"]}

    assert "* Example Owner" in rendered
    assert "mailto:" not in rendered
    assert " - @" not in rendered
    assert "_TODO: Add license information._" in rendered


@pytest.mark.parametrize(
    ("template_name", "expected"),
    [
        ("LICENSE_MIT.md.jinja", "MIT License"),
        ("LICENSE_NONE.md.jinja", "All rights reserved."),
    ],
)
def test_license(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
    template_name: str,
    expected: str,
) -> None:
    with copier_case(features=["core"], core_owner_name="Example Owner") as case:
        rendered = case.render(f"modules/core/files/{template_name}")
        year = case.context["core"]["vars"]["year"]

    assert f"{year} Example Owner" in rendered
    assert expected in rendered


def test_gitignore(
    copier_case: Callable[..., AbstractContextManager[CopierCase]],
) -> None:
    with copier_case(features=["core"]) as case:
        rendered = case.render("modules/core/files/gitignore.jinja")

    assert "### Linux ###" in rendered
    assert "### macOS ###" in rendered
    assert "### VisualStudioCode ###" in rendered
    assert "### Windows ###" in rendered
    assert "### Project Customization ###" in rendered
