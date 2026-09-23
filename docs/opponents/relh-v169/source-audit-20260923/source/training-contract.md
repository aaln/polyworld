# Relh full-neural submission contract (GameVersion 58)

The current relh v169 entry and the 39-feature/22-action v58 trainer are
hybrids. V169 uses a learned linear draft head, but its BASIC shell still
chooses ability upgrades, buyback, shopping, consumables, and emergency routes.
The v58 actor chooses combat and
movement macros, but a macro may still select its target or destination with
hand-written rules. Do not describe either policy as fully neural.

For the next full-neural candidate, the actor must choose the **strategic**
option in every phase. The runtime may encode observations, enumerate visible
objects and legal destinations, mask illegal actions, and execute the chosen
option. It must not replace an inconvenient actor choice with a preferred
class, route, item, target, or emergency override. A legal no-op/wait action is
necessary in each phase where declining to act can be correct.

| Decision family | Learned choice | Legality and observation requirements |
| --- | --- | --- |
| Draft | One of ten hero classes | Mask unavailable classes; include draft order, remaining pick time, and both teams' picks. A pick has a ten-second deadline. |
| Skill points | One of four ability slots or wait | Mask slots that `canLevelAbility` rejects; include level, points, learned ranks, charges, and mana. |
| Buyback | Buy back or wait | Mask buyback while alive or unaffordable; include remaining respawn time, gold, nearby threats, and the 60-second respawn cap. |
| Shop | Item 1–22 or wait | Mask outside own keep, unaffordable items, full six-slot inventory, already-equipped gear, and stacks at eight. Include owned equipment and counts. |
| Consumables and portals | Use slot, destination if needed, or wait | Mask empty/cooling slots. Portal destination must be chosen by the actor from legal observed candidates; preserve the three-second channel and 60-second cooldown. Include interruption risk and spawn recovery. |
| Combat and movement | Order type, visible target, and destination/aim | Actor scores object candidates and team-relative movement/aim choices. Mask unavailable targets and locked/cooling/insufficient-mana spells. Preserve fractional coordinates and both team orientations. |

The full-game training adapter must expose draft decisions **before** the
first battle step and continue exposing decisions during death, shopping, and
level-up. The existing native adapter accepts only one of 22 battle actions
per step; merely adding logits to its current actor would leave the BASIC
shell in control of the other families. A phase tag, candidate masks, and
candidate features are therefore part of the observation/action contract, not
post-export heuristics. Version the contract and validate native/BASIC forward
parity before screening checkpoints.

`extract_v58_draft_examples.py` is the first replay-grounded input step. It
accepts an exact-release `gota_release_audit.nim` JSON result and its matching
completed episode request, requires zero hash mismatches, and emits only
explicit policy picks. Each example has a 33-value team-relative feature
vector (ten legal classes, ten allied picks, ten enemy picks, pick counts,
remaining time), ten-class legal mask, stable player/policy IDs, and the
chosen class. It excludes ten-second deadline autopicks because those are
engine choices. For example:

```sh
uv run --project . python players/users/relh/co-gas/gota-training-v6/extract_v58_draft_examples.py \
  --audit .runtime/path/to/release-audit.json \
  --request .runtime/path/to/episode_request_api.json \
  --output .runtime/gota-draft-examples.json
```

Nine verified round-685 replays yielded 55 commanded draft examples in
`.runtime/gota-neural-phase-20260923/round685-audited-draft-examples.json`.
This is a data-contract smoke, not enough data or outcome evidence to submit a
draft head. Train/validate on disjoint matches and then verify the exported
network makes the same legal choice in both native and BASIC executions.

`extract_v58_skill_examples.py` covers a second phase. The exact-release
auditor now emits all `LevelChanged` and `AbilityLeveled` events in their
original order as `progressionEvents`; its first 300 `eventExamples` are not a
complete training trace. The extractor reconstructs hero levels, unspent
points, and all four ability ranks, checks each upgrade against v58's rank
and level gates, and attaches stable player/policy IDs. It emits only
commanded upgrades. A 24-game, zero-hash-mismatch round-686 audit yielded
1,103 legal upgrade examples across 11 players and all ten hero classes in
`.runtime/gota-neural-phase-20260923/round686-skill-examples.json`.
The dataset contains no decisions to wait, so training a five-way skill head
still requires decision-time native instrumentation. It is a validated
positive-choice corpus, not a deployable full-neural controller.

