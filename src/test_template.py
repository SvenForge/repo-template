from pathlib import Path

import pytest
from copier import run_copy
from copier._main import Worker


TEMPLATE_ROOT = Path(__file__).parents[1]


def assert_no_template_expressions(destination: Path) -> None:
    for path in destination.iterdir():
        if path.is_file():
            content = path.read_text()
            assert "{{" not in content
            assert "{%" not in content


def test_template_renders_core_defaults(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    run_copy(str(TEMPLATE_ROOT), destination, defaults=True)

    assert {path.name for path in destination.iterdir()} == {
        ".gitignore",
        "LICENSE.md",
        "README.md",
    }
    assert "# My Repository" in (destination / "README.md").read_text()
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
            "core_include_license": False,
        },
        defaults=True,
    )

    assert {path.name for path in destination.iterdir()} == {"README.md"}
    readme = (destination / "README.md").read_text()
    assert "_TODO: Add license information._" in readme
    assert_no_template_expressions(destination)


def test_template_renders_custom_metadata(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    with Worker(
        src_path=str(TEMPLATE_ROOT),
        dst_path=destination,
        data={
            "core_repository_name": "Example Project",
            "core_repository_url": "https://example.com/example-project",
            "core_owner_name": "Ada Lovelace",
            "core_owner_email": "ada@example.com",
            "core_owner_user": "ada",
        },
        defaults=True,
    ) as worker:
        worker.run_copy()
        assert worker.answers.combined["core_repository_slug"] == "example-project"

    readme = (destination / "README.md").read_text()
    assert "# [Example Project](https://example.com/example-project)" in readme
    assert "[Ada Lovelace](mailto:ada@example.com) - @ada" in readme
    assert_no_template_expressions(destination)


@pytest.mark.parametrize(
    ("license_name", "expected_readme", "expected_license"),
    [
        ("all-rights-reserved", "All rights reserved.", "All rights reserved."),
        ("mit", "Licensed under the MIT License.", "MIT License"),
    ],
)
def test_template_renders_selected_license(
    tmp_path: Path,
    license_name: str,
    expected_readme: str,
    expected_license: str,
) -> None:
    destination = tmp_path / license_name

    run_copy(
        str(TEMPLATE_ROOT),
        destination,
        data={"core_license": license_name},
        defaults=True,
    )

    assert expected_readme in (destination / "README.md").read_text()
    assert expected_license in (destination / "LICENSE.md").read_text()
    assert_no_template_expressions(destination)
