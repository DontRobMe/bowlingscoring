from __future__ import annotations
from .rules import RuleSet, StandardRules
from .scoring import _validate_rolls, calculate_bowling_score


def _frame_symbols(
    rolls: list[int], start: int, frame: int, rules: RuleSet
) -> tuple[list[str], int]:
    i = start
    symbols: list[str] = []
    is_last = frame == rules.max_frames - 1

    def fmt(v: int) -> str:
        return "-" if v == 0 else str(v)

    if is_last and rules.tenth_frame_extra:
        r1 = rolls[i]
        r2 = rolls[i + 1] if i + 1 < len(rolls) else 0

        if r1 == rules.max_pins:
            symbols.append("X")
            if r2 == rules.max_pins:
                symbols.append("X")
            else:
                symbols.append(fmt(r2))
            r3 = rolls[i + 2] if i + 2 < len(rolls) else 0
            if r3 == rules.max_pins:
                symbols.append("X")
            elif r2 != rules.max_pins and r2 + r3 == rules.max_pins:
                symbols.append("/")
            else:
                symbols.append(fmt(r3))
            i += 3
        elif r1 + r2 == rules.max_pins:
            symbols.append(fmt(r1))
            symbols.append("/")
            r3 = rolls[i + 2] if i + 2 < len(rolls) else 0
            symbols.append("X" if r3 == rules.max_pins else fmt(r3))
            i += 3
        else:
            symbols.append(fmt(r1))
            symbols.append(fmt(r2))
            i += 2
    else:
        r1 = rolls[i]
        if r1 == rules.max_pins:
            symbols = [" ", "X"]
            i += 1
        else:
            r2 = rolls[i + 1] if i + 1 < len(rolls) else 0
            if r1 + r2 == rules.max_pins:
                symbols = [fmt(r1), "/"]
            else:
                symbols = [fmt(r1), fmt(r2)]
            i += 2

    return symbols, i


def get_scoreboard(rolls: list[int], rules: RuleSet = StandardRules) -> str:
    _validate_rolls(rolls, rules)

    frame_symbols: list[list[str]] = []
    frame_scores: list[int] = []

    roll_idx = 0
    for frame in range(rules.max_frames):
        if roll_idx >= len(rolls):
            break
        syms, roll_idx = _frame_symbols(rolls, roll_idx, frame, rules)
        frame_symbols.append(syms)
        frame_scores.append(_score_up_to_frame(rolls, frame + 1, rules))

    # ------------------------------------------------------------------
    # Build the ASCII table
    # ------------------------------------------------------------------
    num_frames = len(frame_symbols)
    last_idx = rules.max_frames - 1
    normal_w = 7
    last_w = 9

    def h_line(left: str, mid: str, right: str, fill: str) -> str:
        parts = []
        for f in range(num_frames):
            w = last_w if (f == last_idx and rules.tenth_frame_extra) else normal_w
            parts.append(fill * w)
        return left + mid.join(parts) + right

    top    = h_line("┌", "┬", "┐", "─")
    sep    = h_line("├", "┼", "┤", "─")
    bottom = h_line("└", "┴", "┘", "─")

    def make_row(cells: list[str]) -> str:
        return "│" + "│".join(cells) + "│"

    header_cells = [
        str(f + 1).center(last_w if (f == last_idx and rules.tenth_frame_extra) else normal_w)
        for f in range(num_frames)
    ]
    roll_cells = [
        " ".join(syms).center(last_w if (f == last_idx and rules.tenth_frame_extra) else normal_w)
        for f, syms in enumerate(frame_symbols)
    ]
    score_cells = [
        str(sc).center(last_w if (f == last_idx and rules.tenth_frame_extra) else normal_w)
        for f, sc in enumerate(frame_scores)
    ]

    lines = []
    if rules.name != "Standard":
        title = f"  Variante : {rules}"
        lines.append(title)

    lines += [top, make_row(header_cells), sep, make_row(roll_cells), sep, make_row(score_cells), bottom]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helper – partial score up to a given frame number
# ---------------------------------------------------------------------------

def _score_up_to_frame(rolls: list[int], up_to: int, rules: RuleSet = StandardRules) -> int:
    total = 0
    i = 0
    for frame in range(up_to):
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

