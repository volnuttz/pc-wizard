import random
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal, cast

import questionary
from pydantic import BaseModel, ConfigDict

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
    BACKGROUND_STARTING_EQUIPMENT,
    BACKGROUNDS,
    CLASS_ALWAYS_PREPARED_SPELLS,
    CLASS_SPELL_LISTS,
    CLASS_STARTING_EQUIPMENT,
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
    Alignment,
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
    StandardLanguage,
    eligible_abilities_for_increase,
    point_buy_cost,
    weapon_mastery_options,
)

DraftStage = Literal["origin", "abilities", "build", "details"]


class OriginDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    character_class: str
    background: str
    species: str
    size: CreatureSize
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
    magic_initiate_choices: list[MagicInitiateChoice]
    skilled_proficiencies: set[str]
    selected_languages: tuple[StandardLanguage, StandardLanguage]


class BuildDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    class_skills: set[str]
    class_choices: ClassChoices
    class_equipment_option: str
    background_equipment_option: Literal["A", "Gold"]
    bard_starting_instrument: str | None = None
    alignment: Alignment


class DetailsDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    backstory: str | None = None
    appearance: str | None = None
    personality: str | None = None


class CharacterDraft(BaseModel):
    """Current-format checkpoints for an incomplete creation session."""

    model_config = ConfigDict(extra="forbid")
    origin: OriginDraft | None = None
    abilities: AbilityScores | None = None
    build: BuildDraft | None = None
    details: DetailsDraft | None = None

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "CharacterDraft":
        return cls.model_validate_json(path.read_text(encoding="utf-8"))


