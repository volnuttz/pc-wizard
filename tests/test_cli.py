from importlib.metadata import version
from pathlib import Path

import pytest
from rich.text import Text
from typer.testing import CliRunner

from pc_wizard import cli
from pc_wizard.cli import app, confirm_overwrite

runner = CliRunner()


def plain_output(output: str) -> str:
    return Text.from_ansi(output).plain


def test_version_option_reports_installed_package_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"pc-wizard {version('pc-wizard')}"


def test_help_lists_version_option() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "--version" in plain_output(result.stdout)


def test_commands_require_a_template() -> None:
    result = runner.invoke(app, ["create", "--help"])

    assert result.exit_code == 0
    output = plain_output(result.stdout)
    assert "--template" in output
    assert "required" in output


def test_help_lists_phase_five_commands_and_options() -> None:
    result = runner.invoke(app, ["--help"])
    output = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "show" in output
    assert "render" not in output
    assert "validate" not in output

    create_help = plain_output(runner.invoke(app, ["create", "--help"]).stdout)
    assert "--from-json" in create_help
    assert "--draft" in create_help
    assert "--force" in create_help


def test_show_complete_character_fixture() -> None:
    fixture = Path(__file__).parent / "fixtures" / "character.json"

    shown = runner.invoke(app, ["show", str(fixture)])

    assert shown.exit_code == 0
    output = plain_output(shown.stdout)
    assert "Binary Smoke Test" in output
    assert "HP 9" in output
    assert "AC 14" in output


def test_missing_character_file_names_the_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    result = runner.invoke(app, ["show", str(missing)])

    assert result.exit_code == 1
    assert str(missing) in plain_output(result.stdout).replace("\n", "")


def test_overwrite_requires_confirmation_unless_forced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "existing.pdf"
    output.touch()

    def deny_confirmation(_message: str, *, default: bool = False) -> bool:
        return False

    monkeypatch.setattr(cli.typer, "confirm", deny_confirmation)

    with pytest.raises(cli.typer.Abort):
        confirm_overwrite([output], force=False)

    confirm_overwrite([output], force=True)


def test_create_noninteractively_from_complete_json(tmp_path: Path) -> None:
    root = Path(__file__).parent.parent
    source = Path(__file__).parent / "fixtures" / "character.json"
    json_output = tmp_path / "character.json"
    pdf_output = tmp_path / "character.pdf"

    result = runner.invoke(
        app,
        [
            "create",
            "--template",
            str(root / "assets" / "character-sheet.pdf"),
            "--from-json",
            str(source),
            "--json",
            str(json_output),
            "--output",
            str(pdf_output),
            "--force",
        ],
    )

    assert result.exit_code == 0
    assert json_output.is_file()
    assert pdf_output.is_file()
