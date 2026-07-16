# Canonical character JSON contract v1

Status: frozen for migration. A character document contains selections only;
derived values and PDF fields are reproducible projections, not persisted data.
All objects reject unknown properties. The reference parser is Pydantic v2, but
the Rust implementation must preserve the accepted/rejected documents and the
error categories captured in the fixtures below.

## Top-level document

Required fields are `name`, `character_class`, `background`, `species`, `size`,
`alignment`, `abilities`, `class_skills`, and `selected_languages`. The remaining
fields are optional with these defaults:

| Fields | Default |
| --- | --- |
| species-choice fields (`dragonborn_ancestry` through `tiefling_spellcasting_ability`) | `null` |
| `class_choices` | empty choice object |
| `class_equipment_option`, `background_equipment_option` | `"A"` |
| `bard_starting_instrument`, `backstory`, `appearance`, `personality` | `null` |
| `tool_proficiencies`, `magic_initiate_choices`, `skilled_proficiencies` | empty collection |
| `level`, `xp` | `1`, `0` |

`abilities` is an object with the six ability names, each an integer from 3 to
20. `selected_languages` contains exactly two distinct values. `class_skills`
and all proficiency/spell/mastery collections are sets semantically; their JSON
array order is not significant on input or a compatibility requirement on output.
`complete-rogue-v1.json` fixes the values, not serializer ordering.

## Closed value sets

- `size`: `Small`, `Medium`
- `alignment`: `Lawful Good`, `Neutral Good`, `Chaotic Good`, `Lawful Neutral`,
  `Neutral`, `Chaotic Neutral`, `Lawful Evil`, `Neutral Evil`, `Chaotic Evil`
- spellcasting ability: `intelligence`, `wisdom`, `charisma`
- standard language: `Common Sign Language`, `Draconic`, `Dwarvish`, `Elvish`,
  `Giant`, `Gnomish`, `Goblin`, `Halfling`, `Orc`
- Dragonborn ancestry: `Black`, `Blue`, `Brass`, `Bronze`, `Copper`, `Gold`,
  `Green`, `Red`, `Silver`, `White`
- Elf lineage: `Drow`, `High Elf`, `Wood Elf`; Keen Senses: `Insight`,
  `Perception`, `Survival`
- Gnome lineage: `Forest Gnome`, `Rock Gnome`; Goliath ancestry: `Cloud Giant`,
  `Fire Giant`, `Frost Giant`, `Hill Giant`, `Stone Giant`, `Storm Giant`
- Tiefling legacy: `Abyssal`, `Chthonic`, `Infernal`
- Origin feat: `Alert`, `Magic Initiate`, `Savage Attacker`, `Skilled`
- Magic Initiate list: `Cleric`, `Druid`, `Wizard`; Divine Order: `Protector`,
  `Thaumaturge`; Primal Order: `Magician`, `Warden`
- `background_equipment_option`: `A`, `Gold`

Classes, backgrounds, species names, skills, tools, equipment, spells, fighting
styles, invocations, and class-equipment package identifiers are validated
against the SRD-derived tables. They are deliberately not duplicated here; the
port inventory must retain their source provenance.

## Cross-field validation and errors

Species-only choices must be present for their matching species and absent for
every other species. Background/feat/class choices, distinct languages, skill
counts, spell selections, starting equipment, ability limits, and level bounds
are cross-field validated. Whitespace-only optional details normalize to `null`.

Errors are not a stable serialization format: implementations may change wording
or ordering. Compatibility requires the same exit class (input rejected), field
location when one exists, and stable error category. `invalid-unknown-field-v1`
requires the category `extra_forbidden` at location `migration_probe`.

## Versioning and compatibility

This document and every `*-v1.json` fixture form schema version 1. A breaking
change requires a new contract version and an explicit reader migration; silently
accepting unknown fields or reinterpreting current values is prohibited.
