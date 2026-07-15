# pc-wizard project roadmap

Last reviewed: 2026-07-15

This document records the current project state, known gaps, planned phases, and
completion criteria. Update it when a task is completed, reprioritized, added, or
removed. The source code and tests remain authoritative when this document and the
implementation disagree.

## Status legend

- `[x]` Complete and verified
- `[ ]` Planned or pending
- `[~]` In progress
- `[!]` Blocked or requires a decision

## Current baseline

Version: `0.2.1`

The repository currently provides:

- [x] Python 3.13 project managed with uv
- [x] Typer CLI with interactive/non-interactive `create` and `show` commands
- [x] Questionary interactive character-creation flow
- [x] Contextual details for highlighted rule and equipment choices
- [x] Rich terminal output
- [x] Pydantic v2 character and creation-workflow validation with JSON
  serialization
- [x] pypdf AcroForm rendering into the separately downloaded official two-page
  character sheet
- [x] All 12 SRD classes represented at a basic level
- [x] All 4 SRD backgrounds represented
- [x] All 9 SRD species represented at a basic level
- [x] Suggested class arrays, standard-array assignment, random score generation,
  and 27-point point-buy with live budget feedback
- [x] Background ability increases with prompt-time score-cap enforcement
- [x] Class and background skill selection
- [x] Language, alignment, and Human/Tiefling Small-or-Medium selection
- [x] Optional backstory, appearance, and personality details
- [x] Derived ability modifiers, saving throws, skill modifiers, HP, initiative,
  proficiency bonus, base AC, and Passive Perception
- [x] JSON save/reload, incomplete-session checkpoints, resume, and final review
- [x] Wheel and source-distribution builds
- [x] MIT license and complete package metadata
- [x] Clean wheel installation and outside-repository `create` workflow
- [x] Published v0.1.0 native executables and SHA-256 files for Linux x86-64,
  Windows x86-64, macOS Apple Silicon, and macOS Intel
- [x] Ruff, Pyright strict mode, pytest, and repository-local Codex guidance

Verified on 2026-07-15:

```text
Ruff format: passed
Ruff lint: passed
Pyright strict: 0 errors
pytest: 157 passed
Coverage: 89.02% line coverage (85% minimum)
CLI help smoke tests (`create` and `show`): passed
uv wheel and sdist builds: passed
Clean wheel create smoke test: passed
Cross-platform native binary builds and smoke tests: passed
GitHub Release v0.1.0 with SHA-256 files: published
```

## Known limitations

### Rules and character creation

- The model accepts levels 1–20, but the creation workflow and most calculations
  only implement level 1.
- Spending starting gold on custom equipment is not yet interactive; gold-route
  characters retain their unspent coins.
- Later-level class choices remain outside the current level-1 scope.

### Validation and persistence

- Character JSON intentionally supports only the current schema. Files produced by
  older releases are not migrated and may fail validation after the schema changes.

### PDF output

- Death-save and magic-item-attunement trackers remain blank because character
  creation does not record active adventuring-state values for them.
- The official character-sheet template must be downloaded separately and supplied
  with `--template`; direct download URLs may change.

### Distribution

- Native executables are unsigned, so Windows SmartScreen and macOS Gatekeeper may
  warn or block first launch.

## Phase 1: Reliable packaging and runtime assets

Goal: make the Python package installable and usable outside the repository.

Status: complete and verified on 2026-07-13.

- [x] Keep the official character sheet out of package distributions.
- [x] Require an explicit `--template` path for `create`.
- [x] Validate the template before starting character creation or rendering.
- [x] Document the official download page and a changeable direct-download URL.
- [x] Exclude `assets/SRD_CC_v5.2.1.pdf` and `assets/character-sheet.pdf` from
  wheel and source distributions.
- [x] Define intentional sdist contents rather than relying on automatic inclusion.
- [x] Add `pc-wizard --version`.
- [x] Add package metadata: MIT license, authors, classifiers, URLs, and keywords.
- [x] Add an SRD attribution and third-party notices document.
- [x] Test wheel installation in a clean isolated environment.
- [x] Test `create` from a directory outside the repository.
- [x] Document `uv tool` install, upgrade, and uninstall instructions.

Exit criteria:

- A clean wheel installation can create and render a character with a separately
  downloaded official template.
- The wheel and sdist contain only intentional, redistributable files.

