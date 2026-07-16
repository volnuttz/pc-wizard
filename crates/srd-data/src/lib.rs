//! SRD 5.2.1-derived identifiers and level-1 rule metadata.
//!
//! The values in this crate were checked against the frozen migration oracle;
//! `assets/SRD_CC_v5.2.1.pdf` remains the normative source.

use std::{collections::BTreeMap, sync::OnceLock};

use serde::Deserialize;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ClassRule {
    pub hit_die: u8,
    pub saves: &'static [&'static str],
    pub skill_count: usize,
    pub skills: &'static [&'static str],
    pub armor: &'static str,
    pub weapons: &'static str,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BackgroundRule {
    pub abilities: &'static [&'static str],
    pub feat: &'static str,
    pub skills: &'static [&'static str],
    pub tool: &'static str,
    pub magic_initiate_list: Option<&'static str>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SpeciesRule {
    pub sizes: &'static [&'static str],
    pub speed: u8,
    pub darkvision_range: Option<u8>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct EquipmentGrant {
    pub name: &'static str,
    pub quantity: u16,
    pub weapon: Option<&'static str>,
}

impl EquipmentGrant {
    const fn one(name: &'static str) -> Self {
        Self {
            name,
            quantity: 1,
            weapon: None,
        }
    }
    const fn many(name: &'static str, quantity: u16) -> Self {
        Self {
            name,
            quantity,
            weapon: None,
        }
    }
    const fn weapon(name: &'static str, weapon: &'static str) -> Self {
        Self {
            name,
            quantity: 1,
            weapon: Some(weapon),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ArmorRule {
    pub category: &'static str,
    pub base_ac: i16,
    pub dexterity_cap: Option<i16>,
    pub strength_requirement: Option<u8>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct WeaponRule {
    pub category: &'static str,
    pub kind: &'static str,
    pub properties: &'static [&'static str],
    pub mastery: &'static str,
    pub damage: &'static str,
    pub damage_type: &'static str,
    pub normal_range: u16,
    pub long_range: Option<u16>,
    pub versatile_damage: Option<&'static str>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SpellList {
    pub cantrips: &'static [&'static str],
    pub level_one_spells: &'static [&'static str],
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
pub struct SpellRule {
    pub casting_time: String,
    pub range: String,
    pub concentration: bool,
    pub ritual: bool,
    pub required_material: Option<String>,
    pub notes: String,
}

#[must_use]
/// Return structured sheet metadata for an SRD creation spell.
///
/// # Panics
///
/// Panics only if the checked-in generated SRD spell fixture is malformed.
pub fn spell_rule(name: &str) -> Option<&'static SpellRule> {
    static RULES: OnceLock<BTreeMap<String, SpellRule>> = OnceLock::new();
    RULES
        .get_or_init(|| {
            serde_json::from_str(include_str!(
                "../../../contracts/fixtures/srd-spells-v1.json"
            ))
            .expect("checked SRD spell fixture is valid")
        })
        .get(name)
}

const CLERIC_CANTRIPS: &[&str] = &[
    "Guidance",
    "Light",
    "Mending",
    "Resistance",
    "Sacred Flame",
    "Spare the Dying",
    "Thaumaturgy",
];
const CLERIC_SPELLS: &[&str] = &[
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
];
const DRUID_CANTRIPS: &[&str] = &[
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
];
const DRUID_SPELLS: &[&str] = &[
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
];
const WIZARD_CANTRIPS: &[&str] = &[
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
];
const WIZARD_SPELLS: &[&str] = &[
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
];
const BARD_CANTRIPS: &[&str] = &[
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
];
const BARD_SPELLS: &[&str] = &[
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
];
const PALADIN_SPELLS: &[&str] = &[
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
];
const RANGER_SPELLS: &[&str] = &[
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
];
const SORCERER_CANTRIPS: &[&str] = &[
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
];
const SORCERER_SPELLS: &[&str] = &[
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
];
const WARLOCK_CANTRIPS: &[&str] = &[
    "Chill Touch",
    "Eldritch Blast",
    "Mage Hand",
    "Minor Illusion",
    "Poison Spray",
    "Prestidigitation",
    "True Strike",
];
const WARLOCK_SPELLS: &[&str] = &[
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
];

#[must_use]
pub fn magic_initiate_spell_list(name: &str) -> Option<SpellList> {
    match name {
        "Cleric" => Some(SpellList {
            cantrips: CLERIC_CANTRIPS,
            level_one_spells: CLERIC_SPELLS,
        }),
        "Druid" => Some(SpellList {
            cantrips: DRUID_CANTRIPS,
            level_one_spells: DRUID_SPELLS,
        }),
        "Wizard" => Some(SpellList {
            cantrips: WIZARD_CANTRIPS,
            level_one_spells: WIZARD_SPELLS,
        }),
        _ => None,
    }
}

#[must_use]
pub fn class_spell_list(name: &str) -> Option<SpellList> {
    match name {
        "Bard" => Some(SpellList {
            cantrips: BARD_CANTRIPS,
            level_one_spells: BARD_SPELLS,
        }),
        "Cleric" => magic_initiate_spell_list("Cleric"),
        "Druid" => magic_initiate_spell_list("Druid"),
        "Paladin" => Some(SpellList {
            cantrips: &[],
            level_one_spells: PALADIN_SPELLS,
        }),
        "Ranger" => Some(SpellList {
            cantrips: &[],
            level_one_spells: RANGER_SPELLS,
        }),
        "Sorcerer" => Some(SpellList {
            cantrips: SORCERER_CANTRIPS,
            level_one_spells: SORCERER_SPELLS,
        }),
        "Warlock" => Some(SpellList {
            cantrips: WARLOCK_CANTRIPS,
            level_one_spells: WARLOCK_SPELLS,
        }),
        "Wizard" => magic_initiate_spell_list("Wizard"),
        _ => None,
    }
}

#[must_use]
pub fn class_always_prepared(name: &str) -> &'static [&'static str] {
    match name {
        "Druid" => &["Speak with Animals"],
        "Ranger" => &["Hunter's Mark"],
        _ => &[],
    }
}

