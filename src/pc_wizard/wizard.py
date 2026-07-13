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
    ClassChoices,
    MagicInitiateChoice,
)
from pc_wizard.rules import (
    ABILITIES,
    ALIGNMENTS,
    ARTISAN_TOOLS,
    BACKGROUND_MAGIC_INITIATE_LISTS,
    BACKGROUNDS,
    CLASS_ALWAYS_PREPARED_SPELLS,
    CLASS_SPELL_LISTS,
    CLASSES,
    DRACONIC_ANCESTORS,
    ELVEN_LINEAGES,
    FIENDISH_LEGACIES,
    FIGHTING_STYLES,
    GNOMISH_LINEAGES,
    GOLIATH_ANCESTRIES,
    KEEN_SENSES_SKILLS,
    LEVEL_ONE_WARLOCK_INVOCATIONS,
    MAGIC_INITIATE_SPELL_LISTS,
    MUSICAL_INSTRUMENTS,
    ORIGIN_FEATS,
    POINT_BUY_BUDGET,
    POINT_BUY_COSTS,
    SKILL_ABILITIES,
    SPECIES,
    SPELLCASTING_ABILITIES,
    STANDARD_ARRAY,
    STANDARD_LANGUAGES,
    TOOLS,
    WEAPON_MASTERY_COUNTS,
    CreatureSize,
    DraconicAncestry,
    ElvenLineage,
    FiendishLegacy,
    GnomishLineage,
    GoliathAncestry,
    KeenSensesSkill,
    MagicInitiateList,
    OriginFeat,
    SpellcastingAbility,
    eligible_abilities_for_increase,
    point_buy_cost,
    weapon_mastery_options,
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


def choose_draconic_ancestry(species_name: str) -> DraconicAncestry | None:
    if species_name != "Dragonborn":
        return None
    return select("Choose a draconic ancestry", tuple(DRACONIC_ANCESTORS))


def choose_elf_traits(
    species_name: str, unavailable_skills: set[str]
) -> tuple[ElvenLineage | None, SpellcastingAbility | None, KeenSensesSkill | None]:
    if species_name != "Elf":
        return None, None, None
    lineage = select("Choose an elven lineage", tuple(ELVEN_LINEAGES))
    spellcasting_ability = select(
        "Choose an Elven Lineage spellcasting ability", SPELLCASTING_ABILITIES
    )
    available_skills = tuple(
        skill for skill in KEEN_SENSES_SKILLS if skill not in unavailable_skills
    )
    keen_senses_skill = cast(
        KeenSensesSkill, select("Choose a Keen Senses skill", available_skills)
    )
    return lineage, spellcasting_ability, keen_senses_skill


def choose_gnome_traits(
    species_name: str,
) -> tuple[GnomishLineage | None, SpellcastingAbility | None]:
    if species_name != "Gnome":
        return None, None
    lineage = select("Choose a Gnomish Lineage", tuple(GNOMISH_LINEAGES))
    spellcasting_ability = select(
        "Choose a Gnomish Lineage spellcasting ability", SPELLCASTING_ABILITIES
    )
    return lineage, spellcasting_ability


def choose_goliath_ancestry(species_name: str) -> GoliathAncestry | None:
    if species_name != "Goliath":
        return None
    return select("Choose a Giant Ancestry", tuple(GOLIATH_ANCESTRIES))


def choose_human_traits(
    species_name: str, unavailable_skills: set[str]
) -> tuple[str | None, OriginFeat | None]:
    if species_name != "Human":
        return None, None
    available_skills = tuple(skill for skill in SKILL_ABILITIES if skill not in unavailable_skills)
    skill = select("Choose an additional Human skill", available_skills)
    origin_feat = select("Choose a Human Origin feat", ORIGIN_FEATS)
    return skill, origin_feat


def choose_tiefling_traits(
    species_name: str,
) -> tuple[FiendishLegacy | None, SpellcastingAbility | None]:
    if species_name != "Tiefling":
        return None, None
    legacy = select("Choose a Fiendish Legacy", tuple(FIENDISH_LEGACIES))
    spellcasting_ability = select(
        "Choose a Fiendish Legacy spellcasting ability", SPELLCASTING_ABILITIES
    )
    return legacy, spellcasting_ability


def choose_magic_initiate(spell_list: MagicInitiateList) -> MagicInitiateChoice:
    spells = MAGIC_INITIATE_SPELL_LISTS[spell_list]
    spellcasting_ability = select(
        f"Choose Magic Initiate ({spell_list}) spellcasting ability",
        SPELLCASTING_ABILITIES,
    )
    cantrips = checkbox(
        f"Choose two Magic Initiate ({spell_list}) cantrips",
        spells.cantrips,
        2,
    )
    level_one_spell = select(
        f"Choose a Magic Initiate ({spell_list}) level 1 spell",
        spells.level_one_spells,
    )
    return MagicInitiateChoice(
        spell_list=spell_list,
        spellcasting_ability=spellcasting_ability,
        cantrips=cast(tuple[str, str], tuple(cantrips)),
        level_one_spell=level_one_spell,
    )


def choose_origin_feat_details(
    background_name: str,
    human_origin_feat: OriginFeat | None,
    unavailable_skills: set[str],
) -> tuple[list[MagicInitiateChoice], set[str]]:
    magic_lists: list[MagicInitiateList] = []
    background_magic_list = BACKGROUND_MAGIC_INITIATE_LISTS.get(background_name)
    if background_magic_list is not None:
        magic_lists.append(background_magic_list)
    if human_origin_feat == "Magic Initiate":
        available_lists = tuple(
            spell_list for spell_list in MAGIC_INITIATE_SPELL_LISTS if spell_list not in magic_lists
        )
        magic_lists.append(
            cast(
                MagicInitiateList,
                select("Choose a Human Magic Initiate spell list", available_lists),
            )
        )
    magic_choices = [choose_magic_initiate(spell_list) for spell_list in magic_lists]

    skilled_proficiencies: set[str] = set()
    if human_origin_feat == "Skilled":
        background_tool = BACKGROUNDS[background_name].tool
        choices = (
            *(skill for skill in SKILL_ABILITIES if skill not in unavailable_skills),
            *(tool for tool in TOOLS if tool != background_tool),
        )
        skilled_proficiencies = set(
            checkbox("Choose three Skilled skill or tool proficiencies", choices, 3)
        )
    return magic_choices, skilled_proficiencies


def choose_class_choices(
    class_name: str, skills: set[str], existing_languages: Sequence[str]
) -> ClassChoices:
    divine_order = (
        select("Choose a Divine Order", ("Protector", "Thaumaturge"))
        if class_name == "Cleric"
        else None
    )
    primal_order = (
        select("Choose a Primal Order", ("Magician", "Warden")) if class_name == "Druid" else None
    )

    mastery_count = WEAPON_MASTERY_COUNTS.get(class_name, 0)
    weapon_masteries: set[str] = (
        set(
            checkbox(
                f"Choose {mastery_count} weapon masteries",
                weapon_mastery_options(class_name),
                mastery_count,
            )
        )
        if mastery_count
        else set()
    )

    tools: set[str] = set()
    if class_name == "Bard":
        tools = set(checkbox("Choose three musical instruments", MUSICAL_INSTRUMENTS, 3))
    elif class_name == "Monk":
        tools = {
            select(
                "Choose an artisan tool or musical instrument",
                (*ARTISAN_TOOLS, *MUSICAL_INSTRUMENTS),
            )
        }

    expertise: set[str] = (
        set(checkbox("Choose two skills for Expertise", tuple(sorted(skills)), 2))
        if class_name == "Rogue"
        else set()
    )
    fighting_style = (
        select("Choose a Fighting Style", FIGHTING_STYLES) if class_name == "Fighter" else None
    )
    eldritch_invocation = (
        select("Choose an Eldritch Invocation", tuple(LEVEL_ONE_WARLOCK_INVOCATIONS))
        if class_name == "Warlock"
        else None
    )
    additional_language = (
        select(
            "Choose the Rogue's additional language",
            tuple(
                language for language in STANDARD_LANGUAGES if language not in existing_languages
            ),
        )
        if class_name == "Rogue"
        else None
    )

    cantrip_count = {
        "Bard": 2,
        "Cleric": 3,
        "Druid": 2,
        "Sorcerer": 4,
        "Warlock": 2,
        "Wizard": 3,
    }.get(class_name, 0)
    if divine_order == "Thaumaturge" or primal_order == "Magician":
        cantrip_count += 1
    prepared_count = {
        "Bard": 4,
        "Cleric": 4,
        "Druid": 4,
        "Paladin": 2,
        "Ranger": 2,
        "Sorcerer": 2,
        "Warlock": 2,
        "Wizard": 4,
    }.get(class_name, 0)
    spell_list = CLASS_SPELL_LISTS.get(class_name)
    cantrips: set[str] = (
        set(
            checkbox(
                f"Choose {cantrip_count} {class_name} cantrips", spell_list.cantrips, cantrip_count
            )
        )
        if spell_list and cantrip_count
        else set()
    )
    spellbook_spells: set[str] = (
        set(checkbox("Choose six level 1 Wizard spellbook spells", spell_list.level_one_spells, 6))
        if class_name == "Wizard" and spell_list
        else set()
    )
    prepared_options = (
        tuple(sorted(spellbook_spells))
        if class_name == "Wizard"
        else (
            tuple(
                spell
                for spell in spell_list.level_one_spells
                if spell not in CLASS_ALWAYS_PREPARED_SPELLS.get(class_name, ())
            )
            if spell_list
            else ()
        )
    )
    prepared_spells: set[str] = (
        set(
            checkbox(
                f"Choose {prepared_count} prepared {class_name} spells",
                prepared_options,
                prepared_count,
            )
        )
        if prepared_count
        else set()
    )
    return ClassChoices(
        weapon_masteries=weapon_masteries,
        tools=tools,
        expertise=expertise,
        cantrips=cantrips,
        prepared_spells=prepared_spells,
        spellbook_spells=spellbook_spells,
        divine_order=divine_order,
        primal_order=primal_order,
        fighting_style=fighting_style,
        eldritch_invocation=eldritch_invocation,
        additional_language=additional_language,
    )


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
    dragonborn_ancestry = choose_draconic_ancestry(species_name)
    background_skills = set(BACKGROUNDS[background_name].skills)
    elf_lineage, elf_spellcasting_ability, elf_keen_senses_skill = choose_elf_traits(
        species_name, background_skills
    )
    gnome_lineage, gnome_spellcasting_ability = choose_gnome_traits(species_name)
    goliath_ancestry = choose_goliath_ancestry(species_name)
    human_skill, human_origin_feat = choose_human_traits(species_name, background_skills)
    tiefling_legacy, tiefling_spellcasting_ability = choose_tiefling_traits(species_name)
    origin_unavailable_skills = set(background_skills)
    if human_skill is not None:
        origin_unavailable_skills.add(human_skill)
    magic_initiate_choices, skilled_proficiencies = choose_origin_feat_details(
        background_name, human_origin_feat, origin_unavailable_skills
    )
    skilled_skills = skilled_proficiencies & set(SKILL_ABILITIES)
    skilled_tools = skilled_proficiencies & set(TOOLS)
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

    class_rule = CLASSES[class_name]
    unavailable_skills: set[str] = set(background_skills)
    if elf_keen_senses_skill is not None:
        unavailable_skills.add(elf_keen_senses_skill)
    if human_skill is not None:
        unavailable_skills.add(human_skill)
    unavailable_skills.update(skilled_skills)
    available = tuple(skill for skill in class_rule.skills if skill not in unavailable_skills)
    class_skills = checkbox(
        f"Choose {class_rule.skill_count} class skills", available, class_rule.skill_count
    )
    all_skills = unavailable_skills | set(class_skills)
    class_choices = choose_class_choices(class_name, all_skills, languages)
    if class_choices.additional_language is not None:
        languages.append(class_choices.additional_language)
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
        dragonborn_ancestry=dragonborn_ancestry,
        elf_lineage=elf_lineage,
        elf_spellcasting_ability=elf_spellcasting_ability,
        elf_keen_senses_skill=elf_keen_senses_skill,
        gnome_lineage=gnome_lineage,
        gnome_spellcasting_ability=gnome_spellcasting_ability,
        goliath_ancestry=goliath_ancestry,
        human_skill=human_skill,
        human_origin_feat=human_origin_feat,
        tiefling_legacy=tiefling_legacy,
        tiefling_spellcasting_ability=tiefling_spellcasting_ability,
        alignment=alignment,
        abilities=AbilityScores(**dict(zip(ABILITIES, values, strict=True))),
        skills=all_skills,
        class_choices=class_choices,
        tool_proficiencies=skilled_tools,
        magic_initiate_choices=magic_initiate_choices,
        skilled_proficiencies=skilled_proficiencies,
        languages=languages,
        backstory=backstory,
        appearance=appearance,
        personality=personality,
    )
