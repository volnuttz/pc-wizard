from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

type CreatureSize = Literal["Small", "Medium"]
type DamageType = Literal["Acid", "Cold", "Fire", "Lightning", "Necrotic", "Poison"]
type DraconicAncestry = Literal[
    "Black", "Blue", "Brass", "Bronze", "Copper", "Gold", "Green", "Red", "Silver", "White"
]
type ElvenLineage = Literal["Drow", "High Elf", "Wood Elf"]
type GnomishLineage = Literal["Forest Gnome", "Rock Gnome"]
type GoliathAncestry = Literal[
    "Cloud Giant", "Fire Giant", "Frost Giant", "Hill Giant", "Stone Giant", "Storm Giant"
]
type FiendishLegacy = Literal["Abyssal", "Chthonic", "Infernal"]
type KeenSensesSkill = Literal["Insight", "Perception", "Survival"]
type MagicInitiateList = Literal["Cleric", "Druid", "Wizard"]
type OriginFeat = Literal["Alert", "Magic Initiate", "Savage Attacker", "Skilled"]
type SpellcastingAbility = Literal["intelligence", "wisdom", "charisma"]
type DivineOrder = Literal["Protector", "Thaumaturge"]
type PrimalOrder = Literal["Magician", "Warden"]
type Alignment = Literal[
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil",
]
type StandardLanguage = Literal[
    "Common Sign Language",
    "Draconic",
    "Dwarvish",
    "Elvish",
    "Giant",
    "Gnomish",
    "Goblin",
    "Halfling",
    "Orc",
]
type Language = Literal[
    "Common",
    "Common Sign Language",
    "Draconic",
    "Dwarvish",
    "Elvish",
    "Giant",
    "Gnomish",
    "Goblin",
    "Halfling",
    "Orc",
]

DRACONIC_ANCESTORS: dict[DraconicAncestry, DamageType] = {
    "Black": "Acid",
    "Blue": "Lightning",
    "Brass": "Fire",
    "Bronze": "Lightning",
    "Copper": "Acid",
    "Gold": "Fire",
    "Green": "Poison",
    "Red": "Fire",
    "Silver": "Cold",
    "White": "Cold",
}


@dataclass(frozen=True, slots=True)
class ElvenLineageRule:
    speed: int
    darkvision_range: int
    cantrip: str
    level_three_spell: str
    level_five_spell: str
    cantrip_replaceable: bool = False


ELVEN_LINEAGES: dict[ElvenLineage, ElvenLineageRule] = {
    "Drow": ElvenLineageRule(30, 120, "Dancing Lights", "Faerie Fire", "Darkness"),
    "High Elf": ElvenLineageRule(
        30, 60, "Prestidigitation", "Detect Magic", "Misty Step", cantrip_replaceable=True
    ),
    "Wood Elf": ElvenLineageRule(35, 60, "Druidcraft", "Longstrider", "Pass without Trace"),
}


@dataclass(frozen=True, slots=True)
class GnomishLineageRule:
    cantrips: tuple[str, ...]
    always_prepared_spells: tuple[str, ...] = ()
    creates_clockwork_devices: bool = False


GNOMISH_LINEAGES: dict[GnomishLineage, GnomishLineageRule] = {
    "Forest Gnome": GnomishLineageRule(
        ("Minor Illusion",), always_prepared_spells=("Speak with Animals",)
    ),
    "Rock Gnome": GnomishLineageRule(
        ("Mending", "Prestidigitation"), creates_clockwork_devices=True
    ),
}


@dataclass(frozen=True, slots=True)
class GoliathAncestryRule:
    benefit_name: str
    trigger: str
    effect: str


GOLIATH_ANCESTRIES: dict[GoliathAncestry, GoliathAncestryRule] = {
    "Cloud Giant": GoliathAncestryRule(
        "Cloud's Jaunt",
        "Bonus Action",
        "Teleport up to 30 feet to an unoccupied space you can see.",
    ),
    "Fire Giant": GoliathAncestryRule(
        "Fire's Burn",
        "Hit",
        "Deal an extra 1d10 Fire damage to the target.",
    ),
    "Frost Giant": GoliathAncestryRule(
        "Frost's Chill",
        "Hit",
        "Deal an extra 1d6 Cold damage and reduce the target's Speed by 10 feet until "
        "the start of your next turn.",
    ),
    "Hill Giant": GoliathAncestryRule(
        "Hill's Tumble",
        "Hit",
        "Give a Large or smaller target the Prone condition.",
    ),
    "Stone Giant": GoliathAncestryRule(
        "Stone's Endurance",
        "Reaction",
        "Reduce incoming damage by 1d12 plus your Constitution modifier.",
    ),
    "Storm Giant": GoliathAncestryRule(
        "Storm's Thunder",
        "Reaction",
        "Deal 1d8 Thunder damage to the damaging creature if it is within 60 feet.",
    ),
}


@dataclass(frozen=True, slots=True)
class FiendishLegacyRule:
    resistance: DamageType
    cantrip: str
    level_three_spell: str
    level_five_spell: str


FIENDISH_LEGACIES: dict[FiendishLegacy, FiendishLegacyRule] = {
    "Abyssal": FiendishLegacyRule("Poison", "Poison Spray", "Ray of Sickness", "Hold Person"),
    "Chthonic": FiendishLegacyRule("Necrotic", "Chill Touch", "False Life", "Ray of Enfeeblement"),
    "Infernal": FiendishLegacyRule("Fire", "Fire Bolt", "Hellish Rebuke", "Darkness"),
}
KEEN_SENSES_SKILLS: tuple[KeenSensesSkill, ...] = ("Insight", "Perception", "Survival")
ORIGIN_FEATS: tuple[OriginFeat, ...] = ("Alert", "Magic Initiate", "Savage Attacker", "Skilled")
ORIGIN_FEAT_DESCRIPTIONS: dict[OriginFeat, str] = {
    "Alert": "Add Proficiency Bonus to Initiative and swap Initiative with a willing ally.",
    "Magic Initiate": "Learn two cantrips and one level 1 spell from one chosen spell list.",
    "Savage Attacker": "Once per turn, roll weapon damage dice twice and use either roll.",
    "Skilled": "Gain proficiency in any combination of three skills or tools.",
}
SPELLCASTING_ABILITIES: tuple[SpellcastingAbility, ...] = (
    "intelligence",
    "wisdom",
    "charisma",
)


