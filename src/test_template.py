from pathlib import Path

import pytest
from copier import run_copy


TEMPLATE_ROOT = Path(__file__).parents[1]


def assert_no_template_expressions(destination: Path) -> None:
    for path in destination.iterdir():
        if path.is_file():
            content = path.read_text()
            assert "{{" not in content
            assert "{%" not in content


def test_template_renders_core_defaults(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    run_copy(str(TEMPLATE_ROOT), destination, defaults=True, vcs_ref="HEAD")

    assert {path.name for path in destination.iterdir()} == {
        ".gitignore",
        "LICENSE.md",
        "README.md",
    }
    readme = (destination / "README.md").read_text()
    assert "# My Repository" in readme
    assert "### Maintainer" in readme
    assert "_TODO: Add contact information._" in readme
    assert "Please see: [LICENSE.md](LICENSE.md)" in readme
    assert "All rights reserved." in (destination / "LICENSE.md").read_text()
    assert "Created by https://www.toptal.com/developers/gitignore/api/" in (
        destination / ".gitignore"
    ).read_text()
    assert_no_template_expressions(destination)


def test_template_renders_readme_only(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    run_copy(
        str(TEMPLATE_ROOT),
        destination,
        data={
            "core_include_gitignore": False,
            "core_license": "NOASSERTION",
        },
        defaults=True,
        vcs_ref="HEAD",
    )

    assert {path.name for path in destination.iterdir()} == {"README.md"}
    assert "_TODO: Add license information._" in (
        destination / "README.md"
    ).read_text()
    assert_no_template_expressions(destination)


def test_template_can_render_empty_repository(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    run_copy(
        str(TEMPLATE_ROOT),
        destination,
        data={
            "core_include_gitignore": False,
            "core_include_readme": False,
            "core_license": "NOASSERTION",
        },
        defaults=True,
        vcs_ref="HEAD",
    )

    assert not destination.exists() or list(destination.iterdir()) == []


def test_template_renders_custom_metadata(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    run_copy(
        str(TEMPLATE_ROOT),
        destination,
        data={
            "core_repository_name": "Example Project",
            "core_repository_url": "https://example.com/example-project",
            "core_owner_name": "Ada Lovelace",
            "core_owner_email": "ada@example.com",
            "core_owner_user": "ada",
        },
        defaults=True,
        vcs_ref="HEAD",
    )

    readme = (destination / "README.md").read_text()
    assert "# [Example Project](https://example.com/example-project)" in readme
    assert "### Maintainer" in readme
    assert "[Ada Lovelace](mailto:ada@example.com) - @ada" in readme
    assert_no_template_expressions(destination)


@pytest.mark.parametrize(
    ("license_name", "expected_readme", "expected_license", "has_license"),
    [
        (
            "NONE",
            "Please see: [LICENSE.md](LICENSE.md)",
            "All rights reserved.",
            True,
        ),
        ("MIT", "Please see: [LICENSE.md](LICENSE.md)", "MIT License", True),
        ("NOASSERTION", "_TODO: Add license information._", "", False),
    ],
)
def test_template_renders_selected_license(
    tmp_path: Path,
    license_name: str,
    expected_readme: str,
    expected_license: str,
    has_license: bool,
) -> None:
    destination = tmp_path / license_name

    run_copy(
        str(TEMPLATE_ROOT),
        destination,
        data={"core_license": license_name},
        defaults=True,
        vcs_ref="HEAD",
    )

    assert expected_readme in (destination / "README.md").read_text()
    license_path = destination / "LICENSE.md"
    assert license_path.exists() is has_license
    if has_license:
        assert expected_license in license_path.read_text()
    assert_no_template_expressions(destination)