#[must_use]
pub fn class_spellcasting_ability(name: &str) -> Option<&'static str> {
    match name {
        "Bard" | "Sorcerer" | "Warlock" | "Paladin" => Some("charisma"),
        "Cleric" | "Druid" | "Ranger" => Some("wisdom"),
        "Wizard" => Some("intelligence"),
        _ => None,
    }
}

#[must_use]
pub fn level_one_spell_slots(name: &str) -> Option<(u8, u8, &'static str)> {
    match name {
        "Warlock" => Some((1, 1, "Short or Long Rest")),
        "Bard" | "Cleric" | "Druid" | "Paladin" | "Ranger" | "Sorcerer" | "Wizard" => {
            Some((1, 2, "Long Rest"))
        }
        _ => None,
    }
}

#[must_use]
pub fn dragonborn_damage_type(ancestry: &str) -> Option<&'static str> {
    match ancestry {
        "Black" | "Copper" => Some("Acid"),
        "Blue" | "Bronze" => Some("Lightning"),
        "Brass" | "Gold" | "Red" => Some("Fire"),
        "Green" => Some("Poison"),
        "Silver" | "White" => Some("Cold"),
        _ => None,
    }
}

#[must_use]
pub fn tiefling_resistance(legacy: &str) -> Option<&'static str> {
    match legacy {
        "Abyssal" => Some("Poison"),
        "Chthonic" => Some("Necrotic"),
        "Infernal" => Some("Fire"),
        _ => None,
    }
}

#[must_use]
pub fn tiefling_cantrip(legacy: &str) -> Option<&'static str> {
    match legacy {
        "Abyssal" => Some("Poison Spray"),
        "Chthonic" => Some("Chill Touch"),
        "Infernal" => Some("Fire Bolt"),
        _ => None,
    }
}

pub const ABILITIES: [&str; 6] = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
];
pub const CLASS_NAMES: [&str; 12] = [
    "Barbarian",
    "Bard",
    "Cleric",
    "Druid",
    "Fighter",
    "Monk",
    "Paladin",
    "Ranger",
    "Rogue",
    "Sorcerer",
    "Warlock",
    "Wizard",
];
pub const BACKGROUND_NAMES: [&str; 4] = ["Acolyte", "Criminal", "Sage", "Soldier"];
pub const SPECIES_NAMES: [&str; 9] = [
    "Dragonborn",
    "Dwarf",
    "Elf",
    "Gnome",
    "Goliath",
    "Halfling",
    "Human",
    "Orc",
    "Tiefling",
];
pub const WEAPON_NAMES: [&str; 38] = [
    "Club",
    "Dagger",
    "Greatclub",
    "Handaxe",
    "Javelin",
    "Light Hammer",
    "Mace",
    "Quarterstaff",
    "Sickle",
    "Spear",
    "Dart",
    "Light Crossbow",
    "Shortbow",
    "Sling",
    "Battleaxe",
    "Flail",
    "Glaive",
    "Greataxe",
    "Greatsword",
    "Halberd",
    "Lance",
    "Longsword",
    "Maul",
    "Morningstar",
    "Pike",
    "Rapier",
    "Scimitar",
    "Shortsword",
    "Trident",
    "Warhammer",
    "War Pick",
    "Whip",
    "Blowgun",
    "Hand Crossbow",
    "Heavy Crossbow",
    "Longbow",
    "Musket",
    "Pistol",
];
pub const ALIGNMENTS: [&str; 9] = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil",
];
pub const STANDARD_LANGUAGES: [&str; 9] = [
    "Common Sign Language",
    "Draconic",
    "Dwarvish",
    "Elvish",
    "Giant",
    "Gnomish",
    "Goblin",
    "Halfling",
    "Orc",
];
pub const SPELLCASTING_ABILITIES: [&str; 3] = ["intelligence", "wisdom", "charisma"];
pub const STANDARD_ARRAY: [u8; 6] = [15, 14, 13, 12, 10, 8];
pub const POINT_BUY_BUDGET: u8 = 27;
pub const ORIGIN_FEATS: [&str; 4] = ["Alert", "Magic Initiate", "Savage Attacker", "Skilled"];
pub const FIGHTING_STYLES: [&str; 4] = [
    "Archery",
    "Defense",
    "Great Weapon Fighting",
    "Two-Weapon Fighting",
];
pub const WARLOCK_INVOCATIONS: [&str; 5] = [
    "Armor of Shadows",
    "Eldritch Mind",
    "Pact of the Blade",
    "Pact of the Chain",
    "Pact of the Tome",
];
pub const ARTISAN_TOOLS: [&str; 17] = [
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
];
pub const MUSICAL_INSTRUMENTS: [&str; 10] = [
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
];

