from pathlib import Path

from pypdf import PdfReader

from pc_wizard.models import AbilityScores, Character, ClassChoices, MagicInitiateChoice
from pc_wizard.pdf import field_values, render_character_sheet, validate_template


def sample() -> Character:
    return Character(
        name="Brunna",
        character_class="Fighter",
        background="Soldier",
        species="Dwarf",
        alignment="Lawful Good",
        abilities=AbilityScores(
            strength=17, dexterity=14, constitution=14, intelligence=8, wisdom=10, charisma=12
        ),
        skills={"Athletics", "Intimidation", "Perception", "Survival"},
        class_choices=ClassChoices(
            weapon_masteries={"Greataxe", "Greatsword", "Longbow"},
            fighting_style="Great Weapon Fighting",
        ),
        languages=["Common", "Dwarvish", "Giant"],
    )


def small_human() -> Character:
    character = sample()
    values = character.model_dump()
    values.update(
        species="Human",
        size="Small",
        human_skill="Insight",
        human_origin_feat="Alert",
        skills=set(character.skills) | {"Insight"},
    )
    return Character.model_validate(values)


def elf_with_keen_senses() -> Character:
    character = sample()
    values = character.model_dump()
    values.update(
        species="Elf",
        elf_lineage="Drow",
        elf_spellcasting_ability="wisdom",
        elf_keen_senses_skill="Insight",
        skills=set(character.skills) | {"Insight"},
    )
    return Character.model_validate(values)


def wood_elf() -> Character:
    character = sample()
    values = character.model_dump()
    values.update(
        species="Elf",
        elf_lineage="Wood Elf",
        elf_spellcasting_ability="wisdom",
        elf_keen_senses_skill="Insight",
        skills=set(character.skills) | {"Insight"},
    )
    return Character.model_validate(values)


def skilled_sage_human() -> Character:
    character = sample()
    values = character.model_dump()
    values.update(
        background="Sage",
        species="Human",
        size="Medium",
        human_skill="Perception",
        human_origin_feat="Skilled",
        skills={
            "Acrobatics",
            "Arcana",
            "Athletics",
            "History",
            "Investigation",
            "Nature",
            "Perception",
        },
        tool_proficiencies={"Alchemist's Supplies"},
        skilled_proficiencies={"Acrobatics", "Athletics", "Alchemist's Supplies"},
        magic_initiate_choices=[
            MagicInitiateChoice(
                spell_list="Wizard",
                spellcasting_ability="intelligence",
                cantrips=("Mage Hand", "Prestidigitation"),
                level_one_spell="Mage Armor",
            )
        ],
    )
    return Character.model_validate(values)


def test_field_values_include_derived_values() -> None:
    values = field_values(sample())
    assert values["Text1"] == "Brunna"
    assert values["Text19"] == "17"
    assert values["Text63"] == "+5"
    assert values["Text27"] == "13"
    assert "Fighting Style: Great Weapon Fighting" in values["Text54"]
    assert "Greataxe (Cleave)" in values["Text54"]


def test_field_values_include_elf_keen_senses_proficiency() -> None:
    assert field_values(elf_with_keen_senses())["Text70"] == "+2"


def test_field_values_include_choice_dependent_species_speed_and_traits() -> None:
    values = field_values(wood_elf())
    assert values["Text16"] == "35"
    assert "Elven Lineage: Wood Elf" in values["Text55"]
    assert "Cantrips: Druidcraft" in values["Text55"]


def test_render_fills_template(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "character-sheet.pdf"
    output = tmp_path / "sheet.pdf"
    render_character_sheet(small_human(), template, output)
    reader = PdfReader(output)
    assert len(reader.pages) == 2
    fields = reader.get_fields()
    assert fields is not None
    assert fields["Text1"]["/V"] == "Brunna"
    assert fields["Text15"]["/V"] == "S"
    assert fields["Text16"]["/V"] == "30"
    assert fields["Text14"]["/V"] == "+4"
    assert "Skillful: Insight" in fields["Text55"]["/V"]
    assert "Versatile: Alert" in fields["Text55"]["/V"]
    assert fields["Text58"]["/V"] == (
        "Alert: Initiative Proficiency; Initiative Swap\n"
        "Savage Attacker: roll weapon damage dice twice once per turn"
    )
    assert "Weapon Mastery: Greataxe (Cleave)" in fields["Text54"]["/V"]
    assert fields["Text59"]["/V"] == "Gaming Set"


def test_render_reads_back_origin_feat_subchoices(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "character-sheet.pdf"
    output = tmp_path / "origin-feats.pdf"

    render_character_sheet(skilled_sage_human(), template, output)

    fields = PdfReader(output).get_fields()
    assert fields is not None
    assert "Skilled: Acrobatics, Alchemist's Supplies, Athletics" in fields["Text58"]["/V"]
    assert "Magic Initiate (Wizard; Intelligence)" in fields["Text58"]["/V"]
    assert fields["Text59"]["/V"] == "Calligrapher's Supplies\nAlchemist's Supplies"


def test_validate_template_rejects_non_pdf(tmp_path: Path) -> None:
    template = tmp_path / "not-a-template.pdf"
    template.write_text("not a PDF")

    try:
        validate_template(template)
    except ValueError as error:
        assert "official sheet" in str(error)
    else:
        raise AssertionError("Invalid template was accepted")