## Phase 2: Self-contained executables and releases

Goal: distribute `pc-wizard` to users who do not have Python or uv installed.

Status: complete and verified on 2026-07-13 with the published v0.1.0 release.

- [x] Add PyInstaller as a development/build dependency.
- [x] Add a deterministic PyInstaller spec file.
- [x] Build and smoke-test a Linux x86-64 one-directory bundle first.
- [x] Build and smoke-test a Linux x86-64 one-file executable that accepts the
  required external template.
- [x] Verify output paths and template validation in frozen and normal modes.
- [x] Add reusable binary smoke tests for `--help`, `--version`, and `create`.
- [x] Add GitHub Actions quality checks on Linux, Windows, and macOS.
- [x] Add native executable builds for:
  - [x] Linux x86-64
  - [x] Windows x86-64
  - [x] macOS Apple Silicon
  - [x] macOS Intel
- [x] Publish versioned artifacts through GitHub Releases.
- [x] Publish SHA-256 checksums.
- [x] Document platform installation, upgrade, and removal steps.
- [x] Evaluate signing and notarization for Windows and macOS; unsigned 0.1.0
  artifacts are documented, with signing deferred pending certificates.

Exit criteria:

- A user can download one artifact for their platform, run `pc-wizard`, and create
  a PDF without installing Python, uv, or dependencies.
- Every published executable is built and smoke-tested on its target operating
  system.

## Phase 3: Complete SRD level-1 creation

Goal: implement the meaningful choices and calculations required for a complete
level-1 SRD character.

Status: complete and verified on 2026-07-13.

### Ability scores and general details

- [x] Add 27-point point-buy with live remaining-point feedback.
- [x] Prevent background increases from exceeding 20 during prompting.
- [x] Validate ability generation and increases at the model boundary.
- [x] Add optional backstory, appearance, and personality prompts.
- [x] Add explicit Small/Medium selection where the species allows it.

### Species choices

- [x] Dragonborn ancestry and damage type
- [x] Elf lineage, spellcasting ability, and Keen Senses skill
- [x] Gnome lineage and spellcasting ability
- [x] Goliath ancestry
- [x] Human additional skill and Origin feat
- [x] Tiefling legacy and spellcasting ability
- [x] Apply choice-dependent speed, senses, resistances, spells, and traits

### Feat choices

- [x] Model Origin feat benefits and required subchoices, including Human
  Versatile choices.

### Class choices

- [x] Barbarian weapon masteries
- [x] Bard instruments, cantrips, and prepared spells
- [x] Cleric Divine Order, cantrips, and prepared spells
- [x] Druid Primal Order, cantrips, and prepared spells
- [x] Fighter Fighting Style and weapon masteries
- [x] Monk artisan tool or musical instrument choice
- [x] Paladin weapon masteries and prepared spells
- [x] Ranger weapon masteries and prepared spells
- [x] Rogue Expertise, additional language, and weapon masteries
- [x] Sorcerer cantrips and prepared spells
- [x] Warlock invocation, cantrips, and prepared spells
- [x] Wizard cantrips, spellbook spells, and prepared spells

The supplied SRD grants Bard Expertise at level 2 and Ranger Expertise at levels
2 and 9, and it does not grant Monk Weapon Mastery at level 1. Those previously
listed items were corrected to match the level-1 scope.

### Equipment and combat values

- [x] Support class equipment package or starting gold.
- [x] Support background equipment package or 50 GP.
- [x] Model individual weapons, armor, shields, gear, ammunition, and coins.
- [x] Calculate AC from equipped armor, shields, and class features.
- [x] Calculate weapon attack bonuses, damage modifiers, ranges, and properties.
- [x] Calculate spellcasting modifier, save DC, and attack bonus.
- [x] Model separate class, Magic Initiate, and species spellcasting profiles,
  including slotless casting resources without inventing spell slots.
- [x] Model level-1 spell slots (prepared-spell choices are completed above).

Exit criteria:

- Every level-1 choice required by the supplied SRD is represented or explicitly
  documented as intentionally deferred.
- Derived values agree with SRD examples and focused tests.

## Phase 4: Complete character-sheet rendering

Goal: render all implemented character data accurately and visibly.

Status: complete and verified on 2026-07-13.

