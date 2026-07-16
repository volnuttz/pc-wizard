//! Canonical character models, validation, and derived values.

use std::collections::BTreeSet;

use pc_wizard_srd_data as srd;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AbilityScores {
    pub strength: u8,
    pub dexterity: u8,
    pub constitution: u8,
    pub intelligence: u8,
    pub wisdom: u8,
    pub charisma: u8,
}

impl AbilityScores {
    #[must_use]
    pub fn modifier(&self, ability: &str) -> i16 {
        let score = match ability {
            "strength" => self.strength,
            "dexterity" => self.dexterity,
            "constitution" => self.constitution,
            "intelligence" => self.intelligence,
            "wisdom" => self.wisdom,
            "charisma" => self.charisma,
            _ => return 0,
        };
        (i16::from(score) - 10).div_euclid(2)
    }

    fn validate(&self) -> Result<(), String> {
        if [
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ]
        .into_iter()
        .any(|score| !(3..=20).contains(&score))
        {
            return Err("ability scores must be between 3 and 20".to_owned());
        }
        Ok(())
    }

    #[must_use]
    pub const fn ordered_values(&self) -> [u8; 6] {
        [
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ]
    }

    #[must_use]
    pub fn score(&self, ability: &str) -> u8 {
        match ability {
            "strength" => self.strength,
            "dexterity" => self.dexterity,
            "constitution" => self.constitution,
            "intelligence" => self.intelligence,
            "wisdom" => self.wisdom,
            "charisma" => self.charisma,
            _ => 0,
        }
    }
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum AbilityGenerationMethod {
    SuggestedArray,
    StandardArray,
    Random,
    PointBuy,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AbilityScoreGeneration {
    pub method: AbilityGenerationMethod,
    pub scores: AbilityScores,
    #[serde(default)]
    pub character_class: Option<String>,
}

impl AbilityScoreGeneration {
    /// Validate an SRD ability-score generation result.
    ///
    /// # Errors
    ///
    /// Returns an error when the scores do not satisfy the selected method.
    pub fn validate(&self) -> Result<(), String> {
        self.scores.validate()?;
        let values = self.scores.ordered_values();
        match self.method {
            AbilityGenerationMethod::SuggestedArray => {
                let expected = self
                    .character_class
                    .as_deref()
                    .and_then(srd::suggested_array)
                    .ok_or_else(|| "suggested array requires a known SRD class".to_owned())?;
                if values != expected {
                    return Err("scores do not match the class suggested array".to_owned());
                }
            }
            AbilityGenerationMethod::StandardArray => {
                let mut actual = values;
                let mut expected = srd::STANDARD_ARRAY;
                actual.sort_unstable();
                expected.sort_unstable();
                if actual != expected {
                    return Err(
                        "scores must assign every standard-array value exactly once".to_owned()
                    );
                }
            }
            AbilityGenerationMethod::Random => {
                if values.into_iter().any(|score| !(3..=18).contains(&score)) {
                    return Err("randomly generated scores must be between 3 and 18".to_owned());
                }
            }
            AbilityGenerationMethod::PointBuy => {
                let cost: Option<u8> = values.into_iter().map(srd::point_buy_cost).sum();
                if cost != Some(srd::POINT_BUY_BUDGET) {
                    return Err("point-buy scores must cost exactly 27 points".to_owned());
                }
            }
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct BackgroundAbilityAdjustment {
    pub background: String,
    pub base_scores: AbilityScores,
    pub increases: std::collections::BTreeMap<String, u8>,
}

impl BackgroundAbilityAdjustment {
    /// Validate and apply an SRD background ability adjustment.
    ///
    /// # Errors
    ///
    /// Returns an error for an unknown background or invalid increases.
    pub fn adjusted_scores(&self) -> Result<AbilityScores, String> {
        let rule = srd::background_rule(&self.background)
            .ok_or_else(|| format!("unknown SRD background: {}", self.background))?;
        if self
            .increases
            .keys()
            .any(|ability| !rule.abilities.contains(&ability.as_str()))
        {
            return Err(
                "background increases contain an ability not granted by the background".to_owned(),
            );
        }
        let mut amounts: Vec<u8> = self.increases.values().copied().collect();
        amounts.sort_unstable();
        if amounts != [1, 2] && amounts != [1, 1, 1] {
            return Err("background increases must be +2/+1 or +1/+1/+1".to_owned());
        }
        let adjusted = AbilityScores {
            strength: increased(&self.base_scores, &self.increases, "strength")?,
            dexterity: increased(&self.base_scores, &self.increases, "dexterity")?,
            constitution: increased(&self.base_scores, &self.increases, "constitution")?,
            intelligence: increased(&self.base_scores, &self.increases, "intelligence")?,
            wisdom: increased(&self.base_scores, &self.increases, "wisdom")?,
            charisma: increased(&self.base_scores, &self.increases, "charisma")?,
        };
        adjusted.validate()?;
        Ok(adjusted)
    }
}

fn increased(
    scores: &AbilityScores,
    increases: &std::collections::BTreeMap<String, u8>,
    ability: &str,
) -> Result<u8, String> {
    scores
        .score(ability)
        .checked_add(increases.get(ability).copied().unwrap_or(0))
        .filter(|score| *score <= 20)
        .ok_or_else(|| format!("background increase would raise {ability} above 20"))
}

#[derive(Debug, Clone, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(default, deny_unknown_fields)]
pub struct ClassChoices {
    pub weapon_masteries: BTreeSet<String>,
    pub tools: BTreeSet<String>,
    pub expertise: BTreeSet<String>,
    pub cantrips: BTreeSet<String>,
    pub prepared_spells: BTreeSet<String>,
    pub spellbook_spells: BTreeSet<String>,
    pub divine_order: Option<String>,
    pub primal_order: Option<String>,
    pub fighting_style: Option<String>,
    pub eldritch_invocation: Option<String>,
    pub additional_language: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct MagicInitiateChoice {
    pub spell_list: String,
    pub spellcasting_ability: String,
    pub cantrips: [String; 2],
    pub level_one_spell: String,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct EquipmentItem {
    pub name: String,
    pub quantity: u16,
    pub category: String,
    pub weapon: Option<String>,
}

#[derive(Debug, Clone, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(default, deny_unknown_fields)]
pub struct CoinPurse {
    pub copper: u16,
    pub silver: u16,
    pub electrum: u16,
    pub gold: u16,
    pub platinum: u16,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct WeaponAttack {
    pub name: String,
    pub attack_bonus: i16,
    pub damage: String,
    pub damage_type: String,
    pub range: String,
    pub properties: Vec<String>,
    pub notes: Vec<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SpellSlotPool {
    pub level: u8,
    pub total: u8,
    pub recovery: String,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SpellcastingProfile {
    pub source: String,
    pub ability: String,
    pub modifier: i16,
    pub save_dc: i16,
    pub attack_bonus: i16,
    pub granted_spell_slots: Vec<SpellSlotPool>,
    pub free_casts: Vec<String>,
}

impl SpellcastingProfile {
    #[must_use]
    pub fn summary(&self) -> String {
        let mut ability = self.ability.clone();
        if let Some(first) = ability.get_mut(0..1) {
            first.make_ascii_uppercase();
        }
        let mut value = format!(
            "{}: {ability} (mod {:+}, save DC {}, attack {:+})",
            self.source, self.modifier, self.save_dc, self.attack_bonus
        );
        if self.granted_spell_slots.is_empty() {
            value.push_str("; grants no spell slots");
        }
        if !self.free_casts.is_empty() {
            value.push_str("; ");
            value.push_str(&self.free_casts.join("; "));
        }
        value
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct SpellTableEntry {
    pub level: u8,
    pub name: String,
    pub casting_time: String,
    pub range: String,
    pub concentration: bool,
    pub ritual: bool,
    pub required_material: bool,
    pub notes: String,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct ClassResource {
    pub name: String,
    pub maximum: i16,
    pub unit: String,
    pub recovery: String,
    pub detail: Option<String>,
}

impl ClassResource {
    #[must_use]
    pub fn summary(&self) -> String {
        let mut parts = vec![format!("{}: {} {}", self.name, self.maximum, self.unit)];
        parts.extend(self.detail.iter().cloned());
        parts.push(self.recovery.clone());
        parts.join("; ")
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Character {
    pub name: String,
    pub character_class: String,
    pub background: String,
    pub species: String,
    pub size: String,
    #[serde(default)]
    pub dragonborn_ancestry: Option<String>,
    #[serde(default)]
    pub elf_lineage: Option<String>,
    #[serde(default)]
    pub elf_spellcasting_ability: Option<String>,
    #[serde(default)]
    pub elf_keen_senses_skill: Option<String>,
    #[serde(default)]
    pub gnome_lineage: Option<String>,
    #[serde(default)]
    pub gnome_spellcasting_ability: Option<String>,
    #[serde(default)]
    pub goliath_ancestry: Option<String>,
    #[serde(default)]
    pub human_skill: Option<String>,
    #[serde(default)]
    pub human_origin_feat: Option<String>,
    #[serde(default)]
    pub tiefling_legacy: Option<String>,
    #[serde(default)]
    pub tiefling_spellcasting_ability: Option<String>,
    pub alignment: String,
    pub abilities: AbilityScores,
    pub class_skills: BTreeSet<String>,
    #[serde(default)]
    pub class_choices: ClassChoices,
    #[serde(default = "default_equipment_option")]
    pub class_equipment_option: String,
    #[serde(default = "default_equipment_option")]
    pub background_equipment_option: String,
    #[serde(default)]
    pub bard_starting_instrument: Option<String>,
    #[serde(default)]
    pub tool_proficiencies: BTreeSet<String>,
    #[serde(default)]
    pub magic_initiate_choices: Vec<MagicInitiateChoice>,
    #[serde(default)]
    pub skilled_proficiencies: BTreeSet<String>,
    pub selected_languages: [String; 2],
    #[serde(default)]
    pub backstory: Option<String>,
    #[serde(default)]
    pub appearance: Option<String>,
    #[serde(default)]
    pub personality: Option<String>,
    #[serde(default = "default_level")]
    pub level: u8,
    #[serde(default)]
    pub xp: u32,
}

fn default_equipment_option() -> String {
    "A".to_owned()
}
const fn default_level() -> u8 {
    1
}

impl Character {
    /// Parse and structurally validate the complete canonical v1 character record.
    ///
    /// # Errors
    ///
    /// Returns an error for malformed JSON, unknown fields, missing required data,
    /// or representative scalar constraints outside their allowed bounds.
    pub fn from_json(source: &str) -> Result<Self, String> {
        let mut character: Self =
            serde_json::from_str(source).map_err(|error| error.to_string())?;
        for detail in [
            &mut character.backstory,
            &mut character.appearance,
            &mut character.personality,
        ] {
            if detail
                .as_deref()
                .is_some_and(|value| value.trim().is_empty())
            {
                *detail = None;
            } else if let Some(value) = detail {
                *value = value.trim().to_owned();
            }
        }
        if character.name.trim().is_empty() {
            return Err("name must not be empty".to_owned());
        }
        if !(1..=20).contains(&character.level) {
            return Err("level must be between 1 and 20".to_owned());
        }
        character.abilities.validate()?;
        if character.selected_languages[0] == character.selected_languages[1] {
            return Err("choose two different standard languages".to_owned());
        }
        character.validate_closed_values()?;
        character.validate_species_choices()?;
        character.validate_origin_choices()?;
        character.validate_class_choices()?;
        character.validate_equipment_choices()?;
        Ok(character)
    }

    fn validate_closed_values(&self) -> Result<(), String> {
        if !["Small", "Medium"].contains(&self.size.as_str()) {
            return Err(format!("invalid size: {}", self.size));
        }
        if !srd::ALIGNMENTS.contains(&self.alignment.as_str()) {
            return Err(format!("invalid alignment: {}", self.alignment));
        }
        if srd::class_rule(&self.character_class).is_none() {
            return Err(format!("unknown SRD class: {}", self.character_class));
        }
        if srd::background_rule(&self.background).is_none() {
            return Err(format!("unknown SRD background: {}", self.background));
        }
        if srd::species_rule(&self.species).is_none() {
            return Err(format!("unknown SRD species: {}", self.species));
        }
        if self
            .selected_languages
            .iter()
            .any(|value| !srd::STANDARD_LANGUAGES.contains(&value.as_str()))
        {
            return Err("invalid standard language".to_owned());
        }
        if self.class_equipment_option != "Gold"
            && !self
                .class_equipment_option
                .bytes()
                .all(|value| value.is_ascii_uppercase())
        {
            return Err("invalid class starting-equipment option".to_owned());
        }
        if !["A", "Gold"].contains(&self.background_equipment_option.as_str()) {
            return Err("invalid background starting-equipment option".to_owned());
        }
        Ok(())
    }

    #[allow(clippy::too_many_lines)]
    fn validate_species_choices(&self) -> Result<(), String> {
        let species = srd::species_rule(&self.species).expect("validated species");
        if !species.sizes.contains(&self.size.as_str()) {
            return Err(format!("invalid size for {}: {}", self.species, self.size));
        }
        validate_required_only(
            self.species == "Dragonborn",
            self.dragonborn_ancestry.is_some(),
            "Dragonborn characters must choose a draconic ancestry",
            "draconic ancestry is only valid for Dragonborn characters",
        )?;
        if let Some(value) = &self.dragonborn_ancestry
            && ![
                "Black", "Blue", "Brass", "Bronze", "Copper", "Gold", "Green", "Red", "Silver",
                "White",
            ]
            .contains(&value.as_str())
        {
            return Err("invalid draconic ancestry".to_owned());
        }
        let elf_choices = self.elf_lineage.is_some()
            && self.elf_spellcasting_ability.is_some()
            && self.elf_keen_senses_skill.is_some();
        let any_elf = self.elf_lineage.is_some()
            || self.elf_spellcasting_ability.is_some()
            || self.elf_keen_senses_skill.is_some();
        if self.species == "Elf" && !elf_choices {
            return Err(
                "Elf characters must choose a lineage, spellcasting ability, and Keen Senses skill"
                    .to_owned(),
            );
        }
        if self.species != "Elf" && any_elf {
            return Err("Elf lineage choices are only valid for Elf characters".to_owned());
        }
        if let Some(value) = &self.elf_lineage
            && !["Drow", "High Elf", "Wood Elf"].contains(&value.as_str())
        {
            return Err("invalid Elven lineage".to_owned());
        }
        if let Some(value) = &self.elf_keen_senses_skill
            && !["Insight", "Perception", "Survival"].contains(&value.as_str())
        {
            return Err("invalid Keen Senses skill".to_owned());
        }
        let all_gnome = self.gnome_lineage.is_some() && self.gnome_spellcasting_ability.is_some();
        let any_gnome = self.gnome_lineage.is_some() || self.gnome_spellcasting_ability.is_some();
        if self.species == "Gnome" && !all_gnome {
            return Err(
                "Gnome characters must choose a Gnomish Lineage and spellcasting ability"
                    .to_owned(),
            );
        }
        if self.species != "Gnome" && any_gnome {
            return Err("Gnomish Lineage choices are only valid for Gnome characters".to_owned());
        }
        if let Some(value) = &self.gnome_lineage
            && !["Forest Gnome", "Rock Gnome"].contains(&value.as_str())
        {
            return Err("invalid Gnomish Lineage".to_owned());
        }
        validate_required_only(
            self.species == "Goliath",
            self.goliath_ancestry.is_some(),
            "Goliath characters must choose a Giant Ancestry",
            "Giant Ancestry is only valid for Goliath characters",
        )?;
        if let Some(value) = &self.goliath_ancestry
            && ![
                "Cloud Giant",
                "Fire Giant",
                "Frost Giant",
                "Hill Giant",
                "Stone Giant",
                "Storm Giant",
            ]
            .contains(&value.as_str())
        {
            return Err("invalid Giant Ancestry".to_owned());
        }
        let all_human = self.human_skill.is_some() && self.human_origin_feat.is_some();
        let any_human = self.human_skill.is_some() || self.human_origin_feat.is_some();
        if self.species == "Human" && !all_human {
            return Err(
                "Human characters must choose an additional skill and Origin feat".to_owned(),
            );
        }
        if self.species != "Human" && any_human {
            return Err("Human species choices are only valid for Human characters".to_owned());
        }
        if let Some(skill) = &self.human_skill
            && srd::skill_ability(skill).is_none()
        {
            return Err(format!("unknown Human Skillful proficiency: {skill}"));
        }
        if let Some(feat) = &self.human_origin_feat
            && !srd::ORIGIN_FEATS.contains(&feat.as_str())
        {
            return Err("invalid Human Origin feat".to_owned());
        }
        let all_tiefling =
            self.tiefling_legacy.is_some() && self.tiefling_spellcasting_ability.is_some();
        let any_tiefling =
            self.tiefling_legacy.is_some() || self.tiefling_spellcasting_ability.is_some();
        if self.species == "Tiefling" && !all_tiefling {
            return Err(
                "Tiefling characters must choose a Fiendish Legacy and spellcasting ability"
                    .to_owned(),
            );
        }
        if self.species != "Tiefling" && any_tiefling {
            return Err(
                "Fiendish Legacy choices are only valid for Tiefling characters".to_owned(),
            );
        }
        if let Some(value) = &self.tiefling_legacy
            && !["Abyssal", "Chthonic", "Infernal"].contains(&value.as_str())
        {
            return Err("invalid Fiendish Legacy".to_owned());
        }
        for ability in [
            &self.elf_spellcasting_ability,
            &self.gnome_spellcasting_ability,
            &self.tiefling_spellcasting_ability,
        ] {
            if let Some(value) = ability
                && !srd::SPELLCASTING_ABILITIES.contains(&value.as_str())
            {
                return Err("invalid species spellcasting ability".to_owned());
            }
        }
        Ok(())
    }

    #[allow(clippy::too_many_lines)]
    fn validate_origin_choices(&self) -> Result<(), String> {
        let background = srd::background_rule(&self.background).expect("validated background");
        if self.human_origin_feat.as_deref() == Some(background.feat)
            && !["Magic Initiate", "Skilled"].contains(&background.feat)
        {
            return Err(format!(
                "the {} Origin feat can be taken only once",
                background.feat
            ));
        }
        if self
            .human_skill
            .as_deref()
            .is_some_and(|skill| background.skills.contains(&skill))
        {
            return Err(
                "the Human Skillful proficiency must be additional to background skills".to_owned(),
            );
        }
        let expected_magic = usize::from(background.magic_initiate_list.is_some())
            + usize::from(self.human_origin_feat.as_deref() == Some("Magic Initiate"));
        if self.magic_initiate_choices.len() != expected_magic {
            return Err(format!(
                "character requires exactly {expected_magic} Magic Initiate choice(s)"
            ));
        }
        let mut lists = BTreeSet::new();
        for choice in &self.magic_initiate_choices {
            let spell_list = srd::magic_initiate_spell_list(&choice.spell_list)
                .ok_or_else(|| "invalid Magic Initiate spell list".to_owned())?;
            if !srd::SPELLCASTING_ABILITIES.contains(&choice.spellcasting_ability.as_str()) {
                return Err("invalid Magic Initiate spellcasting ability".to_owned());
            }
            if choice.cantrips[0] == choice.cantrips[1] {
                return Err("Magic Initiate requires two different cantrips".to_owned());
            }
            if choice
                .cantrips
                .iter()
                .any(|cantrip| !spell_list.cantrips.contains(&cantrip.as_str()))
            {
                return Err(format!(
                    "Magic Initiate cantrips must come from the {} list",
                    choice.spell_list
                ));
            }
            if !spell_list
                .level_one_spells
                .contains(&choice.level_one_spell.as_str())
            {
                return Err(format!(
                    "Magic Initiate level 1 spell must come from the {} list",
                    choice.spell_list
                ));
            }
            if !lists.insert(choice.spell_list.as_str()) {
                return Err(
                    "repeatable Magic Initiate choices must use different spell lists".to_owned(),
                );
            }
        }
        if background
            .magic_initiate_list
            .is_some_and(|required| !lists.contains(required))
        {
            return Err(format!(
                "the {} background requires Magic Initiate ({})",
                self.background,
                background.magic_initiate_list.expect("present")
            ));
        }
        let has_skilled = self.human_origin_feat.as_deref() == Some("Skilled");
        if has_skilled != (self.skilled_proficiencies.len() == 3) {
            return Err(if has_skilled {
                "Skilled requires exactly three skill or tool proficiencies"
            } else {
                "Skilled proficiencies require the Skilled Origin feat"
            }
            .to_owned());
        }
        if self
            .skilled_proficiencies
            .iter()
            .any(|value| srd::skill_ability(value).is_none() && !srd::is_tool(value))
        {
            return Err("unknown Skilled proficiencies".to_owned());
        }
        let existing: BTreeSet<&str> = background
            .skills
            .iter()
            .copied()
            .chain(self.human_skill.as_deref())
            .chain(self.elf_keen_senses_skill.as_deref())
            .collect();
        if self
            .skilled_proficiencies
            .iter()
            .any(|value| existing.contains(value.as_str()))
        {
            return Err(
                "Skilled must grant proficiencies the character does not already have".to_owned(),
            );
        }
        if self
            .skilled_proficiencies
            .iter()
            .filter(|value| srd::is_tool(value))
            .any(|tool| !self.tool_proficiencies.contains(tool))
        {
            return Err("Skilled tool choices must be included in tool proficiencies".to_owned());
        }
        Ok(())
    }

    #[allow(clippy::too_many_lines)]
    fn validate_class_choices(&self) -> Result<(), String> {
        let rule = srd::class_rule(&self.character_class).expect("validated class");
        if self.class_skills.len() != rule.skill_count {
            return Err(format!(
                "{} requires exactly {} class skills",
                self.character_class, rule.skill_count
            ));
        }
        if self
            .class_skills
            .iter()
            .any(|skill| !rule.skills.contains(&skill.as_str()))
        {
            return Err(format!(
                "invalid {} class skill choice",
                self.character_class
            ));
        }
        let mut granted: BTreeSet<&str> = srd::background_rule(&self.background)
            .expect("validated background")
            .skills
            .iter()
            .copied()
            .collect();
        granted.extend(
            self.skilled_proficiencies
                .iter()
                .filter(|value| srd::skill_ability(value).is_some())
                .map(String::as_str),
        );
        granted.extend(self.human_skill.as_deref());
        granted.extend(self.elf_keen_senses_skill.as_deref());
        if self
            .class_skills
            .iter()
            .any(|skill| granted.contains(skill.as_str()))
        {
            return Err("class skills must not duplicate another granted proficiency".to_owned());
        }
        let mastery_count = srd::weapon_mastery_count(&self.character_class);
        if self.class_choices.weapon_masteries.len() != mastery_count {
            return Err(format!(
                "{} requires exactly {mastery_count} weapon masteries",
                self.character_class
            ));
        }
        if self.class_choices.weapon_masteries.iter().any(|weapon| {
            srd::weapon_rule(weapon).is_none_or(|rule| {
                (self.character_class == "Barbarian" && rule.kind != "Melee")
                    || (self.character_class == "Rogue"
                        && rule.category != "Simple"
                        && !rule
                            .properties
                            .iter()
                            .any(|property| ["Finesse", "Light"].contains(property)))
            })
        }) {
            return Err(format!(
                "invalid {} weapon mastery choice",
                self.character_class
            ));
        }
        let expected_tools = if self.character_class == "Bard" {
            3
        } else {
            usize::from(self.character_class == "Monk")
        };
        if self.class_choices.tools.len() != expected_tools {
            return Err(format!(
                "{} requires exactly {expected_tools} class tool choices",
                self.character_class
            ));
        }
        if self.character_class == "Bard"
            && self
                .class_choices
                .tools
                .iter()
                .any(|tool| !srd::MUSICAL_INSTRUMENTS.contains(&tool.as_str()))
        {
            return Err("invalid Bard class tool choice".to_owned());
        }
        if self.character_class == "Monk"
            && self.class_choices.tools.iter().any(|tool| {
                !srd::MUSICAL_INSTRUMENTS.contains(&tool.as_str())
                    && !srd::ARTISAN_TOOLS.contains(&tool.as_str())
            })
        {
            return Err("invalid Monk class tool choice".to_owned());
        }
        let expected_expertise = if self.character_class == "Rogue" {
            2
        } else {
            0
        };
        if self.class_choices.expertise.len() != expected_expertise {
            return Err(format!(
                "{} requires exactly {expected_expertise} Expertise choices",
                self.character_class
            ));
        }
        if self
            .class_choices
            .expertise
            .iter()
            .any(|skill| !self.skills().contains(skill))
        {
            return Err("Expertise choices must be existing skill proficiencies".to_owned());
        }
        validate_required_only(
            self.character_class == "Cleric",
            self.class_choices.divine_order.is_some(),
            "Divine Order is required only for Clerics",
            "Divine Order is required only for Clerics",
        )?;
        validate_required_only(
            self.character_class == "Druid",
            self.class_choices.primal_order.is_some(),
            "Primal Order is required only for Druids",
            "Primal Order is required only for Druids",
        )?;
        validate_required_only(
            self.character_class == "Fighter",
            self.class_choices.fighting_style.is_some(),
            "Fighting Style is required only for Fighters",
            "Fighting Style is required only for Fighters",
        )?;
        validate_required_only(
            self.character_class == "Warlock",
            self.class_choices.eldritch_invocation.is_some(),
            "an Eldritch Invocation is required only for Warlocks",
            "an Eldritch Invocation is required only for Warlocks",
        )?;
        validate_required_only(
            self.character_class == "Rogue",
            self.class_choices.additional_language.is_some(),
            "an additional language is required only for Rogues",
            "an additional language is required only for Rogues",
        )?;
        if let Some(value) = &self.class_choices.divine_order
            && !["Protector", "Thaumaturge"].contains(&value.as_str())
        {
            return Err("invalid Divine Order".to_owned());
        }
        if let Some(value) = &self.class_choices.primal_order
            && !["Magician", "Warden"].contains(&value.as_str())
        {
            return Err("invalid Primal Order".to_owned());
        }
        if let Some(value) = &self.class_choices.fighting_style
            && !srd::FIGHTING_STYLES.contains(&value.as_str())
        {
            return Err("invalid Fighter Fighting Style".to_owned());
        }
        if let Some(value) = &self.class_choices.eldritch_invocation
            && !srd::WARLOCK_INVOCATIONS.contains(&value.as_str())
        {
            return Err("invalid level-1 Warlock invocation".to_owned());
        }
        let mut expected_cantrips = match self.character_class.as_str() {
            "Bard" | "Druid" | "Warlock" => 2,
            "Cleric" | "Wizard" => 3,
            "Sorcerer" => 4,
            _ => 0,
        };
        if self.class_choices.divine_order.as_deref() == Some("Thaumaturge")
            || self.class_choices.primal_order.as_deref() == Some("Magician")
        {
            expected_cantrips += 1;
        }
        if self.class_choices.cantrips.len() != expected_cantrips {
            return Err(format!(
                "invalid number or selection of {} cantrips",
                self.character_class
            ));
        }
        let spell_list = srd::class_spell_list(&self.character_class);
        if self
            .class_choices
            .cantrips
            .iter()
            .any(|spell| spell_list.is_none_or(|list| !list.cantrips.contains(&spell.as_str())))
        {
            return Err(format!(
                "invalid number or selection of {} cantrips",
                self.character_class
            ));
        }
        let expected_prepared = match self.character_class.as_str() {
            "Bard" | "Cleric" | "Druid" | "Wizard" => 4,
            "Paladin" | "Ranger" | "Sorcerer" | "Warlock" => 2,
            _ => 0,
        };
        if self.class_choices.prepared_spells.len() != expected_prepared {
            return Err(format!(
                "invalid number or selection of {} prepared spells",
                self.character_class
            ));
        }
        if self.class_choices.prepared_spells.iter().any(|spell| {
            spell_list.is_none_or(|list| {
                !list.level_one_spells.contains(&spell.as_str())
                    || srd::class_always_prepared(&self.character_class).contains(&spell.as_str())
            })
        }) {
            return Err(format!(
                "invalid number or selection of {} prepared spells",
                self.character_class
            ));
        }
        let expected_spellbook = usize::from(self.character_class == "Wizard") * 6;
        if self.class_choices.spellbook_spells.len() != expected_spellbook {
            return Err(format!(
                "{} requires exactly {expected_spellbook} spellbook spells",
                self.character_class
            ));
        }
        if self.class_choices.spellbook_spells.iter().any(|spell| {
            spell_list.is_none_or(|list| !list.level_one_spells.contains(&spell.as_str()))
        }) {
            return Err("Wizard spellbook spells must be level 1 Wizard spells".to_owned());
        }
        if self.character_class == "Wizard"
            && !self
                .class_choices
                .prepared_spells
                .is_subset(&self.class_choices.spellbook_spells)
        {
            return Err("Wizard prepared spells must be in the character's spellbook".to_owned());
        }
        if let Some(language) = &self.class_choices.additional_language {
            if !srd::STANDARD_LANGUAGES.contains(&language.as_str()) {
                return Err("invalid Rogue additional language".to_owned());
            }
            if self.selected_languages.contains(language) {
                return Err("the Rogue additional language must be a new language".to_owned());
            }
        }
        Ok(())
    }

    fn validate_equipment_choices(&self) -> Result<(), String> {
        if self.class_equipment_option != "Gold"
            && srd::class_equipment(&self.character_class, &self.class_equipment_option).is_none()
        {
            return Err(format!(
                "invalid {} starting-equipment option: {}",
                self.character_class, self.class_equipment_option
            ));
        }
        if self.character_class == "Bard" && self.class_equipment_option != "Gold" {
            if self
                .bard_starting_instrument
                .as_ref()
                .is_none_or(|value| !self.class_choices.tools.contains(value))
            {
                return Err(
                    "the Bard starting instrument must be one of the chosen proficiencies"
                        .to_owned(),
                );
            }
        } else if self.bard_starting_instrument.is_some() {
            return Err(
                "a Bard starting instrument requires the Bard equipment package".to_owned(),
            );
        }
        Ok(())
    }

    #[must_use]
    pub fn skills(&self) -> BTreeSet<String> {
        let mut values: BTreeSet<String> = srd::background_rule(&self.background)
            .map_or(&[][..], |rule| rule.skills)
            .iter()
            .map(|value| (*value).to_owned())
            .collect();
        values.extend(self.class_skills.iter().cloned());
        values.extend(
            self.skilled_proficiencies
                .iter()
                .filter(|value| srd::skill_ability(value).is_some())
                .cloned(),
        );
        values.extend(self.human_skill.iter().cloned());
        values.extend(self.elf_keen_senses_skill.iter().cloned());
        values
    }

    #[must_use]
    pub fn skill_modifier(&self, skill: &str) -> i16 {
        let mut value = self
            .abilities
            .modifier(srd::skill_ability(skill).unwrap_or(""));
        if self.class_choices.expertise.contains(skill) {
            value += i16::from(self.proficiency_bonus()) * 2;
        } else if self.skills().contains(skill) {
            value += i16::from(self.proficiency_bonus());
        }
        if self.class_choices.divine_order.as_deref() == Some("Thaumaturge")
            && ["Arcana", "Religion"].contains(&skill)
        {
            value += self.abilities.modifier("wisdom").max(1);
        }
        if self.class_choices.primal_order.as_deref() == Some("Magician")
            && ["Arcana", "Nature"].contains(&skill)
        {
            value += self.abilities.modifier("wisdom").max(1);
        }
        value
    }

    #[must_use]
    pub fn hit_points(&self) -> i16 {
        i16::from(srd::class_rule(&self.character_class).map_or(0, |rule| rule.hit_die))
            + self.abilities.modifier("constitution")
            + i16::from(self.species == "Dwarf")
    }

    #[must_use]
    pub fn initiative_modifier(&self) -> i16 {
        self.abilities.modifier("dexterity")
            + if srd::background_rule(&self.background).is_some_and(|rule| rule.feat == "Alert")
                || self.human_origin_feat.as_deref() == Some("Alert")
            {
                i16::from(self.proficiency_bonus())
            } else {
                0
            }
    }

    #[must_use]
    pub fn speed(&self) -> u8 {
        let mut speed = if self.elf_lineage.as_deref() == Some("Wood Elf") {
            35
        } else {
            srd::species_rule(&self.species).map_or(0, |rule| rule.speed)
        };
        if self
            .equipped_armor()
            .as_deref()
            .and_then(srd::armor_rule)
            .and_then(|armor| armor.strength_requirement)
            .is_some_and(|required| self.abilities.strength < required)
        {
            speed = speed.saturating_sub(10);
        }
        speed
    }

    #[must_use]
    pub fn armor_class(&self) -> i16 {
        let dexterity = self.abilities.modifier("dexterity");
        let armor = self.equipped_armor();
        let mut value = if let Some(rule) = armor.as_deref().and_then(srd::armor_rule) {
            rule.base_ac
                + match rule.dexterity_cap {
                    Some(cap) => dexterity.min(cap),
                    None => dexterity,
                }
        } else if self.character_class == "Barbarian" {
            10 + dexterity + self.abilities.modifier("constitution")
        } else if self.character_class == "Monk" {
            10 + dexterity + self.abilities.modifier("wisdom")
        } else {
            10 + dexterity
        };
        if armor.is_some() && self.class_choices.fighting_style.as_deref() == Some("Defense") {
            value += 1;
        }
        if self.shield_equipped() {
            value += 2;
        }
        value
    }

    #[must_use]
    pub fn inventory(&self) -> Vec<EquipmentItem> {
        let mut grants = Vec::new();
        if self.class_equipment_option != "Gold"
            && let Some((items, _)) =
                srd::class_equipment(&self.character_class, &self.class_equipment_option)
        {
            grants.extend_from_slice(items);
        }
        if self.background_equipment_option == "A"
            && let Some((items, _)) = srd::background_equipment(&self.background)
        {
            grants.extend_from_slice(items);
        }
        let mut merged: Vec<((String, Option<String>), u16)> = Vec::new();
        for grant in grants {
            let expanded = srd::pack_contents(grant.name).unwrap_or(std::slice::from_ref(&grant));
            for item in expanded {
                let name = match item.name {
                    "Chosen Musical Instrument" => self
                        .bard_starting_instrument
                        .as_deref()
                        .unwrap_or(item.name),
                    "Chosen Monk Tool" => self
                        .class_choices
                        .tools
                        .first()
                        .map_or(item.name, String::as_str),
                    _ => item.name,
                };
                let weapon = item.weapon.or_else(|| srd::weapon_rule(name).map(|_| name));
                let key = (name.to_owned(), weapon.map(str::to_owned));
                if let Some((_, quantity)) =
                    merged.iter_mut().find(|(existing, _)| *existing == key)
                {
                    *quantity += item.quantity;
                } else {
                    merged.push((key, item.quantity));
                }
            }
        }
        merged
            .into_iter()
            .map(|((name, weapon), quantity)| {
                let category = if weapon.is_some() {
                    "Weapon"
                } else if srd::armor_rule(&name).is_some() {
                    "Armor"
                } else if name == "Shield" {
                    "Shield"
                } else if ["Arrow", "Bolt", "Firearm Bullet", "Sling Bullet", "Needle"]
                    .contains(&name.as_str())
                {
                    "Ammunition"
                } else {
                    "Gear"
                };
                EquipmentItem {
                    name,
                    quantity,
                    category: category.to_owned(),
                    weapon,
                }
            })
            .collect()
    }

    #[must_use]
    pub fn coins(&self) -> CoinPurse {
        let class_gold = if self.class_equipment_option == "Gold" {
            srd::class_starting_gold(&self.character_class).unwrap_or(0)
        } else {
            srd::class_equipment(&self.character_class, &self.class_equipment_option)
                .map_or(0, |(_, gold)| gold)
        };
        let background_gold = if self.background_equipment_option == "Gold" {
            50
        } else {
            srd::background_equipment(&self.background).map_or(0, |(_, gold)| gold)
        };
        CoinPurse {
            gold: class_gold + background_gold,
            ..CoinPurse::default()
        }
    }

    #[must_use]
    pub fn equipped_armor(&self) -> Option<String> {
        self.inventory()
            .into_iter()
            .find(|item| item.category == "Armor")
            .map(|item| item.name)
    }

    #[must_use]
    pub fn shield_equipped(&self) -> bool {
        self.inventory()
            .iter()
            .any(|item| item.category == "Shield")
    }

    fn is_weapon_proficient(&self, rule: srd::WeaponRule) -> bool {
        let training = srd::class_rule(&self.character_class).map_or("", |class| class.weapons);
        training == "Simple and Martial"
            || rule.category == "Simple"
            || (self.character_class == "Monk"
                && rule.kind == "Melee"
                && rule.properties.contains(&"Light"))
            || (self.character_class == "Rogue"
                && rule
                    .properties
                    .iter()
                    .any(|property| ["Finesse", "Light"].contains(property)))
    }

    #[must_use]
    #[allow(clippy::too_many_lines)]
    pub fn weapon_attacks(&self) -> Vec<WeaponAttack> {
        self.inventory()
            .into_iter()
            .filter_map(|item| {
                let weapon = item.weapon.as_deref()?;
                let rule = srd::weapon_rule(weapon)?;
                let abilities: &[&str] = if rule.kind == "Ranged" {
                    &["dexterity"]
                } else if rule.properties.contains(&"Finesse") || self.character_class == "Monk" {
                    &["strength", "dexterity"]
                } else {
                    &["strength"]
                };
                let modifier = abilities
                    .iter()
                    .map(|ability| self.abilities.modifier(ability))
                    .max()
                    .unwrap_or(0);
                let mut attack_bonus = modifier
                    + if self.is_weapon_proficient(rule) {
                        i16::from(self.proficiency_bonus())
                    } else {
                        0
                    };
                if self.class_choices.fighting_style.as_deref() == Some("Archery")
                    && rule.kind == "Ranged"
                {
                    attack_bonus += 2;
                }
                let suffix = if modifier == 0 {
                    String::new()
                } else {
                    format!("{modifier:+}")
                };
                let mut notes = Vec::new();
                if item.quantity > 1 {
                    notes.push(format!("Quantity {}", item.quantity));
                }
                if let Some(damage) = rule.versatile_damage {
                    notes.push(format!("Versatile {damage}{suffix}"));
                }
                if self.class_choices.weapon_masteries.contains(weapon) {
                    notes.push(format!("Mastery: {}", rule.mastery));
                }
                if rule.properties.contains(&"Heavy") {
                    let ability = if rule.kind == "Ranged" {
                        self.abilities.dexterity
                    } else {
                        self.abilities.strength
                    };
                    if ability < 13 {
                        notes.push("Heavy: attack rolls have Disadvantage".to_owned());
                    }
                }
                Some(WeaponAttack {
                    name: item.name,
                    attack_bonus,
                    damage: format!("{}{suffix}", rule.damage),
                    damage_type: rule.damage_type.to_owned(),
                    range: rule.long_range.map_or_else(
                        || format!("{} ft.", rule.normal_range),
                        |long| format!("{}/{long} ft.", rule.normal_range),
                    ),
                    properties: rule
                        .properties
                        .iter()
                        .map(|value| (*value).to_owned())
                        .collect(),
                    notes,
                })
            })
            .collect()
    }

    #[must_use]
    pub fn darkvision_range(&self) -> Option<u8> {
        match self.elf_lineage.as_deref() {
            Some("Drow") => Some(120),
            Some("High Elf" | "Wood Elf") => Some(60),
            _ => srd::species_rule(&self.species).and_then(|rule| rule.darkvision_range),
        }
    }

    #[must_use]
    pub fn damage_resistances(&self) -> Vec<String> {
        let mut values = Vec::new();
        if self.species == "Dwarf" {
            values.push("Poison".to_owned());
        }
        if let Some(value) = self
            .dragonborn_ancestry
            .as_deref()
            .and_then(srd::dragonborn_damage_type)
        {
            values.push(value.to_owned());
        }
        if let Some(value) = self
            .tiefling_legacy
            .as_deref()
            .and_then(srd::tiefling_resistance)
        {
            values.push(value.to_owned());
        }
        values.dedup();
        values
    }

    #[must_use]
    pub fn spell_slots(&self) -> Vec<SpellSlotPool> {
        srd::level_one_spell_slots(&self.character_class).map_or_else(
            Vec::new,
            |(level, total, recovery)| {
                vec![SpellSlotPool {
                    level,
                    total,
                    recovery: recovery.to_owned(),
                }]
            },
        )
    }

    fn spellcasting_profile(
        &self,
        source: String,
        ability: &str,
        slots: Vec<SpellSlotPool>,
        free_casts: Vec<String>,
    ) -> SpellcastingProfile {
        let modifier = self.abilities.modifier(ability);
        SpellcastingProfile {
            source,
            ability: ability.to_owned(),
            modifier,
            save_dc: 8 + modifier + i16::from(self.proficiency_bonus()),
            attack_bonus: modifier + i16::from(self.proficiency_bonus()),
            granted_spell_slots: slots,
            free_casts,
        }
    }

    #[must_use]
    pub fn spellcasting_profiles(&self) -> Vec<SpellcastingProfile> {
        let mut profiles = Vec::new();
        if let Some(ability) = srd::class_spellcasting_ability(&self.character_class) {
            profiles.push(self.spellcasting_profile(
                format!("{} Spellcasting", self.character_class),
                ability,
                self.spell_slots(),
                Vec::new(),
            ));
        }
        profiles.extend(self.magic_initiate_choices.iter().map(|choice| {
            self.spellcasting_profile(
                format!("Magic Initiate ({})", choice.spell_list),
                &choice.spellcasting_ability,
                Vec::new(),
                vec![format!(
                    "{}: 1/Long Rest without a spell slot",
                    choice.level_one_spell
                )],
            )
        }));
        let species_ability = self
            .elf_spellcasting_ability
            .as_deref()
            .or(self.gnome_spellcasting_ability.as_deref())
            .or(self.tiefling_spellcasting_ability.as_deref());
        if let Some(ability) = species_ability {
            let source = if let Some(lineage) = &self.elf_lineage {
                format!("Elven Lineage ({lineage})")
            } else if let Some(lineage) = &self.gnome_lineage {
                format!("Gnomish Lineage ({lineage})")
            } else if let Some(legacy) = &self.tiefling_legacy {
                format!("Fiendish Legacy ({legacy})")
            } else {
                "Species Spellcasting".to_owned()
            };
            let free_casts = if self.gnome_lineage.as_deref() == Some("Forest Gnome") {
                vec![format!(
                    "Speak with Animals: {}/Long Rest without a spell slot",
                    self.proficiency_bonus()
                )]
            } else {
                Vec::new()
            };
            profiles.push(self.spellcasting_profile(source, ability, Vec::new(), free_casts));
        }
        profiles
    }

    #[must_use]
    pub fn spellcasting_ability(&self) -> Option<String> {
        self.spellcasting_profiles()
            .first()
            .map(|profile| profile.ability.clone())
    }

    #[must_use]
    pub fn spell_save_dc(&self) -> Option<i16> {
        self.spellcasting_profiles()
            .first()
            .map(|profile| profile.save_dc)
    }

    #[must_use]
    pub fn spell_attack_bonus(&self) -> Option<i16> {
        self.spellcasting_profiles()
            .first()
            .map(|profile| profile.attack_bonus)
    }

    #[must_use]
    pub fn all_cantrips(&self) -> Vec<String> {
        let mut spells = Vec::new();
        let species: Vec<&str> = if let Some(lineage) = self.elf_lineage.as_deref() {
            vec![match lineage {
                "Drow" => "Dancing Lights",
                "High Elf" => "Prestidigitation",
                "Wood Elf" => "Druidcraft",
                _ => "",
            }]
        } else if let Some(lineage) = self.gnome_lineage.as_deref() {
            if lineage == "Forest Gnome" {
                vec!["Minor Illusion"]
            } else {
                vec!["Mending", "Prestidigitation"]
            }
        } else if let Some(legacy) = self.tiefling_legacy.as_deref() {
            vec![srd::tiefling_cantrip(legacy).unwrap_or(""), "Thaumaturgy"]
        } else {
            Vec::new()
        };
        for spell in species
            .into_iter()
            .map(str::to_owned)
            .chain(
                self.magic_initiate_choices
                    .iter()
                    .flat_map(|choice| choice.cantrips.iter().cloned()),
            )
            .chain(self.class_choices.cantrips.iter().cloned())
        {
            if !spell.is_empty() && !spells.contains(&spell) {
                spells.push(spell);
            }
        }
        spells
    }

    #[must_use]
    pub fn all_prepared_spells(&self) -> Vec<String> {
        let mut spells = Vec::new();
        if self.gnome_lineage.as_deref() == Some("Forest Gnome") {
            spells.push("Speak with Animals".to_owned());
        }
        for spell in self
            .magic_initiate_choices
            .iter()
            .map(|choice| choice.level_one_spell.clone())
            .chain(self.class_choices.prepared_spells.iter().cloned())
            .chain(
                srd::class_always_prepared(&self.character_class)
                    .iter()
                    .map(|value| (*value).to_owned()),
            )
        {
            if !spells.contains(&spell) {
                spells.push(spell);
            }
        }
        spells
    }

    #[must_use]
    pub fn spell_table_entries(&self) -> Vec<SpellTableEntry> {
        self.all_cantrips()
            .into_iter()
            .map(|spell| (0, spell))
            .chain(
                self.all_prepared_spells()
                    .into_iter()
                    .map(|spell| (1, spell)),
            )
            .filter_map(|(level, name)| {
                let rule = srd::spell_rule(&name)?;
                Some(SpellTableEntry {
                    level,
                    name,
                    casting_time: rule.casting_time.clone(),
                    range: rule.range.clone(),
                    concentration: rule.concentration,
                    ritual: rule.ritual,
                    required_material: rule.required_material.is_some(),
                    notes: rule.notes.clone(),
                })
            })
            .collect()
    }

    #[must_use]
    pub fn armor_training(&self) -> String {
        if self.class_choices.divine_order.as_deref() == Some("Protector") {
            "Light, Medium, Heavy, Shields".to_owned()
        } else if self.class_choices.primal_order.as_deref() == Some("Warden") {
            "Light, Medium, Shields".to_owned()
        } else {
            srd::class_rule(&self.character_class)
                .map_or("", |rule| rule.armor)
                .to_owned()
        }
    }

    #[must_use]
    pub fn weapon_proficiencies(&self) -> String {
        if self.class_choices.divine_order.as_deref() == Some("Protector")
            || self.class_choices.primal_order.as_deref() == Some("Warden")
        {
            "Simple and Martial".to_owned()
        } else {
            srd::class_rule(&self.character_class)
                .map_or("", |rule| rule.weapons)
                .to_owned()
        }
    }

    #[must_use]
    pub fn all_tool_proficiencies(&self) -> Vec<String> {
        let mut values = vec![
            srd::background_rule(&self.background)
                .map_or("", |rule| rule.tool)
                .to_owned(),
        ];
        for tool in self
            .class_choices
            .tools
            .iter()
            .chain(&self.tool_proficiencies)
        {
            if !values.contains(tool) {
                values.push(tool.clone());
            }
        }
        values
    }

    #[must_use]
    pub fn class_traits(&self) -> Vec<String> {
        let mut traits: Vec<String> = srd::class_features(&self.character_class)
            .iter()
            .map(|value| (*value).to_owned())
            .collect();
        if !self.class_choices.weapon_masteries.is_empty() {
            let selected = self
                .class_choices
                .weapon_masteries
                .iter()
                .map(|weapon| {
                    format!(
                        "{weapon} ({})",
                        srd::weapon_rule(weapon).map_or("", |rule| rule.mastery)
                    )
                })
                .collect::<Vec<_>>()
                .join(", ");
            traits.push(format!("Weapon Mastery: {selected}"));
        }
        if !self.class_choices.tools.is_empty() {
            traits.push(format!(
                "Class Tools: {}",
                self.class_choices
                    .tools
                    .iter()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        if !self.class_choices.expertise.is_empty() {
            traits.push(format!(
                "Expertise: {}",
                self.class_choices
                    .expertise
                    .iter()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        if let Some(value) = &self.class_choices.fighting_style {
            traits.push(format!("Fighting Style: {value}"));
        }
        if let Some(value) = &self.class_choices.eldritch_invocation {
            traits.push(format!("Eldritch Invocation: {value}"));
        }
        if let Some(value) = &self.class_choices.additional_language {
            traits.push(format!("Thieves' Cant: additional language ({value})"));
        }
        if !self.class_choices.cantrips.is_empty() {
            traits.push(format!(
                "Cantrips: {}",
                self.class_choices
                    .cantrips
                    .iter()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        if !self.class_choices.spellbook_spells.is_empty() {
            traits.push(format!(
                "Spellbook: {}",
                self.class_choices
                    .spellbook_spells
                    .iter()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        if !self.class_choices.prepared_spells.is_empty() {
            traits.push(format!(
                "Prepared Spells: {}",
                self.class_choices
                    .prepared_spells
                    .iter()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        traits
    }

    #[must_use]
    pub fn species_traits(&self) -> Vec<String> {
        let mut traits: Vec<String> = srd::species_traits(&self.species)
            .iter()
            .map(|value| (*value).to_owned())
            .collect();
        if let Some(value) = &self.dragonborn_ancestry {
            traits.push(format!(
                "Draconic Ancestry: {value} ({})",
                srd::dragonborn_damage_type(value).unwrap_or("")
            ));
        }
        if let Some(value) = &self.elf_lineage {
            traits.push(format!("Elven Lineage: {value}"));
            traits.push(format!(
                "Keen Senses: {}",
                self.elf_keen_senses_skill.as_deref().unwrap_or("")
            ));
        }
        if let Some(value) = &self.gnome_lineage {
            traits.push(format!("Gnomish Lineage: {value}"));
        }
        if let Some(value) = &self.goliath_ancestry {
            traits.push(format!("Giant Ancestry: {value}"));
        }
        if let Some(value) = &self.human_skill {
            traits.push(format!("Skillful: {value}"));
        }
        if let Some(value) = &self.human_origin_feat {
            traits.push(format!("Versatile: {value}"));
        }
        if let Some(value) = &self.tiefling_legacy {
            traits.push(format!("Fiendish Legacy: {value}"));
        }
        if let Some(value) = self.darkvision_range() {
            traits.push(format!("Darkvision: {value} ft."));
        }
        if !self.damage_resistances().is_empty() {
            traits.push(format!(
                "Damage Resistance: {}",
                self.damage_resistances().join(", ")
            ));
        }
        let species_source = ["Elven Lineage", "Gnomish Lineage", "Fiendish Legacy"];
        if let Some(profile) = self.spellcasting_profiles().into_iter().find(|profile| {
            species_source
                .iter()
                .any(|source| profile.source.starts_with(source))
        }) {
            traits.push(profile.summary());
        }
        let species_cantrips: Vec<String> = if self.elf_lineage.is_some()
            || self.gnome_lineage.is_some()
            || self.tiefling_legacy.is_some()
        {
            let class_and_feat: BTreeSet<String> = self
                .class_choices
                .cantrips
                .iter()
                .cloned()
                .chain(
                    self.magic_initiate_choices
                        .iter()
                        .flat_map(|choice| choice.cantrips.iter().cloned()),
                )
                .collect();
            self.all_cantrips()
                .into_iter()
                .filter(|spell| !class_and_feat.contains(spell))
                .collect()
        } else {
            Vec::new()
        };
        if !species_cantrips.is_empty() {
            traits.push(format!("Cantrips: {}", species_cantrips.join(", ")));
        }
        traits
    }

    #[must_use]
    pub fn origin_feat_traits(&self) -> Vec<String> {
        let mut traits = Vec::new();
        let background = srd::background_rule(&self.background);
        if background.is_some_and(|rule| rule.feat == "Alert")
            || self.human_origin_feat.as_deref() == Some("Alert")
        {
            traits.push("Alert: Initiative Proficiency; Initiative Swap".to_owned());
        }
        if background.is_some_and(|rule| rule.feat == "Savage Attacker")
            || self.human_origin_feat.as_deref() == Some("Savage Attacker")
        {
            traits.push("Savage Attacker: roll weapon damage dice twice once per turn".to_owned());
        }
        if !self.skilled_proficiencies.is_empty() {
            traits.push(format!(
                "Skilled: {}",
                self.skilled_proficiencies
                    .iter()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            ));
        }
        traits
    }

    #[must_use]
    pub fn class_resources(&self) -> Vec<ClassResource> {
        let resource = match self.character_class.as_str() {
            "Barbarian" => ClassResource {
                name: "Rage".to_owned(),
                maximum: 2,
                unit: "uses".to_owned(),
                detail: Some("+2 Rage damage".to_owned()),
                recovery: "regain 1 on Short Rest; all on Long Rest".to_owned(),
            },
            "Bard" => ClassResource {
                name: "Bardic Inspiration".to_owned(),
                maximum: self.abilities.modifier("charisma").max(1),
                unit: "d6 uses".to_owned(),
                detail: None,
                recovery: "regain all on Long Rest".to_owned(),
            },
            "Fighter" => ClassResource {
                name: "Second Wind".to_owned(),
                maximum: 2,
                unit: "uses".to_owned(),
                detail: Some(format!("heal 1d10+{} HP", self.level)),
                recovery: "regain 1 on Short Rest; all on Long Rest".to_owned(),
            },
            "Paladin" => ClassResource {
                name: "Lay on Hands".to_owned(),
                maximum: i16::from(5 * self.level),
                unit: "HP".to_owned(),
                detail: None,
                recovery: "replenishes on Long Rest".to_owned(),
            },
            "Ranger" => ClassResource {
                name: "Favored Enemy".to_owned(),
                maximum: 2,
                unit: "free Hunter's Mark casts".to_owned(),
                detail: None,
                recovery: "regain all on Long Rest".to_owned(),
            },
            "Sorcerer" => ClassResource {
                name: "Innate Sorcery".to_owned(),
                maximum: 2,
                unit: "uses".to_owned(),
                detail: None,
                recovery: "regain all on Long Rest".to_owned(),
            },
            "Warlock" => ClassResource {
                name: "Pact Magic".to_owned(),
                maximum: 1,
                unit: "level-1 slot".to_owned(),
                detail: None,
                recovery: "regain on Short or Long Rest".to_owned(),
            },
            "Wizard" => ClassResource {
                name: "Arcane Recovery".to_owned(),
                maximum: 1,
                unit: "use".to_owned(),
                detail: Some(format!(
                    "recover {} level(s) of spell slots",
                    self.level.div_ceil(2)
                )),
                recovery: "regain on Long Rest".to_owned(),
            },
            _ => return Vec::new(),
        };
        vec![resource]
    }

    #[must_use]
    pub fn passive_perception(&self) -> i16 {
        10 + self.skill_modifier("Perception")
    }

    /// Serialize the canonical record with stable pretty formatting.
    ///
    /// # Errors
    ///
    /// Returns an error if the record cannot be represented as JSON.
    pub fn to_json(&self) -> Result<String, String> {
        serde_json::to_string_pretty(self)
            .map(|mut value| {
                value.push('\n');
                value
            })
            .map_err(|error| error.to_string())
    }

    #[must_use]
    pub fn proficiency_bonus(&self) -> u8 {
        2 + (self.level - 1) / 4
    }
}

fn validate_required_only(
    required: bool,
    present: bool,
    missing: &str,
    extraneous: &str,
) -> Result<(), String> {
    match (required, present) {
        (true, false) => Err(missing.to_owned()),
        (false, true) => Err(extraneous.to_owned()),
        _ => Ok(()),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::{
        AbilityGenerationMethod, AbilityScoreGeneration, AbilityScores,
        BackgroundAbilityAdjustment, Character,
    };

    const COMPLETE_ROGUE: &str = include_str!("../../../fixtures/complete-character.json");

    #[test]
    fn canonical_fixture_round_trips_and_derives_golden_scalars() {
        let character = Character::from_json(COMPLETE_ROGUE).expect("complete fixture is valid");
        assert_eq!(character.hit_points(), 9);
        assert_eq!(character.armor_class(), 14);
        assert_eq!(character.initiative_modifier(), 5);
        assert_eq!(character.passive_perception(), 12);
        assert_eq!(character.speed(), 30);
        assert_eq!(character.coins().gold, 24);
        let attacks = character.weapon_attacks();
        assert_eq!(
            attacks
                .iter()
                .map(|attack| attack.name.as_str())
                .collect::<Vec<_>>(),
            ["Dagger", "Shortsword", "Shortbow"]
        );
        assert_eq!(attacks[0].attack_bonus, 5);
        assert_eq!(attacks[0].damage, "1d4+3");
        assert_eq!(attacks[0].notes, ["Quantity 4", "Mastery: Nick"]);
        let serialized = character.to_json().expect("character serializes");
        assert_eq!(Character::from_json(&serialized), Ok(character));
    }

    #[test]
    fn rejects_unknown_top_level_fields() {
        let error = Character::from_json(
            r#"{"name":"Nix","character_class":"Rogue","background":"Criminal","species":"Tiefling","size":"Medium","alignment":"Neutral","abilities":{"strength":12,"dexterity":17,"constitution":13,"intelligence":15,"wisdom":10,"charisma":8},"class_skills":[],"selected_languages":["Elvish","Halfling"],"migration_probe":true}"#,
        )
        .expect_err("unknown fields are rejected");

        assert!(error.contains("unknown field `migration_probe`"));
    }

    #[test]
    fn rejects_a_nonrepeatable_human_origin_feat_already_granted_by_background() {
        let mut value: serde_json::Value =
            serde_json::from_str(COMPLETE_ROGUE).expect("fixture JSON");
        let object = value.as_object_mut().expect("character object");
        object.insert("species".to_owned(), serde_json::json!("Human"));
        object.insert("human_skill".to_owned(), serde_json::json!("Arcana"));
        object.insert("human_origin_feat".to_owned(), serde_json::json!("Alert"));
        object.insert("tiefling_legacy".to_owned(), serde_json::Value::Null);
        object.insert(
            "tiefling_spellcasting_ability".to_owned(),
            serde_json::Value::Null,
        );
        let error = Character::from_json(&value.to_string()).expect_err("duplicate feat");
        assert!(error.contains("Alert Origin feat can be taken only once"));
    }

    #[test]
    fn validates_all_ability_generation_methods() {
        let standard = AbilityScores {
            strength: 15,
            dexterity: 14,
            constitution: 13,
            intelligence: 12,
            wisdom: 10,
            charisma: 8,
        };
        assert_eq!(
            AbilityScoreGeneration {
                method: AbilityGenerationMethod::StandardArray,
                scores: standard.clone(),
                character_class: None
            }
            .validate(),
            Ok(())
        );
        assert_eq!(
            AbilityScoreGeneration {
                method: AbilityGenerationMethod::SuggestedArray,
                scores: AbilityScores {
                    strength: 12,
                    dexterity: 15,
                    constitution: 13,
                    intelligence: 14,
                    wisdom: 10,
                    charisma: 8
                },
                character_class: Some("Rogue".to_owned())
            }
            .validate(),
            Ok(())
        );
        assert_eq!(
            AbilityScoreGeneration {
                method: AbilityGenerationMethod::PointBuy,
                scores: standard,
                character_class: None
            }
            .validate(),
            Ok(())
        );
    }

    #[test]
    fn applies_background_ability_increases() {
        let adjustment = BackgroundAbilityAdjustment {
            background: "Criminal".to_owned(),
            base_scores: AbilityScores {
                strength: 12,
                dexterity: 15,
                constitution: 13,
                intelligence: 14,
                wisdom: 10,
                charisma: 8,
            },
            increases: BTreeMap::from([
                ("dexterity".to_owned(), 2),
                ("constitution".to_owned(), 1),
            ]),
        };
        let adjusted = adjustment.adjusted_scores().expect("valid adjustment");
        assert_eq!(adjusted.dexterity, 17);
        assert_eq!(adjusted.constitution, 14);
    }

    #[test]
    fn validates_spellcasting_and_wizard_equipment_route() {
        let character = Character::from_json(r#"{
          "name":"Ada","character_class":"Wizard","background":"Sage","species":"Dwarf","size":"Medium","alignment":"Neutral Good",
          "abilities":{"strength":8,"dexterity":12,"constitution":14,"intelligence":17,"wisdom":15,"charisma":10},
          "class_skills":["Investigation","Nature"],
          "class_choices":{"cantrips":["Fire Bolt","Mage Hand","Prestidigitation"],"prepared_spells":["Detect Magic","Mage Armor","Magic Missile","Shield"],"spellbook_spells":["Detect Magic","Find Familiar","Mage Armor","Magic Missile","Shield","Sleep"]},
          "magic_initiate_choices":[{"spell_list":"Wizard","spellcasting_ability":"intelligence","cantrips":["Mage Hand","Prestidigitation"],"level_one_spell":"Mage Armor"}],
          "selected_languages":["Dwarvish","Elvish"]
        }"#).expect("wizard route is valid");
        assert_eq!(character.hit_points(), 9);
        assert_eq!(character.armor_class(), 11);
        assert_eq!(character.coins().gold, 13);
        assert!(
            character
                .inventory()
                .iter()
                .any(|item| item.name == "Spellbook")
        );
        assert!(
            character
                .weapon_attacks()
                .iter()
                .any(|attack| attack.name == "Arcane Focus (Quarterstaff)")
        );
    }
}
