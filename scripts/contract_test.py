"""Run versioned black-box CLI scenarios against either implementation."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "character.json"
TEMPLATE = ROOT / "assets" / "character-sheet.pdf"
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def plain(text: str) -> str:
    return ANSI.sub("", text)


def fail(scenario: str, message: str, result: subprocess.CompletedProcess[str]) -> NoReturn:
    raise AssertionError(
        f"{scenario}: {message}\nexit={result.returncode}\n"
        f"stdout={plain(result.stdout)!r}\nstderr={plain(result.stderr)!r}"
    )


def run(executable: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(executable), *arguments],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )


def require(
    result: subprocess.CompletedProcess[str], scenario: str, *, code: int, text: str
) -> None:
    output = plain(result.stdout + result.stderr)
    if result.returncode != code or text not in output:
        fail(scenario, f"expected exit {code} and text {text!r}", result)


def run_contract(executable: Path) -> None:
    help_result = run(executable, "--help")
    require(help_result, "help", code=0, text="--version")
    for required in ("create", "show"):
        if required not in plain(help_result.stdout + help_result.stderr):
            fail("help", f"missing command {required!r}", help_result)

    require(run(executable, "--version"), "version", code=0, text="pc-wizard ")
    shown = run(executable, "show", str(FIXTURE))
    require(shown, "show-complete", code=0, text="Binary Smoke Test")
    for expected in ("HP 9", "AC 14"):
        if expected not in plain(shown.stdout + shown.stderr):
            fail("show-complete", f"missing {expected!r}", shown)

    missing = ROOT / "contracts" / "does-not-exist.json"
    missing_result = run(executable, "show", str(missing))
    require(missing_result, "show-missing", code=1, text=str(missing))
    require(missing_result, "show-missing", code=1, text="Error:")

    with tempfile.TemporaryDirectory(prefix="pc-wizard-contract-") as directory:
        destination = Path(directory)
        json_output = destination / "character.json"
        pdf_output = destination / "character.pdf"
        created = run(
            executable,
            "create",
            "--template",
            str(TEMPLATE),
            "--from-json",
            str(FIXTURE),
            "--json",
            str(json_output),
            "--output",
            str(pdf_output),
            "--force",
        )
        require(created, "create-from-json", code=0, text="Binary Smoke Test is ready!")
        if not json_output.is_file() or not pdf_output.is_file():
            fail("create-from-json", "expected JSON and PDF outputs", created)

        bad_json = destination / "not-written.json"
        bad_pdf = destination / "not-written.pdf"
        absent_template = destination / "absent.pdf"
        template_error = run(
            executable,
            "create",
            "--template",
            str(absent_template),
            "--from-json",
            str(FIXTURE),
            "--json",
            str(bad_json),
            "--output",
            str(bad_pdf),
            "--force",
        )
        require(template_error, "template-missing", code=1, text="Error:")
        if bad_json.exists() or bad_pdf.exists():
            fail("template-missing", "template validation wrote an output", template_error)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", required=True, type=Path)
    arguments = parser.parse_args()
    if not arguments.executable.is_file():
        parser.error(f"executable does not exist or is not a file: {arguments.executable}")
    run_contract(arguments.executable)
    print("6 contract scenarios passed")


if __name__ == "__main__":
    main()
