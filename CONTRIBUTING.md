# Contributing to pc-wizard

Thanks for helping improve pc-wizard. Please read the repository guidance in
[`AGENTS.md`](AGENTS.md) before making changes.

## Development setup

Use Python 3.13 and uv from the repository root:

```console
uv sync --all-groups
```

The official character-sheet PDF is a development fixture only. Do not modify
the supplied PDFs or include them in distributions.

## Making changes

- Treat `assets/SRD_CC_v5.2.1.pdf` as the authority for game rules.
- Keep JSON as the canonical character record; the PDF is a rendered view.
- Keep validation and derived values in models or rule helpers rather than CLI
  presentation code.
- Add or update tests for every behavior change.
- PDF mapping changes require a write/read-back test using the supported official
  template fixture.
- Explain any new dependency when the standard library and current dependencies
  are insufficient.
- Update `docs/roadmap.md` and `CHANGELOG.md` when the change affects roadmap
  status or user-visible behavior.

## Checks before opening a pull request

```console
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Also run the relevant CLI, PDF, binary, packaging, or workflow checks for the
area you changed. Use the pull-request template to summarize scope and results.

## Pull requests

Keep pull requests focused, describe the user-visible effect, and include
reproduction steps for fixes. Cite the applicable SRD section for rule changes.
Do not include private character data, downloaded templates, build artifacts, or
generated coverage files.

By submitting a contribution, you agree that it may be distributed under the
project's [MIT License](LICENSE).
