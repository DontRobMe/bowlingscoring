from __future__ import annotations
from .rules import RuleSet, StandardRules
from .errors import Errors


class BowlingError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_rolls(rolls: list[int], rules: RuleSet) -> None:
    if not isinstance(rolls, list):
        raise BowlingError(Errors.NOT_A_LIST)

    frame = 0
    i = 0

    while frame < rules.max_frames:
        if i >= len(rolls):
            raise BowlingError(Errors.NOT_ENOUGH_ROLLS.format(frame=frame + 1))

        roll = rolls[i]

        if not isinstance(roll, int) or not (0 <= roll <= rules.max_pins):
            raise BowlingError(Errors.OUT_OF_RANGE.format(i=i, val=roll, max=rules.max_pins))

        if frame == rules.max_frames - 1:
            if rules.tenth_frame_extra:
                _validate_last_frame(rolls, i, rules)
            return

        if roll == rules.max_pins:
            i += 1
            frame += 1
            continue

        if i + 1 >= len(rolls):
            raise BowlingError(Errors.MISSING_SECOND_ROLL.format(frame=frame + 1))

        second = rolls[i + 1]

        if not isinstance(second, int) or not (0 <= second <= rules.max_pins):
            raise BowlingError(Errors.OUT_OF_RANGE.format(i=i + 1, val=second, max=rules.max_pins))

        if roll + second > rules.max_pins:
            raise BowlingError(
                Errors.FRAME_SUM.format(frame=frame + 1, r1=roll, r2=second, total=roll + second, max=rules.max_pins)
            )

        i += 2
        frame += 1


def _validate_last_frame(rolls: list[int], start: int, rules: RuleSet) -> None:
    available = rolls[start:]

    if len(available) < 2:
        raise BowlingError(Errors.LAST_FRAME_SHORT)

    r1, r2 = available[0], available[1]

    for idx, v in enumerate(available[:3]):
        if not isinstance(v, int) or not (0 <= v <= rules.max_pins):
            raise BowlingError(Errors.OUT_OF_RANGE.format(i=idx, val=v, max=rules.max_pins))

    if r1 == rules.max_pins:
        if len(available) < 3:
            raise BowlingError(Errors.LAST_FRAME_STRIKE)
        r3 = available[2]
        if r2 != rules.max_pins and r2 + r3 > rules.max_pins:
            raise BowlingError(Errors.LAST_FRAME_BONUS_SUM.format(r2=r2, r3=r3, total=r2 + r3, max=rules.max_pins))
        return

    if r1 + r2 == rules.max_pins:
        if len(available) < 3:
            raise BowlingError(Errors.LAST_FRAME_SPARE)
        return

    if r1 + r2 > rules.max_pins:
        raise BowlingError(Errors.LAST_FRAME_SUM.format(r1=r1, r2=r2, total=r1 + r2, max=rules.max_pins))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_frame(rolls: list[int], frame: int, i: int, rules: RuleSet) -> tuple[int, int]:
    if rolls[i] == rules.max_pins:
        return rules.strike_rule(rolls, frame, i)
    if i + 1 < len(rolls) and rolls[i] + rolls[i + 1] == rules.max_pins:
        return rules.spare_rule(rolls, frame, i)
    return rules.open_rule(rolls, frame, i)


def calculate_bowling_score(
    rolls: list[int],
    rules: RuleSet = StandardRules,
) -> int:
    _validate_rolls(rolls, rules)

    total = 0
    i = 0

    for frame in range(rules.max_frames):
        if i >= len(rolls):
            break
        score, consumed = _score_frame(rolls, frame, i, rules)
        total += score
        i += consumed

    return total
