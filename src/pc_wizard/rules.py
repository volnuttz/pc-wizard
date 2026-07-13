from dataclasses import dataclass

ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
STANDARD_LANGUAGES = (
    "Common Sign Language",
    "Draconic",
    "Dwarvish",
    "Elvish",
    "Giant",
    "Gnomish",
    "Goblin",
    "Halfling",
    "Orc",
)
ALIGNMENTS = (
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil",
)

SKILL_ABILITIES = {
    "Acrobatics": "dexterity",
    "Animal Handling": "wisdom",
    "Arcana": "intelligence",
    "Athletics": "strength",
    "Deception": "charisma",
    "History": "intelligence",
    "Insight": "wisdom",
    "Intimidation": "charisma",
    "Investigation": "intelligence",
    "Medicine": "wisdom",
    "Nature": "intelligence",
    "Perception": "wisdom",
    "Performance": "charisma",
    "Persuasion": "charisma",
    "Religion": "intelligence",
    "Sleight of Hand": "dexterity",
    "Stealth": "dexterity",
    "Survival": "wisdom",
}


@dataclass(frozen=True, slots=True)
class ClassRule:
    hit_die: int
    saves: tuple[str, str]
    skill_count: int
    skills: tuple[str, ...]
    armor: str
    weapons: str
    standard_array: tuple[int, int, int, int, int, int]
    features: tuple[str, ...]
    equipment: str


CLASSES: dict[str, ClassRule] = {
    "Barbarian": ClassRule(
        12,
        ("strength", "constitution"),
        2,
        ("Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"),
        "Light, Medium, Shields",
        "Simple and Martial",
        (15, 13, 14, 10, 12, 8),
        ("Rage", "Unarmored Defense", "Weapon Mastery"),
        "Greataxe; 4 Handaxes; Explorer's Pack; 15 GP",
    ),
    "Bard": ClassRule(
        8,
        ("dexterity", "charisma"),
        3,
        tuple(SKILL_ABILITIES),
        "Light",
        "Simple",
        (8, 14, 12, 13, 10, 15),
        ("Bardic Inspiration", "Spellcasting"),
        "Leather Armor; 2 Daggers; Musical Instrument; Entertainer's Pack; 19 GP",
    ),
    "Cleric": ClassRule(
        8,
        ("wisdom", "charisma"),
        2,
        ("History", "Insight", "Medicine", "Persuasion", "Religion"),
        "Light, Medium, Shields",
        "Simple",
        (14, 8, 13, 10, 15, 12),
        ("Divine Order", "Spellcasting"),
        "Chain Shirt; Shield; Mace; Holy Symbol; Priest's Pack; 7 GP",
    ),
    "Druid": ClassRule(
        8,
        ("intelligence", "wisdom"),
        2,
        (
            "Animal Handling",
            "Arcana",
            "Insight",
            "Medicine",
            "Nature",
            "Perception",
            "Religion",
            "Survival",
        ),
        "Light, Shields",
        "Simple",
        (8, 12, 14, 13, 15, 10),
        ("Druidic", "Primal Order", "Spellcasting"),
        "Leather Armor; Shield; Sickle; Druidic Focus; Explorer's Pack; 9 GP",
    ),
    "Fighter": ClassRule(
        10,
        ("strength", "constitution"),
        2,
        (
            "Acrobatics",
            "Animal Handling",
            "Athletics",
            "History",
            "Insight",
            "Intimidation",
            "Perception",
            "Persuasion",
            "Survival",
        ),
        "Light, Medium, Heavy, Shields",
        "Simple and Martial",
        (15, 14, 13, 8, 10, 12),
        ("Fighting Style", "Second Wind", "Weapon Mastery"),
        "Chain Mail; Greatsword; Flail; 8 Javelins; Dungeoneer's Pack; 4 GP",
    ),
    "Monk": ClassRule(
        8,
        ("strength", "dexterity"),
        2,
        ("Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"),
        "None",
        "Simple and Martial weapons with Light property",
        (12, 15, 13, 10, 14, 8),
        ("Martial Arts", "Unarmored Defense"),
        "Spear; 5 Daggers; Artisan's Tools; Explorer's Pack; 11 GP",
    ),
    "Paladin": ClassRule(
        10,
        ("wisdom", "charisma"),
        2,
        ("Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"),
        "Light, Medium, Heavy, Shields",
        "Simple and Martial",
        (15, 10, 13, 8, 12, 14),
        ("Lay on Hands", "Spellcasting", "Weapon Mastery"),
        "Chain Mail; Shield; Longsword; 6 Javelins; Holy Symbol; Priest's Pack; 9 GP",
    ),
    "Ranger": ClassRule(
        10,
        ("strength", "dexterity"),
        3,
        (
            "Animal Handling",
            "Athletics",
            "Insight",
            "Investigation",
            "Nature",
            "Perception",
            "Stealth",
            "Survival",
        ),
        "Light, Medium, Shields",
        "Simple and Martial",
        (12, 15, 13, 8, 14, 10),
        ("Favored Enemy", "Spellcasting", "Weapon Mastery"),
        "Studded Leather; Scimitar; Shortsword; Longbow; 20 Arrows; Explorer's Pack; 7 GP",
    ),
    "Rogue": ClassRule(
        8,
        ("dexterity", "intelligence"),
        4,
        (
            "Acrobatics",
            "Athletics",
            "Deception",
            "Insight",
            "Intimidation",
            "Investigation",
            "Perception",
            "Persuasion",
            "Sleight of Hand",
            "Stealth",
        ),
        "Light",
        "Simple and Martial weapons with Finesse or Light property",
        (12, 15, 13, 14, 10, 8),
        ("Expertise", "Sneak Attack", "Thieves' Cant", "Weapon Mastery"),
        "Leather Armor; 2 Daggers; Shortsword; Shortbow; 20 Arrows; "
        "Thieves' Tools; Burglar's Pack; 8 GP",
    ),
    "Sorcerer": ClassRule(
        6,
        ("constitution", "charisma"),
        2,
        ("Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"),
        "None",
        "Simple",
        (10, 13, 14, 8, 12, 15),
        ("Innate Sorcery", "Spellcasting"),
        "Spear; 2 Daggers; Arcane Focus; Dungeoneer's Pack; 28 GP",
    ),
    "Warlock": ClassRule(
        8,
        ("wisdom", "charisma"),
        2,
        ("Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"),
        "Light",
        "Simple",
        (8, 14, 13, 12, 10, 15),
        ("Eldritch Invocations", "Pact Magic"),
        "Leather Armor; Sickle; 2 Daggers; Arcane Focus; Book; Scholar's Pack; 15 GP",
    ),
    "Wizard": ClassRule(
        6,
        ("intelligence", "wisdom"),
        2,
        ("Arcana", "History", "Insight", "Investigation", "Medicine", "Nature", "Religion"),
        "None",
        "Simple",
        (8, 12, 13, 15, 14, 10),
        ("Arcane Recovery", "Ritual Adept", "Spellcasting"),
        "2 Daggers; Arcane Focus; Robe; Spellbook; Scholar's Pack; 5 GP",
    ),
}


