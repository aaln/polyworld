---
id: 2026-09-15-wave-local-balance
policy: GOTA semantic IR
baseline: aaron-gota-ir-waveguard-r4:v2 (unchanged BASIC) and default
candidate: gota_wave_local_balance_20260915
status: inconclusive
hypothesis: >
  R1 limiting combat to six tiles around a retained allied footman prevents distant
  enemies from suppressing wave movement, improving lane presence and fort wins
  against the announced weaker defenses.
decision_rule: >
  Forty fresh independent balanced seed/seat cases: at least four added wins against
  BOTH unchanged v2 and default. Mean per-case rejoin-wave decision share must rise
  by at least ten percentage points versus v2, positive in twenty cases across
  three classes. Conditional120 fresh cases require gains>=5pp/v2 and>=10pp/default,
  paired exact one-sided p<.025 for both, no adverse flag in33 win/timeout/death-rate
  comparisons at .05/33 per reference, and the same mean movement-share gain with
  positive changes in60cases/3classes. Actual-release and hosted incumbent validation
  remain mandatory; this announcement simulation cannot justify promotion.
evals:
  - local:tmp/gota-ir/wave-local-20260915/screen
  - local:tmp/gota-ir/wave-local-20260915/validation
---

# Wave-local combat on the announced balance

## Context

User confirms the creator is still making the patch live. The announcement-only
simulation has towerHP900/1200/1800, tower damage18/24/30, DK heal30 and Warlock
restore24, applied to exact published5422fb0. There are no other source changes.
All source/config/runtime hashes are pinned. Its full provenance is copied into
`tmp/gota-ir/wave-local-20260915/runtime.json` and `announcement.patch`.

Both closed-lever registers checked. The old wave-following-only setting changed
R4, while any visible enemy still caused R1/R2 combat and suppressed that movement.
The existing, previously unevaluated `layered` IR supplied the independent
wave-local targeting operator. This experiment incorporates that one operator
into exact uploaded v2, preserving v2's sustain, equipment and R4 parameters.
It is not the old layered draft's different economy and movement configuration.

The immediately preceding supported-siege experiment got22/40 versus21/40 v2
and22/40 default. Overrides occurred in25cases but structure-target share barely
moved6.66%→6.79%. All120 games finished without draws. These are grounds to address
movement/combat scope rather than retry the rejected structure preference.
Historical public leader tapes showed substantially more movement commands and
lane travel; gear and other differences confound that observational comparison.
This new matched experiment isolates targeting scope.

## Predictions — pre-registered

- If TRUE: the hero has more decisions that rejoin its retained wave, and the
  fixed win-gain gates pass without a harmful class/side pattern in confirmation.
- If FALSE: the rule chases remote escorts, ignores immediate threats or avoids
  useful fights; movement share can rise without sufficient fort-win gains.

## Design

Only R1 changes from exact v2 to `wave_enemy(radius_tiles=6)`. Retain an observed
living allied footman or choose the nearest; attack only enemies within six tiles
of it, preferring footmen, then heroes, then exposed structures. No escort or no
local enemy gives R4 a movement opportunity. This is a spatial filter, not a claim
of reachable paths, safe positioning, tower protection or hidden enemy knowledge.
The full operator and parameter lift between IR and BASIC. Existing real-VM tests
cover its boundaries, retention and complete AST parity; the new bundle also
round-trips exactly. No changes to purchases, healing, casting or movement code.

Screen715300–715339:40 independent seeds, one shuffled slot per seed, four/class;
candidate, v2 and default arms each face nine defaults, identical full competition
configuration. Conditional confirmation718000–718119:120 independent fresh seeds,
twelve/class. All complete-game replays are audited before aggregates; failures
must be preserved and recovered with exact inputs, never scored as losses.
Legitimate game-limit draws remain zero. No optional stopping, retuning or sample
extension. The screen's movement metric is diagnostic, and wins decide progression.

Adversarial critique: movement share is an opportunity proxy, not damage or useful
lane position. Small class samples have low power. The seed floor does not promise
power for modest improvements. The fixed map, default rosters and unpublished
balance all constrain transfer. User intent is local-first, then actual published
release and frozen-incumbent hosted confirmation. A new release gets a new frozen
comparison, and outcomes from different runtimes are never pooled.

## Result

Screen completed: candidate27/40, unchangedv2 23/40, default20/40. All120 replay sequences matched; no failed attempts. Both +4-win gates passed. Mean rejoin-wave decision share increased57.70percentage points, positive inall40cases andalltenclasses. There were0candidate draws,1v2 draw and0default draws. Candidate versusv2 death rate fell .294→.264 per1000decisions. These are screening observations; paired exact p=.2517/v2 and .0835/default do not establish superiority. All40candidate heroes ended with equipment. See [screen report](../wave-local-20260915-screen.html).

The same frozen candidate completed the predeclared 120 fresh-seed validation: 68/120 wins versus unchanged v2 57/120 and default 60/120. Gains were +9.17 points versus v2 (paired exact p=.110774) and +6.67 points versus default (p=.174841). Both significance gates failed; the default gain also missed its 10-point threshold. All 360 complete replay audits passed. Mean rejoin decision share rose 58.33 points, activating in all 120 cases and all classes. The mechanism is supported; superiority remains unconfirmed. See [validation report](../wave-local-20260915-validation.html).

## Verdict

Screen passed; local confirmation failed its predeclared gates. No league promotion. The user separately requested hosted XP while local validation was pending, and later requested multi-episode batching; those directional field runs do not change this local verdict. The evaluated IR preserves the failed confirmation evidence and exact tested BASIC.
