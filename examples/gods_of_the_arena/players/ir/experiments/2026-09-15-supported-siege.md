---
id: 2026-09-15-supported-siege
policy: GOTA semantic IR
baseline: aaron-gota-ir-waveguard-r4:v2 (unchanged BASIC) and default
candidate: gota_supported_siege_20260915
status: inconclusive
hypothesis: >
  After the announced tower reductions, R1 prioritizing nearby exposed structures
  during creep support and adequate health converts more lane openings to fort wins.
decision_rule: >
  Forty independent balanced seed/seat cases, candidate versus unchanged v2 and
  default: at least four added wins against EACH, with target overrides in at least
  twenty cases across three classes. This is a directional simulation screen only.
  Conditional 120 fresh cases require five percentage points over v2 and ten over
  default, paired exact one-sided p<.025 for both, overrides in sixty cases/three
  classes, and no flagged adverse win/timeout/death-rate change at .05/33 across
  overall plus ten classes. Actual published-release and hosted incumbent validation
  are required for promotion; an announcement-based simulation cannot qualify alone.
evals:
  - local:tmp/gota-ir/balance-20260915/screen
---

# Supported siege after the announced balance patch

## Context

The creator announcement supplied by the user gives tower HP 900/1200/1800,
damage 18/24/30, Death Knight passive healing 30, and Warlock passive mana 24.
The live manifest still points to published source 5422fb0, version 2026.9.15.1,
whose values differ. The isolated simulation applies exactly these four edits
to that release. It does not assume any additional unpublished changes.
`tmp/gota-ir/balance-20260915/runtime.json` and `announcement.patch` identify it.

Both closed-lever registers were checked. The prior unconditional structure
weighting lost 25/60 versus 35/60. Its explicitly suggested reopening prerequisite
was concrete support/danger evidence. This experiment implements support, health
and pursuit-distance prerequisites instead of globally raising structure weights.
The latest gear screen was 14/40 versus v2 12/40 and default 10/40; it failed its
v2 gain gate, so this candidate keeps exact v2 equipment and economy unchanged.

The two Red passives already cast automatically when useful during movement and
combat. Their buffs apply to every arm. No redundant explicit casting is added.
Source tower targeting prefers creeps when acquiring a new target but can retain
a hero target; nearby support is not a guarantee of protection.

## Predictions — pre-registered

- If TRUE: target overrides occur in supported structure windows, structure
  attack intent increases, and the candidate passes both fixed win-gain gates.
- If FALSE: the windows are scarce, heroes sacrifice needed farming or fight
  dangerous opponents while distracted, and the candidate fails either gain gate.
  More structure targeting without fort wins does not qualify.

## Design

Only R1 changes from exact uploaded v2. The named `supported_objective_enemy`
operator first computes the baseline nearest enemy. With HP at least 60%, it
prefers an exposed fort, then tower, within eight tiles of self and five tiles of
an observed living allied footman. Squared distance and stable ID break ties.
It revalidates each decision and otherwise keeps the nearest target. It never
reads hidden tower aggro. Its three parameters and complete control flow lift
from BASIC back to the same IR. Reverse parameter edits invalidate beliefs.

Screen: seeds 715200–715239, one shuffled slot per independent seed, four/class;
three arms each with nine default teammates/opponents and one tested seat.
Conditional confirmation uses fresh seeds 717000–717119, twelve/class, with the
same frozen policy. All runs use the full competition config and 28,800-tick cap.
The simulation patch, config, sources, binaries and instruments are hashed before
play. All episodes finish and every replay state sequence is audited before the
stage aggregate. VM failures are preserved and require exact-input recovery;
legitimate game-limit draws remain zero scores. No optional stopping, retuning,
sample extension or outcome-conditioned change of runtime is allowed.

Adversarial critique: observed proximity is not path reachability or proof of
tanking. Structure focus may lose XP or expose the hero to an enemy hero; total
wins decide advancement. Equal buffed passives across arms isolate policy effects
from the balance changes. The small class samples have low power, and the fixed
map plus default opponents limit transfer. Independent fresh seeds address
selection noise, but only hosted matches against frozen incumbents can decide
field strength. If the actual release differs, it needs a separately frozen
evaluation; no old and new runtime outcomes are pooled.

## Result

All120 games and replay state audits completed with zero mismatches and no failed attempts. Candidate22/40, unchanged v2 21/40, default22/40; both +4-win gates failed. Target overrides occurred in25cases across nine classes (2891decisions), but structure-intent share moved only6.66%→6.79%. There were no game-limit draws in any arm. Red wins changed7/20→11/20 and Blue14/20→11/20; these small subgroup results do not establish a side-specific advantage. The paired exact one-sided p versus v2 is .5, versus default .5806. See [report](../supported-siege-20260915-screen.html).

## Verdict

Inconclusive strength; rejected by the fixed screen. The observed support rule activated but did not produce the required win gain. No validation, XP request or upload. Evaluated IR links the results and preserves the exact tested BASIC. Seeds715200–715239 are observed. Do not retry this setting unchanged; movement scope is a distinct next hypothesis.
