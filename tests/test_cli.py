from importlib.metadata import version

from typer.testing import CliRunner

from pc_wizard.cli import app

runner = CliRunner()


def test_version_option_reports_installed_package_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"pc-wizard {version('pc-wizard')}"


def test_help_lists_version_option() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "--version" in result.stdout


def test_commands_require_a_template() -> None:
    for command in ("create", "render"):
        result = runner.invoke(app, [command, "--help"])

        assert result.exit_code == 0
        assert "--template" in result.stdout
        assert "required" in result.stdout
