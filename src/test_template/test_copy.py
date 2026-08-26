from dataclasses import dataclass
from pathlib import Path
import subprocess

import pytest

from .conftest import TEMPLATE_ROOT


@dataclass(frozen=True)
class CopyCase:
    answers: dict[str, str]
    expected_readme: tuple[str, ...]


COPY_CASES = {
    "defaults": CopyCase(
        answers={},
        expected_readme=("# [My Repository]", "* Repository Owner"),
    ),
    "empty-repository": CopyCase(
        answers={
            "features": "[]",
            "core_repository_name": "Empty Repository",
            "core_repository_url": "https://example.com/empty.git",
            "core_owner_name": "Example Owner",
        },
        expected_readme=(
            "# [Empty Repository](https://example.com/empty.git)",
            "* Example Owner",
        ),
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
    assert files == {Path("README.md")}

    readme = (destination / "README.md").read_text()
    for expected in case.expected_readme:
        assert expected in readme
