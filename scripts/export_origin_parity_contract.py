"""Export Python-oracle derived values for every background and species."""

from __future__ import annotations

import json
import runpy

from pc_wizard.models import Character, MagicInitiateChoice
from pc_wizard.rules import BACKGROUNDS, SPECIES


def record(character: Character) -> dict[str, object]:
    return {
        "character": character.model_dump(mode="json"),
        "derived": character.derived_values.model_dump(mode="json"),
    }


def main() -> None:
    base = runpy.run_path("tests/test_models.py")["character"].__wrapped__()
    backgrounds: list[dict[str, object]] = []
    for background in sorted(BACKGROUNDS):
        values = base.model_dump()
        values["background"] = background
        values["magic_initiate_choices"] = {
            "Acolyte": [
                MagicInitiateChoice(
                    spell_list="Cleric",
                    spellcasting_ability="wisdom",
                    cantrips=("Guidance", "Light"),
                    level_one_spell="Bless",
                )
            ],
            "Criminal": [],
            "Sage": base.magic_initiate_choices,
            "Soldier": [],
        }[background]
        backgrounds.append(record(Character.model_validate(values)))
    species_cases: list[dict[str, object]] = []
    species_choices = {
        "Dragonborn": {"dragonborn_ancestry": "Gold"},
        "Elf": {
            "elf_lineage": "High Elf",
            "elf_spellcasting_ability": "intelligence",
            "elf_keen_senses_skill": "Perception",
        },
        "Gnome": {"gnome_lineage": "Forest Gnome", "gnome_spellcasting_ability": "intelligence"},
        "Goliath": {"goliath_ancestry": "Stone Giant"},
        "Human": {"human_skill": "Perception", "human_origin_feat": "Alert"},
        "Tiefling": {"tiefling_legacy": "Infernal", "tiefling_spellcasting_ability": "charisma"},
    }
    species_fields = (
        "dragonborn_ancestry",
        "elf_lineage",
        "elf_spellcasting_ability",
        "elf_keen_senses_skill",
        "gnome_lineage",
        "gnome_spellcasting_ability",
        "goliath_ancestry",
        "human_skill",
        "human_origin_feat",
        "tiefling_legacy",
        "tiefling_spellcasting_ability",
    )
    for species in sorted(SPECIES):
        values = base.model_dump()
        values.update(species=species, size=SPECIES[species].sizes[0])
        values.update({field: None for field in species_fields})
        values.update(species_choices.get(species, {}))
        species_cases.append(record(Character.model_validate(values)))
    print(
        json.dumps({"backgrounds": backgrounds, "species": species_cases}, indent=2, sort_keys=True)
    )


if __name__ == "__main__":
    main()
