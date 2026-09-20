"""Standalone research figure; only measured held-out counts are plotted."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / "docs/microplay/2026-09-20"
research = json.loads((DOC / "research.ir.json").read_text())
totals = research["execution"]["heldout"]["totals"]
strata = research["execution"]["strata"]["automatic_spells"]
arms = ["parent", "finish", "combined"]
labels = ["Original", "Finishing", "Guarded teamwork"]
off = [strata["False"][a]["ally_deaths"] for a in arms]
on = [strata["True"][a]["ally_deaths"] for a in arms]
enemy = [totals[a]["enemy_deaths"] for a in arms]

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(10, 4.7), layout="constrained")
fig.suptitle("Local Gota combat: finishing and guarded teamwork", fontsize=15, fontweight="bold")
axes[0].bar(labels, off, color="#8ebad9", label="Automatic casting off")
axes[0].bar(labels, on, bottom=off, color="#235780", label="Automatic casting on")
axes[0].set_title("Allied deaths · lower is better")
axes[0].set_ylim(0, 76)
axes[0].legend(frameon=False, loc="upper right", fontsize=8)
for i, a in enumerate(arms):
    axes[0].text(i, off[i] + on[i] + 1, str(off[i] + on[i]), ha="center", weight="bold")
axes[1].bar(labels, enemy, color=["#a5afb8", "#5288af", "#39887a"])
axes[1].set_title("Enemy eliminations · higher is better")
axes[1].set_ylim(0, 290)
for i, value in enumerate(enemy):
    axes[1].text(i, value + 4, str(value), ha="center", weight="bold")
for axis in axes:
    axis.set_axisbelow(True)
    axis.grid(axis="y", alpha=.15)
fig.supxlabel("160 constructed six-second scenarios per policy · all ten classes · pinned release 2026.9.16.5\n"
              "Matched layouts are correlated. Explicit casts remain possible when automatic casting is off.", fontsize=8)
fig.savefig(DOC / "heldout.png", dpi=160)
fig.savefig(DOC / "heldout.svg")
plt.close(fig)
print(DOC / "heldout.png")
