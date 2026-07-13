# Changelog

All notable changes to pc-wizard are documented here. The project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Interactive 27-point ability-score point-buy with live remaining-point feedback.
- Background ability-increase prompts omit choices that would raise a score above
  20.
- Ability-generation methods and background increases are validated at the model
  boundary before character construction.
- Optional backstory, appearance, and personality prompts with JSON persistence.
- Explicit Small/Medium selection for Human and Tiefling characters, including
  character-sheet rendering.

## [0.1.0] - 2026-07-13

### Added

- Interactive level-1 SRD 5.2.1 character creation with JSON persistence.
- Two-page AcroForm rendering using a required, separately downloaded official
  character-sheet template.
- Wheel, source distribution, and `uv tool` installation workflows.
- MIT licensing and SRD/character-sheet third-party notices.
- Linux x86-64, Windows x86-64, macOS Apple Silicon, and macOS Intel standalone
  executables with SHA-256 files.
- Cross-platform quality, native-binary, and tag-triggered GitHub Release jobs.

[0.1.0]: https://github.com/volnuttz/pc-wizard/releases/tag/v0.1.0
