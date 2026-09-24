"""Embed the observable, legal-masked v58 draft head in a BASIC policy.

This exports a draft-only hybrid diagnostic. The unchanged battle shell is not
fully neural and must not be described or promoted as such without evidence.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

SCHEMA = "gota-v58-draft-observable-32-v1"


def draft_routine(weights: np.ndarray) -> str:
    if weights.shape != (33, 10) or not np.isfinite(weights).all():
        raise ValueError("expected a finite 33x10 draft head")
    lines = [
        "sub chooseHero()",
        "  if draftTurnId <> selfId then",
        "    exit sub",
        "  end if",
        "  for draftClass = 0 to 9",
        "    draftF(draftClass) = heroAvailable(draftClass)",
        "    draftF(10 + draftClass) = 0",
        "    draftF(20 + draftClass) = 0",
        "  next draftClass",
        "  draftAllyCount = 0",
        "  draftEnemyCount = 0",
        "  for draftPlayer = 0 to draftPlayerCount() - 1",
        "    draftPicked = draftedClass(draftPlayerId(draftPlayer))",
        "    if draftPicked >= 0 then",
        "      if draftPlayerTeam(draftPlayer) = selfTeam then",
        "        draftF(10 + draftPicked) = 1",
        "        draftAllyCount = draftAllyCount + 1",
        "      else",
        "        draftF(20 + draftPicked) = 1",
        "        draftEnemyCount = draftEnemyCount + 1",
        "      end if",
        "    end if",
        "  next draftPlayer",
        "  draftF(30) = draftAllyCount / 5",
        "  draftF(31) = draftEnemyCount / 5",
        "  draftBestClass = -1",
        "  draftBestScore = -2147483647",
    ]
    for class_id in range(10):
        lines.extend(
            [
                f"  if draftF({class_id}) then",
                f"    draftScore = {weights[32, class_id]:.6f}",
            ]
        )
        for feature_id in range(32):
            weight = weights[feature_id, class_id]
            if abs(weight) >= 0.0000005:
                lines.append(
                    f"    draftScore = draftScore + draftF({feature_id}) * {weight:.6f}"
                )
        lines.extend(
            [
                "    if draftScore > draftBestScore then",
                "      draftBestScore = draftScore",
                f"      draftBestClass = {class_id}",
                "    end if",
                "  end if",
            ]
        )
    lines.extend(
        [
            "  if draftBestClass >= 0 then",
            "    draftHero(draftBestClass)",
            "  end if",
            "end sub",
        ]
    )
    return "\n".join(lines)


def export_policy(base: str, weights: np.ndarray) -> str:
    start = base.find("sub chooseHero()")
    end_marker = "\nend sub"
    end = base.find(end_marker, start)
    if start < 0 or end < 0 or base.find("sub chooseHero()", start + 1) >= 0:
        raise ValueError("expected one replaceable chooseHero routine")
    return (
        base[:start]
        + "dim draftF(31)\n"
        + draft_routine(weights)
        + base[end + len(end_marker) :]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with np.load(args.weights, allow_pickle=False) as model:
        if str(model["schema"]) != SCHEMA:
            raise ValueError("draft model schema mismatch")
        weights = model["weights"]
    output = export_policy(args.base.read_text(), weights)
    if len(output.encode()) > 64 * 1024:
        raise ValueError("BASIC output exceeds the GameVersion 58 source limit")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)
    print(f"wrote {len(output.encode())} bytes to {args.output}")


if __name__ == "__main__":
    main()