@dataclass(frozen=True, slots=True)
class BackgroundRule:
    abilities: tuple[str, str, str]
    feat: str
    skills: tuple[str, str]
    tool: str
    equipment: str


BACKGROUNDS = {
    "Acolyte": BackgroundRule(
        ("intelligence", "wisdom", "charisma"),
        "Magic Initiate (Cleric)",
        ("Insight", "Religion"),
        "Calligrapher's Supplies",
        "Calligrapher's Supplies; Book (prayers); Holy Symbol; 10 Parchment; Robe; 8 GP",
    ),
    "Criminal": BackgroundRule(
        ("dexterity", "constitution", "intelligence"),
        "Alert",
        ("Sleight of Hand", "Stealth"),
        "Thieves' Tools",
        "2 Daggers; Thieves' Tools; Crowbar; 2 Pouches; Traveler's Clothes; 16 GP",
    ),
    "Sage": BackgroundRule(
        ("constitution", "intelligence", "wisdom"),
        "Magic Initiate (Wizard)",
        ("Arcana", "History"),
        "Calligrapher's Supplies",
        "Quarterstaff; Calligrapher's Supplies; Book (history); 8 Parchment; Robe; 8 GP",
    ),
    "Soldier": BackgroundRule(
        ("strength", "dexterity", "constitution"),
        "Savage Attacker",
        ("Athletics", "Intimidation"),
        "Gaming Set",
        "Spear; Shortbow; 20 Arrows; Gaming Set; Healer's Kit; Quiver; Traveler's Clothes; 14 GP",
    ),
}


@dataclass(frozen=True, slots=True)
class SpeciesRule:
    size: str
    speed: int
    traits: tuple[str, ...]


SPECIES = {
    "Dragonborn": SpeciesRule(
        "Medium",
        30,
        ("Draconic Ancestry", "Breath Weapon", "Damage Resistance", "Darkvision 60 ft."),
    ),
    "Dwarf": SpeciesRule(
        "Medium",
        30,
        ("Darkvision 120 ft.", "Dwarven Resilience", "Dwarven Toughness", "Stonecunning"),
    ),
    "Elf": SpeciesRule(
        "Medium",
        30,
        ("Darkvision 60 ft.", "Elven Lineage", "Fey Ancestry", "Keen Senses", "Trance"),
    ),
    "Gnome": SpeciesRule("Small", 30, ("Darkvision 60 ft.", "Gnomish Cunning", "Gnomish Lineage")),
    "Goliath": SpeciesRule("Medium", 35, ("Giant Ancestry", "Powerful Build")),
    "Halfling": SpeciesRule(
        "Small", 30, ("Brave", "Halfling Nimbleness", "Luck", "Naturally Stealthy")
    ),
    "Human": SpeciesRule("Medium", 30, ("Resourceful", "Skillful", "Versatile")),
    "Orc": SpeciesRule(
        "Medium", 30, ("Adrenaline Rush", "Darkvision 120 ft.", "Relentless Endurance")
    ),
    "Tiefling": SpeciesRule(
        "Medium", 30, ("Darkvision 60 ft.", "Fiendish Legacy", "Otherworldly Presence")
    ),
}
