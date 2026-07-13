---
name: verify-pc-wizard
description: Validate pc-wizard changes and diagnose failures using the repository's Python 3.13 uv quality gate. Use before handoff, after implementation, when CI or local lint/type/test checks fail, or when CLI and PDF behavior needs targeted verification.
---

# Verify pc-wizard

Run checks from the repository root with `uv`. Fix failures caused by the current
change without rewriting unrelated user work.

## Workflow

1. Inspect the diff and choose targeted checks while iterating:
   - Models or rules: `uv run pytest tests/test_models.py`
   - Wizard prompts: `uv run pytest tests/test_wizard.py`
   - PDF mapping: `uv run pytest tests/test_pdf.py`
   - CLI surface: `uv run pc-wizard --help` and command-specific help
   - Release packaging: `uv run pytest tests/test_package_binary.py`
   - Python distributions: `uv build --clear`, then inspect wheel and sdist
     contents for intentional files only
   - Actions changes: parse every edited workflow as YAML before relying on CI
2. Run the complete gate before handoff:

   ```console
   uv run ruff format --check .
   uv run ruff check .
   uv run pyright
   uv run pytest
   ```

3. If a check fails, report the exact failure, identify whether it is related to
   the current work, make the narrowest appropriate fix, and rerun the failed
   check plus the full gate.
4. For PDF changes, require a real render/read-back test. For CLI changes, require
   help output. For frozen-binary changes, build the affected `.spec` and run:

   ```console
   uv run python scripts/smoke_binary.py \
     PATH_TO_BINARY tests/fixtures/character.json character-sheet.pdf
   ```

   Do not claim interactive behavior was verified when only unit tests ran. Do not
   claim a platform build or GitHub Release passed until its Actions run or release
   assets were inspected.

## Handoff

State the commands run and concise results. Mention checks that could not run and
why. Never describe a partial gate as fully passing.