#[must_use]
pub fn is_tool(name: &str) -> bool {
    ARTISAN_TOOLS.contains(&name)
        || MUSICAL_INSTRUMENTS.contains(&name)
        || [
            "Disguise Kit",
            "Forgery Kit",
            "Gaming Set (Dice)",
            "Gaming Set (Dragonchess)",
            "Gaming Set (Playing Cards)",
            "Gaming Set (Three-Dragon Ante)",
            "Herbalism Kit",
            "Navigator's Tools",
            "Poisoner's Kit",
            "Thieves' Tools",
        ]
        .contains(&name)
}
pub const SKILLS: [&str; 18] = [
    "Acrobatics",
    "Animal Handling",
    "Arcana",
    "Athletics",
    "Deception",
    "History",
    "Insight",
    "Intimidation",
    "Investigation",
    "Medicine",
    "Nature",
    "Perception",
    "Performance",
    "Persuasion",
    "Religion",
    "Sleight of Hand",
    "Stealth",
    "Survival",
];

const BARBARIAN_SKILLS: &[&str] = &[
    "Animal Handling",
    "Athletics",
    "Intimidation",
    "Nature",
    "Perception",
    "Survival",
];
const BARD_SKILLS: &[&str] = &SKILLS;
const CLERIC_SKILLS: &[&str] = &["History", "Insight", "Medicine", "Persuasion", "Religion"];
const DRUID_SKILLS: &[&str] = &[
    "Animal Handling",
    "Arcana",
    "Insight",
    "Medicine",
    "Nature",
    "Perception",
    "Religion",
    "Survival",
];
const FIGHTER_SKILLS: &[&str] = &[
    "Acrobatics",
    "Animal Handling",
    "Athletics",
    "History",
    "Insight",
    "Intimidation",
    "Perception",
    "Persuasion",
    "Survival",
];
const MONK_SKILLS: &[&str] = &[
    "Acrobatics",
    "Athletics",
    "History",
    "Insight",
    "Religion",
    "Stealth",
];
const PALADIN_SKILLS: &[&str] = &[
    "Athletics",
    "Insight",
    "Intimidation",
    "Medicine",
    "Persuasion",
    "Religion",
];
const RANGER_SKILLS: &[&str] = &[
    "Animal Handling",
    "Athletics",
    "Insight",
    "Investigation",
    "Nature",
    "Perception",
    "Stealth",
    "Survival",
];
const ROGUE_SKILLS: &[&str] = &[
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
];
const SORCERER_SKILLS: &[&str] = &[
    "Arcana",
    "Deception",
    "Insight",
    "Intimidation",
    "Persuasion",
    "Religion",
];
const WARLOCK_SKILLS: &[&str] = &[
    "Arcana",
    "Deception",
    "History",
    "Intimidation",
    "Investigation",
    "Nature",
    "Religion",
];
const WIZARD_SKILLS: &[&str] = &[
    "Arcana",
    "History",
    "Insight",
    "Investigation",
    "Medicine",
    "Nature",
    "Religion",
];

#[must_use]
pub fn class_rule(name: &str) -> Option<ClassRule> {
    let rule = match name {
        "Barbarian" => ClassRule {
            hit_die: 12,
            saves: &["strength", "constitution"],
            skill_count: 2,
            skills: BARBARIAN_SKILLS,
            armor: "Light, Medium, Shields",
            weapons: "Simple and Martial",
        },
        "Bard" => ClassRule {
            hit_die: 8,
            saves: &["dexterity", "charisma"],
            skill_count: 3,
            skills: BARD_SKILLS,
            armor: "Light",
            weapons: "Simple",
        },
        "Cleric" => ClassRule {
            hit_die: 8,
            saves: &["wisdom", "charisma"],
            skill_count: 2,
            skills: CLERIC_SKILLS,
            armor: "Light, Medium, Shields",
            weapons: "Simple",
        },
        "Druid" => ClassRule {
            hit_die: 8,
            saves: &["intelligence", "wisdom"],
            skill_count: 2,
            skills: DRUID_SKILLS,
            armor: "Light, Shields",
            weapons: "Simple",
        },
        "Fighter" => ClassRule {
            hit_die: 10,
            saves: &["strength", "constitution"],
            skill_count: 2,
            skills: FIGHTER_SKILLS,
            armor: "Light, Medium, Heavy, Shields",
            weapons: "Simple and Martial",
        },
        "Monk" => ClassRule {
            hit_die: 8,
            saves: &["strength", "dexterity"],
            skill_count: 2,
            skills: MONK_SKILLS,
            armor: "None",
            weapons: "Simple and Martial weapons with Light property",
        },
        "Paladin" => ClassRule {
            hit_die: 10,
            saves: &["wisdom", "charisma"],
            skill_count: 2,
            skills: PALADIN_SKILLS,
            armor: "Light, Medium, Heavy, Shields",
            weapons: "Simple and Martial",
        },
        "Ranger" => ClassRule {
            hit_die: 10,
            saves: &["strength", "dexterity"],
            skill_count: 3,
            skills: RANGER_SKILLS,
            armor: "Light, Medium, Shields",
            weapons: "Simple and Martial",
        },
        "Rogue" => ClassRule {
            hit_die: 8,
            saves: &["dexterity", "intelligence"],
            skill_count: 4,
            skills: ROGUE_SKILLS,
            armor: "Light",
            weapons: "Simple and Martial weapons with Finesse or Light property",
        },
        "Sorcerer" => ClassRule {
            hit_die: 6,
            saves: &["constitution", "charisma"],
            skill_count: 2,
            skills: SORCERER_SKILLS,
            armor: "None",
            weapons: "Simple",
        },
        "Warlock" => ClassRule {
            hit_die: 8,
            saves: &["wisdom", "charisma"],
            skill_count: 2,
            skills: WARLOCK_SKILLS,
            armor: "Light",
            weapons: "Simple",
        },
        "Wizard" => ClassRule {
            hit_die: 6,
            saves: &["intelligence", "wisdom"],
            skill_count: 2,
            skills: WIZARD_SKILLS,
            armor: "None",
            weapons: "Simple",
        },
        _ => return None,
    };
    Some(rule)
}

