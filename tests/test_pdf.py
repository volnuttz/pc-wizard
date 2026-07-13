from pathlib import Path
from typing import Any, cast

import pypdfium2 as pdfium  # pyright: ignore[reportMissingTypeStubs]
import pytest
from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, StreamObject

from pc_wizard.models import AbilityScores, Character, ClassChoices, MagicInitiateChoice
from pc_wizard.pdf import (
    SPELL_CONCENTRATION_FIELDS,
    SPELL_MATERIAL_FIELDS,
    SPELL_RITUAL_FIELDS,
    field_values,
    render_character_sheet,
    validate_template,
)


def rendered_page(path: Path, page_number: int) -> tuple[int, int, int, bytes]:
    pdfium_api = cast(Any, pdfium)
    document = pdfium_api.PdfDocument(path)
    document.init_forms()
    bitmap = document[page_number].render(scale=1, may_draw_forms=True)
    return int(bitmap.width), int(bitmap.height), int(bitmap.stride), bytes(bitmap.buffer)


def changed_pixels(
    before: tuple[int, int, int, bytes],
    after: tuple[int, int, int, bytes],
    bounds: tuple[int, int, int, int],
) -> int:
    width, height, stride, before_pixels = before
    after_width, after_height, after_stride, after_pixels = after
    assert (width, height, stride) == (after_width, after_height, after_stride)
    left, top, right, bottom = bounds
    channels = stride // width
    return sum(
        before_pixels[y * stride + x * channels : y * stride + (x + 1) * channels]
        != after_pixels[y * stride + x * channels : y * stride + (x + 1) * channels]
        for y in range(top, bottom)
        for x in range(left, right)
    )


def sample() -> Character:
    return Character(
        name="Brunna",
        character_class="Fighter",
        background="Soldier",
        species="Dwarf",
        size="Medium",
        alignment="Lawful Good",
        abilities=AbilityScores(
            strength=17, dexterity=14, constitution=14, intelligence=8, wisdom=10, charisma=12
        ),
        class_skills={"Perception", "Survival"},
        class_choices=ClassChoices(
            weapon_masteries={"Greataxe", "Greatsword", "Longbow"},
            fighting_style="Great Weapon Fighting",
        ),
        selected_languages=("Dwarvish", "Giant"),
    )


def small_human() -> Character:
    character = sample()
    values = character.model_dump()
    values.update(
        species="Human",
        size="Small",
        human_skill="Insight",
        human_origin_feat="Alert",
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
    )
    return Character.model_validate(values)


