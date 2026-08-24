from pathlib import Path

from copier import run_copy


TEMPLATE_ROOT = Path(__file__).parents[1]


def test_core_feature_renders_readme(tmp_path: Path) -> None:
    run_copy(
        str(TEMPLATE_ROOT),
        tmp_path,
        data={"features": ["core"], "core_project_name": "Example Project"},
        defaults=True,
    )

    assert (tmp_path / "README.md").read_text(encoding="utf-8") == (
        "# Example Project\n\n"
        "Generated with the `core` feature of Repo Template.\n"
    )


def test_omitting_core_feature_skips_readme(tmp_path: Path) -> None:
    run_copy(
        str(TEMPLATE_ROOT),
        tmp_path,
        data={"features": []},
        defaults=True,
    )

    assert not (tmp_path / "README.md").exists()
    assert list(tmp_path.iterdir()) == []