#[must_use]
pub fn suggested_array(class: &str) -> Option<[u8; 6]> {
    match class {
        "Barbarian" => Some([15, 13, 14, 10, 12, 8]),
        "Bard" => Some([8, 14, 12, 13, 10, 15]),
        "Cleric" => Some([14, 8, 13, 10, 15, 12]),
        "Druid" => Some([8, 12, 14, 13, 15, 10]),
        "Fighter" => Some([15, 14, 13, 8, 10, 12]),
        "Monk" => Some([12, 15, 13, 10, 14, 8]),
        "Paladin" => Some([15, 10, 13, 8, 12, 14]),
        "Ranger" => Some([12, 15, 13, 8, 14, 10]),
        "Rogue" => Some([12, 15, 13, 14, 10, 8]),
        "Sorcerer" => Some([10, 13, 14, 8, 12, 15]),
        "Warlock" => Some([8, 14, 13, 12, 10, 15]),
        "Wizard" => Some([8, 12, 13, 15, 14, 10]),
        _ => None,
    }
}

#[must_use]
pub const fn point_buy_cost(score: u8) -> Option<u8> {
    match score {
        8 => Some(0),
        9 => Some(1),
        10 => Some(2),
        11 => Some(3),
        12 => Some(4),
        13 => Some(5),
        14 => Some(7),
        15 => Some(9),
        _ => None,
    }
}

#[must_use]
pub fn background_rule(name: &str) -> Option<BackgroundRule> {
    let rule = match name {
        "Acolyte" => BackgroundRule {
            abilities: &["intelligence", "wisdom", "charisma"],
            feat: "Magic Initiate",
            skills: &["Insight", "Religion"],
            tool: "Calligrapher's Supplies",
            magic_initiate_list: Some("Cleric"),
        },
        "Criminal" => BackgroundRule {
            abilities: &["dexterity", "constitution", "intelligence"],
            feat: "Alert",
            skills: &["Sleight of Hand", "Stealth"],
            tool: "Thieves' Tools",
            magic_initiate_list: None,
        },
        "Sage" => BackgroundRule {
            abilities: &["constitution", "intelligence", "wisdom"],
            feat: "Magic Initiate",
            skills: &["Arcana", "History"],
            tool: "Calligrapher's Supplies",
            magic_initiate_list: Some("Wizard"),
        },
        "Soldier" => BackgroundRule {
            abilities: &["strength", "dexterity", "constitution"],
            feat: "Savage Attacker",
            skills: &["Athletics", "Intimidation"],
            tool: "Gaming Set",
            magic_initiate_list: None,
        },
        _ => return None,
    };
    Some(rule)
}

#[must_use]
pub fn species_rule(name: &str) -> Option<SpeciesRule> {
    let rule = match name {
        "Dragonborn" | "Elf" => SpeciesRule {
            sizes: &["Medium"],
            speed: 30,
            darkvision_range: Some(60),
        },
        "Dwarf" | "Orc" => SpeciesRule {
            sizes: &["Medium"],
            speed: 30,
            darkvision_range: Some(120),
        },
        "Gnome" => SpeciesRule {
            sizes: &["Small"],
            speed: 30,
            darkvision_range: Some(60),
        },
        "Goliath" => SpeciesRule {
            sizes: &["Medium"],
            speed: 35,
            darkvision_range: None,
        },
        "Halfling" => SpeciesRule {
            sizes: &["Small"],
            speed: 30,
            darkvision_range: None,
        },
        "Human" => SpeciesRule {
            sizes: &["Medium", "Small"],
            speed: 30,
            darkvision_range: None,
        },
        "Tiefling" => SpeciesRule {
            sizes: &["Medium", "Small"],
            speed: 30,
            darkvision_range: Some(60),
        },
        _ => return None,
    };
    Some(rule)
}

#[must_use]
pub fn skill_ability(skill: &str) -> Option<&'static str> {
    match skill {
        "Acrobatics" | "Sleight of Hand" | "Stealth" => Some("dexterity"),
        "Animal Handling" | "Insight" | "Medicine" | "Perception" | "Survival" => Some("wisdom"),
        "Arcana" | "History" | "Investigation" | "Nature" | "Religion" => Some("intelligence"),
        "Athletics" => Some("strength"),
        "Deception" | "Intimidation" | "Performance" | "Persuasion" => Some("charisma"),
        _ => None,
    }
}

#[must_use]
pub fn weapon_mastery_count(class: &str) -> usize {
    match class {
        "Barbarian" | "Paladin" | "Ranger" | "Rogue" => 2,
        "Fighter" => 3,
        _ => 0,
    }
}

