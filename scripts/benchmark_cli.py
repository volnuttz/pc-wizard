"""Record repeatable black-box CLI timing baselines as JSON."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "character.json"
TEMPLATE = ROOT / "assets" / "character-sheet.pdf"


def invoke(command: list[str], arguments: list[str]) -> dict[str, int | float]:
    started = time.perf_counter_ns()
    result = subprocess.run(command + arguments, cwd=ROOT, capture_output=True, check=False)
    elapsed = time.perf_counter_ns() - started
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {result.stderr.decode(errors='replace')}"
        )
    return {"wall_time_ms": round(elapsed / 1_000_000, 3)}


def scenario_arguments(name: str, directory: Path) -> list[str]:
    if name == "help":
        return ["--help"]
    if name == "version":
        return ["--version"]
    if name == "show":
        return ["show", str(FIXTURE)]
    if name == "create":
        directory.mkdir(parents=True, exist_ok=True)
        return [
            "create",
            "--template",
            str(TEMPLATE),
            "--from-json",
            str(FIXTURE),
            "--force",
            "--json",
            str(directory / "character.json"),
            "--output",
            str(directory / "character.pdf"),
        ]
    raise ValueError(f"unknown scenario: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="+", help="Executable and any fixed launcher arguments.")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument(
        "--scenario", choices=("help", "version", "show", "create"), action="append"
    )
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.runs < 1:
        parser.error("--runs must be at least 1")
    scenarios = arguments.scenario or ["help", "version", "show", "create"]
    results: dict[str, list[dict[str, int | float]]] = {}
    with tempfile.TemporaryDirectory(prefix="pc-wizard-benchmark-") as temporary:
        root = Path(temporary)
        for scenario in scenarios:
            samples = [
                invoke(arguments.command, scenario_arguments(scenario, root / str(index)))
                for index in range(arguments.runs)
            ]
            results[scenario] = samples
    report = {
        "schema_version": 1,
        "command": arguments.command,
        "platform": platform.platform(),
        "python": sys.version,
        "runs": arguments.runs,
        "metrics": {
            name: {
                "samples": samples,
                "min_wall_time_ms": min(sample["wall_time_ms"] for sample in samples),
                "median_wall_time_ms": statistics.median(
                    sample["wall_time_ms"] for sample in samples
                ),
            }
            for name, samples in results.items()
        },
        "limitations": [
            "This runner records warm process wall time only.",
            "Cold-start, peak-memory, artifact-size, and one-file-extraction measurements "
            "require platform-specific release harness support.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
