import argparse
import gzip
import hashlib
import io
import tarfile
import zipfile
from pathlib import Path


def package_binary(binary: Path, output_directory: Path, artifact_name: str) -> tuple[Path, Path]:
    """Create a platform archive and its SHA-256 checksum file."""
    output_directory.mkdir(parents=True, exist_ok=True)
    binary_data = binary.read_bytes()

    if binary.suffix.lower() == ".exe":
        archive = output_directory / f"{artifact_name}.zip"
        archive_entry = zipfile.ZipInfo("pc-wizard.exe", date_time=(2020, 1, 1, 0, 0, 0))
        archive_entry.compress_type = zipfile.ZIP_DEFLATED
        archive_entry.external_attr = 0o755 << 16
        with zipfile.ZipFile(archive, "w") as package:
            package.writestr(archive_entry, binary_data)
    else:
        archive = output_directory / f"{artifact_name}.tar.gz"
        archive_entry = tarfile.TarInfo("pc-wizard")
        archive_entry.size = len(binary_data)
        archive_entry.mode = 0o755
        archive_entry.mtime = 0
        with (
            archive.open("wb") as raw_archive,
            gzip.GzipFile(fileobj=raw_archive, mode="wb", filename="", mtime=0) as compressed,
            tarfile.open(fileobj=compressed, mode="w") as package,
        ):
            package.addfile(archive_entry, io.BytesIO(binary_data))

    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum_file = archive.with_name(f"{archive.name}.sha256")
    checksum_file.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    return archive, checksum_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Package and checksum a pc-wizard binary.")
    parser.add_argument("binary", type=Path)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("artifact_name")
    arguments = parser.parse_args()

    archive, checksum = package_binary(
        arguments.binary, arguments.output_directory, arguments.artifact_name
    )
    print(archive)
    print(checksum)


if __name__ == "__main__":
    main()
