from __future__ import annotations
from typing import Callable, Tuple


# ---------------------------------------------------------------------------
# Type de base
# ---------------------------------------------------------------------------

Rule = Callable[[list[int], int, int], Tuple[int, int]]
"""
Une Rule est une fonction qui calcule le score d'un frame et l'avancement
dans la liste de lancers.

Signature : rule(rolls, frame_index, roll_index) -> (frame_score, rolls_consumed)
"""

ValidationRule = Callable[[list[int]], None]
"""
Une ValidationRule lève une BowlingError si la séquence est invalide.
Signature : rule(rolls) -> None
"""


# ---------------------------------------------------------------------------
# Règles de scoring
# ---------------------------------------------------------------------------

def strike_bonus_rule(rolls: list[int], frame: int, i: int) -> Tuple[int, int]:
    bonus = sum(rolls[i + 1: i + 3])
    return (10 + bonus, 1)


def strike_no_bonus_rule(rolls: list[int], frame: int, i: int) -> Tuple[int, int]:
    return (10, 1)


def spare_bonus_rule(rolls: list[int], frame: int, i: int) -> Tuple[int, int]:
    bonus = rolls[i + 2] if i + 2 < len(rolls) else 0
    return (10 + bonus, 2)


def spare_double_bonus_rule(rolls: list[int], frame: int, i: int) -> Tuple[int, int]:
    bonus = rolls[i + 2] if i + 2 < len(rolls) else 0
    return (10 + bonus * 2, 2)


def spare_no_bonus_rule(rolls: list[int], frame: int, i: int) -> Tuple[int, int]:
    return (10, 2)


def open_frame_rule(rolls: list[int], frame: int, i: int) -> Tuple[int, int]:
    return (rolls[i] + (rolls[i + 1] if i + 1 < len(rolls) else 0), 2)


# ---------------------------------------------------------------------------
# Conteneur de règles
# ---------------------------------------------------------------------------

class RuleSet:

    def __init__(
        self,
        name: str,
        max_pins: int,
        max_frames: int,
        strike_rule: Rule = strike_bonus_rule,
        spare_rule: Rule = spare_bonus_rule,
        open_rule: Rule = open_frame_rule,
        tenth_frame_extra: bool = True,
    ) -> None:
        self.name = name
        self.max_pins = max_pins
        self.max_frames = max_frames
        self.strike_rule = strike_rule
        self.spare_rule = spare_rule
        self.open_rule = open_rule
        self.tenth_frame_extra = tenth_frame_extra

    def __str__(self) -> str:
        return (
            f"[{self.name}] "
            f"{self.max_frames} frames · "
            f"{self.max_pins} quilles · "
            f"strike={self.strike_rule.__name__} · "
            f"spare={self.spare_rule.__name__}"
        )

    def __setattr__(self, key: str, value: object) -> None:
        if hasattr(self, "_frozen"):
            raise AttributeError("RuleSet est immuable.")
        super().__setattr__(key, value)

    def _freeze(self) -> "RuleSet":
        super().__setattr__("_frozen", True)
        return self


# ---------------------------------------------------------------------------
# Règles prédéfinies
# ---------------------------------------------------------------------------

StandardRules = RuleSet(
    name="Standard",
    max_pins=10,
    max_frames=10,
)._freeze()

NinePinRules = RuleSet(
    name="9-Pin",
    max_pins=9,
    max_frames=9,
    tenth_frame_extra=False,
)._freeze()

FiveFrameRules = RuleSet(
    name="5-Frame",
    max_pins=10,
    max_frames=5,
)._freeze()

NoBonus = RuleSet(
    name="No-Bonus",
    max_pins=10,
    max_frames=10,
    strike_rule=strike_no_bonus_rule,
    spare_rule=spare_no_bonus_rule,
    tenth_frame_extra=False,
)._freeze()

DoubleSpareRules = RuleSet(
    name="Double-Spare",
    max_pins=10,
    max_frames=10,
    spare_rule=spare_double_bonus_rule,
)._freeze()
