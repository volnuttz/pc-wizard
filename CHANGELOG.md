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
- Dragonborn characters choose a draconic ancestry, which determines their
  Breath Weapon and Damage Resistance damage type.
- Elf characters choose an Elven Lineage, lineage spellcasting ability, and Keen
  Senses skill proficiency.
- Gnome characters choose a Forest or Rock Gnomish Lineage and a lineage
  spellcasting ability.
- Goliath characters choose one of the six SRD Giant Ancestries and retain its
  supernatural boon details.
- Human characters choose an additional skill proficiency and one of the four SRD
  Origin feats.
- Tiefling characters choose an Abyssal, Chthonic, or Infernal legacy and its
  spellcasting ability.
- Species choices now determine speed, Darkvision, damage resistances, cantrips,
  level-gated prepared spells, displayed traits, and character-sheet values.
- Origin feats now apply their level-1 benefits and required choices: Alert adds
  proficiency to Initiative, Magic Initiate selects validated spells, Skilled
  grants three skill/tool proficiencies, and Savage Attacker is retained in the
  character's rendered feat traits.
- All level-1 class choices are now interactive and model-validated, including
  weapon masteries, tools and instruments, Divine and Primal Orders, Fighter
  Fighting Style, Rogue Expertise and language, class spells, the Wizard
  spellbook, and eligible level-1 Eldritch Invocations.
- Class selections and weapon mastery properties are included in the rendered
  class-features field.
- Class and background starting-equipment packages can be chosen independently
  from their starting-gold alternatives, including both Fighter packages and
  the Bard's package instrument choice.
- Starting inventories now model weapons, armor, shields, ammunition, gear, and
  coins as structured derived data.
- Armor Class now accounts for armor, Dexterity limits, shields, Barbarian and
  Monk Unarmored Defense, and the Defense Fighting Style; heavy armor can reduce
  Speed when its Strength requirement is unmet.
- Weapon attacks now include proficiency, attack and damage modifiers, range,
  properties, quantity, Fighting Style adjustments, and unlocked mastery notes.
- Level-1 class spellcasting ability, modifier, save DC, attack bonus, spell-slot
  count, and recovery cadence are calculated from SRD class rules.
- Rendered equipment summaries and Armor Class now reflect the selected starting
  equipment rather than static package descriptions.

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