class DraftSaved(Exception):
    """Signal an intentional exit after retaining the current draft."""


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
    additional_language: StandardLanguage | None = None
    if class_name == "Rogue":
        additional_language = select(
            "Choose the Rogue's additional language",
            tuple(
                language for language in STANDARD_LANGUAGES if language not in existing_languages
            ),
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


def choose_starting_equipment(
    class_name: str,
    background_name: str,
    class_choices: ClassChoices,
) -> tuple[str, Literal["A", "Gold"], str | None]:
    class_rule = CLASS_STARTING_EQUIPMENT[class_name]
    class_labels = {
        f"Package {key}: {package.label} (+{package.gold} GP)": key
        for key, package in class_rule.packages.items()
    }
    class_labels[f"Starting gold: {class_rule.gold} GP"] = "Gold"
    class_label = select("Choose class starting equipment", tuple(class_labels))
    class_option = class_labels[class_label]

    background_rule = BACKGROUND_STARTING_EQUIPMENT[background_name]
    package = background_rule.packages["A"]
    background_labels: dict[str, Literal["A", "Gold"]] = {
        f"Package A: {package.label} (+{package.gold} GP)": "A",
        f"Starting gold: {background_rule.gold} GP": "Gold",
    }
    background_label = select("Choose background starting equipment", tuple(background_labels))
    background_option = background_labels[background_label]

    bard_instrument = None
    if class_name == "Bard" and class_option != "Gold":
        bard_instrument = select(
            "Choose the musical instrument in the Bard package",
            tuple(sorted(class_choices.tools)),
        )
    return class_option, background_option, bard_instrument


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


def collect_origin() -> OriginDraft:
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
    if elf_keen_senses_skill is not None:
        origin_unavailable_skills.add(elf_keen_senses_skill)
    if human_skill is not None:
        origin_unavailable_skills.add(human_skill)
    magic_initiate_choices, skilled_proficiencies = choose_origin_feat_details(
        background_name, human_origin_feat, origin_unavailable_skills
    )
    selected_languages = cast(
        tuple[StandardLanguage, StandardLanguage],
        tuple(checkbox("Choose two languages", STANDARD_LANGUAGES, 2)),
    )
    return OriginDraft(
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
        magic_initiate_choices=magic_initiate_choices,
        skilled_proficiencies=skilled_proficiencies,
        selected_languages=selected_languages,
    )


def collect_abilities(origin: OriginDraft) -> AbilityScores:
    class_name = origin.character_class
    background_name = origin.background

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
    return AbilityScores(**dict(zip(ABILITIES, values, strict=True)))


def collect_build(origin: OriginDraft) -> BuildDraft:
    class_name = origin.character_class
    background_name = origin.background
    background_skills = set(BACKGROUNDS[background_name].skills)
    skilled_skills = origin.skilled_proficiencies & set(SKILL_ABILITIES)

    class_rule = CLASSES[class_name]
    unavailable_skills: set[str] = set(background_skills)
    if origin.elf_keen_senses_skill is not None:
        unavailable_skills.add(origin.elf_keen_senses_skill)
    if origin.human_skill is not None:
        unavailable_skills.add(origin.human_skill)
    unavailable_skills.update(skilled_skills)
    available = tuple(skill for skill in class_rule.skills if skill not in unavailable_skills)
    class_skills = checkbox(
        f"Choose {class_rule.skill_count} class skills", available, class_rule.skill_count
    )
    all_skills = unavailable_skills | set(class_skills)
    class_choices = choose_class_choices(
        class_name, all_skills, ("Common", *origin.selected_languages)
    )
    class_equipment_option, background_equipment_option, bard_starting_instrument = (
        choose_starting_equipment(class_name, background_name, class_choices)
    )
    alignment = select("Choose an alignment", ALIGNMENTS)
    return BuildDraft(
        class_skills=set(class_skills),
        class_choices=class_choices,
        class_equipment_option=class_equipment_option,
        background_equipment_option=background_equipment_option,
        bard_starting_instrument=bard_starting_instrument,
        alignment=alignment,
    )


def collect_details() -> DetailsDraft:
    return DetailsDraft(
        backstory=optional_text("Backstory"),
        appearance=optional_text("Appearance"),
        personality=optional_text("Personality"),
    )


def character_from_draft(draft: CharacterDraft) -> Character:
    if any(stage is None for stage in (draft.origin, draft.abilities, draft.build, draft.details)):
        raise ValueError("the character draft is incomplete")
    origin = cast(OriginDraft, draft.origin)
    abilities = cast(AbilityScores, draft.abilities)
    build = cast(BuildDraft, draft.build)
    details = cast(DetailsDraft, draft.details)
    skilled_tools = origin.skilled_proficiencies & set(TOOLS)
    return Character(
        name=origin.name,
        character_class=origin.character_class,
        background=origin.background,
        species=origin.species,
        size=origin.size,
        dragonborn_ancestry=origin.dragonborn_ancestry,
        elf_lineage=origin.elf_lineage,
        elf_spellcasting_ability=origin.elf_spellcasting_ability,
        elf_keen_senses_skill=origin.elf_keen_senses_skill,
        gnome_lineage=origin.gnome_lineage,
        gnome_spellcasting_ability=origin.gnome_spellcasting_ability,
        goliath_ancestry=origin.goliath_ancestry,
        human_skill=origin.human_skill,
        human_origin_feat=origin.human_origin_feat,
        tiefling_legacy=origin.tiefling_legacy,
        tiefling_spellcasting_ability=origin.tiefling_spellcasting_ability,
        alignment=build.alignment,
        abilities=abilities,
        class_skills=build.class_skills,
        class_choices=build.class_choices,
        class_equipment_option=build.class_equipment_option,
        background_equipment_option=build.background_equipment_option,
        bard_starting_instrument=build.bard_starting_instrument,
        tool_proficiencies=skilled_tools,
        magic_initiate_choices=origin.magic_initiate_choices,
        skilled_proficiencies=origin.skilled_proficiencies,
        selected_languages=origin.selected_languages,
        backstory=details.backstory,
        appearance=details.appearance,
        personality=details.personality,
    )


def review_summary(character: Character) -> str:
    derived = character.derived_values
    return (
        f"\n{character.name} — level 1 {character.species} {character.character_class}\n"
        f"Background: {character.background} | Alignment: {character.alignment}\n"
        f"HP {derived.hit_points} | AC {derived.armor_class} | Speed {derived.speed} ft.\n"
        f"Skills: {', '.join(derived.skills)}\n"
        f"Languages: {', '.join(derived.languages)}\n"
        f"Equipment: {', '.join(item.name for item in derived.equipment) or 'None'}"
    )


def _confirm(message: str) -> bool:
    return cast(bool, _required(questionary.confirm(message, default=False).ask))


def run_wizard(draft_path: Path | None = None) -> Character:
    draft = CharacterDraft()
    if draft_path is not None and draft_path.exists():
        action = select(
            f"A saved creation session exists at {draft_path}",
            ("Resume saved session", "Discard it and start over"),
        )
        if action == "Resume saved session":
            draft = CharacterDraft.load(draft_path)
        elif not _confirm("Discard the saved session and all of its answers?"):
            raise DraftSaved

    while True:
        if draft.origin is None:
            draft.origin = collect_origin()
            draft.abilities = None
            draft.build = None
            draft.details = None
            if draft_path is not None:
                draft.save(draft_path)
        if draft.abilities is None:
            draft.abilities = collect_abilities(draft.origin)
            if draft_path is not None:
                draft.save(draft_path)
        if draft.build is None:
            draft.build = collect_build(draft.origin)
            if draft_path is not None:
                draft.save(draft_path)
        if draft.details is None:
            draft.details = collect_details()
            if draft_path is not None:
                draft.save(draft_path)

        character = character_from_draft(draft)
        questionary.print(review_summary(character))
        action = select(
            "Review your character",
            (
                "Finish and write files",
                "Edit identity and origin",
                "Edit ability scores",
                "Edit class choices and equipment",
                "Edit character details",
                "Save draft and exit",
            ),
        )
        if action == "Finish and write files":
            return character
        if action == "Save draft and exit":
            if draft_path is not None:
                draft.save(draft_path)
            raise DraftSaved
        if action == "Edit identity and origin":
            if not _confirm(
                "Changing identity or origin clears ability, class, equipment, "
                "and detail answers. Continue?"
            ):
                continue
            draft = CharacterDraft()
        elif action == "Edit ability scores":
            draft.abilities = None
        elif action == "Edit class choices and equipment":
            draft.build = None
        else:
            draft.details = None
        if draft_path is not None:
            draft.save(draft_path)
