from pathlib import Path

from pypdf import PdfReader

from pc_wizard.models import AbilityScores, Character
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
        languages=["Common", "Dwarvish", "Giant"],
    )


def test_field_values_include_derived_values() -> None:
    values = field_values(sample())
    assert values["Text1"] == "Brunna"
    assert values["Text19"] == "17"
    assert values["Text63"] == "+5"
    assert values["Text27"] == "13"


def test_render_fills_template(tmp_path: Path) -> None:
    template = Path(__file__).parents[1] / "character-sheet.pdf"
    output = tmp_path / "sheet.pdf"
    render_character_sheet(sample(), template, output)
    reader = PdfReader(output)
    assert len(reader.pages) == 2
    fields = reader.get_fields()
    assert fields is not None
    assert fields["Text1"]["/V"] == "Brunna"


def test_validate_template_rejects_non_pdf(tmp_path: Path) -> None:
    template = tmp_path / "not-a-template.pdf"
    template.write_text("not a PDF")

    try:
        validate_template(template)
    except ValueError as error:
        assert "official sheet" in str(error)
    else:
        raise AssertionError("Invalid template was accepted")