#[must_use]
pub fn armor_rule(name: &str) -> Option<ArmorRule> {
    let rule = match name {
        "Padded Armor" | "Leather Armor" => ArmorRule {
            category: "Light",
            base_ac: 11,
            dexterity_cap: None,
            strength_requirement: None,
        },
        "Studded Leather Armor" => ArmorRule {
            category: "Light",
            base_ac: 12,
            dexterity_cap: None,
            strength_requirement: None,
        },
        "Hide Armor" => ArmorRule {
            category: "Medium",
            base_ac: 12,
            dexterity_cap: Some(2),
            strength_requirement: None,
        },
        "Chain Shirt" => ArmorRule {
            category: "Medium",
            base_ac: 13,
            dexterity_cap: Some(2),
            strength_requirement: None,
        },
        "Scale Mail" | "Breastplate" => ArmorRule {
            category: "Medium",
            base_ac: 14,
            dexterity_cap: Some(2),
            strength_requirement: None,
        },
        "Half Plate Armor" => ArmorRule {
            category: "Medium",
            base_ac: 15,
            dexterity_cap: Some(2),
            strength_requirement: None,
        },
        "Ring Mail" => ArmorRule {
            category: "Heavy",
            base_ac: 14,
            dexterity_cap: Some(0),
            strength_requirement: None,
        },
        "Chain Mail" => ArmorRule {
            category: "Heavy",
            base_ac: 16,
            dexterity_cap: Some(0),
            strength_requirement: Some(13),
        },
        "Splint Armor" => ArmorRule {
            category: "Heavy",
            base_ac: 17,
            dexterity_cap: Some(0),
            strength_requirement: Some(15),
        },
        "Plate Armor" => ArmorRule {
            category: "Heavy",
            base_ac: 18,
            dexterity_cap: Some(0),
            strength_requirement: Some(15),
        },
        _ => return None,
    };
    Some(rule)
}

macro_rules! weapon {
    ($category:expr, $kind:expr, [$($property:expr),*], $mastery:expr, $damage:expr, $damage_type:expr, $range:expr, $long:expr, $versatile:expr) => {
        WeaponRule { category: $category, kind: $kind, properties: &[$($property),*], mastery: $mastery, damage: $damage, damage_type: $damage_type, normal_range: $range, long_range: $long, versatile_damage: $versatile }
    };
}

#[must_use]
#[allow(clippy::too_many_lines)]
pub fn weapon_rule(name: &str) -> Option<WeaponRule> {
    let rule = match name {
        "Club" => weapon!(
            "Simple",
            "Melee",
            ["Light"],
            "Slow",
            "1d4",
            "Bludgeoning",
            5,
            None,
            None
        ),
        "Dagger" => weapon!(
            "Simple",
            "Melee",
            ["Finesse", "Light", "Thrown"],
            "Nick",
            "1d4",
            "Piercing",
            20,
            Some(60),
            None
        ),
        "Greatclub" => weapon!(
            "Simple",
            "Melee",
            ["Two-Handed"],
            "Push",
            "1d8",
            "Bludgeoning",
            5,
            None,
            None
        ),
        "Handaxe" => weapon!(
            "Simple",
            "Melee",
            ["Light", "Thrown"],
            "Vex",
            "1d6",
            "Slashing",
            20,
            Some(60),
            None
        ),
        "Javelin" => weapon!(
            "Simple",
            "Melee",
            ["Thrown"],
            "Slow",
            "1d6",
            "Piercing",
            30,
            Some(120),
            None
        ),
        "Light Hammer" => weapon!(
            "Simple",
            "Melee",
            ["Light", "Thrown"],
            "Nick",
            "1d4",
            "Bludgeoning",
            20,
            Some(60),
            None
        ),
        "Mace" => weapon!(
            "Simple",
            "Melee",
            [],
            "Sap",
            "1d6",
            "Bludgeoning",
            5,
            None,
            None
        ),
        "Quarterstaff" => weapon!(
            "Simple",
            "Melee",
            ["Versatile"],
            "Topple",
            "1d6",
            "Bludgeoning",
            5,
            None,
            Some("1d8")
        ),
        "Sickle" => weapon!(
            "Simple",
            "Melee",
            ["Light"],
            "Nick",
            "1d4",
            "Slashing",
            5,
            None,
            None
        ),
        "Spear" => weapon!(
            "Simple",
            "Melee",
            ["Thrown", "Versatile"],
            "Sap",
            "1d6",
            "Piercing",
            20,
            Some(60),
            Some("1d8")
        ),
        "Dart" => weapon!(
            "Simple",
            "Ranged",
            ["Finesse", "Thrown"],
            "Vex",
            "1d4",
            "Piercing",
            20,
            Some(60),
            None
        ),
        "Light Crossbow" => weapon!(
            "Simple",
            "Ranged",
            ["Ammunition", "Loading", "Two-Handed"],
            "Slow",
            "1d8",
            "Piercing",
            80,
            Some(320),
            None
        ),
        "Shortbow" => weapon!(
            "Simple",
            "Ranged",
            ["Ammunition", "Two-Handed"],
            "Vex",
            "1d6",
            "Piercing",
            80,
            Some(320),
            None
        ),
        "Sling" => weapon!(
            "Simple",
            "Ranged",
            ["Ammunition"],
            "Slow",
            "1d4",
            "Bludgeoning",
            30,
            Some(120),
            None
        ),
        "Battleaxe" => weapon!(
            "Martial",
            "Melee",
            ["Versatile"],
            "Topple",
            "1d8",
            "Slashing",
            5,
            None,
            Some("1d10")
        ),
        "Flail" => weapon!(
            "Martial",
            "Melee",
            [],
            "Sap",
            "1d8",
            "Bludgeoning",
            5,
            None,
            None
        ),
        "Glaive" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Reach", "Two-Handed"],
            "Graze",
            "1d10",
            "Slashing",
            10,
            None,
            None
        ),
        "Greataxe" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Two-Handed"],
            "Cleave",
            "1d12",
            "Slashing",
            5,
            None,
            None
        ),
        "Greatsword" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Two-Handed"],
            "Graze",
            "2d6",
            "Slashing",
            5,
            None,
            None
        ),
        "Halberd" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Reach", "Two-Handed"],
            "Cleave",
            "1d10",
            "Slashing",
            10,
            None,
            None
        ),
        "Lance" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Reach", "Two-Handed"],
            "Topple",
            "1d10",
            "Piercing",
            10,
            None,
            None
        ),
        "Longsword" => weapon!(
            "Martial",
            "Melee",
            ["Versatile"],
            "Sap",
            "1d8",
            "Slashing",
            5,
            None,
            Some("1d10")
        ),
        "Maul" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Two-Handed"],
            "Topple",
            "2d6",
            "Bludgeoning",
            5,
            None,
            None
        ),
        "Morningstar" => weapon!(
            "Martial",
            "Melee",
            [],
            "Sap",
            "1d8",
            "Piercing",
            5,
            None,
            None
        ),
        "Pike" => weapon!(
            "Martial",
            "Melee",
            ["Heavy", "Reach", "Two-Handed"],
            "Push",
            "1d10",
            "Piercing",
            10,
            None,
            None
        ),
        "Rapier" => weapon!(
            "Martial",
            "Melee",
            ["Finesse"],
            "Vex",
            "1d8",
            "Piercing",
            5,
            None,
            None
        ),
        "Scimitar" => weapon!(
            "Martial",
            "Melee",
            ["Finesse", "Light"],
            "Nick",
            "1d6",
            "Slashing",
            5,
            None,
            None
        ),
        "Shortsword" => weapon!(
            "Martial",
            "Melee",
            ["Finesse", "Light"],
            "Vex",
            "1d6",
            "Piercing",
            5,
            None,
            None
        ),
        "Trident" => weapon!(
            "Martial",
            "Melee",
            ["Thrown", "Versatile"],
            "Topple",
            "1d8",
            "Piercing",
            20,
            Some(60),
            Some("1d10")
        ),
        "Warhammer" => weapon!(
            "Martial",
            "Melee",
            ["Versatile"],
            "Push",
            "1d8",
            "Bludgeoning",
            5,
            None,
            Some("1d10")
        ),
        "War Pick" => weapon!(
            "Martial",
            "Melee",
            ["Versatile"],
            "Sap",
            "1d8",
            "Piercing",
            5,
            None,
            Some("1d10")
        ),
        "Whip" => weapon!(
            "Martial",
            "Melee",
            ["Finesse", "Reach"],
            "Slow",
            "1d4",
            "Slashing",
            10,
            None,
            None
        ),
        "Blowgun" => weapon!(
            "Martial",
            "Ranged",
            ["Ammunition", "Loading"],
            "Vex",
            "1",
            "Piercing",
            25,
            Some(100),
            None
        ),
        "Hand Crossbow" => weapon!(
            "Martial",
            "Ranged",
            ["Ammunition", "Light", "Loading"],
            "Vex",
            "1d6",
            "Piercing",
            30,
            Some(120),
            None
        ),
        "Heavy Crossbow" => weapon!(
            "Martial",
            "Ranged",
            ["Ammunition", "Heavy", "Loading", "Two-Handed"],
            "Push",
            "1d10",
            "Piercing",
            100,
            Some(400),
            None
        ),
        "Longbow" => weapon!(
            "Martial",
            "Ranged",
            ["Ammunition", "Heavy", "Two-Handed"],
            "Slow",
            "1d8",
            "Piercing",
            150,
            Some(600),
            None
        ),
        "Musket" => weapon!(
            "Martial",
            "Ranged",
            ["Ammunition", "Loading", "Two-Handed"],
            "Slow",
            "1d12",
            "Piercing",
            40,
            Some(120),
            None
        ),
        "Pistol" => weapon!(
            "Martial",
            "Ranged",
            ["Ammunition", "Loading"],
            "Vex",
            "1d10",
            "Piercing",
            30,
            Some(90),
            None
        ),
        _ => return None,
    };
    Some(rule)
}