def forest_gnome() -> Character:
    character = sample()
    values = character.model_dump()
    values.update(
        species="Gnome",
        size="Small",
        gnome_lineage="Forest Gnome",
        gnome_spellcasting_ability="wisdom",
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
        class_skills={"Intimidation", "Survival"},
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


def rogue_expert() -> Character:
    return Character(
        name="Nix",
        character_class="Rogue",
        background="Criminal",
        species="Tiefling",
        size="Medium",
        tiefling_legacy="Infernal",
        tiefling_spellcasting_ability="charisma",
        alignment="Neutral",
        abilities=AbilityScores(
            strength=12,
            dexterity=17,
            constitution=13,
            intelligence=15,
            wisdom=10,
            charisma=8,
        ),
        class_skills={"Deception", "Investigation", "Perception", "Persuasion"},
        class_choices=ClassChoices(
            weapon_masteries={"Dagger", "Shortsword"},
            expertise={"Sleight of Hand", "Stealth"},
            additional_language="Draconic",
        ),
        selected_languages=("Elvish", "Halfling"),
    )


def wizard_spellcaster() -> Character:
    return Character(
        name="Ada",
        character_class="Wizard",
        background="Sage",
        species="Dwarf",
        size="Medium",
        alignment="Neutral Good",
        abilities=AbilityScores(
            strength=8,
            dexterity=12,
            constitution=14,
            intelligence=17,
            wisdom=15,
            charisma=10,
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


def test_field_values_include_derived_values() -> None:
    values = field_values(sample())
    assert values["Text1"] == "Brunna"
    assert values["Text64"] == "17"
    assert values["Text19"] == "+2"
    assert values["Text91"] == "+5"
    assert values["Text14"] == "13"
    assert values["Text13"] == "16"
    assert values["Text26"] == "+2"
    assert values["Text27"] == "30"
    assert values["Text28"] == "M"
    assert values["Text29"] == "12"
    assert values["Text30"] == "Greatsword"
    assert values["Text31"] == "+5"
    assert values["Text32"] == "2d6+3 Slashing"
    assert "Mastery: Graze" in values["Text33"]
    assert "Chain Mail" in values["Text99"]
    assert "8 x Javelin" in values["Text99"]
    assert values["Text269"] == "18"
    assert "Fighting Style: Great Weapon Fighting" in values["Text54"]
    assert "Greataxe (Cleave)" in values["Text54"]
    assert "Second Wind: 2 uses" in values["Text55"]
    assert values["Check Box37"] == "/Yes"
    assert values["Check Box32"] == "/Yes"
    assert values["Check Box33"] == "/Off"
    assert values["Check Box38"] == "/Yes"
    assert values["Check Box31"] == "/Yes"
    assert values["Check Box34"] == "/Off"
    assert all(
        values[field] == "/Yes"
        for field in ("Check Box12", "Check Box13", "Check Box14", "Check Box15")
    )


def test_field_values_include_elf_keen_senses_proficiency() -> None:
    assert field_values(elf_with_keen_senses())["Text77"] == "+2"


def test_field_values_include_choice_dependent_species_speed_and_traits() -> None:
    values = field_values(wood_elf())
    assert values["Text27"] == "35"
    assert "Elven Lineage: Wood Elf" in values["Text57"]
    assert "Cantrips: Druidcraft" in values["Text57"]


@pytest.mark.parametrize(
    ("character", "ability", "modifier", "save_dc", "attack_bonus", "trait_field"),
    [
        (wood_elf(), "Wisdom", "+0", "10", "+2", "Text57"),
        (forest_gnome(), "Wisdom", "+0", "10", "+2", "Text57"),
        (rogue_expert(), "Charisma", "-1", "9", "+1", "Text57"),
        (skilled_sage_human(), "Intelligence", "-1", "9", "+1", "Text58"),
    ],
)
def test_side_spellcasting_fills_global_summary_without_inventing_slots(
    character: Character,
    ability: str,
    modifier: str,
    save_dc: str,
    attack_bonus: str,
    trait_field: str,
) -> None:
    values = field_values(character)

    assert values["Text111"] == ability
    assert values["Text93"] == modifier
    assert values["Text94"] == save_dc
    assert values["Text95"] == attack_bonus
    assert values["Text112"] == ""
    assert "save DC" in values[trait_field]
    assert "attack" in values[trait_field]


def test_field_values_include_spellcasting_values_spells_and_slots() -> None:
    values = field_values(wizard_spellcaster())
    assert values["Text111"] == "Intelligence"
    assert values["Text93"] == "+3"
    assert values["Text94"] == "13"
    assert values["Text95"] == "+5"
    assert values["Text96"] == "Ink-stained fingers and silver braids."
    assert values["Text97"] == (
        "Backstory\nRaised in a mountain archive.\n\nPersonality\nPatient, curious, and direct."
    )
    assert "Arcane Recovery: 1 use" in values["Text55"]
    assert values["Text112"] == "2"
    assert values["Text113"] == ""
    assert [values[f"Text105.{row}"] for row in range(7)] == ["0", "0", "0", "1", "1", "1", "1"]
    assert [values[f"Text106.{row}"] for row in range(7)] == [
        "Mage Hand",
        "Prestidigitation",
        "Fire Bolt",
        "Mage Armor",
        "Detect Magic",
        "Magic Missile",
        "Shield",
    ]
    assert values["Text107.0"] == "Action"
    assert values["Text109.0"] == "30 feet"
    assert values["Text108"] == "Duration: 1 minute"
    assert values["Check Box252.0"] == "/Off"
    assert values["Check Box253.0"] == "/Off"
    assert values["Check Box254.0.0"] == "/Off"
    assert values["Check Box254.0.3"] == "/Yes"
    assert values["Check Box252.4"] == "/Yes"
    assert values["Check Box253.4"] == "/Yes"
    assert values["Check Box254.0.4"] == "/Off"
    assert values["Text211"] == "Duration: up to 10 minutes"


def test_spell_checkbox_fields_cover_all_thirty_rows_in_visual_order() -> None:
    assert len(SPELL_CONCENTRATION_FIELDS) == 30
    assert len(SPELL_RITUAL_FIELDS) == 30
    assert len(SPELL_MATERIAL_FIELDS) == 30
    assert SPELL_CONCENTRATION_FIELDS[6:8] == ("Check Box252.6", "Check Box255.0")
    assert SPELL_CONCENTRATION_FIELDS[19:21] == ("Check Box255.12", "Check Box258.0")
    assert SPELL_RITUAL_FIELDS[6:8] == ("Check Box253.6", "Check Box256.0")
    assert SPELL_MATERIAL_FIELDS[6:8] == ("Check Box254.0.6", "Check Box257.0")


def test_render_fills_template(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "assets" / "character-sheet.pdf"
    output = tmp_path / "sheet.pdf"
    render_character_sheet(small_human(), template, output)
    reader = PdfReader(output)
    assert len(reader.pages) == 2
    fields = reader.get_fields()
    assert fields is not None
    assert fields["Text1"]["/V"] == "Brunna"
    assert fields["Text6"]["/V"] == "Soldier"
    assert fields["Text7"]["/V"] == "Fighter"
    assert fields["Text8"]["/V"] == "Human"
    assert fields["Text11"]["/V"] == "1"
    assert fields["Text12"]["/V"] == "0"
    assert fields["Text13"]["/V"] == "16"
    assert fields["Text14"]["/V"] == "12"
    assert fields["Text16"]["/V"] == "12"
    assert fields["Text17"]["/V"] == "1d10"
    assert fields["Text19"]["/V"] == "+2"
    assert fields["Text26"]["/V"] == "+4"
    assert fields["Text27"]["/V"] == "30"
    assert fields["Text28"]["/V"] == "S"
    assert fields["Text29"]["/V"] == "12"
    assert "Skillful: Insight" in fields["Text57"]["/V"]
    assert "Versatile: Alert" in fields["Text57"]["/V"]
    assert fields["Text58"]["/V"] == (
        "Alert: Initiative Proficiency; Initiative Swap\n"
        "Savage Attacker: roll weapon damage dice twice once per turn"
    )
    assert "Weapon Mastery: Greataxe (Cleave)" in fields["Text54"]["/V"]
    assert "Second Wind: 2 uses" in fields["Text55"]["/V"]
    assert fields["Text59"]["/V"] == "Simple and Martial"
    assert fields["Text60"]["/V"] == "Gaming Set"
    assert fields["Text30"]["/V"] == "Greatsword"
    assert fields["Text31"]["/V"] == "+5"
    assert fields["Text32"]["/V"] == "2d6+3 Slashing"
    assert "Mastery: Graze" in fields["Text33"]["/V"]
    assert "Chain Mail" in fields["Text99"]["/V"]
    assert "8 x Javelin" in fields["Text99"]["/V"]
    assert fields["Text269"]["/V"] == "18"
    assert fields["Text100"]["/V"] == "Lawful Good"
    assert fields["Text98"]["/V"] == "Common\nDwarvish\nGiant"
    assert fields["Check Box37"]["/V"] == "/Yes"
    assert fields["Check Box32"]["/V"] == "/Yes"
    assert fields["Check Box33"]["/V"] == "/Off"
    assert fields["Check Box13"]["/V"] == "/Yes"
    assert fields["Check Box15"]["/V"] == "/Yes"


def test_render_reads_back_skill_expertise_and_armor_indicators(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "assets" / "character-sheet.pdf"
    output = tmp_path / "expertise.pdf"

    render_character_sheet(rogue_expert(), template, output)

    fields = PdfReader(output).get_fields()
    assert fields is not None
    assert fields["Check Box35"]["/V"] == "/Yes"
    assert fields["Check Box36"]["/V"] == "/Yes"
    assert fields["Check Box38"]["/V"] == "/Off"
    assert fields["Text89"]["/V"] == "+7"
    assert fields["Text90"]["/V"] == "+7"
    assert "Expertise: Sleight of Hand, Stealth" in fields["Text54"]["/V"]
    assert fields["Check Box13"]["/V"] == "/Yes"
    assert fields["Check Box14"]["/V"] == "/Off"


def test_render_reads_back_origin_feat_subchoices(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "assets" / "character-sheet.pdf"
    output = tmp_path / "origin-feats.pdf"

    render_character_sheet(skilled_sage_human(), template, output)

    fields = PdfReader(output).get_fields()
    assert fields is not None
    assert "Skilled: Acrobatics, Alchemist's Supplies, Athletics" in fields["Text58"]["/V"]
    assert "Magic Initiate (Wizard): Intelligence" in fields["Text58"]["/V"]
    assert "save DC 9, attack +1" in fields["Text58"]["/V"]
    assert "grants no spell slots" in fields["Text58"]["/V"]
    assert "Mage Armor: 1/Long Rest without a spell slot" in fields["Text58"]["/V"]
    assert fields["Text111"]["/V"] == "Intelligence"
    assert fields["Text93"]["/V"] == "-1"
    assert fields["Text94"]["/V"] == "9"
    assert fields["Text95"]["/V"] == "+1"
    assert fields["Text112"]["/V"] == ""
    assert fields["Text60"]["/V"] == "Calligrapher's Supplies\nAlchemist's Supplies"


def test_render_reads_back_spellcaster_fields(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "assets" / "character-sheet.pdf"
    output = tmp_path / "spellcaster.pdf"

    render_character_sheet(wizard_spellcaster(), template, output)

    fields = PdfReader(output).get_fields()
    assert fields is not None
    assert fields["Text111"]["/V"] == "Intelligence"
    assert fields["Text93"]["/V"] == "+3"
    assert fields["Text94"]["/V"] == "13"
    assert fields["Text95"]["/V"] == "+5"
    assert fields["Text112"]["/V"] == "2"
    assert fields["Text105.0"]["/V"] == "0"
    assert fields["Text106.0"]["/V"] == "Mage Hand"
    assert fields["Text105.3"]["/V"] == "1"
    assert fields["Text106.3"]["/V"] == "Mage Armor"
    assert fields["Text107.3"]["/V"] == "Action"
    assert fields["Text109.3"]["/V"] == "Touch"
    assert fields["Check Box254.0.3"]["/V"] == "/Yes"
    assert fields["Check Box252.4"]["/V"] == "/Yes"
    assert fields["Check Box253.4"]["/V"] == "/Yes"
    assert fields["Check Box254.0.4"]["/V"] == "/Off"
    assert fields["Check Box255.0"]["/V"] == "/Off"
    assert fields["Check Box258.0"]["/V"] == "/Off"
    assert fields["Text211"]["/V"] == "Duration: up to 10 minutes"
    assert fields["Text96"]["/V"] == "Ink-stained fingers and silver braids."
    assert fields["Text97"]["/V"] == (
        "Backstory\nRaised in a mountain archive.\n\nPersonality\nPatient, curious, and direct."
    )
    assert "Arcane Recovery: 1 use" in fields["Text55"]["/V"]


def test_render_autosizes_long_text_appearances(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "assets" / "character-sheet.pdf"
    output = tmp_path / "autosized.pdf"
    render_character_sheet(sample(), template, output)

    reader = PdfReader(output)
    annotations = cast(ArrayObject, reader.pages[0]["/Annots"])
    attack_notes = next(
        annotation
        for annotation_reference in annotations
        if (annotation := cast(DictionaryObject, annotation_reference.get_object())).get("/T")
        == "Text33"
    )
    assert attack_notes["/DA"] == "/Helv 0 Tf 0 g"
    appearance_dictionary = cast(DictionaryObject, attack_notes["/AP"])
    appearance_stream = cast(StreamObject, appearance_dictionary["/N"].get_object())
    appearance = appearance_stream.get_data().decode("latin-1")
    font_size = float(appearance.split("/Helv ", 1)[1].split(" Tf", 1)[0])
    assert 0 < font_size < 12


def test_rendered_pages_change_each_mapped_region(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "assets" / "character-sheet.pdf"
    martial_output = tmp_path / "martial.pdf"
    spellcaster_output = tmp_path / "spellcaster.pdf"
    render_character_sheet(sample(), template, martial_output)
    render_character_sheet(wizard_spellcaster(), template, spellcaster_output)

    blank_page_one = rendered_page(template, 0)
    martial_page = rendered_page(martial_output, 0)
    for bounds in (
        (20, 15, 595, 180),
        (230, 195, 595, 325),
        (230, 355, 595, 570),
        (15, 600, 595, 775),
    ):
        assert changed_pixels(blank_page_one, martial_page, bounds) > 20

    blank_page_two = rendered_page(template, 1)
    spellcaster_page = rendered_page(spellcaster_output, 1)
    for bounds in (
        (10, 15, 140, 135),
        (175, 80, 395, 135),
        (15, 175, 400, 650),
        (415, 35, 595, 285),
        (415, 340, 595, 750),
    ):
        assert changed_pixels(blank_page_two, spellcaster_page, bounds) > 20


def test_validate_template_rejects_non_pdf(tmp_path: Path) -> None:
    template = tmp_path / "not-a-template.pdf"
    template.write_text("not a PDF")

    try:
        validate_template(template)
    except ValueError as error:
        assert "official sheet" in str(error)
    else:
        raise AssertionError("Invalid template was accepted")
