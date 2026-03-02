import pytest
from bowling import (
    BowlingError,
    RuleSet,
    calculate_bowling_score,
    get_scoreboard,
    StandardRules,
    NinePinRules,
    FiveFrameRules,
    NoBonus,
    DoubleSpareRules,
)
from bowling.rules import (
    strike_bonus_rule,
    strike_no_bonus_rule,
    spare_bonus_rule,
    spare_double_bonus_rule,
    spare_no_bonus_rule,
    open_frame_rule,
)


def rolls_of(pins: int, count: int) -> list[int]:
    return [pins] * count


# =============================================================================
# TESTS UNITAIRES
# Chaque test cible une seule fonction, un seul comportement.
# =============================================================================


class TestOpenFrame:
    def test_single_open_frame(self):
        assert calculate_bowling_score([3, 6] + rolls_of(0, 18)) == 9

    def test_all_ones(self):
        assert calculate_bowling_score(rolls_of(1, 20)) == 20

    def test_gutter_game(self):
        assert calculate_bowling_score(rolls_of(0, 20)) == 0

    def test_all_nines(self):
        assert calculate_bowling_score([9, 0] * 10) == 90

    def test_mixed_open_frames(self):
        rolls = [3, 4, 2, 6, 1, 7, 0, 5, 4, 3, 2, 5, 1, 6, 3, 4, 2, 5, 1, 4]
        assert calculate_bowling_score(rolls) == sum(rolls)


class TestSpare:
    def test_spare_followed_by_7(self):
        assert calculate_bowling_score([5, 5, 7, 0] + rolls_of(0, 16)) == 24

    def test_spare_bonus_uses_only_next_roll(self):
        assert calculate_bowling_score([0, 10, 3, 4] + rolls_of(0, 16)) == 20

    def test_spare_in_first_frame_only(self):
        assert calculate_bowling_score([7, 3, 0, 0] + rolls_of(0, 16)) == 10

    def test_all_spare_game(self):
        assert calculate_bowling_score([5, 5] * 10 + [5]) == 150

    def test_spare_with_zero_bonus(self):
        assert calculate_bowling_score([4, 6, 0, 0] + rolls_of(0, 16)) == 10


class TestStrike:
    def test_strike_followed_by_4_and_5(self):
        assert calculate_bowling_score([10, 4, 5] + rolls_of(0, 16)) == 28

    def test_strike_bonus_uses_next_two_rolls(self):
        assert calculate_bowling_score([10, 3, 6] + rolls_of(0, 16)) == 28

    def test_strike_followed_by_gutter(self):
        assert calculate_bowling_score([10, 0, 0] + rolls_of(0, 16)) == 10

    def test_turkey(self):
        assert calculate_bowling_score([10, 10, 10, 0, 0] + rolls_of(0, 12)) == 60

    def test_six_consecutive_strikes(self):
        assert calculate_bowling_score([10] * 6 + [0, 0] * 4) == 150

    def test_strike_then_spare(self):
        assert calculate_bowling_score([10, 5, 5, 0, 0] + rolls_of(0, 14)) == 30


class TestTenthFrame:
    def test_open_tenth(self):
        assert calculate_bowling_score(rolls_of(0, 18) + [3, 4]) == 7

    def test_spare_in_tenth(self):
        assert calculate_bowling_score(rolls_of(0, 18) + [5, 5, 7]) == 17

    def test_spare_with_zero_bonus_in_tenth(self):
        assert calculate_bowling_score(rolls_of(0, 18) + [5, 5, 0]) == 10

    def test_strike_in_tenth(self):
        assert calculate_bowling_score(rolls_of(0, 18) + [10, 3, 6]) == 19

    def test_three_strikes_in_tenth(self):
        assert calculate_bowling_score(rolls_of(0, 18) + [10, 10, 10]) == 30

    def test_strike_then_spare_in_tenth(self):
        assert calculate_bowling_score(rolls_of(0, 18) + [10, 5, 5]) == 20


class TestFullGames:
    def test_perfect_game(self):
        assert calculate_bowling_score([10] * 12) == 300

    def test_gutter_game(self):
        assert calculate_bowling_score([0] * 20) == 0

    def test_all_spare_150(self):
        assert calculate_bowling_score([5, 5] * 10 + [5]) == 150

    def test_mixed_game_187(self):
        assert calculate_bowling_score([10, 9, 1, 5, 5, 7, 2, 10, 10, 10, 9, 0, 8, 2, 9, 1, 10]) == 187

    def test_all_ones(self):
        assert calculate_bowling_score([1] * 20) == 20


