from pathlib import Path

from copier import run_copy


TEMPLATE_ROOT = Path(__file__).parents[1]


def test_template_renders_with_defaults(tmp_path: Path) -> None:
    destination = tmp_path / "repository"

    run_copy(str(TEMPLATE_ROOT), destination, defaults=True)

    assert destination.is_dir()