@dataclass(frozen=True, slots=True)
class MagicInitiateSpellList:
    cantrips: tuple[str, ...]
    level_one_spells: tuple[str, ...]


MAGIC_INITIATE_SPELL_LISTS: dict[MagicInitiateList, MagicInitiateSpellList] = {
    "Cleric": MagicInitiateSpellList(
        (
            "Guidance",
            "Light",
            "Mending",
            "Resistance",
            "Sacred Flame",
            "Spare the Dying",
            "Thaumaturgy",
        ),
        (
            "Bane",
            "Bless",
            "Command",
            "Create or Destroy Water",
            "Cure Wounds",
            "Detect Evil and Good",
            "Detect Magic",
            "Detect Poison and Disease",
            "Guiding Bolt",
            "Healing Word",
            "Inflict Wounds",
            "Protection from Evil and Good",
            "Purify Food and Drink",
            "Sanctuary",
            "Shield of Faith",
        ),
    ),
    "Druid": MagicInitiateSpellList(
        (
            "Druidcraft",
            "Elementalism",
            "Guidance",
            "Mending",
            "Message",
            "Poison Spray",
            "Produce Flame",
            "Resistance",
            "Shillelagh",
            "Spare the Dying",
            "Starry Wisp",
        ),
        (
            "Animal Friendship",
            "Charm Person",
            "Create or Destroy Water",
            "Cure Wounds",
            "Detect Magic",
            "Detect Poison and Disease",
            "Entangle",
            "Faerie Fire",
            "Fog Cloud",
            "Goodberry",
            "Healing Word",
            "Ice Knife",
            "Jump",
            "Longstrider",
            "Protection from Evil and Good",
            "Purify Food and Drink",
            "Speak with Animals",
            "Thunderwave",
        ),
    ),
    "Wizard": MagicInitiateSpellList(
        (
            "Acid Splash",
            "Chill Touch",
            "Dancing Lights",
            "Elementalism",
            "Fire Bolt",
            "Light",
            "Mage Hand",
            "Mending",
            "Message",
            "Minor Illusion",
            "Poison Spray",
            "Prestidigitation",
            "Ray of Frost",
            "Shocking Grasp",
            "True Strike",
        ),
        (
            "Alarm",
            "Burning Hands",
            "Charm Person",
            "Chromatic Orb",
            "Color Spray",
            "Comprehend Languages",
            "Detect Magic",
            "Disguise Self",
            "Expeditious Retreat",
            "False Life",
            "Feather Fall",
            "Find Familiar",
            "Floating Disk",
            "Fog Cloud",
            "Grease",
            "Hideous Laughter",
            "Ice Knife",
            "Identify",
            "Illusory Script",
            "Jump",
            "Longstrider",
            "Mage Armor",
            "Magic Missile",
            "Protection from Evil and Good",
            "Ray of Sickness",
            "Shield",
            "Silent Image",
            "Sleep",
            "Thunderwave",
            "Unseen Servant",
        ),
    ),
}

CLASS_SPELL_LISTS: dict[str, MagicInitiateSpellList] = {
    "Bard": MagicInitiateSpellList(
        (
            "Dancing Lights",
            "Light",
            "Mage Hand",
            "Mending",
            "Message",
            "Minor Illusion",
            "Prestidigitation",
            "Starry Wisp",
            "True Strike",
            "Vicious Mockery",
        ),
        (
            "Animal Friendship",
            "Bane",
            "Charm Person",
            "Color Spray",
            "Command",
            "Comprehend Languages",
            "Cure Wounds",
            "Detect Magic",
            "Disguise Self",
            "Dissonant Whispers",
            "Faerie Fire",
            "Feather Fall",
            "Healing Word",
            "Heroism",
            "Hideous Laughter",
            "Identify",
            "Illusory Script",
            "Longstrider",
            "Silent Image",
            "Sleep",
            "Speak with Animals",
            "Thunderwave",
            "Unseen Servant",
        ),
    ),
    "Cleric": MAGIC_INITIATE_SPELL_LISTS["Cleric"],
    "Druid": MAGIC_INITIATE_SPELL_LISTS["Druid"],
    "Paladin": MagicInitiateSpellList(
        (),
        (
            "Bless",
            "Command",
            "Cure Wounds",
            "Detect Evil and Good",
            "Detect Magic",
            "Detect Poison and Disease",
            "Divine Favor",
            "Divine Smite",
            "Heroism",
            "Protection from Evil and Good",
            "Purify Food and Drink",
            "Searing Smite",
            "Shield of Faith",
        ),
    ),
    "Ranger": MagicInitiateSpellList(
        (),
        (
            "Alarm",
            "Animal Friendship",
            "Cure Wounds",
            "Detect Magic",
            "Detect Poison and Disease",
            "Ensnaring Strike",
            "Entangle",
            "Fog Cloud",
            "Goodberry",
            "Hunter's Mark",
            "Jump",
            "Longstrider",
            "Speak with Animals",
        ),
    ),
    "Sorcerer": MagicInitiateSpellList(
        (
            "Acid Splash",
            "Chill Touch",
            "Dancing Lights",
            "Elementalism",
            "Fire Bolt",
            "Light",
            "Mage Hand",
            "Mending",
            "Message",
            "Minor Illusion",
            "Poison Spray",
            "Prestidigitation",
            "Ray of Frost",
            "Shocking Grasp",
            "Sorcerous Burst",
            "True Strike",
        ),
        (
            "Burning Hands",
            "Charm Person",
            "Chromatic Orb",
            "Color Spray",
            "Comprehend Languages",
            "Detect Magic",
            "Disguise Self",
            "Expeditious Retreat",
            "False Life",
            "Feather Fall",
            "Fog Cloud",
            "Grease",
            "Ice Knife",
            "Jump",
            "Mage Armor",
            "Magic Missile",
            "Ray of Sickness",
            "Shield",
            "Silent Image",
            "Sleep",
            "Thunderwave",
        ),
    ),
    "Warlock": MagicInitiateSpellList(
        (
            "Chill Touch",
            "Eldritch Blast",
            "Mage Hand",
            "Minor Illusion",
            "Poison Spray",
            "Prestidigitation",
            "True Strike",
        ),
        (
            "Bane",
            "Charm Person",
            "Comprehend Languages",
            "Detect Magic",
            "Expeditious Retreat",
            "Hellish Rebuke",
            "Hex",
            "Hideous Laughter",
            "Illusory Script",
            "Protection from Evil and Good",
            "Speak with Animals",
            "Unseen Servant",
        ),
    ),
    "Wizard": MAGIC_INITIATE_SPELL_LISTS["Wizard"],
}

