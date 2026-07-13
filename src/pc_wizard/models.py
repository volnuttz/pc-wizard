from enum import StrEnum
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from pc_wizard.rules import (
    ABILITIES,
    BACKGROUNDS,
    CLASSES,
    MAX_ABILITY_SCORE,
    POINT_BUY_BUDGET,
    SKILL_ABILITIES,
    SPECIES,
    STANDARD_ARRAY,
    CreatureSize,
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


class Character(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    character_class: str
    background: str
    species: str
    size: CreatureSize | None = None
    alignment: str
    abilities: AbilityScores
    skills: set[str] = Field(default_factory=set)
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
    def valid_species_size(self) -> Self:
        allowed = SPECIES[self.species].sizes
        if self.size is None:
            self.size = allowed[0]
        elif self.size not in allowed:
            raise ValueError(
                f"invalid size for {self.species}: {self.size}; expected {' or '.join(allowed)}"
            )
        return self

    @property
    def character_size(self) -> CreatureSize:
        if self.size is None:
            raise RuntimeError("character size was not resolved during validation")
        return self.size

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
