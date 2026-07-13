import random
from collections.abc import Sequence
from typing import cast

import pytest

from pc_wizard import wizard
from pc_wizard.models import AbilityGenerationMethod
from pc_wizard.rules import POINT_BUY_BUDGET, eligible_abilities_for_increase, point_buy_cost
from pc_wizard.wizard import (
    apply_background_increases,
    choose_species_size,
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