CLASS_ALWAYS_PREPARED_SPELLS: dict[str, tuple[str, ...]] = {
    "Druid": ("Speak with Animals",),
    "Ranger": ("Hunter's Mark",),
}


@dataclass(frozen=True, slots=True)
class SpellRule:
    casting_time: str
    range: str
    components: str
    duration: str

    @property
    def concentration(self) -> bool:
        return self.duration.startswith("Concentration")

    @property
    def ritual(self) -> bool:
        return "Ritual" in self.casting_time

    @property
    def required_material(self) -> str | None:
        marker = "M ("
        if marker not in self.components:
            return None
        return self.components.split(marker, 1)[1].removesuffix(")")

    @property
    def table_casting_time(self) -> str:
        return self.casting_time.split(", which", 1)[0].replace(" or Ritual", "")

    @property
    def table_notes(self) -> str:
        duration = self.duration.removeprefix("Concentration, ").removeprefix("Concentration ")
        return f"Duration: {duration}"


_SPELL_RULE_DATA: dict[str, tuple[str, str, str, str]] = {
    "Acid Splash": ("Action", "60 feet", "V, S", "Instantaneous"),
    "Alarm": ("1 minute or Ritual", "30 feet", "V, S, M (a bell and silver wire)", "8 hours"),
    "Animal Friendship": ("Action", "30 feet", "V, S, M (a morsel of food)", "24 hours"),
    "Bane": ("Action", "30 feet", "V, S, M (a drop of blood)", "Concentration, up to 1 minute"),
    "Bless": (
        "Action",
        "30 feet",
        "V, S, M (a Holy Symbol worth 5+ GP)",
        "Concentration, up to 1 minute",
    ),
    "Burning Hands": ("Action", "Self", "V, S", "Instantaneous"),
    "Charm Person": ("Action", "30 feet", "V, S", "1 hour"),
    "Chill Touch": ("Action", "Touch", "V, S", "Instantaneous"),
    "Chromatic Orb": ("Action", "90 feet", "V, S, M (a diamond worth 50+ GP)", "Instantaneous"),
    "Color Spray": ("Action", "Self", "V, S, M (a pinch of colorful sand)", "Instantaneous"),
    "Command": ("Action", "60 feet", "V", "Instantaneous"),
    "Comprehend Languages": (
        "Action or Ritual",
        "Self",
        "V, S, M (a pinch of soot and salt)",
        "1 hour",
    ),
    "Create or Destroy Water": (
        "Action",
        "30 feet",
        "V, S, M (a mix of water and sand)",
        "Instantaneous",
    ),
    "Cure Wounds": ("Action", "Touch", "V, S", "Instantaneous"),
    "Dancing Lights": (
        "Action",
        "120 feet",
        "V, S, M (a bit of phosphorus)",
        "Concentration, up to 1 minute",
    ),
    "Detect Evil and Good": ("Action", "Self", "V, S", "Concentration, up to 10 minutes"),
    "Detect Magic": ("Action or Ritual", "Self", "V, S", "Concentration, up to 10 minutes"),
    "Detect Poison and Disease": (
        "Action or Ritual",
        "Self",
        "V, S, M (a yew leaf)",
        "Concentration, up to 10 minutes",
    ),
    "Disguise Self": ("Action", "Self", "V, S", "1 hour"),
    "Dissonant Whispers": ("Action", "60 feet", "V", "Instantaneous"),
    "Divine Favor": ("Bonus Action", "Self", "V, S", "1 minute"),
    "Divine Smite": (
        "Bonus Action, which you take immediately after hitting a target with a Melee "
        "weapon or an Unarmed Strike",
        "Self",
        "V",
        "Instantaneous",
    ),
    "Druidcraft": ("Action", "30 feet", "V, S", "Instantaneous"),
    "Eldritch Blast": ("Action", "120 feet", "V, S", "Instantaneous"),
    "Elementalism": ("Action", "30 feet", "V, S", "Instantaneous"),
    "Ensnaring Strike": (
        "Bonus Action, which you take immediately after hitting a creature with a weapon",
        "Self",
        "V",
        "Concentration, up to 1 minute",
    ),
    "Entangle": ("Action", "90 feet", "V, S", "Concentration, up to 1 minute"),
    "Expeditious Retreat": ("Bonus Action", "Self", "V, S", "Concentration, up to 10 minutes"),
    "Faerie Fire": ("Action", "60 feet", "V", "Concentration, up to 1 minute"),
    "False Life": ("Action", "Self", "V, S, M (a drop of alcohol)", "Instantaneous"),
    "Feather Fall": (
        "Reaction, which you take when you or a creature you can see within 60 feet of you falls",
        "60 feet",
        "V, M (a small feather or piece of down)",
        "1 minute",
    ),
    "Find Familiar": (
        "1 hour or Ritual",
        "10 feet",
        "V, S, M (burning incense worth 10+ GP, which the spell consumes)",
        "Instantaneous",
    ),
    "Fire Bolt": ("Action", "120 feet", "V, S", "Instantaneous"),
    "Floating Disk": ("Action or Ritual", "30 feet", "V, S, M (a drop of mercury)", "1 hour"),
    "Fog Cloud": ("Action", "120 feet", "V, S", "Concentration, up to 1 hour"),
    "Goodberry": ("Action", "Self", "V, S, M (a sprig of mistletoe)", "24 hours"),
    "Grease": ("Action", "60 feet", "V, S, M (a bit of pork rind or butter)", "1 minute"),
    "Guidance": ("Action", "Touch", "V, S", "Concentration, up to 1 minute"),
    "Guiding Bolt": ("Action", "120 feet", "V, S", "1 round"),
    "Healing Word": ("Bonus Action", "60 feet", "V", "Instantaneous"),
    "Hellish Rebuke": (
        "Reaction, which you take in response to taking damage from a creature that you "
        "can see within 60 feet of yourself",
        "60 feet",
        "V, S",
        "Instantaneous",
    ),
    "Heroism": ("Action", "Touch", "V, S", "Concentration, up to 1 minute"),
    "Hex": (
        "Bonus Action",
        "90 feet",
        "V, S, M (the petrified eye of a newt)",
        "Concentration, up to 1 hour",
    ),
    "Hideous Laughter": (
        "Action",
        "30 feet",
        "V, S, M (a tart and a feather)",
        "Concentration, up to 1 minute",
    ),
    "Hunter's Mark": ("Bonus Action", "90 feet", "V", "Concentration, up to 1 hour"),
    "Ice Knife": ("Action", "60 feet", "S, M (a drop of water or a piece of ice)", "Instantaneous"),
    "Identify": ("1 minute or Ritual", "Touch", "V, S, M (a pearl worth 100+ GP)", "Instantaneous"),
    "Illusory Script": (
        "1 minute or Ritual",
        "Touch",
        "S, M (ink worth 10+ GP, which the spell consumes)",
        "10 days",
    ),
    "Inflict Wounds": ("Action", "Touch", "V, S", "Instantaneous"),
    "Jump": ("Bonus Action", "Touch", "V, S, M (a grasshopper's hind leg)", "1 minute"),
    "Light": ("Action", "Touch", "V, M (a firefly or phosphorescent moss)", "1 hour"),
    "Longstrider": ("Action", "Touch", "V, S, M (a pinch of dirt)", "1 hour"),
    "Mage Armor": ("Action", "Touch", "V, S, M (a piece of cured leather)", "8 hours"),
    "Mage Hand": ("Action", "30 feet", "V, S", "1 minute"),
    "Magic Missile": ("Action", "120 feet", "V, S", "Instantaneous"),
    "Mending": ("1 minute", "Touch", "V, S, M (two lodestones)", "Instantaneous"),
    "Message": ("Action", "120 feet", "S, M (a copper wire)", "1 round"),
    "Minor Illusion": ("Action", "30 feet", "S, M (a bit of fleece)", "1 minute"),
    "Poison Spray": ("Action", "30 feet", "V, S", "Instantaneous"),
    "Prestidigitation": ("Action", "10 feet", "V, S", "Up to 1 hour"),
    "Produce Flame": ("Bonus Action", "Self", "V, S", "10 minutes"),
    "Protection from Evil and Good": (
        "Action",
        "Touch",
        "V, S, M (a flask of Holy Water worth 25+ GP, which the spell consumes)",
        "Concentration, up to 10 minutes",
    ),
    "Purify Food and Drink": ("Action or Ritual", "10 feet", "V, S", "Instantaneous"),
    "Ray of Frost": ("Action", "60 feet", "V, S", "Instantaneous"),
    "Ray of Sickness": ("Action", "60 feet", "V, S", "Instantaneous"),
    "Resistance": ("Action", "Touch", "V, S", "Concentration, up to 1 minute"),
    "Sacred Flame": ("Action", "60 feet", "V, S", "Instantaneous"),
    "Sanctuary": (
        "Bonus Action",
        "30 feet",
        "V, S, M (a shard of glass from a mirror)",
        "1 minute",
    ),
    "Searing Smite": (
        "Bonus Action, which you take immediately after hitting a target with a Melee "
        "weapon or an Unarmed Strike",
        "Self",
        "V",
        "1 minute",
    ),
    "Shield": (
        "Reaction, which you take when you are hit by an attack roll or targeted by the "
        "Magic Missile spell",
        "Self",
        "V, S",
        "1 round",
    ),
    "Shield of Faith": (
        "Bonus Action",
        "60 feet",
        "V, S, M (a prayer scroll)",
        "Concentration, up to 10 minutes",
    ),
    "Shillelagh": ("Bonus Action", "Self", "V, S, M (mistletoe)", "1 minute"),
    "Shocking Grasp": ("Action", "Touch", "V, S", "Instantaneous"),
    "Silent Image": (
        "Action",
        "60 feet",
        "V, S, M (a bit of fleece)",
        "Concentration, up to 10 minutes",
    ),
    "Sleep": (
        "Action",
        "60 feet",
        "V, S, M (a pinch of sand or rose petals)",
        "Concentration, up to 1 minute",
    ),
    "Sorcerous Burst": ("Action", "120 feet", "V, S", "Instantaneous"),
    "Spare the Dying": ("Action", "15 feet", "V, S", "Instantaneous"),
    "Speak with Animals": ("Action or Ritual", "Self", "V, S", "10 minutes"),
    "Starry Wisp": ("Action", "60 feet", "V, S", "Instantaneous"),
    "Thaumaturgy": ("Action", "30 feet", "V", "Up to 1 minute"),
    "Thunderwave": ("Action", "Self", "V, S", "Instantaneous"),
    "True Strike": (
        "Action",
        "Self",
        "S, M (a weapon with which you have proficiency and that is worth 1+ CP)",
        "Instantaneous",
    ),
    "Unseen Servant": (
        "Action or Ritual",
        "60 feet",
        "V, S, M (a bit of string and of wood)",
        "1 hour",
    ),
    "Vicious Mockery": ("Action", "60 feet", "V", "Instantaneous"),
}

