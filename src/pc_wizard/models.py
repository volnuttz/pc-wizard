from enum import StrEnum
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from pc_wizard.rules import (
    ABILITIES,
    BACKGROUND_MAGIC_INITIATE_LISTS,
    BACKGROUND_ORIGIN_FEATS,
    BACKGROUNDS,
    CLASSES,
    DRACONIC_ANCESTORS,
    ELVEN_LINEAGES,
    FIENDISH_LEGACIES,
    GNOMISH_LINEAGES,
    GOLIATH_ANCESTRIES,
    MAGIC_INITIATE_SPELL_LISTS,
    MAX_ABILITY_SCORE,
    POINT_BUY_BUDGET,
    SKILL_ABILITIES,
    SPECIES,
    STANDARD_ARRAY,
    TOOLS,
    CreatureSize,
    DamageType,
    DraconicAncestry,
    ElvenLineage,
    ElvenLineageRule,
    FiendishLegacy,
    FiendishLegacyRule,
    GnomishLineage,
    GnomishLineageRule,
    GoliathAncestry,
    GoliathAncestryRule,
    KeenSensesSkill,
    MagicInitiateList,
    OriginFeat,
    SpellcastingAbility,
    point_buy_cost,
)


class AbilityScores(BaseModel):
    model_config = ConfigDict(extra="forbid")
    strength: int = Field(ge=3, le=20)
    dexterity: int = Field(ge=3, le=20)
    constitution: int = Field(ge=3, le=20)
    intelligence: int = Field(ge=3, le=20)
    wisdom: int = Field(ge=3, le=20)
    charisma: int = Field(ge=3, le=20)

    def modifier(self, ability: str) -> int:
        return (getattr(self, ability) - 10) // 2

    def ordered_values(self) -> tuple[int, int, int, int, int, int]:
        return (
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        )


class AbilityGenerationMethod(StrEnum):
    SUGGESTED_ARRAY = "suggested_array"
    STANDARD_ARRAY = "standard_array"
    RANDOM = "random"
    POINT_BUY = "point_buy"


class AbilityScoreGeneration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method: AbilityGenerationMethod
    scores: AbilityScores
    character_class: str | None = None

    @model_validator(mode="after")
    def valid_generation(self) -> Self:
        values = self.scores.ordered_values()
        if self.method is AbilityGenerationMethod.SUGGESTED_ARRAY:
            if self.character_class not in CLASSES:
                raise ValueError("suggested array requires a known SRD class")
            if values != CLASSES[self.character_class].standard_array:
                raise ValueError("scores do not match the class suggested array")
        elif self.method is AbilityGenerationMethod.STANDARD_ARRAY:
            if sorted(values) != sorted(STANDARD_ARRAY):
                raise ValueError("scores must assign every standard-array value exactly once")
        elif self.method is AbilityGenerationMethod.RANDOM:
            if any(score < 3 or score > 18 for score in values):
                raise ValueError("randomly generated scores must be between 3 and 18")
        elif point_buy_cost(values) != POINT_BUY_BUDGET:
            raise ValueError(f"point-buy scores must cost exactly {POINT_BUY_BUDGET} points")
        return self


class BackgroundAbilityAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    background: str
    base_scores: AbilityScores
    increases: dict[str, int]

    @model_validator(mode="after")
    def valid_adjustment(self) -> Self:
        if self.background not in BACKGROUNDS:
            raise ValueError(f"unknown SRD background: {self.background}")
        allowed = set(BACKGROUNDS[self.background].abilities)
        if not set(self.increases).issubset(allowed):
            raise ValueError(
                "background increases contain an ability not granted by the background"
            )
        if sorted(self.increases.values()) not in ([1, 2], [1, 1, 1]):
            raise ValueError("background increases must be +2/+1 or +1/+1/+1")
        for ability, amount in self.increases.items():
            if getattr(self.base_scores, ability) + amount > MAX_ABILITY_SCORE:
                raise ValueError(f"background increase would raise {ability} above 20")
        return self

    @property
    def adjusted_scores(self) -> AbilityScores:
        values = {
            ability: getattr(self.base_scores, ability) + self.increases.get(ability, 0)
            for ability in ABILITIES
        }
        return AbilityScores.model_validate(values)


class MagicInitiateChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    spell_list: MagicInitiateList
    spellcasting_ability: SpellcastingAbility
    cantrips: tuple[str, str]
    level_one_spell: str

    @model_validator(mode="after")
    def valid_spells(self) -> Self:
        spell_list = MAGIC_INITIATE_SPELL_LISTS[self.spell_list]
        if self.cantrips[0] == self.cantrips[1]:
            raise ValueError("Magic Initiate requires two different cantrips")
        if any(cantrip not in spell_list.cantrips for cantrip in self.cantrips):
            raise ValueError(f"Magic Initiate cantrips must come from the {self.spell_list} list")
        if self.level_one_spell not in spell_list.level_one_spells:
            raise ValueError(
                f"Magic Initiate level 1 spell must come from the {self.spell_list} list"
            )
        return self


class Character(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    character_class: str
    background: str
    species: str
    size: CreatureSize | None = None
    dragonborn_ancestry: DraconicAncestry | None = None
    elf_lineage: ElvenLineage | None = None
    elf_spellcasting_ability: SpellcastingAbility | None = None
    elf_keen_senses_skill: KeenSensesSkill | None = None
    gnome_lineage: GnomishLineage | None = None
    gnome_spellcasting_ability: SpellcastingAbility | None = None
    goliath_ancestry: GoliathAncestry | None = None
    human_skill: str | None = None
    human_origin_feat: OriginFeat | None = None
    tiefling_legacy: FiendishLegacy | None = None
    tiefling_spellcasting_ability: SpellcastingAbility | None = None
    alignment: str
    abilities: AbilityScores
    skills: set[str] = Field(default_factory=set)
    tool_proficiencies: set[str] = Field(default_factory=set)
    magic_initiate_choices: list[MagicInitiateChoice] = Field(
        default_factory=lambda: list[MagicInitiateChoice]()
    )
    skilled_proficiencies: set[str] = Field(default_factory=set)
    languages: list[str] = Field(default_factory=lambda: ["Common"])
    backstory: str | None = None
    appearance: str | None = None
    personality: str | None = None
    level: int = Field(default=1, ge=1, le=20)
    xp: int = Field(default=0, ge=0)

    @field_validator("backstory", "appearance", "personality", mode="before")
    @classmethod
    def normalize_optional_detail(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @model_validator(mode="after")
    def valid_species_choices(self) -> Self:
        allowed = SPECIES[self.species].sizes
        if self.size is None:
            self.size = allowed[0]
        elif self.size not in allowed:
            raise ValueError(
                f"invalid size for {self.species}: {self.size}; expected {' or '.join(allowed)}"
            )
        if self.species == "Dragonborn" and self.dragonborn_ancestry is None:
            raise ValueError("Dragonborn characters must choose a draconic ancestry")
        if self.species != "Dragonborn" and self.dragonborn_ancestry is not None:
            raise ValueError("draconic ancestry is only valid for Dragonborn characters")
        elf_choices = (
            self.elf_lineage,
            self.elf_spellcasting_ability,
            self.elf_keen_senses_skill,
        )
        if self.species == "Elf":
            if any(choice is None for choice in elf_choices):
                raise ValueError(
                    "Elf characters must choose a lineage, spellcasting ability, "
                    "and Keen Senses skill"
                )
            if self.elf_keen_senses_skill not in self.skills:
                raise ValueError(
                    "the Elf Keen Senses skill must be included in skill proficiencies"
                )
        elif any(choice is not None for choice in elf_choices):
            raise ValueError("Elf lineage choices are only valid for Elf characters")
        gnome_choices = (self.gnome_lineage, self.gnome_spellcasting_ability)
        if self.species == "Gnome":
            if any(choice is None for choice in gnome_choices):
                raise ValueError(
                    "Gnome characters must choose a Gnomish Lineage and spellcasting ability"
                )
        elif any(choice is not None for choice in gnome_choices):
            raise ValueError("Gnomish Lineage choices are only valid for Gnome characters")
        if self.species == "Goliath" and self.goliath_ancestry is None:
            raise ValueError("Goliath characters must choose a Giant Ancestry")
        if self.species != "Goliath" and self.goliath_ancestry is not None:
            raise ValueError("Giant Ancestry is only valid for Goliath characters")
        human_choices = (self.human_skill, self.human_origin_feat)
        if self.species == "Human":
            if any(choice is None for choice in human_choices):
                raise ValueError("Human characters must choose an additional skill and Origin feat")
            if self.human_skill not in SKILL_ABILITIES:
                raise ValueError(f"unknown Human Skillful proficiency: {self.human_skill}")
            if self.human_skill in BACKGROUNDS[self.background].skills:
                raise ValueError(
                    "the Human Skillful proficiency must be additional to background skills"
                )
            if self.human_skill not in self.skills:
                raise ValueError(
                    "the Human Skillful proficiency must be included in skill proficiencies"
                )
        elif any(choice is not None for choice in human_choices):
            raise ValueError("Human species choices are only valid for Human characters")
        tiefling_choices = (self.tiefling_legacy, self.tiefling_spellcasting_ability)
        if self.species == "Tiefling":
            if any(choice is None for choice in tiefling_choices):
                raise ValueError(
                    "Tiefling characters must choose a Fiendish Legacy and spellcasting ability"
                )
        elif any(choice is not None for choice in tiefling_choices):
            raise ValueError("Fiendish Legacy choices are only valid for Tiefling characters")
        return self

    @model_validator(mode="after")
    def valid_origin_feat_choices(self) -> Self:
        background_feat = BACKGROUND_ORIGIN_FEATS[self.background]
        if self.human_origin_feat == background_feat and self.human_origin_feat not in (
            "Magic Initiate",
            "Skilled",
        ):
            raise ValueError(f"the {self.human_origin_feat} Origin feat can be taken only once")

        background_magic_list = BACKGROUND_MAGIC_INITIATE_LISTS.get(self.background)
        expected_magic_choices = int(background_magic_list is not None) + int(
            self.human_origin_feat == "Magic Initiate"
        )
        if len(self.magic_initiate_choices) != expected_magic_choices:
            raise ValueError(
                f"character requires exactly {expected_magic_choices} Magic Initiate choice(s)"
            )
        chosen_lists = [choice.spell_list for choice in self.magic_initiate_choices]
        if len(set(chosen_lists)) != len(chosen_lists):
            raise ValueError("repeatable Magic Initiate choices must use different spell lists")
        if background_magic_list is not None and background_magic_list not in chosen_lists:
            raise ValueError(
                f"the {self.background} background requires "
                f"Magic Initiate ({background_magic_list})"
            )

        has_skilled = self.human_origin_feat == "Skilled"
        if has_skilled and len(self.skilled_proficiencies) != 3:
            raise ValueError("Skilled requires exactly three skill or tool proficiencies")
        if not has_skilled and self.skilled_proficiencies:
            raise ValueError("Skilled proficiencies require the Skilled Origin feat")
        unknown = self.skilled_proficiencies - (set(SKILL_ABILITIES) | set(TOOLS))
        if unknown:
            raise ValueError(f"unknown Skilled proficiencies: {', '.join(sorted(unknown))}")
        existing = set(BACKGROUNDS[self.background].skills)
        if self.human_skill is not None:
            existing.add(self.human_skill)
        if self.skilled_proficiencies & existing:
            raise ValueError("Skilled must grant proficiencies the character does not already have")
        skilled_skills = self.skilled_proficiencies & set(SKILL_ABILITIES)
        skilled_tools = self.skilled_proficiencies & set(TOOLS)
        if not skilled_skills.issubset(self.skills):
            raise ValueError("Skilled skill choices must be included in skill proficiencies")
        if not skilled_tools.issubset(self.tool_proficiencies):
            raise ValueError("Skilled tool choices must be included in tool proficiencies")
        return self

    @property
    def character_size(self) -> CreatureSize:
        if self.size is None:
            raise RuntimeError("character size was not resolved during validation")
        return self.size

    @property
    def dragonborn_damage_type(self) -> DamageType | None:
        if self.dragonborn_ancestry is None:
            return None
        return DRACONIC_ANCESTORS[self.dragonborn_ancestry]

    @property
    def elven_lineage_rule(self) -> ElvenLineageRule | None:
        if self.elf_lineage is None:
            return None
        return ELVEN_LINEAGES[self.elf_lineage]

    @property
    def gnomish_lineage_rule(self) -> GnomishLineageRule | None:
        if self.gnome_lineage is None:
            return None
        return GNOMISH_LINEAGES[self.gnome_lineage]

    @property
    def goliath_ancestry_rule(self) -> GoliathAncestryRule | None:
        if self.goliath_ancestry is None:
            return None
        return GOLIATH_ANCESTRIES[self.goliath_ancestry]

    @property
    def fiendish_legacy_rule(self) -> FiendishLegacyRule | None:
        if self.tiefling_legacy is None:
            return None
        return FIENDISH_LEGACIES[self.tiefling_legacy]

    @property
    def speed(self) -> int:
        lineage = self.elven_lineage_rule
        if lineage is not None:
            return lineage.speed
        return SPECIES[self.species].speed

    @property
    def darkvision_range(self) -> int | None:
        lineage = self.elven_lineage_rule
        if lineage is not None:
            return lineage.darkvision_range
        return SPECIES[self.species].darkvision_range

    @property
    def damage_resistances(self) -> tuple[DamageType, ...]:
        resistances = list(SPECIES[self.species].resistances)
        if self.dragonborn_damage_type is not None:
            resistances.append(self.dragonborn_damage_type)
        legacy = self.fiendish_legacy_rule
        if legacy is not None:
            resistances.append(legacy.resistance)
        return tuple(dict.fromkeys(resistances))

    @property
    def species_spellcasting_ability(self) -> SpellcastingAbility | None:
        return (
            self.elf_spellcasting_ability
            or self.gnome_spellcasting_ability
            or self.tiefling_spellcasting_ability
        )

    @property
    def species_cantrips(self) -> tuple[str, ...]:
        lineage = self.elven_lineage_rule
        if lineage is not None:
            return (lineage.cantrip,)
        gnomish_lineage = self.gnomish_lineage_rule
        if gnomish_lineage is not None:
            return gnomish_lineage.cantrips
        legacy = self.fiendish_legacy_rule
        if legacy is not None:
            return (legacy.cantrip, "Thaumaturgy")
        return ()

    @property
    def species_prepared_spells(self) -> tuple[str, ...]:
        spells: list[str] = []
        lineage = self.elven_lineage_rule
        if lineage is not None:
            if self.level >= 3:
                spells.append(lineage.level_three_spell)
            if self.level >= 5:
                spells.append(lineage.level_five_spell)
        gnomish_lineage = self.gnomish_lineage_rule
        if gnomish_lineage is not None:
            spells.extend(gnomish_lineage.always_prepared_spells)
        legacy = self.fiendish_legacy_rule
        if legacy is not None:
            if self.level >= 3:
                spells.append(legacy.level_three_spell)
            if self.level >= 5:
                spells.append(legacy.level_five_spell)
        return tuple(spells)

    @property
    def species_traits(self) -> tuple[str, ...]:
        traits = list(SPECIES[self.species].traits)
        if self.dragonborn_ancestry is not None:
            traits.append(
                f"Draconic Ancestry: {self.dragonborn_ancestry} ({self.dragonborn_damage_type})"
            )
        if self.elf_lineage is not None:
            traits.extend(
                (
                    f"Elven Lineage: {self.elf_lineage}",
                    f"Keen Senses: {self.elf_keen_senses_skill}",
                )
            )
        if self.gnome_lineage is not None:
            traits.append(f"Gnomish Lineage: {self.gnome_lineage}")
        ancestry = self.goliath_ancestry_rule
        if self.goliath_ancestry is not None and ancestry is not None:
            traits.append(
                f"Giant Ancestry: {self.goliath_ancestry} — "
                f"{ancestry.benefit_name}: {ancestry.effect}"
            )
        if self.human_skill is not None:
            traits.append(f"Skillful: {self.human_skill}")
        if self.human_origin_feat is not None:
            traits.append(f"Versatile: {self.human_origin_feat}")
        if self.tiefling_legacy is not None:
            traits.append(f"Fiendish Legacy: {self.tiefling_legacy}")
        if self.darkvision_range is not None:
            traits.append(f"Darkvision: {self.darkvision_range} ft.")
        if self.damage_resistances:
            traits.append(f"Damage Resistance: {', '.join(self.damage_resistances)}")
        if self.species_spellcasting_ability is not None:
            traits.append(
                f"Species Spellcasting Ability: {self.species_spellcasting_ability.title()}"
            )
        if self.species_cantrips:
            traits.append(f"Cantrips: {', '.join(self.species_cantrips)}")
        if self.species_prepared_spells:
            traits.append(f"Always Prepared: {', '.join(self.species_prepared_spells)}")
        return tuple(traits)

    @property
    def origin_feats(self) -> tuple[OriginFeat, ...]:
        feats: list[OriginFeat] = [BACKGROUND_ORIGIN_FEATS[self.background]]
        if self.human_origin_feat is not None:
            feats.append(self.human_origin_feat)
        return tuple(feats)

    @property
    def initiative_modifier(self) -> int:
        value = self.abilities.modifier("dexterity")
        if "Alert" in self.origin_feats:
            value += self.proficiency_bonus
        return value

    @property
    def all_tool_proficiencies(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((BACKGROUNDS[self.background].tool, *self.tool_proficiencies)))

    @property
    def feat_cantrips(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                cantrip for choice in self.magic_initiate_choices for cantrip in choice.cantrips
            )
        )

    @property
    def feat_prepared_spells(self) -> tuple[str, ...]:
        return tuple(choice.level_one_spell for choice in self.magic_initiate_choices)

    @property
    def origin_feat_traits(self) -> tuple[str, ...]:
        traits: list[str] = []
        if "Alert" in self.origin_feats:
            traits.append("Alert: Initiative Proficiency; Initiative Swap")
        if "Savage Attacker" in self.origin_feats:
            traits.append("Savage Attacker: roll weapon damage dice twice once per turn")
        if self.skilled_proficiencies:
            traits.append(f"Skilled: {', '.join(sorted(self.skilled_proficiencies))}")
        traits.extend(
            f"Magic Initiate ({choice.spell_list}; {choice.spellcasting_ability.title()}): "
            f"{', '.join(choice.cantrips)}; {choice.level_one_spell}"
            for choice in self.magic_initiate_choices
        )
        return tuple(traits)

    @field_validator("character_class")
    @classmethod
    def known_class(cls, value: str) -> str:
        if value not in CLASSES:
            raise ValueError(f"unknown SRD class: {value}")
        return value

    @field_validator("background")
    @classmethod
    def known_background(cls, value: str) -> str:
        if value not in BACKGROUNDS:
            raise ValueError(f"unknown SRD background: {value}")
        return value

    @field_validator("species")
    @classmethod
    def known_species(cls, value: str) -> str:
        if value not in SPECIES:
            raise ValueError(f"unknown SRD species: {value}")
        return value

    @property
    def proficiency_bonus(self) -> int:
        return 2 + (self.level - 1) // 4

    @property
    def hit_points(self) -> int:
        bonus = 1 if self.species == "Dwarf" else 0
        return (
            CLASSES[self.character_class].hit_die + self.abilities.modifier("constitution") + bonus
        )

    @property
    def armor_class(self) -> int:
        return 10 + self.abilities.modifier("dexterity")

    @property
    def passive_perception(self) -> int:
        return 10 + self.skill_modifier("Perception")

    def skill_modifier(self, skill: str) -> int:
        value = self.abilities.modifier(SKILL_ABILITIES[skill])
        return value + (self.proficiency_bonus if skill in self.skills else 0)

    def saving_throw(self, ability: str) -> int:
        value = self.abilities.modifier(ability)
        return value + (
            self.proficiency_bonus if ability in CLASSES[self.character_class].saves else 0
        )

    def save_json(self, path: Path) -> None:
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> Self:
        return cls.model_validate_json(path.read_text(encoding="utf-8"))


def signed(value: int) -> str:
    return f"{value:+d}"