const EXPLORER_PACK: &[EquipmentGrant] = &[
    EquipmentGrant::one("Backpack"),
    EquipmentGrant::one("Bedroll"),
    EquipmentGrant::many("Oil", 2),
    EquipmentGrant::many("Rations", 10),
    EquipmentGrant::one("Rope"),
    EquipmentGrant::one("Tinderbox"),
    EquipmentGrant::many("Torch", 10),
    EquipmentGrant::one("Waterskin"),
];
const DUNGEONEER_PACK: &[EquipmentGrant] = &[
    EquipmentGrant::one("Backpack"),
    EquipmentGrant::one("Caltrops"),
    EquipmentGrant::one("Crowbar"),
    EquipmentGrant::many("Oil", 2),
    EquipmentGrant::many("Rations", 10),
    EquipmentGrant::one("Rope"),
    EquipmentGrant::one("Tinderbox"),
    EquipmentGrant::many("Torch", 10),
    EquipmentGrant::one("Waterskin"),
];
const ENTERTAINER_PACK: &[EquipmentGrant] = &[
    EquipmentGrant::one("Backpack"),
    EquipmentGrant::one("Bedroll"),
    EquipmentGrant::one("Bell"),
    EquipmentGrant::one("Bullseye Lantern"),
    EquipmentGrant::many("Costume", 3),
    EquipmentGrant::one("Mirror"),
    EquipmentGrant::many("Oil", 8),
    EquipmentGrant::many("Rations", 9),
    EquipmentGrant::one("Tinderbox"),
    EquipmentGrant::one("Waterskin"),
];
const PRIEST_PACK: &[EquipmentGrant] = &[
    EquipmentGrant::one("Backpack"),
    EquipmentGrant::one("Blanket"),
    EquipmentGrant::one("Holy Water"),
    EquipmentGrant::one("Lamp"),
    EquipmentGrant::many("Rations", 7),
    EquipmentGrant::one("Robe"),
    EquipmentGrant::one("Tinderbox"),
];
const SCHOLAR_PACK: &[EquipmentGrant] = &[
    EquipmentGrant::one("Backpack"),
    EquipmentGrant::one("Book"),
    EquipmentGrant::one("Ink"),
    EquipmentGrant::one("Ink Pen"),
    EquipmentGrant::one("Lamp"),
    EquipmentGrant::many("Oil", 10),
    EquipmentGrant::many("Parchment", 10),
    EquipmentGrant::one("Tinderbox"),
];