SPELL_RULES = {
    name: SpellRule(casting_time, range_, components, duration)
    for name, (casting_time, range_, components, duration) in _SPELL_RULE_DATA.items()
}

FIGHTING_STYLES = ("Archery", "Defense", "Great Weapon Fighting", "Two-Weapon Fighting")
LEVEL_ONE_WARLOCK_INVOCATIONS = {
    "Armor of Shadows": "Cast Mage Armor on yourself without a spell slot.",
    "Eldritch Mind": "Advantage on Constitution saves to maintain Concentration.",
    "Pact of the Blade": "Conjure or bond with a pact weapon.",
    "Pact of the Chain": "Learn Find Familiar and cast it without a spell slot.",
    "Pact of the Tome": "Conjure a Book of Shadows with cantrips and rituals.",
}

ARTISAN_TOOLS = (
    "Alchemist's Supplies",
    "Brewer's Supplies",
    "Calligrapher's Supplies",
    "Carpenter's Tools",
    "Cartographer's Tools",
    "Cobbler's Tools",
    "Cook's Utensils",
    "Glassblower's Tools",
    "Jeweler's Tools",
    "Leatherworker's Tools",
    "Mason's Tools",
    "Painter's Supplies",
    "Potter's Tools",
    "Smith's Tools",
    "Tinker's Tools",
    "Weaver's Tools",
    "Woodcarver's Tools",
)
MUSICAL_INSTRUMENTS = (
    "Musical Instrument (Bagpipes)",
    "Musical Instrument (Drum)",
    "Musical Instrument (Dulcimer)",
    "Musical Instrument (Flute)",
    "Musical Instrument (Horn)",
    "Musical Instrument (Lute)",
    "Musical Instrument (Lyre)",
    "Musical Instrument (Pan Flute)",
    "Musical Instrument (Shawm)",
    "Musical Instrument (Viol)",
)