class TestValidationOutOfRange:
    def test_negative_roll(self):
        with pytest.raises(BowlingError, match="out of range"):
            calculate_bowling_score([-1] + rolls_of(0, 19))

    def test_roll_above_10(self):
        with pytest.raises(BowlingError, match="out of range"):
            calculate_bowling_score([11] + rolls_of(0, 19))

    def test_minus_100(self):
        with pytest.raises(BowlingError, match="out of range"):
            calculate_bowling_score([-100] + rolls_of(0, 19))

    def test_second_roll_negative(self):
        with pytest.raises(BowlingError, match="out of range"):
            calculate_bowling_score([3, -1] + rolls_of(0, 18))

    def test_second_roll_above_10(self):
        with pytest.raises(BowlingError, match="out of range"):
            calculate_bowling_score([3, 11] + rolls_of(0, 18))


class TestValidationFrameSum:
    def test_sum_11_rejected(self):
        with pytest.raises(BowlingError, match="sum of rolls"):
            calculate_bowling_score([6, 5] + rolls_of(0, 18))

    def test_sum_10_is_valid(self):
        assert calculate_bowling_score([5, 5] * 10 + [0]) == 145

    def test_sum_9_is_valid(self):
        assert calculate_bowling_score([4, 5] + rolls_of(0, 18)) == 9

    def test_sum_violation_in_middle_frame(self):
        with pytest.raises(BowlingError, match="sum of rolls"):
            calculate_bowling_score(rolls_of(0, 8) + [7, 4] + rolls_of(0, 10))