#[must_use]
pub fn pack_contents(name: &str) -> Option<&'static [EquipmentGrant]> {
    match name {
        "Explorer's Pack" => Some(EXPLORER_PACK),
        "Dungeoneer's Pack" => Some(DUNGEONEER_PACK),
        "Entertainer's Pack" => Some(ENTERTAINER_PACK),
        "Priest's Pack" => Some(PRIEST_PACK),
        "Scholar's Pack" => Some(SCHOLAR_PACK),
        _ => None,
    }
}

const BARBARIAN_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Greataxe"),
    EquipmentGrant::many("Handaxe", 4),
    EquipmentGrant::one("Explorer's Pack"),
];
const BARD_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Leather Armor"),
    EquipmentGrant::many("Dagger", 2),
    EquipmentGrant::one("Chosen Musical Instrument"),
    EquipmentGrant::one("Entertainer's Pack"),
];
const CLERIC_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Chain Shirt"),
    EquipmentGrant::one("Shield"),
    EquipmentGrant::one("Mace"),
    EquipmentGrant::one("Holy Symbol"),
    EquipmentGrant::one("Priest's Pack"),
];
const DRUID_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Leather Armor"),
    EquipmentGrant::one("Shield"),
    EquipmentGrant::one("Sickle"),
    EquipmentGrant::weapon("Druidic Focus (Quarterstaff)", "Quarterstaff"),
    EquipmentGrant::one("Explorer's Pack"),
    EquipmentGrant::one("Herbalism Kit"),
];
const FIGHTER_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Chain Mail"),
    EquipmentGrant::one("Greatsword"),
    EquipmentGrant::one("Flail"),
    EquipmentGrant::many("Javelin", 8),
    EquipmentGrant::one("Dungeoneer's Pack"),
];
const FIGHTER_B: &[EquipmentGrant] = &[
    EquipmentGrant::one("Studded Leather Armor"),
    EquipmentGrant::one("Scimitar"),
    EquipmentGrant::one("Shortsword"),
    EquipmentGrant::one("Longbow"),
    EquipmentGrant::many("Arrow", 20),
    EquipmentGrant::one("Quiver"),
    EquipmentGrant::one("Dungeoneer's Pack"),
];
const MONK_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Spear"),
    EquipmentGrant::many("Dagger", 5),
    EquipmentGrant::one("Chosen Monk Tool"),
    EquipmentGrant::one("Explorer's Pack"),
];
const PALADIN_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Chain Mail"),
    EquipmentGrant::one("Shield"),
    EquipmentGrant::one("Longsword"),
    EquipmentGrant::many("Javelin", 6),
    EquipmentGrant::one("Holy Symbol"),
    EquipmentGrant::one("Priest's Pack"),
];
const RANGER_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Studded Leather Armor"),
    EquipmentGrant::one("Scimitar"),
    EquipmentGrant::one("Shortsword"),
    EquipmentGrant::one("Longbow"),
    EquipmentGrant::many("Arrow", 20),
    EquipmentGrant::one("Quiver"),
    EquipmentGrant::one("Druidic Focus (Sprig of Mistletoe)"),
    EquipmentGrant::one("Explorer's Pack"),
];
const ROGUE_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Leather Armor"),
    EquipmentGrant::many("Dagger", 2),
    EquipmentGrant::one("Shortsword"),
    EquipmentGrant::one("Shortbow"),
    EquipmentGrant::many("Arrow", 20),
    EquipmentGrant::one("Quiver"),
    EquipmentGrant::one("Thieves' Tools"),
    EquipmentGrant::one("Burglar's Pack"),
];
const SORCERER_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Spear"),
    EquipmentGrant::many("Dagger", 2),
    EquipmentGrant::one("Arcane Focus (Crystal)"),
    EquipmentGrant::one("Dungeoneer's Pack"),
];
const WARLOCK_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Leather Armor"),
    EquipmentGrant::one("Sickle"),
    EquipmentGrant::many("Dagger", 2),
    EquipmentGrant::one("Arcane Focus (Orb)"),
    EquipmentGrant::one("Book (Occult Lore)"),
    EquipmentGrant::one("Scholar's Pack"),
];
const WIZARD_A: &[EquipmentGrant] = &[
    EquipmentGrant::many("Dagger", 2),
    EquipmentGrant::weapon("Arcane Focus (Quarterstaff)", "Quarterstaff"),
    EquipmentGrant::one("Robe"),
    EquipmentGrant::one("Spellbook"),
    EquipmentGrant::one("Scholar's Pack"),
];

#[must_use]
pub fn class_equipment(class: &str, option: &str) -> Option<(&'static [EquipmentGrant], u16)> {
    match (class, option) {
        ("Barbarian", "A") => Some((BARBARIAN_A, 15)),
        ("Bard", "A") => Some((BARD_A, 19)),
        ("Cleric", "A") => Some((CLERIC_A, 7)),
        ("Druid", "A") => Some((DRUID_A, 9)),
        ("Fighter", "A") => Some((FIGHTER_A, 4)),
        ("Fighter", "B") => Some((FIGHTER_B, 11)),
        ("Monk", "A") => Some((MONK_A, 11)),
        ("Paladin", "A") => Some((PALADIN_A, 9)),
        ("Ranger", "A") => Some((RANGER_A, 7)),
        ("Rogue", "A") => Some((ROGUE_A, 8)),
        ("Sorcerer", "A") => Some((SORCERER_A, 28)),
        ("Warlock", "A") => Some((WARLOCK_A, 15)),
        ("Wizard", "A") => Some((WIZARD_A, 5)),
        _ => None,
    }
}

