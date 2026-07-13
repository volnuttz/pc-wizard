import hashlib
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("binary_name", "archive_suffix", "archive_member"),
    [
        ("pc-wizard", ".tar.gz", "pc-wizard"),
        ("pc-wizard.exe", ".zip", "pc-wizard.exe"),
    ],
)
def test_package_binary(
    tmp_path: Path, binary_name: str, archive_suffix: str, archive_member: str
) -> None:
    binary = tmp_path / binary_name
    binary.write_bytes(b"executable contents")
    output_directory = tmp_path / "packages"
    script = Path(__file__).parents[1] / "scripts" / "package_binary.py"

    result = subprocess.run(
        [sys.executable, script, binary, output_directory, "pc-wizard-test"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    archive = output_directory / f"pc-wizard-test{archive_suffix}"
    checksum_file = archive.with_name(f"{archive.name}.sha256")
    assert archive.name == f"pc-wizard-test{archive_suffix}"
    expected_checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert checksum_file.read_text(encoding="utf-8") == f"{expected_checksum}  {archive.name}\n"
    if archive_suffix == ".zip":
        with zipfile.ZipFile(archive) as package:
            assert package.read(archive_member) == b"executable contents"
    else:
        with tarfile.open(archive, "r:gz") as package:
            extracted = package.extractfile(archive_member)
            assert extracted is not None
            assert extracted.read() == b"executable contents"
