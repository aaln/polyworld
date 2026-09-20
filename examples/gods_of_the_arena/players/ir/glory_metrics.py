"""GOTA tournament Score/Glory, separate from the live league's binary Elo.

Source: tools/tournaments.nim::gameValues at repository commit1d7eb72.
Compute over all appearances (including losses and draws), never just winners.
"""
from collections import defaultdict
from fractions import Fraction

TICKS_PER_MINUTE = 1440
PENALTY_PER_MINUTE = 100


def seat_values(result):
    """Return exact fractional values; missing XP is an error, not zero."""
    if type(result.get("ticks")) is not int or not 0 <= result["ticks"] <= 28800:
        raise ValueError("Invalid full-game tick count")
    scores, xp = result.get("scores"), result.get("total_xp")
    if not isinstance(scores, list) or len(scores) != 10:
        raise ValueError("Ten seat scores are required")
    if not isinstance(xp, list) or len(xp) != 10:
        raise ValueError("Ten lifetime-XP values are required")
    outcome = result.get("outcome")
    if outcome not in {"RedTeam", "BlueTeam", "time_limit"}:
        raise ValueError("Unknown game outcome")
    penalty = Fraction(PENALTY_PER_MINUTE * result["ticks"], TICKS_PER_MINUTE)
    rows = []
    for slot in range(10):
        expected = int((outcome == "RedTeam" and slot < 5) or
                       (outcome == "BlueTeam" and slot >= 5))
        if type(scores[slot]) is not int or scores[slot] != expected:
            raise ValueError("Binary seat score disagrees with team outcome")
        if type(xp[slot]) is not int or xp[slot] < 0:
            raise ValueError("Lifetime XP must be a nonnegative integer")
        score = Fraction(xp[slot]) - penalty
        rows.append({"win": scores[slot], "xp": xp[slot], "time_penalty": penalty,
                     "score": score, "glory": score * scores[slot]})
    return rows


def policy_values(result, seats):
    """Average repeated policy seats within a game, as the mono ladder does."""
    if len(seats) != 10:
        raise ValueError("Ten policy seats are required")
    grouped = defaultdict(list)
    for policy, values in zip(seats, seat_values(result)):
        grouped[policy].append(values)
    return {policy: {metric: sum(row[metric] for row in rows) / len(rows)
                     for metric in rows[0]} for policy, rows in grouped.items()}


def json_values(values):
    return {name: float(value) if isinstance(value, Fraction) else value
            for name, value in values.items()}
