import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from pc_wizard.models import AbilityGenerationMethod, AbilityScoreGeneration, AbilityScores
from pc_wizard.rules import (
    ABILITIES,
    eligible_abilities_for_increase,
)


@st.composite
def point_buy_values(draw: st.DrawFn) -> list[int]:
    base = draw(
        st.sampled_from(
            (
                (15, 15, 15, 8, 8, 8),
                (15, 15, 14, 10, 8, 8),
                (15, 14, 13, 12, 10, 8),
            )
        )
    )
    return list(draw(st.permutations(base)))


def ability_scores(values: list[int]) -> AbilityScores:
    return AbilityScores.model_validate(dict(zip(ABILITIES, values, strict=True)))


@given(st.integers(min_value=3, max_value=20))
def test_ability_modifiers_follow_the_score_formula(score: int) -> None:
    scores = ability_scores([score] * len(ABILITIES))

    assert all(scores.modifier(ability) == (score - 10) // 2 for ability in ABILITIES)


@given(point_buy_values())
def test_point_buy_accepts_exactly_budgeted_scores(values: list[int]) -> None:
    generation = AbilityScoreGeneration(
        method=AbilityGenerationMethod.POINT_BUY,
        scores=ability_scores(values),
    )

    assert generation.scores.ordered_values() == tuple(values)


@given(point_buy_values(), st.integers(min_value=0, max_value=5))
def test_point_buy_rejects_scores_that_miss_the_budget(values: list[int], index: int) -> None:
    values[index] = 8 if values[index] != 8 else 9

    with pytest.raises(ValidationError, match="point-buy scores must cost exactly 27 points"):
        AbilityScoreGeneration(
            method=AbilityGenerationMethod.POINT_BUY,
            scores=ability_scores(values),
        )


@given(
    st.dictionaries(
        st.sampled_from(ABILITIES),
        st.integers(min_value=3, max_value=20),
        min_size=len(ABILITIES),
        max_size=len(ABILITIES),
    ),
    st.lists(st.sampled_from(ABILITIES), min_size=1, max_size=len(ABILITIES), unique=True),
    st.integers(min_value=1, max_value=20),
)
def test_eligible_abilities_match_the_score_cap(
    scores: dict[str, int], abilities: list[str], amount: int
) -> None:
    eligible = eligible_abilities_for_increase(scores, abilities, amount)
    expected = tuple(ability for ability in abilities if scores[ability] + amount <= 20)

    assert eligible == expected