TOOLS = (
    *ARTISAN_TOOLS,
    "Disguise Kit",
    "Forgery Kit",
    "Gaming Set (Dice)",
    "Gaming Set (Dragonchess)",
    "Gaming Set (Playing Cards)",
    "Gaming Set (Three-Dragon Ante)",
    "Herbalism Kit",
    *MUSICAL_INSTRUMENTS,
    "Navigator's Tools",
    "Poisoner's Kit",
    "Thieves' Tools",
)

ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
MAX_ABILITY_SCORE = 20
POINT_BUY_BUDGET = 27
STANDARD_ARRAY = (15, 14, 13, 12, 10, 8)
POINT_BUY_COSTS = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
}


def point_buy_cost(values: Sequence[int]) -> int:
    try:
        return sum(POINT_BUY_COSTS[value] for value in values)
    except KeyError as error:
        raise ValueError(f"point-buy scores must be between 8 and 15: {error.args[0]}") from error


def eligible_abilities_for_increase(
    scores: Mapping[str, int], abilities: Sequence[str], amount: int
) -> tuple[str, ...]:
    if amount < 1:
        raise ValueError("ability-score increase must be positive")
    return tuple(ability for ability in abilities if scores[ability] + amount <= MAX_ABILITY_SCORE)


STANDARD_LANGUAGES: tuple[StandardLanguage, ...] = (
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
ALIGNMENTS: tuple[Alignment, ...] = (
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
class WeaponRule:
    category: Literal["Simple", "Martial"]
    kind: Literal["Melee", "Ranged"]
    properties: tuple[str, ...]
    mastery: str


@dataclass(frozen=True, slots=True)
class WeaponCombatRule:
    damage: str
    damage_type: Literal["Bludgeoning", "Piercing", "Slashing"]
    normal_range: int = 5
    long_range: int | None = None
    versatile_damage: str | None = None


WEAPONS: dict[str, WeaponRule] = {
    "Club": WeaponRule("Simple", "Melee", ("Light",), "Slow"),
    "Dagger": WeaponRule("Simple", "Melee", ("Finesse", "Light", "Thrown"), "Nick"),
    "Greatclub": WeaponRule("Simple", "Melee", ("Two-Handed",), "Push"),
    "Handaxe": WeaponRule("Simple", "Melee", ("Light", "Thrown"), "Vex"),
    "Javelin": WeaponRule("Simple", "Melee", ("Thrown",), "Slow"),
    "Light Hammer": WeaponRule("Simple", "Melee", ("Light", "Thrown"), "Nick"),
    "Mace": WeaponRule("Simple", "Melee", (), "Sap"),
    "Quarterstaff": WeaponRule("Simple", "Melee", ("Versatile",), "Topple"),
    "Sickle": WeaponRule("Simple", "Melee", ("Light",), "Nick"),
    "Spear": WeaponRule("Simple", "Melee", ("Thrown", "Versatile"), "Sap"),
    "Dart": WeaponRule("Simple", "Ranged", ("Finesse", "Thrown"), "Vex"),
    "Light Crossbow": WeaponRule(
        "Simple", "Ranged", ("Ammunition", "Loading", "Two-Handed"), "Slow"
    ),
    "Shortbow": WeaponRule("Simple", "Ranged", ("Ammunition", "Two-Handed"), "Vex"),
    "Sling": WeaponRule("Simple", "Ranged", ("Ammunition",), "Slow"),
    "Battleaxe": WeaponRule("Martial", "Melee", ("Versatile",), "Topple"),
    "Flail": WeaponRule("Martial", "Melee", (), "Sap"),
    "Glaive": WeaponRule("Martial", "Melee", ("Heavy", "Reach", "Two-Handed"), "Graze"),
    "Greataxe": WeaponRule("Martial", "Melee", ("Heavy", "Two-Handed"), "Cleave"),
    "Greatsword": WeaponRule("Martial", "Melee", ("Heavy", "Two-Handed"), "Graze"),
    "Halberd": WeaponRule("Martial", "Melee", ("Heavy", "Reach", "Two-Handed"), "Cleave"),
    "Lance": WeaponRule("Martial", "Melee", ("Heavy", "Reach", "Two-Handed"), "Topple"),
    "Longsword": WeaponRule("Martial", "Melee", ("Versatile",), "Sap"),
    "Maul": WeaponRule("Martial", "Melee", ("Heavy", "Two-Handed"), "Topple"),
    "Morningstar": WeaponRule("Martial", "Melee", (), "Sap"),
    "Pike": WeaponRule("Martial", "Melee", ("Heavy", "Reach", "Two-Handed"), "Push"),
    "Rapier": WeaponRule("Martial", "Melee", ("Finesse",), "Vex"),
    "Scimitar": WeaponRule("Martial", "Melee", ("Finesse", "Light"), "Nick"),
    "Shortsword": WeaponRule("Martial", "Melee", ("Finesse", "Light"), "Vex"),
    "Trident": WeaponRule("Martial", "Melee", ("Thrown", "Versatile"), "Topple"),
    "Warhammer": WeaponRule("Martial", "Melee", ("Versatile",), "Push"),
    "War Pick": WeaponRule("Martial", "Melee", ("Versatile",), "Sap"),
    "Whip": WeaponRule("Martial", "Melee", ("Finesse", "Reach"), "Slow"),
    "Blowgun": WeaponRule("Martial", "Ranged", ("Ammunition", "Loading"), "Vex"),
    "Hand Crossbow": WeaponRule("Martial", "Ranged", ("Ammunition", "Light", "Loading"), "Vex"),
    "Heavy Crossbow": WeaponRule(
        "Martial", "Ranged", ("Ammunition", "Heavy", "Loading", "Two-Handed"), "Push"
    ),
    "Longbow": WeaponRule("Martial", "Ranged", ("Ammunition", "Heavy", "Two-Handed"), "Slow"),
    "Musket": WeaponRule("Martial", "Ranged", ("Ammunition", "Loading", "Two-Handed"), "Slow"),
    "Pistol": WeaponRule("Martial", "Ranged", ("Ammunition", "Loading"), "Vex"),
}

WEAPON_COMBAT_RULES: dict[str, WeaponCombatRule] = {
    "Club": WeaponCombatRule("1d4", "Bludgeoning"),
    "Dagger": WeaponCombatRule("1d4", "Piercing", 20, 60),
    "Greatclub": WeaponCombatRule("1d8", "Bludgeoning"),
    "Handaxe": WeaponCombatRule("1d6", "Slashing", 20, 60),
    "Javelin": WeaponCombatRule("1d6", "Piercing", 30, 120),
    "Light Hammer": WeaponCombatRule("1d4", "Bludgeoning", 20, 60),
    "Mace": WeaponCombatRule("1d6", "Bludgeoning"),
    "Quarterstaff": WeaponCombatRule("1d6", "Bludgeoning", versatile_damage="1d8"),
    "Sickle": WeaponCombatRule("1d4", "Slashing"),
    "Spear": WeaponCombatRule("1d6", "Piercing", 20, 60, "1d8"),
    "Dart": WeaponCombatRule("1d4", "Piercing", 20, 60),
    "Light Crossbow": WeaponCombatRule("1d8", "Piercing", 80, 320),
    "Shortbow": WeaponCombatRule("1d6", "Piercing", 80, 320),
    "Sling": WeaponCombatRule("1d4", "Bludgeoning", 30, 120),
    "Battleaxe": WeaponCombatRule("1d8", "Slashing", versatile_damage="1d10"),
    "Flail": WeaponCombatRule("1d8", "Bludgeoning"),
    "Glaive": WeaponCombatRule("1d10", "Slashing", 10),
    "Greataxe": WeaponCombatRule("1d12", "Slashing"),
    "Greatsword": WeaponCombatRule("2d6", "Slashing"),
    "Halberd": WeaponCombatRule("1d10", "Slashing", 10),
    "Lance": WeaponCombatRule("1d10", "Piercing", 10),
    "Longsword": WeaponCombatRule("1d8", "Slashing", versatile_damage="1d10"),
    "Maul": WeaponCombatRule("2d6", "Bludgeoning"),
    "Morningstar": WeaponCombatRule("1d8", "Piercing"),
    "Pike": WeaponCombatRule("1d10", "Piercing", 10),
    "Rapier": WeaponCombatRule("1d8", "Piercing"),
    "Scimitar": WeaponCombatRule("1d6", "Slashing"),
    "Shortsword": WeaponCombatRule("1d6", "Piercing"),
    "Trident": WeaponCombatRule("1d8", "Piercing", 20, 60, "1d10"),
    "Warhammer": WeaponCombatRule("1d8", "Bludgeoning", versatile_damage="1d10"),
    "War Pick": WeaponCombatRule("1d8", "Piercing", versatile_damage="1d10"),
    "Whip": WeaponCombatRule("1d4", "Slashing", 10),
    "Blowgun": WeaponCombatRule("1", "Piercing", 25, 100),
    "Hand Crossbow": WeaponCombatRule("1d6", "Piercing", 30, 120),
    "Heavy Crossbow": WeaponCombatRule("1d10", "Piercing", 100, 400),
    "Longbow": WeaponCombatRule("1d8", "Piercing", 150, 600),
    "Musket": WeaponCombatRule("1d12", "Piercing", 40, 120),
    "Pistol": WeaponCombatRule("1d10", "Piercing", 30, 90),
}


@dataclass(frozen=True, slots=True)
class ArmorRule:
    category: Literal["Light", "Medium", "Heavy"]
    base_ac: int
    dexterity_cap: int | None
    strength_requirement: int | None = None
    stealth_disadvantage: bool = False


ARMOR: dict[str, ArmorRule] = {
    "Padded Armor": ArmorRule("Light", 11, None, stealth_disadvantage=True),
    "Leather Armor": ArmorRule("Light", 11, None),
    "Studded Leather Armor": ArmorRule("Light", 12, None),
    "Hide Armor": ArmorRule("Medium", 12, 2),
    "Chain Shirt": ArmorRule("Medium", 13, 2),
    "Scale Mail": ArmorRule("Medium", 14, 2, stealth_disadvantage=True),
    "Breastplate": ArmorRule("Medium", 14, 2),
    "Half Plate Armor": ArmorRule("Medium", 15, 2, stealth_disadvantage=True),
    "Ring Mail": ArmorRule("Heavy", 14, 0, stealth_disadvantage=True),
    "Chain Mail": ArmorRule("Heavy", 16, 0, 13, True),
    "Splint Armor": ArmorRule("Heavy", 17, 0, 15, True),
    "Plate Armor": ArmorRule("Heavy", 18, 0, 15, True),
}


@dataclass(frozen=True, slots=True)
class EquipmentGrant:
    name: str
    quantity: int = 1
    weapon: str | None = None


@dataclass(frozen=True, slots=True)
class EquipmentPackage:
    label: str
    items: tuple[EquipmentGrant, ...]
    gold: int


@dataclass(frozen=True, slots=True)
class StartingEquipmentRule:
    packages: dict[str, EquipmentPackage]
    gold: int


CLASS_STARTING_EQUIPMENT: dict[str, StartingEquipmentRule] = {
    "Barbarian": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Greataxe and Handaxes",
                (
                    EquipmentGrant("Greataxe"),
                    EquipmentGrant("Handaxe", 4),
                    EquipmentGrant("Explorer's Pack"),
                ),
                15,
            )
        },
        75,
    ),
    "Bard": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Leather armor and instruments",
                (
                    EquipmentGrant("Leather Armor"),
                    EquipmentGrant("Dagger", 2),
                    EquipmentGrant("Chosen Musical Instrument"),
                    EquipmentGrant("Entertainer's Pack"),
                ),
                19,
            )
        },
        90,
    ),
    "Cleric": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Chain shirt, shield, and mace",
                (
                    EquipmentGrant("Chain Shirt"),
                    EquipmentGrant("Shield"),
                    EquipmentGrant("Mace"),
                    EquipmentGrant("Holy Symbol"),
                    EquipmentGrant("Priest's Pack"),
                ),
                7,
            )
        },
        110,
    ),
    "Druid": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Leather armor, shield, and sickle",
                (
                    EquipmentGrant("Leather Armor"),
                    EquipmentGrant("Shield"),
                    EquipmentGrant("Sickle"),
                    EquipmentGrant("Druidic Focus (Quarterstaff)", weapon="Quarterstaff"),
                    EquipmentGrant("Explorer's Pack"),
                    EquipmentGrant("Herbalism Kit"),
                ),
                9,
            )
        },
        50,
    ),
    "Fighter": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Chain mail and heavy weapons",
                (
                    EquipmentGrant("Chain Mail"),
                    EquipmentGrant("Greatsword"),
                    EquipmentGrant("Flail"),
                    EquipmentGrant("Javelin", 8),
                    EquipmentGrant("Dungeoneer's Pack"),
                ),
                4,
            ),
            "B": EquipmentPackage(
                "Studded leather and ranged weapons",
                (
                    EquipmentGrant("Studded Leather Armor"),
                    EquipmentGrant("Scimitar"),
                    EquipmentGrant("Shortsword"),
                    EquipmentGrant("Longbow"),
                    EquipmentGrant("Arrow", 20),
                    EquipmentGrant("Quiver"),
                    EquipmentGrant("Dungeoneer's Pack"),
                ),
                11,
            ),
        },
        155,
    ),
    "Monk": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Spear, daggers, and chosen tool",
                (
                    EquipmentGrant("Spear"),
                    EquipmentGrant("Dagger", 5),
                    EquipmentGrant("Chosen Monk Tool"),
                    EquipmentGrant("Explorer's Pack"),
                ),
                11,
            )
        },
        50,
    ),
    "Paladin": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Chain mail, shield, and longsword",
                (
                    EquipmentGrant("Chain Mail"),
                    EquipmentGrant("Shield"),
                    EquipmentGrant("Longsword"),
                    EquipmentGrant("Javelin", 6),
                    EquipmentGrant("Holy Symbol"),
                    EquipmentGrant("Priest's Pack"),
                ),
                9,
            )
        },
        150,
    ),
    "Ranger": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Studded leather and ranger weapons",
                (
                    EquipmentGrant("Studded Leather Armor"),
                    EquipmentGrant("Scimitar"),
                    EquipmentGrant("Shortsword"),
                    EquipmentGrant("Longbow"),
                    EquipmentGrant("Arrow", 20),
                    EquipmentGrant("Quiver"),
                    EquipmentGrant("Druidic Focus (Sprig of Mistletoe)"),
                    EquipmentGrant("Explorer's Pack"),
                ),
                7,
            )
        },
        150,
    ),
    "Rogue": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Leather armor and rogue weapons",
                (
                    EquipmentGrant("Leather Armor"),
                    EquipmentGrant("Dagger", 2),
                    EquipmentGrant("Shortsword"),
                    EquipmentGrant("Shortbow"),
                    EquipmentGrant("Arrow", 20),
                    EquipmentGrant("Quiver"),
                    EquipmentGrant("Thieves' Tools"),
                    EquipmentGrant("Burglar's Pack"),
                ),
                8,
            )
        },
        100,
    ),
    "Sorcerer": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Spear, daggers, and arcane focus",
                (
                    EquipmentGrant("Spear"),
                    EquipmentGrant("Dagger", 2),
                    EquipmentGrant("Arcane Focus (Crystal)"),
                    EquipmentGrant("Dungeoneer's Pack"),
                ),
                28,
            )
        },
        50,
    ),
    "Warlock": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Leather armor and occult gear",
                (
                    EquipmentGrant("Leather Armor"),
                    EquipmentGrant("Sickle"),
                    EquipmentGrant("Dagger", 2),
                    EquipmentGrant("Arcane Focus (Orb)"),
                    EquipmentGrant("Book (Occult Lore)"),
                    EquipmentGrant("Scholar's Pack"),
                ),
                15,
            )
        },
        100,
    ),
    "Wizard": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Daggers, focus, and spellbook",
                (
                    EquipmentGrant("Dagger", 2),
                    EquipmentGrant("Arcane Focus (Quarterstaff)", weapon="Quarterstaff"),
                    EquipmentGrant("Robe"),
                    EquipmentGrant("Spellbook"),
                    EquipmentGrant("Scholar's Pack"),
                ),
                5,
            )
        },
        55,
    ),
}

