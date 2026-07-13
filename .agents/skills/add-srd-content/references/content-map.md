# SRD content map

## Code responsibilities

- `rules.py`: immutable source data and rule metadata.
- `models.py`: schema validation, calculated values, and JSON round trips.
- `wizard.py`: ordering and collection of interactive choices.
- `pdf.py`: projection of a valid character onto the sheet.
- `cli.py`: command boundaries, errors, and terminal presentation.

## Character-creation sequence

Follow SRD 5.2.1 pages 19–23: choose class; determine background, species, and
languages; determine ability scores; choose alignment; fill derived details.

## Current invariants

- Package: `pc_wizard`; command: `pc-wizard`.
- Python: `>=3.13,<3.14`.
- Characters start at level 1 and 0 XP.
- Background skill proficiencies combine with non-duplicating class choices.
- Background increases affect only its three listed abilities and cannot raise a
  score above 20.
- Proficiency bonus is derived from level.
- Dwarf toughness contributes to maximum HP.
- Human and Tiefling explicitly choose Small or Medium; every other current SRD
  species has a fixed size.
- JSON is canonical; PDFs are generated artifacts.
- Character JSON uses only the current schema. Do not add schema versions,
  migrations, compatibility aliases, or legacy-shape fallbacks.
- The official character-sheet template is external and always supplied through
  `--template`; it is never a package or release asset.

## Test routing

- Rule calculations and validation: `tests/test_models.py`.
- Score generation and prompt helpers: `tests/test_wizard.py`.
- Field projection and PDF write/read-back: `tests/test_pdf.py`.