class TestValidationTypes:
    def test_string_rejected(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score("10 10 10")  # type: ignore[arg-type]

    def test_none_rejected(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score(None)  # type: ignore[arg-type]

    def test_float_in_list_rejected(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score([5.0, 5] + rolls_of(0, 18))  # type: ignore[list-item]

    def test_string_in_list_rejected(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score(["X"] + rolls_of(0, 19))  # type: ignore[list-item]


class TestValidationSequence:
    def test_empty_list(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score([])

    def test_only_one_frame(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score([5, 3])

    def test_nine_frames_only(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score(rolls_of(0, 18))

    def test_missing_second_roll(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score([3])


class TestValidationTenthFrame:
    def test_spare_without_bonus(self):
        with pytest.raises(BowlingError, match="spare requires one additional"):
            calculate_bowling_score(rolls_of(0, 18) + [5, 5])

    def test_strike_with_one_bonus_only(self):
        with pytest.raises(BowlingError, match="strike requires two additional"):
            calculate_bowling_score(rolls_of(0, 18) + [10, 3])

    def test_strike_with_no_bonus(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score(rolls_of(0, 18) + [10])

    def test_bonus_sum_exceeds_pins(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score(rolls_of(0, 18) + [10, 3, 8])

    def test_open_frame_sum_exceeds_pins(self):
        with pytest.raises(BowlingError):
            calculate_bowling_score(rolls_of(0, 18) + [6, 5])


class TestRulesStandard:
    def test_default_equals_explicit(self):
        rolls = [10] * 12
        assert calculate_bowling_score(rolls) == calculate_bowling_score(rolls, rules=StandardRules)

    def test_perfect_game(self):
        assert calculate_bowling_score([10] * 12, rules=StandardRules) == 300

    def test_gutter_game(self):
        assert calculate_bowling_score([0] * 20, rules=StandardRules) == 0

    def test_all_spare(self):
        assert calculate_bowling_score([5, 5] * 10 + [5], rules=StandardRules) == 150

    def test_mixed_187(self):
        assert calculate_bowling_score([10, 9, 1, 5, 5, 7, 2, 10, 10, 10, 9, 0, 8, 2, 9, 1, 10], rules=StandardRules) == 187


class TestRulesFiveFrame:
    def test_perfect_game(self):
        assert calculate_bowling_score([10] * 7, rules=FiveFrameRules) == 150

    def test_gutter_game(self):
        assert calculate_bowling_score([0] * 10, rules=FiveFrameRules) == 0

    def test_all_spare(self):
        assert calculate_bowling_score([5, 5] * 5 + [5], rules=FiveFrameRules) == 75

    def test_open_frames(self):
        assert calculate_bowling_score([3, 4] * 5, rules=FiveFrameRules) == 35

    def test_strike_then_open(self):
        assert calculate_bowling_score([10, 4, 5] + rolls_of(0, 6), rules=FiveFrameRules) == 28


class TestRulesNinePin:
    def test_open_frames(self):
        assert calculate_bowling_score([4, 4] * 9, rules=NinePinRules) == 72

    def test_gutter_game(self):
        assert calculate_bowling_score([0] * 18, rules=NinePinRules) == 0

    def test_all_ones(self):
        assert calculate_bowling_score([1] * 18, rules=NinePinRules) == 18

    def test_strike_score(self):
        rolls = [9, 4, 4] + rolls_of(0, 14)
        assert calculate_bowling_score(rolls, rules=NinePinRules) == 26

    def test_roll_of_10_rejected(self):
        with pytest.raises(BowlingError, match="out of range"):
            calculate_bowling_score([10] + rolls_of(0, 16), rules=NinePinRules)

    def test_roll_of_9_accepted(self):
        assert calculate_bowling_score([9] + rolls_of(0, 16), rules=NinePinRules) >= 9


class TestRulesNoBonus:
    def test_strike_counts_as_pins_only(self):
        assert calculate_bowling_score([10] + rolls_of(0, 18), rules=NoBonus) == 10

    def test_spare_counts_as_pins_only(self):
        assert calculate_bowling_score([5, 5, 7, 0] + rolls_of(0, 16), rules=NoBonus) == 17

    def test_perfect_game_is_100(self):
        assert calculate_bowling_score([10] * 12, rules=NoBonus) == 100

    def test_all_spare_is_100(self):
        assert calculate_bowling_score([5, 5] * 10 + [5], rules=NoBonus) == 100

    def test_open_frame_unchanged(self):
        assert calculate_bowling_score([3, 4] + rolls_of(0, 18), rules=NoBonus) == 7


class TestRulesDoubleSpare:
    def test_bonus_is_doubled(self):
        rolls = [5, 5, 7, 0] + rolls_of(0, 16)
        assert calculate_bowling_score(rolls, rules=DoubleSpareRules) == calculate_bowling_score(rolls, rules=StandardRules) + 7

    def test_all_spare_higher_than_standard(self):
        rolls = [5, 5] * 10 + [5]
        assert calculate_bowling_score(rolls, rules=DoubleSpareRules) > 150

    def test_strike_unaffected(self):
        rolls = [10, 4, 5] + rolls_of(0, 16)
        assert calculate_bowling_score(rolls, rules=DoubleSpareRules) == calculate_bowling_score(rolls, rules=StandardRules)

    def test_open_frame_unaffected(self):
        rolls = [3, 4] + rolls_of(0, 18)
        assert calculate_bowling_score(rolls, rules=DoubleSpareRules) == calculate_bowling_score(rolls, rules=StandardRules)


class TestRulesCustom:
    def test_3_frames_no_bonus(self):
        custom = RuleSet(
            name="T", max_pins=10, max_frames=3,
            strike_rule=strike_no_bonus_rule,
            spare_rule=spare_no_bonus_rule,
            tenth_frame_extra=False,
        )
        assert calculate_bowling_score([5, 3, 4, 4, 10], rules=custom) == 26

    def test_custom_max_pins_6(self):
        custom = RuleSet(name="6P", max_pins=6, max_frames=5, tenth_frame_extra=False)
        assert calculate_bowling_score([6, 3, 2] + rolls_of(0, 7), rules=custom) == 20

    def test_ruleset_is_frozen(self):
        with pytest.raises(AttributeError):
            StandardRules.max_pins = 99  # type: ignore[misc]

    def test_ruleset_str(self):
        assert "Standard" in str(StandardRules)
        assert "10" in str(StandardRules)

    def test_validation_with_custom_max_pins(self):
        custom = RuleSet(name="C7", max_pins=7, max_frames=5, tenth_frame_extra=False)
        with pytest.raises(BowlingError, match="sum of rolls"):
            calculate_bowling_score([5, 3] + rolls_of(0, 8), rules=custom)

    def test_custom_strike_rule_function(self):
        custom = RuleSet(
            name="TripleStrike", max_pins=10, max_frames=10,
            strike_rule=lambda rolls, frame, i: (30, 1),
            tenth_frame_extra=False,
        )
        assert calculate_bowling_score([10] + rolls_of(0, 18), rules=custom) == 30

    def test_custom_spare_rule_function(self):
        custom = RuleSet(
            name="FlatSpare", max_pins=10, max_frames=10,
            spare_rule=lambda rolls, frame, i: (5, 2),
            tenth_frame_extra=False,
        )
        assert calculate_bowling_score([5, 5] + rolls_of(0, 18), rules=custom) == 5

