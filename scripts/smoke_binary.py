import argparse
import subprocess
import tempfile
from pathlib import Path

from pypdf import PdfReader

OFFICIAL_TEMPLATE_PAGE = "https://www.dndbeyond.com/resources/1779-d-d-character-sheets"


def completed(binary: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [binary, *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test a frozen pc-wizard executable.")
    parser.add_argument("binary", type=Path)
    parser.add_argument("character_json", type=Path)
    parser.add_argument("template", type=Path)
    arguments = parser.parse_args()

    help_result = completed(arguments.binary, "--help")
    assert help_result.returncode == 0, help_result.stderr
    assert "create" in help_result.stdout and "show" in help_result.stdout

    version_result = completed(arguments.binary, "--version")
    assert version_result.returncode == 0, version_result.stderr
    assert version_result.stdout.startswith("pc-wizard ")

    with tempfile.TemporaryDirectory(prefix="pc-wizard-binary-smoke-") as directory:
        temporary_directory = Path(directory)
        missing_template = temporary_directory / "missing.pdf"
        rejected_output = temporary_directory / "rejected.pdf"
        invalid_result = completed(
            arguments.binary,
            "create",
            "--from-json",
            str(arguments.character_json),
            "--template",
            str(missing_template),
            "--output",
            str(rejected_output),
        )
        assert invalid_result.returncode == 1
        assert OFFICIAL_TEMPLATE_PAGE in invalid_result.stdout
        assert not rejected_output.exists()

        rendered_output = temporary_directory / "rendered.pdf"
        render_result = completed(
            arguments.binary,
            "create",
            "--from-json",
            str(arguments.character_json),
            "--template",
            str(arguments.template),
            "--output",
            str(rendered_output),
            "--json",
            str(temporary_directory / "character.json"),
            "--force",
        )
        assert render_result.returncode == 0, render_result.stdout + render_result.stderr
        reader = PdfReader(rendered_output)
        assert len(reader.pages) == 2
        assert reader.get_fields()

    print(f"Smoke tests passed: {arguments.binary}")


if __name__ == "__main__":
    main()
