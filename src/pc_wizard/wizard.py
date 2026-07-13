import random
from collections.abc import Callable, Sequence
from typing import Any, cast

import questionary

from pc_wizard.models import (
    AbilityGenerationMethod,
    AbilityScoreGeneration,
    AbilityScores,
    BackgroundAbilityAdjustment,
    Character,
)
from pc_wizard.rules import (
    ABILITIES,
    ALIGNMENTS,
    BACKGROUNDS,
    CLASSES,
    POINT_BUY_BUDGET,
    POINT_BUY_COSTS,
    SPECIES,
    STANDARD_ARRAY,
    STANDARD_LANGUAGES,
    CreatureSize,
    eligible_abilities_for_increase,
    point_buy_cost,
)

Ask = Callable[[], Any]
ABILITY_GENERATION_CHOICES = {
    "Suggested array for class": AbilityGenerationMethod.SUGGESTED_ARRAY,
    "Standard array": AbilityGenerationMethod.STANDARD_ARRAY,
    "Roll 4d6 drop lowest": AbilityGenerationMethod.RANDOM,
    "Point cost (27 points)": AbilityGenerationMethod.POINT_BUY,
}


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


def optional_text(message: str) -> str | None:
    value = cast(str, _required(questionary.text(f"{message} (optional)").ask))
    return value.strip() or None


def choose_species_size(species_name: str) -> CreatureSize:
    sizes = SPECIES[species_name].sizes
    if len(sizes) == 1:
        return sizes[0]
    return select("Choose a size", sizes)


def generated_scores(
    method: AbilityGenerationMethod, rng: random.Random | None = None
) -> list[int]:
    if method is AbilityGenerationMethod.STANDARD_ARRAY:
        return list(STANDARD_ARRAY)
    if method is not AbilityGenerationMethod.RANDOM:
        raise ValueError(f"scores cannot be generated directly for method: {method}")
    roller = rng or random.Random()
    return [
        sum(sorted((roller.randint(1, 6) for _ in range(4)), reverse=True)[:3]) for _ in range(6)
    ]


def point_buy_scores() -> list[int]:
    values = [8] * len(ABILITIES)
    while True:
        remaining = POINT_BUY_BUDGET - point_buy_cost(values)
        summary = ", ".join(
            f"{ability.title()} {value}" for ability, value in zip(ABILITIES, values, strict=True)
        )
        ability = select(
            f"Point cost — {remaining} points remaining ({summary})",
            (*ABILITIES, "Finish"),
        )
        if ability == "Finish":
            if remaining == 0:
                return values
            questionary.print(f"Spend the remaining {remaining} points before finishing.")
            continue

        index = ABILITIES.index(ability)
        available = remaining + POINT_BUY_COSTS[values[index]]
        choices = tuple(score for score, cost in POINT_BUY_COSTS.items() if cost <= available)
        values[index] = select(
            f"Set {ability.title()} ({remaining} points remaining)",
            choices,
        )


def apply_background_increases(values: Sequence[int], background_name: str) -> list[int]:
    adjusted = list(values)
    scores: dict[str, int] = dict(zip(ABILITIES, adjusted, strict=True))
    background_abilities = BACKGROUNDS[background_name].abilities
    plus_one_candidates = eligible_abilities_for_increase(scores, background_abilities, 1)
    plus_two_candidates = tuple(
        ability
        for ability in eligible_abilities_for_increase(scores, background_abilities, 2)
        if any(other != ability for other in plus_one_candidates)
    )

    methods: list[str] = []
    if plus_two_candidates:
        methods.append("+2 to one and +1 to another")
    if len(plus_one_candidates) == len(background_abilities):
        methods.append("+1 to all three")
    if not methods:
        raise ValueError("no legal background ability increases remain")

    boost_method = select("Apply background ability increases", methods)
    increases: dict[str, int]
    if boost_method.startswith("+2"):
        plus_two = select("Ability to increase by 2", plus_two_candidates)
        plus_one = select(
            "Different ability to increase by 1",
            tuple(ability for ability in plus_one_candidates if ability != plus_two),
        )
        increases = {plus_two: 2, plus_one: 1}
    else:
        increases = dict.fromkeys(background_abilities, 1)
    adjustment = BackgroundAbilityAdjustment(
        background=background_name,
        base_scores=AbilityScores(**scores),
        increases=increases,
    )
    return list(adjustment.adjusted_scores.ordered_values())


def run_wizard() -> Character:
    name = text("Character name")
    class_name = select("Choose a class", tuple(CLASSES))
    background_name = select("Choose a background", tuple(BACKGROUNDS))
    species_name = select("Choose a species", tuple(SPECIES))
    size = choose_species_size(species_name)
    languages = ["Common", *checkbox("Choose two languages", STANDARD_LANGUAGES, 2)]

    method_label = select("Generate ability scores", tuple(ABILITY_GENERATION_CHOICES))
    method = ABILITY_GENERATION_CHOICES[method_label]
    if method is AbilityGenerationMethod.SUGGESTED_ARRAY:
        values = list(CLASSES[class_name].standard_array)
    elif method is AbilityGenerationMethod.POINT_BUY:
        values = point_buy_scores()
    else:
        pool = generated_scores(method)
        values: list[int] = []
        for ability in ABILITIES:
            score = select(f"Assign {ability.title()} (remaining: {pool})", tuple(pool))
            values.append(score)
            pool.remove(score)

    generation = AbilityScoreGeneration(
        method=method,
        scores=AbilityScores(**dict(zip(ABILITIES, values, strict=True))),
        character_class=class_name,
    )
    values = apply_background_increases(generation.scores.ordered_values(), background_name)

    background = BACKGROUNDS[background_name]
    class_rule = CLASSES[class_name]
    available = tuple(skill for skill in class_rule.skills if skill not in background.skills)
    class_skills = checkbox(
        f"Choose {class_rule.skill_count} class skills", available, class_rule.skill_count
    )
    alignment = select("Choose an alignment", ALIGNMENTS)
    backstory = optional_text("Backstory")
    appearance = optional_text("Appearance")
    personality = optional_text("Personality")
    return Character(
        name=name.strip(),
        character_class=class_name,
        background=background_name,
        species=species_name,
        size=size,
        alignment=alignment,
        abilities=AbilityScores(**dict(zip(ABILITIES, values, strict=True))),
        skills=set(background.skills) | set(class_skills),
        languages=languages,
        backstory=backstory,
        appearance=appearance,
        personality=personality,
    )
