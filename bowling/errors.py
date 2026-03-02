from __future__ import annotations


class Errors:
    NOT_A_LIST           = "rolls must be a list of integers."
    OUT_OF_RANGE         = "Roll {i} value {val!r} is out of range [0, {max}]."
    NOT_ENOUGH_ROLLS     = "Not enough rolls: expected data for frame {frame}."
    MISSING_SECOND_ROLL  = "Not enough rolls: missing second roll for frame {frame}."
    FRAME_SUM            = "Frame {frame}: sum of rolls ({r1} + {r2} = {total}) exceeds {max}."
    LAST_FRAME_SHORT     = "Not enough rolls for the last frame."
    LAST_FRAME_STRIKE    = "Last frame: a strike requires two additional bonus rolls."
    LAST_FRAME_SPARE     = "Last frame: a spare requires one additional bonus roll."
    LAST_FRAME_BONUS_SUM = "Last frame bonus rolls: {r2} + {r3} = {total} exceeds {max}."
    LAST_FRAME_SUM       = "Last frame: sum {r1} + {r2} = {total} exceeds {max}."
    RULESET_IMMUTABLE    = "RuleSet est immuable."
    RULESET_MAX_PINS     = "max_pins doit être >= 1."
    RULESET_MAX_FRAMES   = "max_frames doit être >= 1."