BACKGROUND_STARTING_EQUIPMENT: dict[str, StartingEquipmentRule] = {
    "Acolyte": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Acolyte equipment",
                (
                    EquipmentGrant("Calligrapher's Supplies"),
                    EquipmentGrant("Book (Prayers)"),
                    EquipmentGrant("Holy Symbol"),
                    EquipmentGrant("Parchment", 10),
                    EquipmentGrant("Robe"),
                ),
                8,
            )
        },
        50,
    ),
    "Criminal": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Criminal equipment",
                (
                    EquipmentGrant("Dagger", 2),
                    EquipmentGrant("Thieves' Tools"),
                    EquipmentGrant("Crowbar"),
                    EquipmentGrant("Pouch", 2),
                    EquipmentGrant("Traveler's Clothes"),
                ),
                16,
            )
        },
        50,
    ),
    "Sage": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Sage equipment",
                (
                    EquipmentGrant("Quarterstaff"),
                    EquipmentGrant("Calligrapher's Supplies"),
                    EquipmentGrant("Book (History)"),
                    EquipmentGrant("Parchment", 8),
                    EquipmentGrant("Robe"),
                ),
                8,
            )
        },
        50,
    ),
    "Soldier": StartingEquipmentRule(
        {
            "A": EquipmentPackage(
                "Soldier equipment",
                (
                    EquipmentGrant("Spear"),
                    EquipmentGrant("Shortbow"),
                    EquipmentGrant("Arrow", 20),
                    EquipmentGrant("Gaming Set"),
                    EquipmentGrant("Healer's Kit"),
                    EquipmentGrant("Quiver"),
                    EquipmentGrant("Traveler's Clothes"),
                ),
                14,
            )
        },
        50,
    ),
}

