import json
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from pc_wizard.models import (
    AbilityGenerationMethod,
    AbilityScoreGeneration,
    AbilityScores,
    BackgroundAbilityAdjustment,
    Character,
    ClassChoices,
    MagicInitiateChoice,
)


@pytest.fixture
def character() -> Character:
    return Character(
        name="Ada",
        character_class="Wizard",
        background="Sage",
        species="Dwarf",
        size="Medium",
        alignment="Neutral Good",
        abilities=AbilityScores(
            strength=8, dexterity=12, constitution=14, intelligence=17, wisdom=15, charisma=10
        ),
        class_skills={"Investigation", "Nature"},
        class_choices=ClassChoices(
            cantrips={"Fire Bolt", "Mage Hand", "Prestidigitation"},
            spellbook_spells={
                "Detect Magic",
                "Find Familiar",
                "Mage Armor",
                "Magic Missile",
                "Shield",
                "Sleep",
            },
            prepared_spells={"Detect Magic", "Mage Armor", "Magic Missile", "Shield"},
        ),
        magic_initiate_choices=[
            MagicInitiateChoice(
                spell_list="Wizard",
                spellcasting_ability="intelligence",
                cantrips=("Mage Hand", "Prestidigitation"),
                level_one_spell="Mage Armor",
            )
        ],
        selected_languages=("Dwarvish", "Elvish"),
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
    assert character.speed == 30
    assert character.darkvision_range == 120
    assert character.damage_resistances == ("Poison",)
    assert character.feat_cantrips == ("Mage Hand", "Prestidigitation")
    assert character.feat_prepared_spells == ("Mage Armor",)


def test_json_round_trip(character: Character, tmp_path: Path) -> None:
    path = tmp_path / "ada.json"
    character.save_json(path)
    assert Character.load_json(path) == character


def test_character_json_contains_selections_not_derived_aggregates(character: Character) -> None:
    data = character.model_dump(mode="json")

    assert set(data["class_skills"]) == {"Investigation", "Nature"}
    assert data["selected_languages"] == ["Dwarvish", "Elvish"]
    assert "skills" not in data
    assert "languages" not in data
    assert character.derived_values.skills == tuple(sorted(character.skills))
    assert character.derived_values.languages == character.languages


def test_alignment_and_languages_use_srd_identifiers(character: Character) -> None:
    data = character.model_dump(mode="json")
    data["alignment"] = "Chaotic Hungry"
    with pytest.raises(ValidationError, match="alignment"):
        Character.model_validate(data)

    data = character.model_dump(mode="json")
    data["selected_languages"] = ["Elvish", "Elvish"]
    with pytest.raises(ValidationError, match="two different standard languages"):
        Character.model_validate(data)

    data["selected_languages"] = ["Elvish", "Undercommon"]
    with pytest.raises(ValidationError, match="selected_languages"):
        Character.model_validate(data)


def test_class_skill_cannot_duplicate_an_origin_proficiency(character: Character) -> None:
    data = character.model_dump(mode="json")
    data["class_skills"] = ["Arcana", "Investigation"]

    with pytest.raises(ValidationError, match="must not duplicate"):
        Character.model_validate(data)


def test_starting_packages_create_structured_inventory_and_coins(character: Character) -> None:
    inventory = {(item.name, item.quantity, item.category) for item in character.inventory}

    assert ("Dagger", 2, "Weapon") in inventory
    assert ("Arcane Focus (Quarterstaff)", 1, "Weapon") in inventory
    assert ("Spellbook", 1, "Gear") in inventory
    assert ("Parchment", 8, "Gear") in inventory
    assert character.coins.gold == 13
    assert character.equipment_summary.endswith("Coins: 13 GP")


def test_starting_gold_options_preserve_coins_without_package_items(
    character: Character,
) -> None:
    values = character.model_dump()
    values.update(class_equipment_option="Gold", background_equipment_option="Gold")

    wealthy = Character.model_validate(values)

    assert wealthy.inventory == ()
    assert wealthy.coins.gold == 105
    assert wealthy.weapon_attacks == ()


def test_armor_shields_unarmored_defense_and_strength_requirement(
    character: Character,
) -> None:
    fighter_values = character.model_dump()
    fighter_values.update(
        character_class="Fighter",
        background="Soldier",
        abilities={
            "strength": 17,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 8,
            "wisdom": 10,
            "charisma": 12,
        },
        class_choices=ClassChoices(
            weapon_masteries={"Greatsword", "Flail", "Javelin"},
            fighting_style="Defense",
        ),
        class_skills={"Perception", "Survival"},
        magic_initiate_choices=[],
    )
    fighter = Character.model_validate(fighter_values)
    assert fighter.equipped_armor == "Chain Mail"
    assert fighter.armor_class == 17

    paladin_values = fighter.model_dump()
    paladin_values.update(
        character_class="Paladin",
        abilities={**paladin_values["abilities"], "strength": 12},
        class_choices=ClassChoices(
            weapon_masteries={"Longsword", "Javelin"},
            prepared_spells={"Bless", "Divine Smite"},
        ),
        class_skills={"Insight", "Persuasion"},
    )
    paladin = Character.model_validate(paladin_values)
    assert paladin.armor_class == 18
    assert paladin.speed == 20

    barbarian_values = fighter.model_dump()
    barbarian_values.update(
        character_class="Barbarian",
        class_choices=ClassChoices(weapon_masteries={"Greataxe", "Handaxe"}),
        class_skills={"Nature", "Perception"},
    )
    barbarian = Character.model_validate(barbarian_values)
    assert barbarian.equipped_armor is None
    assert barbarian.armor_class == 14

    monk_values = fighter.model_dump()
    monk_values.update(
        character_class="Monk",
        class_choices=ClassChoices(tools={"Smith's Tools"}),
        class_skills={"History", "Stealth"},
    )
    monk = Character.model_validate(monk_values)
    assert monk.armor_class == 12


def test_weapon_attacks_include_proficiency_damage_range_properties_and_mastery() -> None:
    fighter = Character(
        name="Brunna",
        character_class="Fighter",
        background="Soldier",
        species="Dwarf",
        size="Medium",
        alignment="Lawful Good",
        abilities=AbilityScores(
            strength=17,
            dexterity=14,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=12,
        ),
        class_skills={"Perception", "Survival"},
        class_choices=ClassChoices(
            weapon_masteries={"Greatsword", "Flail", "Javelin"},
            fighting_style="Great Weapon Fighting",
        ),
        selected_languages=("Dwarvish", "Giant"),
    )

    attacks = {attack.name: attack for attack in fighter.weapon_attacks}

    assert attacks["Greatsword"].attack_bonus == 5
    assert attacks["Greatsword"].damage == "2d6+3"
    assert attacks["Greatsword"].damage_type == "Slashing"
    assert attacks["Greatsword"].range == "5 ft."
    assert attacks["Greatsword"].properties == ("Heavy", "Two-Handed")
    assert "Mastery: Graze" in attacks["Greatsword"].notes
    assert attacks["Javelin"].range == "30/120 ft."
    assert "Quantity 8" in attacks["Javelin"].notes


def test_archery_and_finesse_choose_the_correct_attack_modifier(character: Character) -> None:
    values = character.model_dump()
    values.update(
        character_class="Fighter",
        background="Soldier",
        class_equipment_option="B",
        class_choices=ClassChoices(
            weapon_masteries={"Longbow", "Scimitar", "Shortsword"},
            fighting_style="Archery",
        ),
        class_skills={"Perception", "Survival"},
        magic_initiate_choices=[],
    )
    fighter = Character.model_validate(values)
    attacks = {attack.name: attack for attack in fighter.weapon_attacks}

    assert attacks["Longbow"].attack_bonus == 5
    assert attacks["Scimitar"].attack_bonus == 3
    assert attacks["Scimitar"].damage == "1d6+1"


@pytest.mark.parametrize(
    ("class_name", "ability", "modifier", "slots", "recovery"),
    [
        ("Bard", "charisma", 0, 2, "Long Rest"),
        ("Cleric", "wisdom", 2, 2, "Long Rest"),
        ("Druid", "wisdom", 2, 2, "Long Rest"),
        ("Paladin", "charisma", 0, 2, "Long Rest"),
        ("Ranger", "wisdom", 2, 2, "Long Rest"),
        ("Sorcerer", "charisma", 0, 2, "Long Rest"),
        ("Warlock", "charisma", 0, 1, "Short or Long Rest"),
        ("Wizard", "intelligence", 3, 2, "Long Rest"),
    ],
)
def test_level_one_spellcasting_values_and_slots(
    character: Character,
    class_name: str,
    ability: str,
    modifier: int,
    slots: int,
    recovery: str,
) -> None:
    choices = {
        "Bard": ClassChoices(
            tools={
                "Musical Instrument (Drum)",
                "Musical Instrument (Flute)",
                "Musical Instrument (Lute)",
            },
            cantrips={"Light", "Vicious Mockery"},
            prepared_spells={"Cure Wounds", "Faerie Fire", "Healing Word", "Thunderwave"},
        ),
        "Cleric": ClassChoices(
            divine_order="Protector",
            cantrips={"Guidance", "Light", "Sacred Flame"},
            prepared_spells={"Bless", "Cure Wounds", "Guiding Bolt", "Healing Word"},
        ),
        "Druid": ClassChoices(
            primal_order="Warden",
            cantrips={"Druidcraft", "Shillelagh"},
            prepared_spells={"Entangle", "Faerie Fire", "Goodberry", "Healing Word"},
        ),
        "Paladin": ClassChoices(
            weapon_masteries={"Longsword", "Javelin"},
            prepared_spells={"Bless", "Divine Smite"},
        ),
        "Ranger": ClassChoices(
            weapon_masteries={"Longbow", "Scimitar"},
            prepared_spells={"Cure Wounds", "Ensnaring Strike"},
        ),
        "Sorcerer": ClassChoices(
            cantrips={"Fire Bolt", "Light", "Mage Hand", "Sorcerous Burst"},
            prepared_spells={"Magic Missile", "Shield"},
        ),
        "Warlock": ClassChoices(
            cantrips={"Eldritch Blast", "Prestidigitation"},
            prepared_spells={"Charm Person", "Hex"},
            eldritch_invocation="Pact of the Chain",
        ),
        "Wizard": character.class_choices,
    }[class_name]
    values = character.model_dump()
    class_skills = {
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
    }[class_name]
    values.update(character_class=class_name, class_choices=choices, class_skills=class_skills)
    if class_name == "Bard":
        values["bard_starting_instrument"] = "Musical Instrument (Flute)"
    caster = Character.model_validate(values)

    assert caster.spellcasting_ability == ability
    assert caster.spellcasting_modifier == modifier
    assert caster.spell_save_dc == 10 + modifier
    assert caster.spell_attack_bonus == 2 + modifier
    assert caster.spell_slots[0].total == slots
    assert caster.spell_slots[0].recovery == recovery


def test_level_one_class_resources_are_structured(character: Character) -> None:
    resource = character.class_resources[0]

    assert resource.name == "Arcane Recovery"
    assert resource.maximum == 1
    assert resource.unit == "use"
    assert resource.recovery == "regain on Long Rest"
    assert resource.detail == "recover 1 level(s) of spell slots"
    assert resource.summary == (
        "Arcane Recovery: 1 use; recover 1 level(s) of spell slots; regain on Long Rest"
    )


@pytest.mark.parametrize(
    ("class_name", "choices"),
    [
        ("Barbarian", ClassChoices(weapon_masteries={"Greataxe", "Handaxe"})),
        (
            "Bard",
            ClassChoices(
                tools={
                    "Musical Instrument (Drum)",
                    "Musical Instrument (Flute)",
                    "Musical Instrument (Lute)",
                },
                cantrips={"Light", "Vicious Mockery"},
                prepared_spells={"Cure Wounds", "Faerie Fire", "Healing Word", "Thunderwave"},
            ),
        ),
        (
            "Cleric",
            ClassChoices(
                divine_order="Thaumaturge",
                cantrips={"Guidance", "Light", "Sacred Flame", "Thaumaturgy"},
                prepared_spells={"Bless", "Cure Wounds", "Guiding Bolt", "Healing Word"},
            ),
        ),
        (
            "Druid",
            ClassChoices(
                primal_order="Warden",
                cantrips={"Druidcraft", "Shillelagh"},
                prepared_spells={"Entangle", "Faerie Fire", "Goodberry", "Healing Word"},
            ),
        ),
        (
            "Fighter",
            ClassChoices(
                weapon_masteries={"Greataxe", "Greatsword", "Longbow"},
                fighting_style="Defense",
            ),
        ),
        ("Monk", ClassChoices(tools={"Smith's Tools"})),
        (
            "Paladin",
            ClassChoices(
                weapon_masteries={"Longsword", "Javelin"},
                prepared_spells={"Bless", "Divine Smite"},
            ),
        ),
        (
            "Ranger",
            ClassChoices(
                weapon_masteries={"Longbow", "Scimitar"},
                prepared_spells={"Cure Wounds", "Ensnaring Strike"},
            ),
        ),
        (
            "Rogue",
            ClassChoices(
                weapon_masteries={"Dagger", "Shortsword"},
                expertise={"Arcana", "History"},
                additional_language="Draconic",
            ),
        ),
        (
            "Sorcerer",
            ClassChoices(
                cantrips={"Fire Bolt", "Light", "Mage Hand", "Sorcerous Burst"},
                prepared_spells={"Magic Missile", "Shield"},
            ),
        ),
        (
            "Warlock",
            ClassChoices(
                cantrips={"Eldritch Blast", "Prestidigitation"},
                prepared_spells={"Charm Person", "Hex"},
                eldritch_invocation="Pact of the Chain",
            ),
        ),
        (
            "Wizard",
            ClassChoices(
                cantrips={"Fire Bolt", "Mage Hand", "Prestidigitation"},
                spellbook_spells={
                    "Detect Magic",
                    "Find Familiar",
                    "Mage Armor",
                    "Magic Missile",
                    "Shield",
                    "Sleep",
                },
                prepared_spells={"Detect Magic", "Mage Armor", "Magic Missile", "Shield"},
            ),
        ),
    ],
)
def test_validates_level_one_choices_for_every_class(
    character: Character, class_name: str, choices: ClassChoices
) -> None:
    values = character.model_dump()
    class_skills = {
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
    }[class_name]
    values.update(character_class=class_name, class_choices=choices, class_skills=class_skills)
    if class_name == "Bard":
        values["bard_starting_instrument"] = "Musical Instrument (Flute)"
    result = Character.model_validate(values)

    assert result.class_choices == choices
    expected_resource = {
        "Barbarian": ("Rage", 2),
        "Bard": ("Bardic Inspiration", 1),
        "Fighter": ("Second Wind", 2),
        "Paladin": ("Lay on Hands", 5),
        "Ranger": ("Favored Enemy", 2),
        "Sorcerer": ("Innate Sorcery", 2),
        "Warlock": ("Pact Magic", 1),
        "Wizard": ("Arcane Recovery", 1),
    }.get(class_name)
    assert (
        (result.class_resources[0].name, result.class_resources[0].maximum)
        if result.class_resources
        else None
    ) == expected_resource


def test_class_choices_enforce_eligibility_and_derived_benefits(character: Character) -> None:
    values = character.model_dump()
    values.update(
        character_class="Rogue",
        class_choices=ClassChoices(
            weapon_masteries={"Greatsword", "Longsword"},
            expertise={"Arcana", "History"},
            additional_language="Draconic",
        ),
        class_skills={"Investigation", "Perception", "Persuasion", "Sleight of Hand"},
    )
    with pytest.raises(ValidationError, match="invalid Rogue weapon mastery"):
        Character.model_validate(values)

    values.update(
        character_class="Cleric",
        class_choices=ClassChoices(
            divine_order="Thaumaturge",
            cantrips={"Guidance", "Light", "Sacred Flame", "Thaumaturgy"},
            prepared_spells={"Bless", "Cure Wounds", "Guiding Bolt", "Healing Word"},
        ),
        class_skills={"Insight", "Medicine"},
    )
    cleric = Character.model_validate(values)
    assert cleric.skill_modifier("Arcana") == 7
    assert "Speak with Animals" not in cleric.class_prepared_spells

    values["class_choices"] = ClassChoices(
        divine_order="Protector",
        cantrips={"Guidance", "Light", "Sacred Flame"},
        prepared_spells={"Bless", "Cure Wounds", "Guiding Bolt", "Healing Word"},
    )
    protector = Character.model_validate(values)
    assert protector.weapon_proficiencies == "Simple and Martial"
    assert protector.armor_training == "Light, Medium, Heavy, Shields"

    values.update(
        character_class="Ranger",
        class_skills={"Perception", "Stealth", "Survival"},
        class_choices=ClassChoices(
            weapon_masteries={"Longbow", "Scimitar"},
            prepared_spells={"Cure Wounds", "Hunter's Mark"},
        ),
    )
    with pytest.raises(ValidationError, match="invalid number or selection"):
        Character.model_validate(values)


def test_binary_smoke_fixture_is_valid() -> None:
    fixture = Path(__file__).parent / "fixtures" / "character.json"
    payload = cast(dict[str, object], json.loads(fixture.read_text(encoding="utf-8")))
    class_choices = cast(dict[str, object], payload["class_choices"])

    character = Character.load_json(fixture)

    assert set(payload) == set(Character.model_fields)
    assert set(class_choices) == set(ClassChoices.model_fields)
    assert "schema_version" not in payload
    assert character.name == "Binary Smoke Test"
    assert character.character_size == "Medium"
    assert character.initiative_modifier == 5
    assert character.backstory is None
    assert character.appearance is None
    assert character.personality is None


def test_character_json_rejects_schema_version(character: Character) -> None:
    payload = character.model_dump()
    payload["schema_version"] = 1

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Character.model_validate(payload)


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


def test_species_size_is_required_and_validates(character: Character) -> None:
    values = character.model_dump()
    del values["size"]
    with pytest.raises(ValidationError, match="Field required"):
        Character.model_validate(values)

    values.update(
        species="Human",
        size="Small",
        human_skill="Perception",
        human_origin_feat="Alert",
    )
    assert Character.model_validate(values).character_size == "Small"

    values.update(species="Dwarf", size="Small")
    with pytest.raises(ValidationError, match="invalid size for Dwarf"):
        Character.model_validate(values)

    values.update(
        species="Gnome",
        size="Small",
        human_skill=None,
        human_origin_feat=None,
        gnome_lineage="Forest Gnome",
        gnome_spellcasting_ability="intelligence",
    )
    assert Character.model_validate(values).character_size == "Small"


@pytest.mark.parametrize(
    ("ancestry", "damage_type"),
    [
        ("Black", "Acid"),
        ("Blue", "Lightning"),
        ("Brass", "Fire"),
        ("Bronze", "Lightning"),
        ("Copper", "Acid"),
        ("Gold", "Fire"),
        ("Green", "Poison"),
        ("Red", "Fire"),
        ("Silver", "Cold"),
        ("White", "Cold"),
    ],
)
def test_dragonborn_ancestry_determines_damage_type(
    character: Character, ancestry: str, damage_type: str
) -> None:
    values = character.model_dump()
    values.update(species="Dragonborn", dragonborn_ancestry=ancestry)

    dragonborn = Character.model_validate(values)

    assert dragonborn.dragonborn_damage_type == damage_type
    assert dragonborn.damage_resistances == (damage_type,)
    assert dragonborn.darkvision_range == 60
    assert f"Draconic Ancestry: {ancestry} ({damage_type})" in dragonborn.species_traits


def test_dragonborn_ancestry_round_trips_through_json(character: Character, tmp_path: Path) -> None:
    values = character.model_dump()
    values.update(species="Dragonborn", dragonborn_ancestry="Silver")
    dragonborn = Character.model_validate(values)
    path = tmp_path / "dragonborn.json"

    dragonborn.save_json(path)
    restored = Character.load_json(path)

    assert restored == dragonborn
    assert restored.dragonborn_damage_type == "Cold"


def test_dragonborn_ancestry_is_required_and_species_specific(character: Character) -> None:
    values = character.model_dump()
    values.update(species="Dragonborn", dragonborn_ancestry=None)
    with pytest.raises(ValidationError, match="must choose a draconic ancestry"):
        Character.model_validate(values)

    values.update(species="Dwarf", dragonborn_ancestry="Gold")
    with pytest.raises(ValidationError, match="only valid for Dragonborn"):
        Character.model_validate(values)


@pytest.mark.parametrize(
    ("lineage", "expected_rule"),
    [
        ("Drow", (30, 120, "Dancing Lights", False)),
        ("High Elf", (30, 60, "Prestidigitation", True)),
        ("Wood Elf", (35, 60, "Druidcraft", False)),
    ],
)
def test_elf_lineage_records_level_one_rule_metadata(
    character: Character,
    lineage: str,
    expected_rule: tuple[int, int, str, bool],
) -> None:
    values = character.model_dump()
    values.update(
        species="Elf",
        elf_lineage=lineage,
        elf_spellcasting_ability="wisdom",
        elf_keen_senses_skill="Perception",
    )

    elf = Character.model_validate(values)
    rule = elf.elven_lineage_rule

    assert rule is not None
    assert (
        rule.speed,
        rule.darkvision_range,
        rule.cantrip,
        rule.cantrip_replaceable,
    ) == expected_rule
    assert elf.speed == rule.speed
    assert elf.darkvision_range == rule.darkvision_range
    assert elf.species_cantrips == (rule.cantrip,)


def test_elf_choices_round_trip_through_json(character: Character, tmp_path: Path) -> None:
    values = character.model_dump()
    values.update(
        species="Elf",
        elf_lineage="High Elf",
        elf_spellcasting_ability="intelligence",
        elf_keen_senses_skill="Insight",
    )
    elf = Character.model_validate(values)
    path = tmp_path / "elf.json"

    elf.save_json(path)

    assert Character.load_json(path) == elf


def test_elf_lineage_spells_are_prepared_at_their_required_levels(character: Character) -> None:
    values = character.model_dump()
    values.update(
        species="Elf",
        elf_lineage="Drow",
        elf_spellcasting_ability="charisma",
        elf_keen_senses_skill="Perception",
        level=5,
    )

    elf = Character.model_validate(values)

    assert elf.species_prepared_spells == ("Faerie Fire", "Darkness")


def test_elf_choices_are_required_species_specific_and_derived(character: Character) -> None:
    values = character.model_dump()
    values.update(species="Elf")
    with pytest.raises(ValidationError, match="must choose a lineage"):
        Character.model_validate(values)

    values.update(
        elf_lineage="Wood Elf",
        elf_spellcasting_ability="charisma",
        elf_keen_senses_skill="Survival",
    )
    elf = Character.model_validate(values)
    assert "Survival" in elf.skills

    values.update(species="Dwarf")
    with pytest.raises(ValidationError, match="only valid for Elf"):
        Character.model_validate(values)


@pytest.mark.parametrize(
    ("lineage", "expected_rule"),
    [
        ("Forest Gnome", (("Minor Illusion",), ("Speak with Animals",), False)),
        ("Rock Gnome", (("Mending", "Prestidigitation"), (), True)),
    ],
)
def test_gnome_lineage_records_level_one_rule_metadata(
    character: Character,
    lineage: str,
    expected_rule: tuple[tuple[str, ...], tuple[str, ...], bool],
) -> None:
    values = character.model_dump()
    values.update(
        species="Gnome",
        size="Small",
        gnome_lineage=lineage,
        gnome_spellcasting_ability="wisdom",
    )

    gnome = Character.model_validate(values)
    rule = gnome.gnomish_lineage_rule

    assert rule is not None
    assert (
        rule.cantrips,
        rule.always_prepared_spells,
        rule.creates_clockwork_devices,
    ) == expected_rule
    assert gnome.species_cantrips == rule.cantrips
    assert gnome.species_prepared_spells == rule.always_prepared_spells


def test_gnome_choices_round_trip_through_json(character: Character, tmp_path: Path) -> None:
    values = character.model_dump()
    values.update(
        species="Gnome",
        size="Small",
        gnome_lineage="Rock Gnome",
        gnome_spellcasting_ability="charisma",
    )
    gnome = Character.model_validate(values)
    path = tmp_path / "gnome.json"

    gnome.save_json(path)

    assert Character.load_json(path) == gnome


def test_gnome_choices_are_required_and_species_specific(character: Character) -> None:
    values = character.model_dump()
    values.update(species="Gnome", size="Small")
    with pytest.raises(ValidationError, match="must choose a Gnomish Lineage"):
        Character.model_validate(values)

    values.update(
        species="Dwarf",
        size="Medium",
        gnome_lineage="Forest Gnome",
        gnome_spellcasting_ability="intelligence",
    )
    with pytest.raises(ValidationError, match="only valid for Gnome"):
        Character.model_validate(values)


@pytest.mark.parametrize(
    ("ancestry", "benefit_name", "trigger", "effect_fragment"),
    [
        ("Cloud Giant", "Cloud's Jaunt", "Bonus Action", "30 feet"),
        ("Fire Giant", "Fire's Burn", "Hit", "1d10 Fire"),
        ("Frost Giant", "Frost's Chill", "Hit", "1d6 Cold"),
        ("Hill Giant", "Hill's Tumble", "Hit", "Prone"),
        ("Stone Giant", "Stone's Endurance", "Reaction", "1d12"),
        ("Storm Giant", "Storm's Thunder", "Reaction", "1d8 Thunder"),
    ],
)
def test_goliath_ancestry_records_boon_metadata(
    character: Character,
    ancestry: str,
    benefit_name: str,
    trigger: str,
    effect_fragment: str,
) -> None:
    values = character.model_dump()
    values.update(species="Goliath", goliath_ancestry=ancestry)

    goliath = Character.model_validate(values)
    rule = goliath.goliath_ancestry_rule

    assert rule is not None
    assert rule.benefit_name == benefit_name
    assert rule.trigger == trigger
    assert effect_fragment in rule.effect
    assert any(benefit_name in trait for trait in goliath.species_traits)


def test_goliath_ancestry_round_trips_through_json(character: Character, tmp_path: Path) -> None:
    values = character.model_dump()
    values.update(species="Goliath", goliath_ancestry="Stone Giant")
    goliath = Character.model_validate(values)
    path = tmp_path / "goliath.json"

    goliath.save_json(path)

    assert Character.load_json(path) == goliath


def test_goliath_ancestry_is_required_and_species_specific(character: Character) -> None:
    values = character.model_dump()
    values.update(species="Goliath")
    with pytest.raises(ValidationError, match="must choose a Giant Ancestry"):
        Character.model_validate(values)

    values.update(species="Dwarf", goliath_ancestry="Cloud Giant")
    with pytest.raises(ValidationError, match="only valid for Goliath"):
        Character.model_validate(values)


def test_human_skill_and_origin_feat_are_applied_and_round_trip(
    character: Character, tmp_path: Path
) -> None:
    values = character.model_dump()
    values.update(
        species="Human",
        human_skill="Perception",
        human_origin_feat="Skilled",
        tool_proficiencies={"Alchemist's Supplies"},
        skilled_proficiencies={"Acrobatics", "Athletics", "Alchemist's Supplies"},
    )
    human = Character.model_validate(values)
    path = tmp_path / "human.json"

    human.save_json(path)
    restored = Character.load_json(path)

    assert restored == human
    assert restored.skill_modifier("Perception") == 4
    assert "Skillful: Perception" in restored.species_traits
    assert "Versatile: Skilled" in restored.species_traits
    assert restored.all_tool_proficiencies == (
        "Calligrapher's Supplies",
        "Alchemist's Supplies",
    )


def test_human_choices_are_required_additional_and_species_specific(character: Character) -> None:
    values = character.model_dump()
    values.update(species="Human")
    with pytest.raises(ValidationError, match="must choose an additional skill"):
        Character.model_validate(values)

    values.update(
        human_skill="Arcana",
        human_origin_feat="Alert",
    )
    with pytest.raises(ValidationError, match="must be additional to background skills"):
        Character.model_validate(values)

    values.update(species="Dwarf", human_skill="Perception")
    with pytest.raises(ValidationError, match="only valid for Human"):
        Character.model_validate(values)


def test_magic_initiate_validates_spells_and_repeatable_lists(character: Character) -> None:
    with pytest.raises(ValidationError, match="cantrips must come from the Cleric list"):
        MagicInitiateChoice(
            spell_list="Cleric",
            spellcasting_ability="wisdom",
            cantrips=("Fire Bolt", "Guidance"),
            level_one_spell="Bless",
        )

    values = character.model_dump()
    values.update(
        species="Human",
        human_skill="Perception",
        human_origin_feat="Magic Initiate",
        magic_initiate_choices=[
            *character.magic_initiate_choices,
            MagicInitiateChoice(
                spell_list="Druid",
                spellcasting_ability="wisdom",
                cantrips=("Druidcraft", "Produce Flame"),
                level_one_spell="Goodberry",
            ),
        ],
    )
    human = Character.model_validate(values)
    assert human.feat_cantrips == (
        "Mage Hand",
        "Prestidigitation",
        "Druidcraft",
        "Produce Flame",
    )
    assert human.feat_prepared_spells == ("Mage Armor", "Goodberry")

    values["magic_initiate_choices"][1] = character.magic_initiate_choices[0]
    with pytest.raises(ValidationError, match="must use different spell lists"):
        Character.model_validate(values)


def test_origin_feat_subchoices_are_required(character: Character) -> None:
    values = character.model_dump()
    values["magic_initiate_choices"] = []
    with pytest.raises(ValidationError, match="requires exactly 1 Magic Initiate choice"):
        Character.model_validate(values)

    values = character.model_dump()
    values.update(
        species="Human",
        human_skill="Perception",
        human_origin_feat="Skilled",
    )
    with pytest.raises(ValidationError, match="Skilled requires exactly three"):
        Character.model_validate(values)


def test_nonrepeatable_origin_feat_cannot_duplicate_background(character: Character) -> None:
    values = character.model_dump()
    values.update(
        background="Criminal",
        species="Human",
        human_skill="Arcana",
        human_origin_feat="Alert",
        magic_initiate_choices=[],
    )

    with pytest.raises(ValidationError, match="Alert Origin feat can be taken only once"):
        Character.model_validate(values)


@pytest.mark.parametrize(
    ("legacy", "resistance", "cantrip", "level_three_spell", "level_five_spell"),
    [
        ("Abyssal", "Poison", "Poison Spray", "Ray of Sickness", "Hold Person"),
        ("Chthonic", "Necrotic", "Chill Touch", "False Life", "Ray of Enfeeblement"),
        ("Infernal", "Fire", "Fire Bolt", "Hellish Rebuke", "Darkness"),
    ],
)
def test_tiefling_legacy_applies_resistance_and_spells(
    character: Character,
    legacy: str,
    resistance: str,
    cantrip: str,
    level_three_spell: str,
    level_five_spell: str,
) -> None:
    values = character.model_dump()
    values.update(
        species="Tiefling",
        tiefling_legacy=legacy,
        tiefling_spellcasting_ability="charisma",
        level=5,
    )

    tiefling = Character.model_validate(values)

    assert tiefling.darkvision_range == 60
    assert tiefling.damage_resistances == (resistance,)
    assert tiefling.species_cantrips == (cantrip, "Thaumaturgy")
    assert tiefling.species_prepared_spells == (level_three_spell, level_five_spell)


def test_tiefling_choices_round_trip_and_validate_species(
    character: Character, tmp_path: Path
) -> None:
    values = character.model_dump()
    values.update(species="Tiefling")
    with pytest.raises(ValidationError, match="must choose a Fiendish Legacy"):
        Character.model_validate(values)

    values.update(tiefling_legacy="Infernal", tiefling_spellcasting_ability="wisdom")
    tiefling = Character.model_validate(values)
    path = tmp_path / "tiefling.json"
    tiefling.save_json(path)
    assert Character.load_json(path) == tiefling

    values.update(species="Dwarf")
    with pytest.raises(ValidationError, match="only valid for Tiefling"):
        Character.model_validate(values)


def test_rejects_unknown_class() -> None:
    with pytest.raises(ValidationError, match="unknown SRD class"):
        Character(
            name="Ada",
            character_class="Artificer",
            background="Sage",
            species="Human",
            size="Medium",
            alignment="Neutral",
            class_skills={"Arcana", "History"},
            selected_languages=("Elvish", "Giant"),
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
