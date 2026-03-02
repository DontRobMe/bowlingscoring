from __future__ import annotations
from .rules import RuleSet, StandardRules


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class BowlingError(ValueError):
    """Raised when a roll sequence violates bowling rules."""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_rolls(rolls: list[int], rules: RuleSet) -> None:
    if not isinstance(rolls, list):
        raise BowlingError("rolls must be a list of integers.")

    frame = 0
    i = 0

    while frame < rules.max_frames:
        if i >= len(rolls):
            raise BowlingError(
                f"Not enough rolls: expected data for frame {frame + 1}."
            )

        roll = rolls[i]

        if not isinstance(roll, int) or not (0 <= roll <= rules.max_pins):
            raise BowlingError(
                f"Roll {i} value {roll!r} is out of range [0, {rules.max_pins}]."
            )

        if frame == rules.max_frames - 1:
            if rules.tenth_frame_extra:
                _validate_last_frame(rolls, i, rules)
            return

        if roll == rules.max_pins:
            i += 1
            frame += 1
            continue

        if i + 1 >= len(rolls):
            raise BowlingError(
                f"Not enough rolls: missing second roll for frame {frame + 1}."
            )

        second = rolls[i + 1]

        if not isinstance(second, int) or not (0 <= second <= rules.max_pins):
            raise BowlingError(
                f"Roll {i + 1} value {second!r} is out of range [0, {rules.max_pins}]."
            )

        if roll + second > rules.max_pins:
            raise BowlingError(
                f"Frame {frame + 1}: sum of rolls ({roll} + {second} = "
                f"{roll + second}) exceeds {rules.max_pins}."
            )

        i += 2
        frame += 1


def _validate_last_frame(rolls: list[int], start: int, rules: RuleSet) -> None:
    available = rolls[start:]

    if len(available) < 2:
        raise BowlingError(f"Not enough rolls for the last frame.")

    r1, r2 = available[0], available[1]

    for idx, v in enumerate(available[:3]):
        if not isinstance(v, int) or not (0 <= v <= rules.max_pins):
            raise BowlingError(
                f"Last frame roll {idx + 1} value {v!r} is out of range "
                f"[0, {rules.max_pins}]."
            )

    if r1 == rules.max_pins:
        if len(available) < 3:
            raise BowlingError(
                "Last frame: a strike requires two additional bonus rolls."
            )
        r3 = available[2]
        if r2 != rules.max_pins and r2 + r3 > rules.max_pins:
            raise BowlingError(
                f"Last frame bonus rolls: {r2} + {r3} = {r2 + r3} "
                f"exceeds {rules.max_pins}."
            )
        return

    if r1 + r2 == rules.max_pins:
        if len(available) < 3:
            raise BowlingError(
                "Last frame: a spare requires one additional bonus roll."
            )
        return

    if r1 + r2 > rules.max_pins:
        raise BowlingError(
            f"Last frame: sum {r1} + {r2} = {r1 + r2} exceeds {rules.max_pins}."
        )


# ---------------------------------------------------------------------------
# Scoring — chaque frame est délégué à la Rule correspondante
# ---------------------------------------------------------------------------

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

        if rolls[i] == rules.max_pins:
            score, consumed = rules.strike_rule(rolls, frame, i)

        elif i + 1 < len(rolls) and rolls[i] + rolls[i + 1] == rules.max_pins:
            score, consumed = rules.spare_rule(rolls, frame, i)

        else:
            score, consumed = rules.open_rule(rolls, frame, i)

        total += score
        i += consumed

    return total