CLASS_SPELLCASTING_ABILITIES: dict[str, SpellcastingAbility] = {
    "Bard": "charisma",
    "Cleric": "wisdom",
    "Druid": "wisdom",
    "Paladin": "charisma",
    "Ranger": "wisdom",
    "Sorcerer": "charisma",
    "Warlock": "charisma",
    "Wizard": "intelligence",
}

LEVEL_ONE_SPELL_SLOTS: dict[str, tuple[int, int]] = {
    "Bard": (1, 2),
    "Cleric": (1, 2),
    "Druid": (1, 2),
    "Paladin": (1, 2),
    "Ranger": (1, 2),
    "Sorcerer": (1, 2),
    "Warlock": (1, 1),
    "Wizard": (1, 2),
}

WEAPON_MASTERY_COUNTS = {
    "Barbarian": 2,
    "Fighter": 3,
    "Paladin": 2,
    "Ranger": 2,
    "Rogue": 2,
}


def weapon_mastery_options(character_class: str) -> tuple[str, ...]:
    if character_class == "Barbarian":
        return tuple(name for name, rule in WEAPONS.items() if rule.kind == "Melee")
    if character_class == "Rogue":
        return tuple(
            name
            for name, rule in WEAPONS.items()
            if rule.category == "Simple" or {"Finesse", "Light"} & set(rule.properties)
        )
    return tuple(WEAPONS)


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

