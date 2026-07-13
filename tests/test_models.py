from pathlib import Path

import pytest
from pydantic import ValidationError

from pc_wizard.models import (
    AbilityGenerationMethod,
    AbilityScoreGeneration,
    AbilityScores,
    BackgroundAbilityAdjustment,
    Character,
)


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
        backstory="Raised in a mountain archive.",
        appearance="Ink-stained fingers and silver braids.",
        personality="Patient, curious, and direct.",
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


def test_binary_smoke_fixture_is_valid() -> None:
    fixture = Path(__file__).parent / "fixtures" / "character.json"

    character = Character.load_json(fixture)

    assert character.name == "Binary Smoke Test"
    assert character.character_size == "Medium"
    assert character.backstory is None
    assert character.appearance is None
    assert character.personality is None


def test_optional_character_details_are_normalized(character: Character) -> None:
    values = character.model_dump()
    values.update(
        backstory="  A wandering archivist.  ",
        appearance="   ",
        personality="  Quietly determined. ",
    )

    normalized = Character.model_validate(values)

    assert normalized.backstory == "A wandering archivist."
    assert normalized.appearance is None
    assert normalized.personality == "Quietly determined."


def test_species_size_defaults_and_validates(character: Character) -> None:
    values = character.model_dump()
    values.update(species="Human", size="Small")
    assert Character.model_validate(values).character_size == "Small"

    values.update(species="Dwarf", size="Small")
    with pytest.raises(ValidationError, match="invalid size for Dwarf"):
        Character.model_validate(values)

    values.pop("size")
    values["species"] = "Gnome"
    assert Character.model_validate(values).character_size == "Small"


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


def test_validates_each_ability_generation_method() -> None:
    standard = AbilityScores(
        strength=8, dexterity=15, constitution=13, intelligence=14, wisdom=12, charisma=10
    )
    assert (
        AbilityScoreGeneration(
            method=AbilityGenerationMethod.STANDARD_ARRAY,
            scores=standard,
        ).scores
        == standard
    )
    assert (
        AbilityScoreGeneration(
            method=AbilityGenerationMethod.SUGGESTED_ARRAY,
            scores=AbilityScores(
                strength=8, dexterity=12, constitution=13, intelligence=15, wisdom=14, charisma=10
            ),
            character_class="Wizard",
        ).character_class
        == "Wizard"
    )
    assert (
        AbilityScoreGeneration(
            method=AbilityGenerationMethod.RANDOM,
            scores=AbilityScores(
                strength=3, dexterity=18, constitution=12, intelligence=9, wisdom=14, charisma=7
            ),
        ).method
        is AbilityGenerationMethod.RANDOM
    )
    assert (
        AbilityScoreGeneration(
            method=AbilityGenerationMethod.POINT_BUY,
            scores=AbilityScores(
                strength=15, dexterity=15, constitution=13, intelligence=12, wisdom=8, charisma=8
            ),
        ).method
        is AbilityGenerationMethod.POINT_BUY
    )


@pytest.mark.parametrize(
    ("method", "scores", "message"),
    [
        (
            AbilityGenerationMethod.STANDARD_ARRAY,
            AbilityScores(
                strength=15,
                dexterity=14,
                constitution=13,
                intelligence=12,
                wisdom=10,
                charisma=10,
            ),
            "every standard-array value",
        ),
        (
            AbilityGenerationMethod.RANDOM,
            AbilityScores(
                strength=19,
                dexterity=14,
                constitution=13,
                intelligence=12,
                wisdom=10,
                charisma=8,
            ),
            "between 3 and 18",
        ),
        (
            AbilityGenerationMethod.POINT_BUY,
            AbilityScores(
                strength=15,
                dexterity=14,
                constitution=13,
                intelligence=12,
                wisdom=8,
                charisma=8,
            ),
            "exactly 27 points",
        ),
    ],
)
def test_rejects_invalid_ability_generation(
    method: AbilityGenerationMethod,
    scores: AbilityScores,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        AbilityScoreGeneration(method=method, scores=scores)


def test_background_adjustment_validates_pattern_background_and_cap() -> None:
    base = AbilityScores(
        strength=19, dexterity=20, constitution=18, intelligence=10, wisdom=10, charisma=10
    )
    adjustment = BackgroundAbilityAdjustment(
        background="Soldier",
        base_scores=base,
        increases={"strength": 1, "constitution": 2},
    )
    assert adjustment.adjusted_scores == AbilityScores(
        strength=20, dexterity=20, constitution=20, intelligence=10, wisdom=10, charisma=10
    )

    with pytest.raises(ValidationError, match="not granted by the background"):
        BackgroundAbilityAdjustment(
            background="Soldier",
            base_scores=base,
            increases={"wisdom": 2, "strength": 1},
        )
    with pytest.raises(ValidationError, match=r"must be \+2/\+1 or \+1/\+1/\+1"):
        BackgroundAbilityAdjustment(
            background="Soldier",
            base_scores=base,
            increases={"strength": 1, "constitution": 1},
        )
    with pytest.raises(ValidationError, match="above 20"):
        BackgroundAbilityAdjustment(
            background="Soldier",
            base_scores=base,
            increases={"dexterity": 1, "constitution": 2},
        )