```sh
uv run --project . python players/users/relh/co-gas/gota-training-v6/extract_v58_skill_examples.py \
  --audit .runtime/path/to/release-audit-progression.json \
  --request .runtime/path/to/episode_request_api.json \
  --output .runtime/gota-skill-examples.json
```

The 2026-09-23 audit expanded this to 96 hash-verified GameVersion 58 games
from rounds 683–686: 558 commanded choices and 402 deadline autopicks. All 558
commanded choices had the full pick clock remaining. The BASIC host exposes
the picks and availability but no remaining-time query, so
`train_v58_draft_head.py` deliberately drops that constant, unavailable input.
Its 32-feature linear head trained on 153 decisions by the four leading
players in rounds 683–685. On 51 distinct round-686 decisions, its top-one
choice accuracy was 78.4% and negative log likelihood was 0.563, versus 72.5%
and 1.118 for a legal-masked class-frequency baseline. The epoch was selected
on this same validation set. These are **imitation diagnostics**, not an
independent test or evidence of better match score. The next round or a
separate held-out set is needed for that; the live policy still uses its
hand-written draft routine.

To reproduce the development result from the locally retained audit files:

```sh
uv run --project . python players/users/relh/co-gas/gota-training-v6/train_v58_draft_head.py \
  --train .runtime/gota-neural-phase-20260923/round683-draft-examples.json \
          .runtime/gota-neural-phase-20260923/round684-draft-examples.json \
          .runtime/gota-neural-phase-20260923/round685-draft-examples.json \
  --validation .runtime/gota-neural-phase-20260923/round686-draft-examples.json \
  --leaderboard .runtime/gota-continuation-20260923-pass9/round686-live-readback.json \
  --output .runtime/gota-neural-phase-20260923/draft-head-observable32.npz
```

On a local macOS checkout, `squeue` is absent. Capture it from a Slurm host
first (`ssh metta0 'squeue --json -u metta' > .runtime/.../squeue.json`), then
pass `--squeue-json` to `co-gas gota slurm-capacity`; invoking the command
without that file raises `FileNotFoundError`. The 2026-09-23 14:31 UTC capacity
read showed eight existing running/pending B300 GPUs against the campaign
limit of two, so no new GPU job was launched.

For release-exact Nim probes, a parent `nim.cfg` can silently put an older
Polyworld source ahead of the checked-out v58 source. That produced an
unsupported replay-format error despite the
probe importing v58 GotA modules. Build with `nim c --skipParentCfg:on
-d:release` and
explicit paths to the v58 source and dependencies pinned by its
`coworld/dependencies.lock`; verify the binary against a hash-checked v58
replay before trusting any result. The release flag also avoids an
unoptimized full-game audit taking several times longer. The draft diagnostic
also exposed a BASIC
parser constraint: `dim` array declarations belong at top level, not inside
`sub chooseHero()`. `export_v58_draft_head.py` now emits its array declaration
before the subroutine and checks the 64 KiB source limit.

Measure provenance in exact-release replays. For each of the six families,
record offered decisions, masked choices, actor-selected choices, accepted
orders, rejected orders, and deterministic fallback choices. The full-neural
claim requires actor provenance for every strategic family, no strategic
fallback, zero replay hash mismatches, and no VM failures. A legal action mask
or exact target-coordinate conversion is not a strategic fallback. Compare
both colors, public leaders, relh v169, and protected Richard with completed
hosted XP before replacing relh.

Current failure evidence is in the training [README](README.md): five
hash-verified round-685 relh low-score games were all melee picks, including
two explicit melee choices with a ranged carry available. The earlier v168
hand-written draft change kept relh at zero and hurt Richard in paired XP.
That makes learned phase-aware drafting a priority without treating a simple
draft override as a proven fix. GPU training remains subject to the
[Slurm campaign limit](../../../../../docs/slurm.md); check live capacity
before each launch.
