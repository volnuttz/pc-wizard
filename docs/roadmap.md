# pc-wizard project roadmap

Last reviewed: 2026-07-13

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

Version: `0.1.0`

The repository currently provides:

- [x] Python 3.13 project managed with uv
- [x] Typer CLI with `create` and `render` commands
- [x] Questionary interactive character-creation flow
- [x] Rich terminal output
- [x] Pydantic v2 character validation and JSON serialization
- [x] pypdf AcroForm rendering into the supplied two-page character sheet
- [x] All 12 SRD classes represented at a basic level
- [x] All 4 SRD backgrounds represented
- [x] All 9 SRD species represented at a basic level
- [x] Suggested class arrays, standard-array assignment, and random score generation
- [x] Background ability increases
- [x] Class and background skill selection
- [x] Language and alignment selection
- [x] Derived ability modifiers, saving throws, skill modifiers, HP, initiative,
  proficiency bonus, base AC, and Passive Perception
- [x] JSON save and reload
- [x] Wheel and source-distribution builds
- [x] MIT license and complete package metadata
- [x] Clean wheel installation and outside-repository `create`/`render` workflows
- [x] Ruff, Pyright strict mode, pytest, and repository-local Codex guidance

Verified on 2026-07-13:

```text
Ruff format: passed
Ruff lint: passed
Pyright strict: 0 errors
pytest: 11 passed
CLI help smoke tests: passed
uv wheel and sdist builds: passed
Clean wheel create/render smoke tests: passed
```

## Known limitations

### Rules and character creation

- Armor Class currently uses only `10 + Dexterity modifier`; armor, shields, and
  alternate class calculations are not applied.
- The model accepts levels 1–20, but the creation workflow and most calculations
  only implement level 1.
- Background increases are validated only when the final `AbilityScores` model is
  built; the prompt should prevent scores above 20.
- Point-buy ability generation is not implemented.
- Species subchoices and granted choices are not modeled.
- Class feature choices are not modeled.
- Starting-equipment alternatives and starting-gold choices are not interactive.
- Weapons, attacks, damage, coins, spells, and spell slots are incomplete.
- Expertise and similar selectable proficiency upgrades are not implemented.

### Validation and persistence

- Alignment, skills, and languages are not fully validated against SRD choices.
- Cross-field rules, such as exact proficiency counts and allowed background
  increases, are not enforced by the model.
- Character JSON has no explicit schema version or migration strategy.
- An interrupted wizard cannot be resumed.

### PDF output

- Many checkbox fields are not populated, including skill, saving-throw, and armor
  proficiencies.
- Weapons, damage, coins, spellcasting values, spell lists, and spell slots are not
  fully rendered.
- Tests verify stored AcroForm values but do not perform visual regression checks.
- The official character-sheet template must be downloaded separately and supplied
  with `--template`; direct download URLs may change.

### Distribution

- A Linux x86-64 one-directory executable has been built and smoke-tested locally,
  but there are no automated cross-platform or published release builds.

## Phase 1: Reliable packaging and runtime assets

Goal: make the Python package installable and usable outside the repository.

Status: complete and verified on 2026-07-13.

- [x] Keep the official character sheet out of package distributions.
- [x] Require an explicit `--template` path for `create` and `render`.
- [x] Validate the template before starting character creation or rendering.
- [x] Document the official download page and a changeable direct-download URL.
- [x] Exclude `SRD_CC_v5.2.1.pdf` and `character-sheet.pdf` from wheel and source
  distributions.
- [x] Define intentional sdist contents rather than relying on automatic inclusion.
- [x] Add `pc-wizard --version`.
- [x] Add package metadata: MIT license, authors, classifiers, URLs, and keywords.
- [x] Add an SRD attribution and third-party notices document.
- [x] Test wheel installation in a clean isolated environment.
- [x] Test `create` and `render` from a directory outside the repository.
- [x] Document `uv tool` install, upgrade, and uninstall instructions.

Exit criteria:

- A clean wheel installation can create and render a character with a separately
  downloaded official template.
- The wheel and sdist contain only intentional, redistributable files.

## Phase 2: Self-contained executables and releases

Goal: distribute `pc-wizard` to users who do not have Python or uv installed.

Status: in progress; the Linux x86-64 one-directory milestone is verified.

- [x] Add PyInstaller as a development/build dependency.
- [x] Add a deterministic PyInstaller spec file.
- [x] Build and smoke-test a Linux x86-64 one-directory bundle first.
- [x] Build and smoke-test a Linux x86-64 one-file executable that accepts the
  required external template.
- [x] Verify output paths and template validation in frozen and normal modes.
- [x] Add reusable binary smoke tests for `--help`, `--version`, and `render`.
- [x] Add GitHub Actions quality checks on Linux, Windows, and macOS.
- [ ] Add native executable builds for:
  - [x] Linux x86-64
  - [ ] Windows x86-64
  - [ ] macOS Apple Silicon
  - [ ] macOS Intel, if supported by the release environment
- [ ] Publish versioned artifacts through GitHub Releases.
- [ ] Publish SHA-256 checksums.
- [ ] Document platform installation, upgrade, and removal steps.
- [ ] Evaluate signing and notarization for Windows and macOS.

Exit criteria:

- A user can download one artifact for their platform, run `pc-wizard`, and create
  a PDF without installing Python, uv, or dependencies.
- Every published executable is built and smoke-tested on its target operating
  system.

## Phase 3: Complete SRD level-1 creation

