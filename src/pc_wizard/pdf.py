from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from pypdf.generic import NameObject, TextStringObject

from pc_wizard.models import Character, signed
from pc_wizard.rules import ABILITIES, CLASSES

ABILITY_FIELDS = {
    "strength": ("Text64", "Text21", "Text91"),
    "dexterity": ("Text66", "Text22", "Text87"),
    "constitution": ("Text67", "Text24", "Text86"),
    "intelligence": ("Text63", "Text20", "Text69"),
    "wisdom": ("Text65", "Text23", "Text75"),
    "charisma": ("Text68", "Text25", "Text81"),
}
SKILL_FIELDS = {
    "Animal Handling": "Text76",
    "Insight": "Text77",
    "Medicine": "Text78",
    "Perception": "Text79",
    "Survival": "Text80",
    "Deception": "Text82",
    "Intimidation": "Text83",
    "Performance": "Text84",
    "Persuasion": "Text85",
    "Acrobatics": "Text88",
    "Sleight of Hand": "Text89",
    "Stealth": "Text90",
    "Athletics": "Text92",
    "Arcana": "Text70",
    "History": "Text71",
    "Investigation": "Text72",
    "Nature": "Text73",
    "Religion": "Text74",
}
SAVING_THROW_CHECKBOXES = {
    "strength": "Check Box37",
    "dexterity": "Check Box33",
    "constitution": "Check Box32",
    "intelligence": "Check Box4",
    "wisdom": "Check Box21",
    "charisma": "Check Box26",
}
SKILL_CHECKBOXES = {
    "Animal Handling": "Check Box22",
    "Insight": "Check Box23",
    "Medicine": "Check Box25",
    "Perception": "Check Box31",
    "Survival": "Check Box24",
    "Deception": "Check Box27",
    "Intimidation": "Check Box28",
    "Performance": "Check Box30",
    "Persuasion": "Check Box29",
    "Acrobatics": "Check Box34",
    "Sleight of Hand": "Check Box35",
    "Stealth": "Check Box36",
    "Athletics": "Check Box38",
    "Arcana": "Check Box16",
    "History": "Check Box17",
    "Investigation": "Check Box19",
    "Nature": "Check Box20",
    "Religion": "Check Box18",
}
ARMOR_TRAINING_CHECKBOXES = {
    "Light": "Check Box13",
    "Medium": "Check Box14",
    "Heavy": "Check Box15",
    "Shields": "Check Box12",
}
ATTACK_FIELDS = (
    ("Text30", "Text31", "Text32", "Text33"),
    ("Text34", "Text35", "Text36", "Text37"),
    ("Text38", "Text39", "Text40", "Text41"),
    ("Text42", "Text43", "Text44", "Text45"),
    ("Text46", "Text47", "Text48", "Text49"),
    ("Text50", "Text51", "Text52", "Text53"),
)
COIN_FIELDS = {
    "copper": "Text226",
    "silver": "Text267",
    "electrum": "Text268",
    "gold": "Text269",
    "platinum": "Text270",
}
SPELL_SLOT_FIELDS = {
    1: "Text112",
    2: "Text113",
    3: "Text114",
    4: "Text117",
    5: "Text116",
    6: "Text115",
    7: "Text118",
    8: "Text119",
    9: "Text120",
}
SPELL_NOTES_FIELDS = (
    "Text108",
    "Text208",
    "Text209",
    "Text210",
    "Text211",
    "Text212",
    "Text213",
    "Text214",
    "Text215",
    "Text216",
    "Text217",
    "Text218",
    "Text219",
    "Text220",
    "Text221",
    "Text222",
    "Text223",
    "Text224",
    "Text225",
    "Text227",
    "Text228",
    "Text229",
    "Text230",
    "Text244",
    "Text231",
    "Text232",
    "Text233",
    "Text234",
    "Text235",
    "Text236",
)
SPELL_ROW_COUNT = 30
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
    "Text12",
    "Text13",
    "Text14",
    "Text15",
    "Text16",
    "Text17",
    "Text18",
    "Text26",
    "Text27",
    "Text28",
    "Text29",
    "Text30",
    "Text31",
    "Text32",
    "Text33",
    "Text54",
    "Text55",
    "Text57",
    "Text58",
    "Text59",
    "Text60",
    "Text93",
    "Text94",
    "Text95",
    "Text96",
    "Text97",
    "Text98",
    "Text99",
    "Text100",
    "Text111",
    "Text226",
    "Text267",
    "Text268",
    "Text269",
    "Text270",
}
EXPECTED_TEMPLATE_FIELDS = (
    BASE_FIELDS
    | set(SKILL_FIELDS.values())
    | set(SAVING_THROW_CHECKBOXES.values())
    | set(SKILL_CHECKBOXES.values())
    | set(ARMOR_TRAINING_CHECKBOXES.values())
    | {field for attack_fields in ATTACK_FIELDS for field in attack_fields}
    | set(COIN_FIELDS.values())
    | set(SPELL_SLOT_FIELDS.values())
    | set(SPELL_NOTES_FIELDS)
    | {
        f"{column}.{row}"
        for column in ("Text105", "Text106", "Text107", "Text109")
        for row in range(SPELL_ROW_COUNT)
    }
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
    equipment = "\n".join(
        f"{item.quantity} x {item.name}" if item.quantity > 1 else item.name
        for item in character.inventory
    )
    values = {
        "Text1": character.name,
        "Text6": character.background,
        "Text7": character.character_class,
        "Text8": character.species,
        "Text9": "",
        "Text11": str(character.level),
        "Text12": str(character.xp),
        "Text13": str(character.armor_class),
        "Text14": str(character.hit_points),
        "Text15": "",
        "Text16": str(character.hit_points),
        "Text17": f"1d{class_rule.hit_die}",
        "Text18": "",
        "Text19": signed(character.proficiency_bonus),
        "Text26": signed(character.initiative_modifier),
        "Text27": str(character.speed),
        "Text28": character.character_size[0],
        "Text29": str(character.passive_perception),
        "Text54": "\n".join(character.class_traits),
        "Text55": "\n".join(resource.summary for resource in character.class_resources),
        "Text57": "\n".join(character.species_traits),
        "Text58": "\n".join(character.origin_feat_traits),
        "Text59": character.weapon_proficiencies,
        "Text60": "\n".join(character.all_tool_proficiencies),
        "Text93": (
            signed(character.spellcasting_modifier)
            if character.spellcasting_modifier is not None
            else ""
        ),
        "Text94": str(character.spell_save_dc) if character.spell_save_dc is not None else "",
        "Text95": (
            signed(character.spell_attack_bonus) if character.spell_attack_bonus is not None else ""
        ),
        "Text96": character.appearance or "",
        "Text97": "\n\n".join(
            detail
            for detail in (
                f"Backstory\n{character.backstory}" if character.backstory else "",
                f"Personality\n{character.personality}" if character.personality else "",
            )
            if detail
        ),
        "Text98": "\n".join(character.languages),
        "Text99": equipment,
        "Text100": character.alignment,
        "Text111": (
            character.spellcasting_ability.title()
            if character.spellcasting_ability is not None
            else ""
        ),
    }
    for ability in ABILITIES:
        score_field, modifier_field, save_field = ABILITY_FIELDS[ability]
        values[score_field] = str(getattr(character.abilities, ability))
        values[modifier_field] = signed(character.abilities.modifier(ability))
        values[save_field] = signed(character.saving_throw(ability))
        values[SAVING_THROW_CHECKBOXES[ability]] = (
            "/Yes" if ability in CLASSES[character.character_class].saves else "/Off"
        )
    for skill, field in SKILL_FIELDS.items():
        values[field] = signed(character.skill_modifier(skill))
        values[SKILL_CHECKBOXES[skill]] = "/Yes" if skill in character.skills else "/Off"
    for training, field in ARMOR_TRAINING_CHECKBOXES.items():
        values[field] = "/Yes" if training in character.armor_training else "/Off"
    for attack_fields, attack in zip(ATTACK_FIELDS, character.weapon_attacks, strict=False):
        name_field, bonus_field, damage_field, notes_field = attack_fields
        notes = (f"Range {attack.range}", *attack.properties, *attack.notes)
        values[name_field] = attack.name
        values[bonus_field] = signed(attack.attack_bonus)
        values[damage_field] = f"{attack.damage} {attack.damage_type}"
        values[notes_field] = "; ".join(notes)
    for attack_fields in ATTACK_FIELDS[len(character.weapon_attacks) :]:
        for field in attack_fields:
            values[field] = ""
    for denomination, field in COIN_FIELDS.items():
        values[field] = str(getattr(character.coins, denomination))
    for level, field in SPELL_SLOT_FIELDS.items():
        pool = next((slot for slot in character.spell_slots if slot.level == level), None)
        values[field] = str(pool.total) if pool is not None else ""
    spells = tuple((0, spell) for spell in character.all_cantrips) + tuple(
        (1, spell) for spell in character.all_prepared_spells
    )
    for row in range(SPELL_ROW_COUNT):
        level, name = spells[row] if row < len(spells) else ("", "")
        values[f"Text105.{row}"] = str(level)
        values[f"Text106.{row}"] = name
        values[f"Text107.{row}"] = ""
        values[f"Text109.{row}"] = ""
        values[SPELL_NOTES_FIELDS[row]] = ""
    return values


def _enable_text_autosizing(writer: PdfWriter) -> None:
    for page in writer.pages:
        for annotation_reference in page.get("/Annots", ()):
            annotation = annotation_reference.get_object()
            parent_reference = annotation.get("/Parent")
            parent = parent_reference.get_object() if parent_reference is not None else annotation
            if annotation.get("/FT") == "/Tx" or parent.get("/FT") == "/Tx":
                annotation[NameObject("/DA")] = TextStringObject("/Helv 0 Tf 0 g")


def render_character_sheet(character: Character, template: Path, output: Path) -> None:
    validate_template(template)
    reader = PdfReader(template)
    writer = PdfWriter(clone_from=reader)
    _enable_text_autosizing(writer)
    values = field_values(character)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        writer.write(stream)
