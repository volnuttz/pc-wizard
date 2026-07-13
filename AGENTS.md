# pc-wizard contributor guidance

## Project scope

- Build a Python 3.13 CLI that creates D&D characters from
  `assets/SRD_CC_v5.2.1.pdf` and renders them with the separately downloaded
  official `assets/character-sheet.pdf` development fixture.
- Treat the supplied SRD PDF as the authority for game rules. Do not silently mix
  in rules from the Player's Handbook, older SRDs, third-party sources, or memory.
- Keep JSON as the canonical character record. The filled PDF is a rendered view.
- The current product scope is level-1 character creation unless a task explicitly
  expands it.

## Repository map

- `src/pc_wizard/rules.py`: SRD-derived data and rule metadata.
- `src/pc_wizard/models.py`: Pydantic models and derived character values.
- `src/pc_wizard/wizard.py`: interactive Questionary workflow.
- `src/pc_wizard/pdf.py`: character-sheet AcroForm mapping and rendering.
- `src/pc_wizard/cli.py`: Typer commands and Rich output.
- `tests/`: unit and PDF integration tests.
- `CHANGELOG.md`: versioned user-visible release history.
- `docs/codex.md`: Codex usage and repository skills.
- `docs/releasing.md`: versioning, release recovery, and signing policy.
- `docs/roadmap.md`: current baseline, known gaps, phases, and pending tasks.
- `scripts/`: frozen-binary smoke testing and release packaging.
- `pc-wizard.spec` / `pc-wizard-onefile.spec`: PyInstaller build definitions.
- `.github/workflows/`: cross-platform quality, binary, checksum, and release jobs.
- `.agents/skills/`: reusable Codex workflows for this repository.

## Working rules

- Use `uv` for environments, dependencies, and command execution. Do not add pip,
  Poetry, or requirements-file workflows.
- Use modern Python 3.13 annotations and keep Pyright strict mode clean.
- Put validation and derived game logic in models or rule helpers, not in CLI
  presentation code.
- Keep prompts thin: gather choices in `wizard.py`, validate in Pydantic models,
  and render from a completed `Character`.
- Preserve user changes and avoid modifying the source PDFs.
- Keep the official character-sheet template out of wheels, sdists, standalone
  executables, and release assets. Require it through `--template`.
- Keep `docs/roadmap.md` current when completing, adding, blocking, or
  reprioritizing roadmap work. Mark tasks complete only after verification.
- Add or update tests for every behavior change. PDF mapping changes require a
  write/read-back test against the supported official template used as the local
  development fixture.
- When adding dependencies, explain why the standard library and current
  dependencies are insufficient.

## Required verification

Run the smallest relevant tests while iterating. Before handing off code changes,
run the full gate:

```console
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Also run `uv run pc-wizard --help` after changing commands or options. For an
interactive-flow change, exercise the affected path or test the prompt adapters.
For packaging or release changes, build the affected PyInstaller spec and run
`scripts/smoke_binary.py`; validate workflow YAML when Actions files change.

## Repository skills

- Use `$add-srd-content` for SRD-derived classes, backgrounds, species, spells,
  equipment, feats, or character-creation rules.
- Use `$maintain-pdf-mapping` for `character-sheet.pdf`, AcroForm fields, or
  `src/pc_wizard/pdf.py` changes.
- Use `$verify-pc-wizard` for pre-handoff validation or diagnosing quality-gate
  failures.
