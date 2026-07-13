import random
from collections.abc import Sequence
from typing import cast

import pytest

from pc_wizard import wizard
from pc_wizard.models import AbilityGenerationMethod, ClassChoices, MagicInitiateChoice
from pc_wizard.rules import (
    POINT_BUY_BUDGET,
    MagicInitiateList,
    eligible_abilities_for_increase,
    point_buy_cost,
)
from pc_wizard.wizard import (
    apply_background_increases,
    choose_class_choices,
    choose_draconic_ancestry,
    choose_elf_traits,
    choose_gnome_traits,
    choose_goliath_ancestry,
    choose_human_traits,
    choose_magic_initiate,
    choose_origin_feat_details,
    choose_species_size,
    choose_tiefling_traits,
    generated_scores,
    optional_text,
    point_buy_scores,
)


def test_standard_array() -> None:
    assert generated_scores(AbilityGenerationMethod.STANDARD_ARRAY) == [15, 14, 13, 12, 10, 8]


def test_random_scores_are_valid() -> None:
    scores = generated_scores(AbilityGenerationMethod.RANDOM, random.Random(42))
    assert len(scores) == 6
    assert all(3 <= score <= 18 for score in scores)


def test_point_buy_cost() -> None:
    assert point_buy_cost([15, 15, 13, 12, 8, 8]) == POINT_BUY_BUDGET

    with pytest.raises(ValueError, match="between 8 and 15"):
        point_buy_cost([16])


def test_point_buy_scores_show_remaining_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers: list[str | int] = [
        "Finish",
        "strength",
        15,
        "dexterity",
        15,
        "constitution",
        13,
        "intelligence",
        12,
        "Finish",
    ]
    messages: list[str] = []
    notices: list[str] = []

    def fake_select[T](message: str, choices: Sequence[T]) -> T:
        messages.append(message)
        answer = answers.pop(0)
        assert answer in choices
        return cast(T, answer)

    def fake_print(value: object) -> None:
        notices.append(str(value))

    monkeypatch.setattr(wizard, "select", fake_select)
    monkeypatch.setattr(wizard.questionary, "print", fake_print)

    assert point_buy_scores() == [15, 15, 13, 12, 8, 8]
    assert not answers
    assert notices == ["Spend the remaining 27 points before finishing."]
    assert any("27 points remaining" in message for message in messages)
    assert any("18 points remaining" in message for message in messages)
    assert any("9 points remaining" in message for message in messages)
    assert any("4 points remaining" in message for message in messages)
    assert any("0 points remaining" in message for message in messages)


