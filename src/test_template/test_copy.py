from dataclasses import dataclass
from pathlib import Path
import subprocess

import pytest

from .conftest import TEMPLATE_ROOT


@dataclass(frozen=True)
class CopyCase:
    answers: dict[str, str]
    expected_files: set[Path]
    expected_readme: tuple[str, ...]


COPY_CASES = {
    "defaults": CopyCase(
        answers={},
        expected_files={Path(".gitignore"), Path("LICENSE.md"), Path("README.md")},
        expected_readme=("# My Repository", "_TODO: Add contact information._"),
    ),
    "empty-repository": CopyCase(
        answers={
            "core_include_readme": "false",
            "core_license": "NOASSERTION",
            "core_include_gitignore": "false",
        },
        expected_files=set(),
        expected_readme=(),
    ),
}


@pytest.mark.parametrize("case", COPY_CASES.values(), ids=COPY_CASES.keys())
def test_copy(tmp_path: Path, case: CopyCase) -> None:
    destination = tmp_path / "repository"
    command = [
        "copier",
        "copy",
        "--defaults",
        "--quiet",
        str(TEMPLATE_ROOT),
        str(destination),
    ]
    for name, value in case.answers.items():
        command.extend(("--data", f"{name}={value}"))

    subprocess.run(command, check=True)

    files = {
        path.relative_to(destination)
        for path in destination.rglob("*")
        if path.is_file()
    }
    assert files == case.expected_files

    if case.expected_readme:
        readme = (destination / "README.md").read_text()
        for expected in case.expected_readme:
            assert expected in readme