#[must_use]
pub fn class_starting_gold(class: &str) -> Option<u16> {
    match class {
        "Barbarian" => Some(75),
        "Bard" => Some(90),
        "Cleric" => Some(110),
        "Druid" | "Monk" | "Sorcerer" => Some(50),
        "Fighter" => Some(155),
        "Paladin" | "Ranger" => Some(150),
        "Rogue" | "Warlock" => Some(100),
        "Wizard" => Some(55),
        _ => None,
    }
}

#[must_use]
pub fn class_features(class: &str) -> &'static [&'static str] {
    match class {
        "Barbarian" => &["Rage", "Unarmored Defense", "Weapon Mastery"],
        "Bard" => &["Bardic Inspiration", "Spellcasting"],
        "Cleric" => &["Divine Order", "Spellcasting"],
        "Druid" => &["Druidic", "Primal Order", "Spellcasting"],
        "Fighter" => &["Fighting Style", "Second Wind", "Weapon Mastery"],
        "Monk" => &["Martial Arts", "Unarmored Defense"],
        "Paladin" => &["Lay on Hands", "Spellcasting", "Weapon Mastery"],
        "Ranger" => &["Favored Enemy", "Spellcasting", "Weapon Mastery"],
        "Rogue" => &[
            "Expertise",
            "Sneak Attack",
            "Thieves' Cant",
            "Weapon Mastery",
        ],
        "Sorcerer" => &["Innate Sorcery", "Spellcasting"],
        "Warlock" => &["Eldritch Invocations", "Pact Magic"],
        "Wizard" => &["Arcane Recovery", "Ritual Adept", "Spellcasting"],
        _ => &[],
    }
}

#[must_use]
pub fn species_traits(species: &str) -> &'static [&'static str] {
    match species {
        "Dragonborn" => &["Breath Weapon"],
        "Dwarf" => &["Dwarven Resilience", "Dwarven Toughness", "Stonecunning"],
        "Elf" => &["Fey Ancestry", "Trance"],
        "Gnome" => &["Gnomish Cunning"],
        "Goliath" => &["Giant Ancestry", "Powerful Build"],
        "Halfling" => &["Brave", "Halfling Nimbleness", "Luck", "Naturally Stealthy"],
        "Human" => &["Resourceful", "Skillful", "Versatile"],
        "Orc" => &["Adrenaline Rush", "Relentless Endurance"],
        "Tiefling" => &["Otherworldly Presence"],
        _ => &[],
    }
}

const ACOLYTE_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Calligrapher's Supplies"),
    EquipmentGrant::one("Book (Prayers)"),
    EquipmentGrant::one("Holy Symbol"),
    EquipmentGrant::many("Parchment", 10),
    EquipmentGrant::one("Robe"),
];
const CRIMINAL_A: &[EquipmentGrant] = &[
    EquipmentGrant::many("Dagger", 2),
    EquipmentGrant::one("Thieves' Tools"),
    EquipmentGrant::one("Crowbar"),
    EquipmentGrant::many("Pouch", 2),
    EquipmentGrant::one("Traveler's Clothes"),
];
const SAGE_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Quarterstaff"),
    EquipmentGrant::one("Calligrapher's Supplies"),
    EquipmentGrant::one("Book (History)"),
    EquipmentGrant::many("Parchment", 8),
    EquipmentGrant::one("Robe"),
];
const SOLDIER_A: &[EquipmentGrant] = &[
    EquipmentGrant::one("Spear"),
    EquipmentGrant::one("Shortbow"),
    EquipmentGrant::many("Arrow", 20),
    EquipmentGrant::one("Gaming Set"),
    EquipmentGrant::one("Healer's Kit"),
    EquipmentGrant::one("Quiver"),
    EquipmentGrant::one("Traveler's Clothes"),
];

#[must_use]
pub fn background_equipment(background: &str) -> Option<(&'static [EquipmentGrant], u16)> {
    match background {
        "Acolyte" => Some((ACOLYTE_A, 8)),
        "Criminal" => Some((CRIMINAL_A, 16)),
        "Sage" => Some((SAGE_A, 8)),
        "Soldier" => Some((SOLDIER_A, 14)),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::{background_rule, class_rule, skill_ability, species_rule};

    #[test]
    fn inventories_are_complete() {
        assert_eq!(
            12,
            [
                "Barbarian",
                "Bard",
                "Cleric",
                "Druid",
                "Fighter",
                "Monk",
                "Paladin",
                "Ranger",
                "Rogue",
                "Sorcerer",
                "Warlock",
                "Wizard"
            ]
            .into_iter()
            .filter_map(class_rule)
            .count()
        );
        assert_eq!(
            4,
            ["Acolyte", "Criminal", "Sage", "Soldier"]
                .into_iter()
                .filter_map(background_rule)
                .count()
        );
        assert_eq!(
            9,
            [
                "Dragonborn",
                "Dwarf",
                "Elf",
                "Gnome",
                "Goliath",
                "Halfling",
                "Human",
                "Orc",
                "Tiefling"
            ]
            .into_iter()
            .filter_map(species_rule)
            .count()
        );
        assert_eq!(Some("wisdom"), skill_ability("Perception"));
    }
}
