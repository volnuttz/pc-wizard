# pc-wizard

An interactive command-line wizard for creating level-1 D&D characters using the
rules in `SRD_CC_v5.2.1.pdf`. It saves validated JSON and fills the supplied
`character-sheet.pdf` AcroForm.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Install and run

Download the official fillable character sheet before creating or rendering a
character:

- [Official character-sheet downloads](https://www.dndbeyond.com/resources/1779-d-d-character-sheets)
- [Direct PDF download](https://media.dndbeyond.com/compendium-images/free-rules/ph/character-sheet.pdf)

The direct PDF URL is maintained by D&D Beyond and may change. If it stops working,
use the official downloads page to find the current 2024 fillable sheet.

```console
uv sync
uv run pc-wizard create --template character-sheet.pdf
```

By default, creation writes `character.json` and `character-sheet-filled.pdf`.
The template must be supplied explicitly each time. Output paths can be changed:

```console
uv run pc-wizard create --template character-sheet.pdf --output my-hero.pdf --json my-hero.json
uv run pc-wizard render my-hero.json --template character-sheet.pdf --output another-copy.pdf
```

Run `uv run pc-wizard --help` for all options. Cancel the interactive wizard at
any prompt with Ctrl-C.

## Install a standalone executable

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

On Windows PowerShell, compare the output of this command with the hash at the
start of the downloaded `.sha256` file:

```powershell
Get-FileHash .\pc-wizard-windows-x86_64.zip -Algorithm SHA256
```

Extract the archive and place `pc-wizard` (or `pc-wizard.exe`) in a directory on
your `PATH`. Upgrade by replacing that file with the verified file from a newer
release. Uninstall by deleting it. The binaries are currently unsigned, so Windows
SmartScreen or macOS Gatekeeper may warn on first launch; see
[`docs/releasing.md`](docs/releasing.md#signing-and-notarization).

## Install as a uv tool

Install the command globally from GitHub without cloning the repository:

```console
uv tool install git+https://github.com/volnuttz/pc-wizard.git
pc-wizard --version
```

From an existing checkout, install the current working tree instead:

```console
uv tool install .
```

Upgrade a GitHub installation or remove the tool with:

```console
uv tool upgrade pc-wizard
uv tool uninstall pc-wizard
```

## Development

```console
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Build the platform-native one-directory executable with PyInstaller:

```console
uv run pyinstaller --clean --noconfirm pc-wizard.spec
dist/pc-wizard/pc-wizard --version
uv run python scripts/smoke_binary.py \
  dist/pc-wizard/pc-wizard tests/fixtures/character.json character-sheet.pdf
```

PyInstaller builds for the current operating system only. The generated `build/`
and `dist/` directories are not source artifacts and are ignored by Git.

Build and smoke-test the single-file executable with:

```console
uv run pyinstaller --clean --noconfirm pc-wizard-onefile.spec
uv run python scripts/smoke_binary.py \
  dist/pc-wizard-onefile tests/fixtures/character.json character-sheet.pdf
```

The current wizard targets level-1 creation and the player options published in
SRD 5.2.1: 12 classes, 4 backgrounds, and 9 species. The JSON file is the
canonical character record; the PDF is a rendered output.

SRD attribution, template copyright information, and current licensing limitations
are recorded in
[`THIRD_PARTY_NOTICES.md`](src/pc_wizard/THIRD_PARTY_NOTICES.md).

## Codex contributors

Repository guidance lives in `AGENTS.md`, with task-specific workflows under
`.agents/skills/`. See [`docs/codex.md`](docs/codex.md) for usage and example
prompts.

## Roadmap

The verified project baseline, known limitations, planned phases, and task
checklists are maintained in [`docs/roadmap.md`](docs/roadmap.md).

## License

pc-wizard's original source code is available under the [MIT License](LICENSE).
SRD attribution and character-sheet terms are documented separately in the
[third-party notices](src/pc_wizard/THIRD_PARTY_NOTICES.md).
