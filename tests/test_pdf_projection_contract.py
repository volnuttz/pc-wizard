import json
import subprocess
import sys
from pathlib import Path


def test_projection_export_matches_the_frozen_rogue_contract(tmp_path: Path) -> None:
    output = tmp_path / "projection.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/export_pdf_projection_contract.py",
            "contracts/fixtures/complete-rogue-v1.json",
            str(output),
        ],
        check=True,
    )
    exported = json.loads(output.read_text(encoding="utf-8"))
    expected = json.loads(Path("contracts/fixtures/pdf-rogue-v1.json").read_text(encoding="utf-8"))

    assert exported["field_count"] == expected["field_count"]
    assert exported["projection_sha256"] == expected["projection_sha256"]
