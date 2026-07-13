# pc-wizard

An interactive command-line wizard for creating level-1 D&D characters using the
rules in `SRD_CC_v5.2.1.pdf`. It saves validated JSON and fills the supplied
`character-sheet.pdf` AcroForm.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Install and run

```console
uv sync
uv run pc-wizard create
```

By default, creation writes `character.json` and `character-sheet-filled.pdf`.
Paths can be changed:

```console
uv run pc-wizard create --output my-hero.pdf --json my-hero.json
uv run pc-wizard render my-hero.json --output another-copy.pdf
```

Run `uv run pc-wizard --help` for all options. Cancel the interactive wizard at
any prompt with Ctrl-C.

## Development

```console
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

The current wizard targets level-1 creation and the player options published in
SRD 5.2.1: 12 classes, 4 backgrounds, and 9 species. The JSON file is the
canonical character record; the PDF is a rendered output.

## Codex contributors

Repository guidance lives in `AGENTS.md`, with task-specific workflows under
`.agents/skills/`. See [`docs/codex.md`](docs/codex.md) for usage and example
prompts.

## Roadmap

The verified project baseline, known limitations, planned phases, and task
checklists are maintained in [`docs/roadmap.md`](docs/roadmap.md).
