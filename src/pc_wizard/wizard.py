import random
from collections.abc import Callable, Sequence
from typing import Any, cast

import questionary

from pc_wizard.models import AbilityScores, Character
from pc_wizard.rules import (
    ABILITIES,
    ALIGNMENTS,
    BACKGROUNDS,
    CLASSES,
    SPECIES,
    STANDARD_LANGUAGES,
)

Ask = Callable[[], Any]


def _required(ask: Ask) -> Any:
    value = ask()
    if value is None:
        raise KeyboardInterrupt
    return value


def select[T](message: str, choices: Sequence[T]) -> T:
    prompt_choices = cast(Any, list(choices))
    return cast(T, _required(questionary.select(message, choices=prompt_choices).ask))


def checkbox[T](message: str, choices: Sequence[T], count: int) -> list[T]:
    while True:
        prompt_choices = cast(Any, list(choices))
        result = cast(list[T], _required(questionary.checkbox(message, choices=prompt_choices).ask))
        if len(result) == count:
            return result
        questionary.print(f"Please choose exactly {count}.")


def text(message: str) -> str:
    def nonempty(value: str) -> bool:
        return bool(value.strip())

    return cast(str, _required(questionary.text(message, validate=nonempty).ask))


def generated_scores(method: str, rng: random.Random | None = None) -> list[int]:
    if method == "Standard array":
        return [15, 14, 13, 12, 10, 8]
    roller = rng or random.Random()
    return [
        sum(sorted((roller.randint(1, 6) for _ in range(4)), reverse=True)[:3]) for _ in range(6)
    ]


def run_wizard() -> Character:
    name = text("Character name")
    class_name = select("Choose a class", tuple(CLASSES))
    background_name = select("Choose a background", tuple(BACKGROUNDS))
    species_name = select("Choose a species", tuple(SPECIES))
    languages = ["Common", *checkbox("Choose two languages", STANDARD_LANGUAGES, 2)]

    method = select(
        "Generate ability scores",
        ("Suggested array for class", "Standard array", "Roll 4d6 drop lowest"),
    )
    if method == "Suggested array for class":
        values = list(CLASSES[class_name].standard_array)
    else:
        pool = generated_scores(method)
        values: list[int] = []
        for ability in ABILITIES:
            score = select(f"Assign {ability.title()} (remaining: {pool})", tuple(pool))
            values.append(score)
            pool.remove(score)

    background = BACKGROUNDS[background_name]
    boost_method = select(
        "Apply background ability increases", ("+2 to one and +1 to another", "+1 to all three")
    )
    if boost_method.startswith("+2"):
        plus_two = select("Ability to increase by 2", background.abilities)
        plus_one = select(
            "Different ability to increase by 1",
            tuple(x for x in background.abilities if x != plus_two),
        )
        values[ABILITIES.index(plus_two)] += 2
        values[ABILITIES.index(plus_one)] += 1
    else:
        for ability in background.abilities:
            values[ABILITIES.index(ability)] += 1

    class_rule = CLASSES[class_name]
    available = tuple(skill for skill in class_rule.skills if skill not in background.skills)
    class_skills = checkbox(
        f"Choose {class_rule.skill_count} class skills", available, class_rule.skill_count
    )
    alignment = select("Choose an alignment", ALIGNMENTS)
    return Character(
        name=name.strip(),
        character_class=class_name,
        background=background_name,
        species=species_name,
        alignment=alignment,
        abilities=AbilityScores(**dict(zip(ABILITIES, values, strict=True))),
        skills=set(background.skills) | set(class_skills),
        languages=languages,
    )
