import random

from pc_wizard.wizard import generated_scores


def test_standard_array() -> None:
    assert generated_scores("Standard array") == [15, 14, 13, 12, 10, 8]


def test_random_scores_are_valid() -> None:
    scores = generated_scores("Roll 4d6 drop lowest", random.Random(42))
    assert len(scores) == 6
    assert all(3 <= score <= 18 for score in scores)
