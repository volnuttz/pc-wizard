# pc-wizard

A native interactive command-line wizard for creating level-1 D&D characters
from SRD 5.2.1. It saves a validated canonical JSON record and fills a separately
downloaded official `character-sheet.pdf` AcroForm.

## Install and run

Download the archive and matching `.sha256` file for your platform from the
[latest GitHub Release](https://github.com/volnuttz/pc-wizard/releases/latest):

- `pc-wizard-linux-x86_64.tar.gz`
- `pc-wizard-windows-x86_64.zip`
- `pc-wizard-macos-arm64.tar.gz` for Apple Silicon
- `pc-wizard-macos-x86_64.tar.gz` for Intel Macs

Verify the archive before extracting it:

```console
# Linux
sha256sum --check pc-wizard-linux-x86_64.tar.gz.sha256

# macOS
shasum --algorithm 256 --check pc-wizard-macos-arm64.tar.gz.sha256
```

On Windows PowerShell, compare `Get-FileHash` with the hash in the downloaded
`.sha256` file:

```powershell
Get-FileHash .\pc-wizard-windows-x86_64.zip -Algorithm SHA256
```

Extract the archive and place `pc-wizard` (or `pc-wizard.exe`) on `PATH`. No
Python runtime or package manager is required. The binaries are unsigned, so
Windows SmartScreen or macOS Gatekeeper may warn on first launch.

Download the official fillable character sheet before creating a character:

- [Official character-sheet downloads](https://www.dndbeyond.com/resources/1779-d-d-character-sheets)
- [Direct PDF download](https://media.dndbeyond.com/compendium-images/free-rules/ph/character-sheet.pdf)

The direct URL may change. The native renderer validates the exact supported
two-page AcroForm before prompting or writing outputs.

```console
pc-wizard create --template character-sheet.pdf
pc-wizard validate character.json
pc-wizard show character.json
pc-wizard create --template character-sheet.pdf --from-json character.json --force
```

Creation writes `character.json` and `character-sheet-filled.pdf` by default.
Use `--json`, `--output`, and `--draft` to choose other paths. Existing outputs
require confirmation unless `--force` is supplied. Interactive creation saves a
checkpoint after every completed stage, supports final review and editing, and
resumes from the same draft path.

Character JSON is the canonical current-schema record. The PDF is a rendered
view; older or unknown JSON shapes are rejected rather than silently migrated.

## Build from source

The workspace pins Rust 1.88.0:

```console
rustup toolchain install 1.88.0 --profile minimal --component rustfmt --component clippy
cargo +1.88.0 build --release --locked -p pc-wizard-cli
target/release/pc-wizard --version
```

The complete development gate is:

```console
cargo +1.88.0 fmt --check
cargo +1.88.0 clippy --workspace --all-targets -- -D warnings
cargo +1.88.0 test --workspace --locked
cargo +1.88.0 audit
cargo +1.88.0 deny check
```

The current scope covers all 12 SRD classes, 4 backgrounds, and 9 species at
level 1, including suggested/standard arrays, rolled scores, 27-point point buy,
background increases, class and origin choices, equipment, combat values,
spellcasting, checkpoint/resume, and the full supported character-sheet mapping.

The completed Python-to-Rust parity and performance results are summarized in
[`docs/rust-migration.md`](docs/rust-migration.md). The legacy Python
implementation and migration-only generated artifacts were retired after the
verified `v0.3.0` native release.

See [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md), and the
[roadmap](docs/roadmap.md). SRD attribution and template terms are in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

pc-wizard's original source code is available under the [MIT License](LICENSE).
