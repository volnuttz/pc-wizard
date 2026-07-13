from pathlib import Path

import pytest
from pydantic import ValidationError

from pc_wizard.models import AbilityScores, Character


@pytest.fixture
def character() -> Character:
    return Character(
        name="Ada",
        character_class="Wizard",
        background="Sage",
        species="Dwarf",
        alignment="Neutral Good",
        abilities=AbilityScores(
            strength=8, dexterity=12, constitution=14, intelligence=17, wisdom=15, charisma=10
        ),
        skills={"Arcana", "History", "Investigation", "Nature"},
        languages=["Common", "Dwarvish", "Elvish"],
    )


def test_derived_values(character: Character) -> None:
    assert character.proficiency_bonus == 2
    assert character.hit_points == 9
    assert character.armor_class == 11
    assert character.skill_modifier("Arcana") == 5
    assert character.saving_throw("intelligence") == 5
    assert character.passive_perception == 12


def test_json_round_trip(character: Character, tmp_path: Path) -> None:
    path = tmp_path / "ada.json"
    character.save_json(path)
    assert Character.load_json(path) == character


def test_rejects_unknown_class() -> None:
    with pytest.raises(ValidationError, match="unknown SRD class"):
        Character(
            name="Ada",
            character_class="Artificer",
            background="Sage",
            species="Human",
            alignment="Neutral",
            abilities=AbilityScores(
                strength=10, dexterity=10, constitution=10, intelligence=10, wisdom=10, charisma=10
            ),
        )
