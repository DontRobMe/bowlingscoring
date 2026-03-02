import pytest
from bowling import (
    BowlingError,
    RuleSet,
    get_scoreboard,
    StandardRules,
    NinePinRules,
    FiveFrameRules,
    NoBonus,
    DoubleSpareRules,
    strike_no_bonus_rule,
    spare_no_bonus_rule,
)


def rolls_of(pins: int, count: int) -> list[int]:
    return [pins] * count


# =============================================================================
# TESTS D'INTÉGRATION
# Chaque test vérifie la chaîne complète : validation → scoring → rendu ASCII.
# =============================================================================


class TestScoreboardAsciiStructure:
    def test_returns_string(self):
        assert isinstance(get_scoreboard([0] * 20), str)

    def test_contains_box_drawing_chars(self):
        result = get_scoreboard([0] * 20)
        for char in ["┌", "┐", "└", "┘", "│"]:
            assert char in result

    def test_standard_has_seven_lines(self):
        result = get_scoreboard([0] * 20)
        assert len(result.split("\n")) == 7

    def test_standard_has_ten_frame_numbers(self):
        result = get_scoreboard([0] * 20)
        header = result.split("\n")[1]
        for i in range(1, 11):
            assert str(i) in header

    def test_invalid_rolls_raises_error(self):
        with pytest.raises(BowlingError):
            get_scoreboard([-1] + [0] * 19)


class TestScoreboardFrameSymbols:
    def test_strike_shows_X(self):
        assert "X" in get_scoreboard([10] * 12)

    def test_spare_shows_slash(self):
        assert "/" in get_scoreboard([5, 5] * 10 + [5])

    def test_zero_shows_dash(self):
        assert "-" in get_scoreboard([0] * 20)

    def test_open_frame_shows_digits(self):
        result = get_scoreboard([3, 4] + rolls_of(0, 18))
        assert "3" in result
        assert "4" in result

    def test_three_strikes_in_tenth(self):
        result = get_scoreboard(rolls_of(0, 18) + [10, 10, 10])
        assert result.split("\n")[3].count("X") == 3

    def test_no_X_in_gutter_game(self):
        assert "X" not in get_scoreboard([0] * 20)

    def test_no_slash_in_gutter_game(self):
        assert "/" not in get_scoreboard([0] * 20)


class TestScoreboardCumulativeDisplay:
    def test_perfect_game_shows_300(self):
        assert "300" in get_scoreboard([10] * 12)

    def test_perfect_game_intermediate_scores(self):
        result = get_scoreboard([10] * 12)
        for score in ["30", "60", "90", "120", "150", "180", "210", "240", "270", "300"]:
            assert score in result

    def test_all_spare_shows_150(self):
        assert "150" in get_scoreboard([5, 5] * 10 + [5])

    def test_mixed_game_shows_187(self):
        assert "187" in get_scoreboard([10, 9, 1, 5, 5, 7, 2, 10, 10, 10, 9, 0, 8, 2, 9, 1, 10])

    def test_gutter_game_score_line_is_zeros(self):
        score_line = get_scoreboard([0] * 20).split("\n")[5]
        assert all(c in "│ 0" for c in score_line)

    def test_strike_then_open_cumulative(self):
        result = get_scoreboard([10, 4, 5] + rolls_of(0, 16))
        assert "19" in result
        assert "28" in result


class TestScoreboardFiveFrameLayout:
    def test_variant_name_in_output(self):
        assert "5-Frame" in get_scoreboard([0] * 10, rules=FiveFrameRules)

    def test_has_five_frame_columns(self):
        header = get_scoreboard([0] * 10, rules=FiveFrameRules).split("\n")[2]
        assert "5" in header

    def test_no_sixth_frame_column(self):
        header = get_scoreboard([0] * 10, rules=FiveFrameRules).split("\n")[2]
        assert "6" not in header

    def test_perfect_game_shows_150(self):
        assert "150" in get_scoreboard([10] * 7, rules=FiveFrameRules)

    def test_table_has_eight_lines(self):
        assert len(get_scoreboard([0] * 10, rules=FiveFrameRules).split("\n")) == 8


class TestScoreboardNinePinLayout:
    def test_variant_name_in_output(self):
        assert "9-Pin" in get_scoreboard([0] * 18, rules=NinePinRules)

    def test_has_nine_frame_columns(self):
        header = get_scoreboard([0] * 18, rules=NinePinRules).split("\n")[2]
        assert "9" in header

    def test_no_tenth_frame_column(self):
        header = get_scoreboard([0] * 18, rules=NinePinRules).split("\n")[2]
        assert "10" not in header

    def test_strike_at_9_pins_shows_X(self):
        assert "X" in get_scoreboard([9] + rolls_of(0, 16), rules=NinePinRules)

    def test_table_has_eight_lines(self):
        assert len(get_scoreboard([0] * 18, rules=NinePinRules).split("\n")) == 8


class TestScoreboardNoBonusDisplay:
    def test_variant_name_in_output(self):
        assert "No-Bonus" in get_scoreboard([0] * 20, rules=NoBonus)

    def test_perfect_game_shows_100(self):
        assert "100" in get_scoreboard([10] * 12, rules=NoBonus)

    def test_perfect_game_does_not_show_300(self):
        assert "300" not in get_scoreboard([10] * 12, rules=NoBonus)

    def test_all_spare_shows_100(self):
        assert "100" in get_scoreboard([5, 5] * 10 + [5], rules=NoBonus)

    def test_strike_still_shows_X(self):
        assert "X" in get_scoreboard([10] + rolls_of(0, 18), rules=NoBonus)


class TestScoreboardDoubleSpareDisplay:
    def test_variant_name_in_output(self):
        assert "Double-Spare" in get_scoreboard([0] * 20, rules=DoubleSpareRules)

    def test_all_spare_score_above_150(self):
        assert "150" not in get_scoreboard([5, 5] * 10 + [5], rules=DoubleSpareRules)

    def test_spare_symbol_still_shows(self):
        assert "/" in get_scoreboard([5, 5] * 10 + [5], rules=DoubleSpareRules)


class TestScoreboardCustomRuleSetLayout:
    def test_custom_variant_name_in_output(self):
        custom = RuleSet(name="MaVariante", max_pins=10, max_frames=3, tenth_frame_extra=False)
        assert "MaVariante" in get_scoreboard([3, 4, 2, 5, 1, 6], rules=custom)

    def test_standard_has_no_variant_prefix(self):
        assert "Variante" not in get_scoreboard([0] * 20, rules=StandardRules)

    def test_custom_3_frames_header(self):
        custom = RuleSet(name="3F", max_pins=10, max_frames=3, tenth_frame_extra=False)
        header = get_scoreboard([3, 4, 2, 5, 1, 6], rules=custom).split("\n")[2]
        assert "3" in header
        assert "4" not in header

