"""Export one Python-oracle character and derived projection for every class."""

from __future__ import annotations

import json
import runpy

from pc_wizard.models import Character

SKILLS = {
    "Barbarian": {"Nature", "Perception"},
    "Bard": {"Investigation", "Nature", "Perception"},
    "Cleric": {"Insight", "Medicine"},
    "Druid": {"Nature", "Perception"},
    "Fighter": {"Perception", "Survival"},
    "Monk": {"Insight", "Stealth"},
    "Paladin": {"Insight", "Persuasion"},
    "Ranger": {"Nature", "Perception", "Survival"},
    "Rogue": {"Investigation", "Perception", "Persuasion", "Stealth"},
    "Sorcerer": {"Insight", "Persuasion"},
    "Warlock": {"Investigation", "Nature"},
    "Wizard": {"Investigation", "Nature"},
}


def main() -> None:
    tests = runpy.run_path("tests/test_models.py")
    base = tests["character"].__wrapped__()
    parameterized = tests["test_validates_level_one_choices_for_every_class"]
    choices = parameterized.pytestmark[0].args[1]
    output: list[dict[str, object]] = []
    for class_name, class_choices in choices:
        values = base.model_dump()
        values.update(
            character_class=class_name,
            class_choices=class_choices,
            class_skills=SKILLS[class_name],
        )
        if class_name == "Bard":
            values["bard_starting_instrument"] = "Musical Instrument (Flute)"
        character = Character.model_validate(values)
        output.append(
            {
                "character": character.model_dump(mode="json"),
                "derived": character.derived_values.model_dump(mode="json"),
                "class_resources": [
                    resource.model_dump(mode="json") for resource in character.class_resources
                ],
            }
        )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
