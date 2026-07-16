# CLI compatibility contract v1

Status: frozen for the Python-to-Rust migration. The Python 0.2.1 behavior is the
reference. Additive commands or options are permitted only when they do not alter
these scenarios.

## Commands

| Surface | Required behavior |
| --- | --- |
| `pc-wizard --help` | exits 0; describes `create`, `show`, and `--version`. |
| `pc-wizard --version` | exits 0; stdout is `pc-wizard <installed-version>`. |
| `pc-wizard show CHARACTER_JSON` | reads a complete current-schema JSON file and prints selected plus derived values. Missing or invalid files exit 1 and identify the supplied path. |
| `pc-wizard create --template TEMPLATE --from-json INPUT --json JSON --output PDF --force` | validates the template, validates input JSON, writes canonical JSON and a filled PDF, exits 0, and identifies both outputs. |
| `pc-wizard create --template MISSING ...` | exits 1 before prompting or overwriting output, with a template error. |

## Shared behavior

- `create --template` is mandatory for all creation modes.
- Existing `--output` or `--json` files require confirmation unless `--force` is
  supplied. A declined confirmation cancels the command without overwriting.
- Ctrl-C during creation exits 130 and reports the checkpoint state.
- User-facing operational and validation failures are printed to stdout with an
  `Error:` marker and exit 1. Argument parsing failures follow the CLI parser's
  normal nonzero usage-error behavior.
- ANSI styling and table border geometry are presentation details; contract tests
  compare plain text only.
- `character.json` is the current schema only. Unknown fields and invalid enum or
  cross-field combinations are rejected; old-schema migration is not implied.

## Scenario fixtures

| ID | Fixture | Expected result |
| --- | --- | --- |
| `help` | none | exit 0; command names and version option present |
| `version` | none | exit 0; version line present |
| `show-complete` | `tests/fixtures/character.json` | exit 0; name, HP 9, AC 14 present |
| `show-missing` | absent path | exit 1; path and `Error:` present |
| `create-from-json` | complete character + supported template | exit 0; JSON and PDF written |
| `template-missing` | absent template | exit 1; no output files written |

