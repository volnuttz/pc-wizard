from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from pc_wizard.rules import BACKGROUNDS, CLASSES, SKILL_ABILITIES, SPECIES


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


class Character(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    character_class: str
    background: str
    species: str
    alignment: str
    abilities: AbilityScores
    skills: set[str] = Field(default_factory=set)
    languages: list[str] = Field(default_factory=lambda: ["Common"])
    level: int = Field(default=1, ge=1, le=20)
    xp: int = Field(default=0, ge=0)

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
