---
{
  "id": "2026-09-15-ordered-loadout",
  "policy": "GOTA semantic IR",
  "baseline": "aaron-gota-ir-waveguard-r4:v2 (6d0ff780-652f-47a8-82b3-336cb7a10a56), unchanged BASIC; current default",
  "candidate": "gota_ordered_loadout_20260915; BASIC a2948fd27e4d736b030e45a4e9554c5a9b8b99c60514d530c90339e0ced81541",
  "status": "inconclusive",
  "hypothesis": "Replacing E2 class-specific cheap gear with a five-item ordered damage/armor loadout accelerates basic-attack last hits and growth while preserving a permanent healing slot, increasing fort wins.",
  "decision_rule": "Screen 40 independent balanced seed/seat cases: >=4 added wins over BOTH current v2 and default; accepted planned gear in >=20 cases across >=3 classes. If passed, freeze same candidate for 120 fresh balanced cases: >=5pp over v2 and >=10pp over default with paired exact one-sided p<.025 for both; activation >=60 cases / >=3 classes; no adverse flag in 33 win/timeout/death-rate comparisons at .05/33 per reference. All games and replay audits complete before each aggregate. Hosted matched confirmation required before league promotion.",
  "evals": [
    "local:tmp/gota-ir/upgrade-20260915/screen",
    "conditional-local:tmp/gota-ir/upgrade-20260915/validation"
  ]
}
---

# Ordered damage/armor equipment

## Context

The league now runs 2026.9.15.1, published source 5422fb0c4b230ca7bfa57a69e450a369da2dabe9. Current v2 remains #3. Three public hosted replays were replayed to completion with zero state mismatches. Across Berserker, Arcanist and Ranger, red-kite:v13 held dagger, longsword, armor, axe and spellbook with healing stock; our inspected heroes often had cheap gear and fewer damage upgrades. The leader also moves differently, so the history is motivation, not causal evidence. Public actions/inventory are available; private source was not retrieved. Both local and optimizer closed-lever registers checked. This is distinct from the rejected four-gear cap and early HP purchase order on the older game.

## Predictions — pre-registered

- If TRUE: accepted equipment follows the declared sequence across classes, delivers more basic-attack damage and useful growth, and wins exceed both thresholds without flagged adverse class outcomes.
- If FALSE: consumables delay the next purchase, the plan sacrifices mobility/mana/survival, or gear grows without enough fort wins. A working purchase sequence alone is insufficient.

## Design

Only E2 changes from exact uploaded v2. All classes buy first missing item in [11 dagger, 13 longsword, 16 armor, 18 axe, 20 spellbook], at most one gear attempt per decision; inspect live inventory and require space, let the host enforce remaining gold. No changes to v2 combat, wave fallback, healing or mana buying. The sequence uses five permanent slots; pre-existing consumables can still block gear. BASIC is generated from the IR and reversed into the IR with complete AST checks. Current game facts are version-specific; old performance claims are explicitly historical.

Three matched arms, nine defaults around one tested seat. Forty fresh independent seeds 715100–715139, one shuffled seat per seed, four cases per class. Predeclared screen is directional only and gates 120 fresh seeds 716000–716119, 12/class, same frozen candidate. Competition map preset seed 54 / size 116 is identical across arms; match seeds vary. Old validation seeds are not reused. All source, binary, instrument and configuration hashes are frozen in plan.json. Runtime source matches the published release, and three hosted replays have matched this local simulator; local results still cannot establish field strength.

Adversarial critique: whole loadout is one equipment algorithm change; a positive result does not separately identify armor, order or capacity as causal. End gear count is deliberately reduced, so it is descriptive rather than a harm gate. Win, in-game timeout and deaths per decision are checked overall and across ten classes (33 comparisons/reference). Class sample size is low power. Local fills can hide team interactions and movement weaknesses; hosted confirmation against pinned incumbents is mandatory. N floors are conservative engineering choices rather than a power guarantee. No early aggregate inspection, optional stopping, retuning, extra candidates or sample extension inside this experiment. Native VM failures are not zero scores; preserved exact-input recovery is required. Legitimate in-game tick-limit timeouts ARE zero scores and remain in all comparisons. Initial attempt failures are reported separately.

The user has authorized autonomous policy improvement and promotion of a validated replacement. A failed local candidate does not get submitted. There is no universal requirement to stop the broader improvement task after a rejected hypothesis; a different hypothesis requires its own record.

## Result

All 120 games and replay state audits completed, zero invalid runs scored and no failed attempts. Candidate 14/40 wins; exact v2 12/40; default 10/40. The candidate made 107 accepted planned purchases across all 40 cases and ten classes. It passed the default gain gate but missed the required four added wins versus v2 (only two). See `ordered-loadout-20260915-result.json`.

## Verdict

Inconclusive strength; fixed screen rejected advancement. No validation, XP requests or upload were launched. Gear execution is supported, but increased strength is unconfirmed. Before reading the outcome, the creator announcement independently caused old-release confirmation to be deferred; the completed screen also failed on its own terms. Seeds 715100–715139 are observed. A future study on a materially different balance release needs a distinct rationale and preregistration.