def test_background_increase_prompts_exclude_scores_above_20(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(("+2 to one and +1 to another", "constitution", "strength"))
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        choices = tuple(choices)
        prompts.append((message, choices))
        answer = next(answers)
        assert answer in choices
        return answer

    monkeypatch.setattr(wizard, "select", fake_select)

    result = apply_background_increases(
        [19, 20, 18, 10, 10, 10],
        "Soldier",
    )

    assert result == [20, 20, 20, 10, 10, 10]
    assert prompts == [
        ("Apply background ability increases", ("+2 to one and +1 to another",)),
        ("Ability to increase by 2", ("constitution",)),
        ("Different ability to increase by 1", ("strength",)),
    ]


def test_background_all_three_increase_requires_room_for_each_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_select(message: str, choices: Sequence[str]) -> str:
        assert message == "Apply background ability increases"
        assert tuple(choices) == ("+1 to all three",)
        return "+1 to all three"

    monkeypatch.setattr(wizard, "select", fake_select)

    assert apply_background_increases(
        [19, 19, 19, 10, 10, 10],
        "Soldier",
    ) == [20, 20, 20, 10, 10, 10]


def test_eligible_background_increases_require_positive_amount() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        eligible_abilities_for_increase({"strength": 10}, ("strength",), 0)


def test_optional_text_can_be_skipped_or_trimmed(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(("   ", "  Raised by traveling scholars.  "))
    messages: list[str] = []

    class FakePrompt:
        def ask(self) -> str:
            return next(answers)

    def fake_text(message: str) -> FakePrompt:
        messages.append(message)
        return FakePrompt()

    monkeypatch.setattr(wizard.questionary, "text", fake_text)

    assert optional_text("Backstory") is None
    assert optional_text("Backstory") == "Raised by traveling scholars."
    assert messages == ["Backstory (optional)", "Backstory (optional)"]


def test_species_size_prompt_only_appears_for_srd_choices(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        prompts.append((message, tuple(choices)))
        return "Small"

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_species_size("Human") == "Small"
    assert choose_species_size("Tiefling") == "Small"
    assert choose_species_size("Dwarf") == "Medium"
    assert prompts == [
        ("Choose a size", ("Medium", "Small")),
        ("Choose a size", ("Medium", "Small")),
    ]


def test_draconic_ancestry_prompt_only_appears_for_dragonborn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        prompts.append((message, tuple(choices)))
        return "Gold"

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_draconic_ancestry("Dragonborn") == "Gold"
    assert choose_draconic_ancestry("Dwarf") is None
    assert prompts == [
        (
            "Choose a draconic ancestry",
            (
                "Black",
                "Blue",
                "Brass",
                "Bronze",
                "Copper",
                "Gold",
                "Green",
                "Red",
                "Silver",
                "White",
            ),
        )
    ]


def test_elf_trait_prompts_collect_choices_without_duplicate_background_skill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(("Drow", "intelligence", "Perception"))
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        choices = tuple(choices)
        prompts.append((message, choices))
        answer = next(answers)
        assert answer in choices
        return answer

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_elf_traits("Elf", {"Insight"}) == ("Drow", "intelligence", "Perception")
    assert prompts == [
        ("Choose an elven lineage", ("Drow", "High Elf", "Wood Elf")),
        (
            "Choose an Elven Lineage spellcasting ability",
            ("intelligence", "wisdom", "charisma"),
        ),
        ("Choose a Keen Senses skill", ("Perception", "Survival")),
    ]


def test_elf_trait_prompts_are_skipped_for_other_species(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_select(message: str, choices: Sequence[str]) -> str:
        raise AssertionError(f"unexpected prompt: {message}, {tuple(choices)}")

    monkeypatch.setattr(wizard, "select", unexpected_select)

    assert choose_elf_traits("Dwarf", set()) == (None, None, None)


def test_gnome_trait_prompts_collect_lineage_and_spellcasting_ability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(("Forest Gnome", "wisdom"))
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        choices = tuple(choices)
        prompts.append((message, choices))
        answer = next(answers)
        assert answer in choices
        return answer

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_gnome_traits("Gnome") == ("Forest Gnome", "wisdom")
    assert prompts == [
        ("Choose a Gnomish Lineage", ("Forest Gnome", "Rock Gnome")),
        (
            "Choose a Gnomish Lineage spellcasting ability",
            ("intelligence", "wisdom", "charisma"),
        ),
    ]


def test_gnome_trait_prompts_are_skipped_for_other_species(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_select(message: str, choices: Sequence[str]) -> str:
        raise AssertionError(f"unexpected prompt: {message}, {tuple(choices)}")

    monkeypatch.setattr(wizard, "select", unexpected_select)

    assert choose_gnome_traits("Dwarf") == (None, None)


def test_goliath_ancestry_prompt_only_appears_for_goliath(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        prompts.append((message, tuple(choices)))
        return "Stone Giant"

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_goliath_ancestry("Goliath") == "Stone Giant"
    assert choose_goliath_ancestry("Dwarf") is None
    assert prompts == [
        (
            "Choose a Giant Ancestry",
            (
                "Cloud Giant",
                "Fire Giant",
                "Frost Giant",
                "Hill Giant",
                "Stone Giant",
                "Storm Giant",
            ),
        )
    ]


def test_human_trait_prompts_collect_additional_skill_and_origin_feat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(("Perception", "Alert"))
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        choices = tuple(choices)
        prompts.append((message, choices))
        answer = next(answers)
        assert answer in choices
        return answer

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_human_traits("Human", {"Athletics"}) == ("Perception", "Alert")
    assert choose_human_traits("Dwarf", set()) == (None, None)
    assert prompts[0][0] == "Choose an additional Human skill"
    assert "Athletics" not in prompts[0][1]
    assert "Perception" in prompts[0][1]
    assert prompts[1] == (
        "Choose a Human Origin feat",
        ("Alert", "Magic Initiate", "Savage Attacker", "Skilled"),
    )


def test_tiefling_trait_prompts_collect_legacy_and_spellcasting_ability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answers = iter(("Chthonic", "charisma"))
    prompts: list[tuple[str, tuple[str, ...]]] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        choices = tuple(choices)
        prompts.append((message, choices))
        answer = next(answers)
        assert answer in choices
        return answer

    monkeypatch.setattr(wizard, "select", fake_select)

    assert choose_tiefling_traits("Tiefling") == ("Chthonic", "charisma")
    assert choose_tiefling_traits("Dwarf") == (None, None)
    assert prompts == [
        ("Choose a Fiendish Legacy", ("Abyssal", "Chthonic", "Infernal")),
        (
            "Choose a Fiendish Legacy spellcasting ability",
            ("intelligence", "wisdom", "charisma"),
        ),
    ]


def test_magic_initiate_prompts_collect_valid_spells(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = iter(("wisdom", "Bless"))

    def fake_select(message: str, choices: Sequence[str]) -> str:
        answer = next(selected)
        assert answer in choices
        return answer

    def fake_checkbox(message: str, choices: Sequence[str], count: int) -> list[str]:
        assert message == "Choose two Magic Initiate (Cleric) cantrips"
        assert count == 2
        assert "Guidance" in choices
        return ["Guidance", "Light"]

    monkeypatch.setattr(wizard, "select", fake_select)
    monkeypatch.setattr(wizard, "checkbox", fake_checkbox)

    assert choose_magic_initiate("Cleric") == MagicInitiateChoice(
        spell_list="Cleric",
        spellcasting_ability="wisdom",
        cantrips=("Guidance", "Light"),
        level_one_spell="Bless",
    )


def test_origin_feat_details_configure_background_and_repeat_magic_initiate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configured: list[MagicInitiateList] = []

    def fake_select(message: str, choices: Sequence[str]) -> str:
        assert message == "Choose a Human Magic Initiate spell list"
        assert tuple(choices) == ("Cleric", "Druid")
        return "Druid"

    def fake_magic(spell_list: MagicInitiateList) -> MagicInitiateChoice:
        configured.append(spell_list)
        if spell_list == "Wizard":
            return MagicInitiateChoice(
                spell_list="Wizard",
                spellcasting_ability="intelligence",
                cantrips=("Mage Hand", "Mending"),
                level_one_spell="Magic Missile",
            )
        return MagicInitiateChoice(
            spell_list="Druid",
            spellcasting_ability="wisdom",
            cantrips=("Druidcraft", "Guidance"),
            level_one_spell="Goodberry",
        )

    monkeypatch.setattr(wizard, "select", fake_select)
    monkeypatch.setattr(wizard, "choose_magic_initiate", fake_magic)

    choices, skilled = choose_origin_feat_details("Sage", "Magic Initiate", {"Arcana"})

    assert [choice.spell_list for choice in choices] == ["Wizard", "Druid"]
    assert configured == ["Wizard", "Druid"]
    assert skilled == set()


def test_origin_feat_details_collect_three_skilled_proficiencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_checkbox(message: str, choices: Sequence[str], count: int) -> list[str]:
        assert message == "Choose three Skilled skill or tool proficiencies"
        assert count == 3
        assert "Athletics" not in choices
        assert "Perception" in choices
        assert "Alchemist's Supplies" in choices
        return ["Perception", "Alchemist's Supplies", "Disguise Kit"]

    monkeypatch.setattr(wizard, "checkbox", fake_checkbox)

    magic, skilled = choose_origin_feat_details("Soldier", "Skilled", {"Athletics"})

    assert magic == []
    assert skilled == {"Perception", "Alchemist's Supplies", "Disguise Kit"}


def test_wizard_class_choices_collect_spellbook_before_prepared_spells(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, int]] = []
    spellbook = [
        "Detect Magic",
        "Find Familiar",
        "Mage Armor",
        "Magic Missile",
        "Shield",
        "Sleep",
    ]

    def fake_checkbox(message: str, choices: Sequence[str], count: int) -> list[str]:
        calls.append((message, count))
        if "cantrips" in message:
            return ["Fire Bolt", "Mage Hand", "Prestidigitation"]
        if "spellbook" in message:
            return spellbook
        assert tuple(choices) == tuple(sorted(spellbook))
        return ["Detect Magic", "Mage Armor", "Magic Missile", "Shield"]

    monkeypatch.setattr(wizard, "checkbox", fake_checkbox)

    choices = choose_class_choices("Wizard", {"Arcana", "History"}, ["Common", "Elvish"])

    assert choices == ClassChoices(
        cantrips={"Fire Bolt", "Mage Hand", "Prestidigitation"},
        spellbook_spells=set(spellbook),
        prepared_spells={"Detect Magic", "Mage Armor", "Magic Missile", "Shield"},
    )
    assert [count for _, count in calls] == [3, 6, 4]


def test_rogue_class_choices_limit_masteries_and_add_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_checkbox(message: str, choices: Sequence[str], count: int) -> list[str]:
        if "weapon masteries" in message:
            assert "Shortsword" in choices
            assert "Greatsword" not in choices
            return ["Dagger", "Shortsword"]
        assert message == "Choose two skills for Expertise"
        return ["Stealth", "Perception"]

    def fake_select(message: str, choices: Sequence[str]) -> str:
        assert message == "Choose the Rogue's additional language"
        assert "Elvish" not in choices
        return "Draconic"

    monkeypatch.setattr(wizard, "checkbox", fake_checkbox)
    monkeypatch.setattr(wizard, "select", fake_select)

    choices = choose_class_choices(
        "Rogue", {"Stealth", "Perception", "Sleight of Hand"}, ["Common", "Elvish"]
    )

    assert choices.expertise == {"Stealth", "Perception"}
    assert choices.additional_language == "Draconic"