BACKGROUND_ORIGIN_FEATS: dict[str, OriginFeat] = {
    "Acolyte": "Magic Initiate",
    "Criminal": "Alert",
    "Sage": "Magic Initiate",
    "Soldier": "Savage Attacker",
}
BACKGROUND_MAGIC_INITIATE_LISTS: dict[str, MagicInitiateList] = {
    "Acolyte": "Cleric",
    "Sage": "Wizard",
}


@dataclass(frozen=True, slots=True)
class SpeciesRule:
    sizes: tuple[CreatureSize, ...]
    speed: int
    traits: tuple[str, ...]
    darkvision_range: int | None = None
    resistances: tuple[DamageType, ...] = ()


SPECIES = {
    "Dragonborn": SpeciesRule(
        ("Medium",),
        30,
        ("Breath Weapon",),
        darkvision_range=60,
    ),
    "Dwarf": SpeciesRule(
        ("Medium",),
        30,
        ("Dwarven Resilience", "Dwarven Toughness", "Stonecunning"),
        darkvision_range=120,
        resistances=("Poison",),
    ),
    "Elf": SpeciesRule(
        ("Medium",),
        30,
        ("Fey Ancestry", "Trance"),
        darkvision_range=60,
    ),
    "Gnome": SpeciesRule(("Small",), 30, ("Gnomish Cunning",), darkvision_range=60),
    "Goliath": SpeciesRule(("Medium",), 35, ("Giant Ancestry", "Powerful Build")),
    "Halfling": SpeciesRule(
        ("Small",), 30, ("Brave", "Halfling Nimbleness", "Luck", "Naturally Stealthy")
    ),
    "Human": SpeciesRule(("Medium", "Small"), 30, ("Resourceful", "Skillful", "Versatile")),
    "Orc": SpeciesRule(
        ("Medium",),
        30,
        ("Adrenaline Rush", "Relentless Endurance"),
        darkvision_range=120,
    ),
    "Tiefling": SpeciesRule(
        ("Medium", "Small"),
        30,
        ("Otherworldly Presence",),
        darkvision_range=60,
    ),
}