Goal: implement the meaningful choices and calculations required for a complete
level-1 SRD character.

### Ability scores and general details

- [ ] Add 27-point point-buy with live remaining-point feedback.
- [ ] Prevent background increases from exceeding 20 during prompting.
- [ ] Validate ability generation and increases at the model boundary.
- [ ] Add optional backstory, appearance, and personality prompts.
- [ ] Add explicit Small/Medium selection where the species allows it.

### Species choices

- [ ] Dragonborn ancestry and damage type
- [ ] Elf lineage, spellcasting ability, and Keen Senses skill
- [ ] Gnome lineage and spellcasting ability
- [ ] Goliath ancestry
- [ ] Human additional skill and Origin feat
- [ ] Tiefling legacy and spellcasting ability
- [ ] Apply choice-dependent speed, senses, resistances, spells, and traits

### Class choices

- [ ] Barbarian weapon masteries
- [ ] Bard instruments, Expertise, cantrips, and prepared spells
- [ ] Cleric Divine Order, cantrips, and prepared spells
- [ ] Druid Primal Order, cantrips, and prepared spells
- [ ] Fighter Fighting Style and weapon masteries
- [ ] Monk artisan tool and weapon mastery choices
- [ ] Paladin weapon masteries and prepared spells
- [ ] Ranger Expertise, weapon masteries, and prepared spells
- [ ] Rogue Expertise and weapon masteries
- [ ] Sorcerer cantrips and prepared spells
- [ ] Warlock invocation, cantrips, and prepared spells
- [ ] Wizard cantrips, spellbook spells, and prepared spells

### Equipment and combat values

- [ ] Support class equipment package or starting gold.
- [ ] Support background equipment package or 50 GP.
- [ ] Model individual weapons, armor, shields, gear, ammunition, and coins.
- [ ] Calculate AC from equipped armor, shields, and class features.
- [ ] Calculate weapon attack bonuses, damage modifiers, ranges, and properties.
- [ ] Calculate spellcasting modifier, save DC, and attack bonus.
- [ ] Model level-1 spell slots and prepared spells.

Exit criteria:

- Every level-1 choice required by the supplied SRD is represented or explicitly
  documented as intentionally deferred.
- Derived values agree with SRD examples and focused tests.

## Phase 4: Complete character-sheet rendering

Goal: render all implemented character data accurately and visibly.

- [ ] Map and fill saving-throw proficiency checkboxes.
- [ ] Map and fill skill proficiency and Expertise indicators.
- [ ] Map and fill armor-training checkboxes.
- [ ] Fill weapon names, attack bonuses, damage, type, and notes.
- [ ] Fill equipment and coin fields structurally.
- [ ] Fill spellcasting ability, modifier, save DC, and attack bonus.
- [ ] Fill cantrips, prepared spells, and spell-slot fields.
- [ ] Fill class-specific resources where the template supports them.
- [ ] Confirm long text fits or uses appropriate font sizing.
- [ ] Add representative PDF read-back tests for martial and spellcasting characters.
- [ ] Add visual or rendered-page regression testing.

Exit criteria:

- A generated sheet contains all implemented character information in the correct
  fields and remains readable in common PDF viewers.

## Phase 5: Model durability and user experience

Goal: make saved characters reliable and the wizard pleasant to use over time.

- [ ] Add `schema_version` to character JSON.
- [ ] Define migrations for older schemas.
- [ ] Validate alignment, skills, languages, and cross-field rules.
- [ ] Replace unconstrained rule strings with enums or validated identifiers where
  this improves correctness.
- [ ] Separate user selections from derived values explicitly.
- [ ] Add save-and-resume support for incomplete creation sessions.
- [ ] Add a final review screen before writing files.
- [ ] Add back navigation or confirmation for destructive choice changes.
- [ ] Add non-interactive creation from a complete JSON input.
- [ ] Add `validate` and `show` commands.
- [ ] Improve actionable error messages for missing or invalid templates and JSON.
- [ ] Avoid overwriting existing outputs without confirmation or `--force`.

Exit criteria:

- Old character files either migrate cleanly or fail with a clear compatibility
  message.
- Users can review, resume, validate, and safely render characters.

## Phase 6: Engineering and release practices

Goal: make changes and releases repeatable, reviewable, and safe.

- [ ] Add continuous integration for Ruff, Pyright, pytest, package builds, and
  clean-install tests.
- [ ] Add a test-coverage report and agree on a minimum threshold.
- [ ] Extract reusable character fixtures for tests.
- [ ] Add parameterized tests for every class, background, and species.
- [ ] Add property-based tests for scores, modifiers, and point-buy constraints.
- [ ] Add dependency update automation.
- [ ] Add dependency vulnerability review or audit automation.
- [ ] Add a changelog and release checklist.
- [ ] Adopt semantic versioning and tagged releases.
- [ ] Add contributor and code-of-conduct documents if outside contributors are
  expected.
- [ ] Add issue and pull-request templates.
- [ ] Add release notes describing schema or output compatibility changes.

Exit criteria:

- Pull requests receive automated quality feedback.
- A version tag produces reviewed, reproducible release artifacts.

## Suggested milestone order

1. Package the runtime template and prove a clean wheel installation.
2. Produce and test one Linux standalone executable.
3. Add cross-platform CI and release artifacts.
4. Complete level-1 choices and calculations in small vertical slices.
5. Expand PDF coverage alongside each completed rule slice.
6. Add schema migration and resume support before distributing many saved files.

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
