from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from pc_wizard.models import Character, signed
from pc_wizard.rules import ABILITIES, BACKGROUNDS, CLASSES, SPECIES

ABILITY_FIELDS = {
    "strength": ("Text19", "Text20", "Text63"),
    "dexterity": ("Text21", "Text23", "Text65"),
    "constitution": ("Text22", "Text24", "Text67"),
    "intelligence": ("Text91", "Text92", "Text64"),
    "wisdom": ("Text87", "Text90", "Text66"),
    "charisma": ("Text86", "Text89", "Text68"),
}
SKILL_FIELDS = {
    "Animal Handling": "Text69",
    "Insight": "Text70",
    "Medicine": "Text71",
    "Perception": "Text72",
    "Survival": "Text73",
    "Deception": "Text74",
    "Intimidation": "Text75",
    "Performance": "Text76",
    "Persuasion": "Text77",
    "Acrobatics": "Text78",
    "Sleight of Hand": "Text79",
    "Stealth": "Text80",
    "Athletics": "Text81",
    "Arcana": "Text82",
    "History": "Text83",
    "Investigation": "Text84",
    "Nature": "Text85",
    "Religion": "Text88",
}
TEMPLATE_DOWNLOAD_URL = (
    "https://media.dndbeyond.com/compendium-images/free-rules/ph/character-sheet.pdf"
)
TEMPLATE_PAGE_URL = "https://www.dndbeyond.com/resources/1779-d-d-character-sheets"
BASE_FIELDS = {
    "Text1",
    "Text6",
    "Text7",
    "Text8",
    "Text9",
    "Text11",
    "Text14",
    "Text15",
    "Text16",
    "Text17",
    "Text18",
    "Text26",
    "Text27",
    "Text28",
    "Text29",
    "Text54",
    "Text55",
    "Text57",
    "Text58",
    "Text59",
    "Text60",
    "Text93",
    "Text111",
    "Text226",
}
EXPECTED_TEMPLATE_FIELDS = (
    BASE_FIELDS
    | set(SKILL_FIELDS.values())
    | {field for fields_for_ability in ABILITY_FIELDS.values() for field in fields_for_ability}
)


def validate_template(template: Path) -> None:
    """Validate that a PDF is the supported official character-sheet template."""
    try:
        reader = PdfReader(template)
    except (OSError, PdfReadError) as error:
        raise ValueError(
            f"Unable to read PDF template {template}. Download the official sheet from "
            f"{TEMPLATE_PAGE_URL}."
        ) from error
    fields = reader.get_fields()
    missing_fields = EXPECTED_TEMPLATE_FIELDS - set(fields or {})
    if len(reader.pages) != 2 or missing_fields:
        raise ValueError(
            f"Incompatible PDF template {template}. Download the supported official sheet from "
            f"{TEMPLATE_DOWNLOAD_URL} (this direct URL may change; see {TEMPLATE_PAGE_URL})."
        )


def field_values(character: Character) -> dict[str, str]:
    class_rule = CLASSES[character.character_class]
    background = BACKGROUNDS[character.background]
    species = SPECIES[character.species]
    values = {
        "Text1": character.name,
        "Text6": character.character_class,
        "Text7": str(character.level),
        "Text8": character.background,
        "Text9": character.species,
        "Text11": str(character.xp),
        "Text14": signed(character.abilities.modifier("dexterity")),
        "Text15": species.size[0],
        "Text16": str(species.speed),
        "Text17": str(character.passive_perception),
        "Text18": signed(character.proficiency_bonus),
        "Text26": str(character.armor_class),
        "Text27": str(character.hit_points),
        "Text28": str(character.hit_points),
        "Text29": f"1d{class_rule.hit_die}",
        "Text54": "\n".join(class_rule.features),
        "Text55": "\n".join(species.traits),
        "Text57": f"Class: {class_rule.equipment}\nBackground: {background.equipment}",
        "Text58": f"Feat: {background.feat}",
        "Text59": background.tool,
        "Text60": class_rule.weapons,
        "Text93": character.alignment,
        "Text111": character.name,
        "Text226": "\n".join(character.languages),
    }
    for ability in ABILITIES:
        score_field, modifier_field, save_field = ABILITY_FIELDS[ability]
        values[score_field] = str(getattr(character.abilities, ability))
        values[modifier_field] = signed(character.abilities.modifier(ability))
        values[save_field] = signed(character.saving_throw(ability))
    for skill, field in SKILL_FIELDS.items():
        values[field] = signed(character.skill_modifier(skill))
    return values


def render_character_sheet(character: Character, template: Path, output: Path) -> None:
    validate_template(template)
    reader = PdfReader(template)
    writer = PdfWriter(clone_from=reader)
    values = field_values(character)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        writer.write(stream)