- [x] Map and fill saving-throw proficiency checkboxes.
- [x] Map and fill skill proficiency and Expertise indicators.
- [x] Map and fill armor-training checkboxes.
- [x] Fill weapon names, attack bonuses, damage, type, and notes.
- [x] Fill equipment and coin fields structurally.
- [x] Fill spellcasting ability, modifier, save DC, and attack bonus.
- [x] Use class spellcasting as the sheet's primary summary when present; otherwise
  fill it from Magic Initiate or species spellcasting, while listing every
  additional profile and slotless resource in its trait section.
- [x] Fill cantrips, prepared spells, and spell-slot fields.
- [x] Fill spell casting time, range, Concentration, Ritual, Required Material,
  and duration notes for every level-1 creation spell.
- [x] Fill optional backstory, appearance, and personality fields.
- [x] Fill class-specific resources where the template supports them.
- [x] Confirm long text fits or uses appropriate font sizing.
- [x] Add representative PDF read-back tests for martial and spellcasting characters.
- [x] Add visual or rendered-page regression testing.

Exit criteria:

- A generated sheet contains all implemented character information in the correct
  fields and remains readable in common PDF viewers.

## Phase 5: Model durability and user experience

Goal: make current-schema character files reliable and the wizard pleasant to use.

- [x] Validate alignment, skills, languages, and cross-field rules.
- [x] Replace unconstrained rule strings with enums or validated identifiers where
  this improves correctness.
- [x] Separate user selections from derived values explicitly.
- [x] Add save-and-resume support for incomplete creation sessions.
- [x] Add a final review screen before writing files.
- [x] Add back navigation or confirmation for destructive choice changes.
- [x] Add non-interactive creation from a complete JSON input.
- [x] Add `show` command.
- [x] Improve actionable error messages for missing or invalid templates and JSON.
- [x] Avoid overwriting existing outputs without confirmation or `--force`.
- [x] Show contextual SRD details while highlighting classes, backgrounds,
  species choices, feats, spells, weapons, and equipment.

Status: complete and verified on 2026-07-13.

Exit criteria:

- Current-schema character files validate consistently, and users can review,
  resume, and create PDFs from them.

## Phase 6: Engineering and release practices

Goal: make changes and releases repeatable, reviewable, and safe.

- [~] Continuous integration runs Ruff, Pyright, pytest, and package builds on
  Linux, Windows, and macOS; automate the existing clean-install test procedure.
- [x] Add a test-coverage report and agree on a minimum threshold (85% line
  coverage, reported and enforced in the quality workflow).
- [~] A reusable character JSON fixture supports model and binary smoke tests;
  extract broader fixtures as character coverage grows.
- [x] Add parameterized tests for every class, background, and species.
- [x] Add property-based tests for scores, modifiers, and point-buy constraints.
- [x] Add dependency update automation for uv and GitHub Actions.
- [x] Add dependency vulnerability review or audit automation with pip-audit.
- [x] Add a changelog and release checklist.
- [x] Adopt semantic versioning and tagged releases.
- [x] Add contributor and code-of-conduct documents for outside contributors.
- [x] Add issue and pull-request templates.
- [x] Add release notes describing user-visible behavior and output changes.

Exit criteria:

- Pull requests receive automated quality feedback.
- A version tag produces reviewed, reproducible release artifacts.

## Suggested milestone order

1. [x] Require a separately downloaded template and prove a clean wheel
   installation.
2. [x] Produce and test one Linux standalone executable.
3. [x] Add cross-platform CI and release artifacts.
4. Complete level-1 choices and calculations in small vertical slices.
5. Expand PDF coverage alongside each completed rule slice.
6. Add validation, review, and resume support for the current character schema.

Prefer vertical slices after packaging. For example, complete Fighter choices,
equipment, calculations, PDF fields, and tests together rather than adding every
class prompt first and postponing calculations and rendering.

## Roadmap maintenance

When completing roadmap work:

1. Change the task marker to `[x]` only after implementation and relevant tests
   pass.
2. Update the `Last reviewed` date.
3. Add newly discovered work to the appropriate phase.
4. Record blockers with `[!]` and a short explanation.
5. Keep implementation details in issues or pull requests; keep this document at
   milestone and task level.
6. Update the current baseline when a release changes supported behavior.
7. Run the repository quality gate before committing roadmap changes that accompany
   code changes.
