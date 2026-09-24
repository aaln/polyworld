# Useful semantic knowledge

The executable source of truth is the [deployed portable pair](../policies/deployed). The [controller index](controller.ir.json) exposes its 21 ordered skills and source locations. Open the historical library only for the component or experiment being investigated. Original files are byte-preserved; annotations below govern their present interpretation.

## Retained components and their provenance

| Component | Useful detail | Evidence boundary |
|---|---|---|
| Legal draft and upgrades | Availability-masked draft; strong Crossbow preference and ranged fallback; spend legal ranks. Warlock/Lich E unlock supports control. | Draft-only improvement came from an older first-pick study; it is not a universal hero ranking. |
| Attack recovery | After an observed basic hit, move for a simulation tick before reacquiring. Same-decision walk+attack is not equivalent. | Existing mechanics evidence; post-hit movement is not guaranteed to improve every new hero/context. |
| Portal recovery | Critical field retreat, no home recall inside own keep, live inventory/readiness checks, persisted channel lock across the completion boundary. | Historical 160-game portal study +11.56% mean; inherited today, not re-isolated on release62. |
| Core-aware buyback | Four unique core items 11/16/18/19: remaining respawn >5s and price+100 reserve. Otherwise >25s and price+200. | Historical 400-game study +30.18%; the same ranged core on every class is a current hypothesis to revisit. |
| Blue opening | Blue first-team-seat ranged hero starts centrally; coordinated base-recovery timing avoids wasting a scroll. | Historical 400-game study +15.68% pooled; copying geometric mirroring alone previously failed. |
| Druid lane sustain | Interrupt health-only return for safe, available healing, bounded hold and recovery thresholds; preserve useful shopping and urgent escape. | Druid-only 400-game study +44.17% in its late-draft scope; broader all-class versions failed. |
| Crowd control | Schedule suitable stun/silence/root before retreat/tower movement consumes the action opportunity. Preserve healing mana, basic attacks and other legal channels. | Current mechanics fixtures; prior release61 80-pair pilot +2.64%. No guarantee that adding control cannot lower score. |
| Lane selection | One bounded early switch to a less allied-crowded lane, with travel/danger guards and persistent assignment. | Release61 improvement did not repeat alone in release62. The combined lane/neutral bundle earned the deployed pilot result. |
| Neutral fallback/pull | Visible tier-eligible mobs, health/threat guards, bounded camp-to-wave pull, handoff/time limits and no returning-mob targeting. | Current combined pilot +19.01% against a research parent in four contexts; broad incumbent comparison is now in `RESULTS.md`. |
| XP proximity | Crossbow steps inside six-tile creep credit radius when safe. | Kill count and nominal attack reach are not XP receipt. Neutral credit needs the same range/alive/floor checks. |

Original experiments are copied under [library/games/gods_of_the_arena/experiments](../library/games/gods_of_the_arena/experiments). [Library manifest](../library/manifest.json) maps every copy and historical pair to its source hash, binding, game version and origin. Historical deployment flags do not override current qualification.

## Failed or deferred changes worth remembering

| Hypothesis | Original result | How it constrains a new test |
|---|---|---|
| All-class field sustain | 240 games, -10.73% mean; less unnecessary retreat did not improve points | Preserve wave income and resource/kit differences; reducing travel alone is insufficient. |
| All-class lane recovery | 320 games, -5.26%; blue Ranger declined sharply | The later Druid-only variant needed its own fresh 400-game test. |
| Richard's guarded siege transfer | Broad 400-game gate failed; a separate blue-Druid 400-game test was nearly flat | Scoring relatively better than Richard can still worsen the gap to Andre without raising our own score. |
| Remove deliberate building targets | 400 games, -27.58% | Buildings award kill XP; attack-move and later engine changes also matter. No universal building ban. |
| Only short building finishes | 400 games, -1.82%, inconclusive mean gain; original joint gate failed | Keep the frozen result; future gates use expected score only. |
| Explicit sustain / weak-hero survival | Replay60 400 games, -8.72%; deaths fell while income also fell | Survival is valuable through XP-minus-time. No hosted Arcanist/Warlock coverage in that study. |
| Reward divided by attack/travel work | Eight native matched comparisons nearly flat, mixed side effects | Useful discrete proxy, not calibrated expected XP/time; no hosted efficacy result. |
| Single-scroll outbound portal | Prepared local source, hosted study deferred | Still a distinct hypothesis; assess escape reserve, destination income and travel saved together. |
| Weak-neutral direct attack | Current 60 pairs, -129.45 mean points, interval [-318.25,+41.65] | More neutral kills did not improve aggregate score. Test access and eligibility rather than broadening target guards again unchanged. |

A failed old-engine test is evidence about that intervention and scope, not a permanent prohibition. A new test needs a changed mechanism/context and a frozen rationale; do not relabel the same old results as fresh evidence.

## Opponent models

| Model | What is established | What is not established |
|---|---|---|
| [Khors v180](../opponents/khors-v180/README.md) | 28 appearances on release62; frequent hero-over-creep choices, neutral downtime harvesting, estimated last-hit choices; does attack structures | Exact latent priorities, memory, causal transfer value or executable surrogate. Only five appearances have all ten VMs clean. |
| [Relh v169](../library/docs/opponents/relh-v169/source-audit-20260923/README.md) | Exact source; legal-masked linear draft head; battle body identical to Richard174; eight whole-source reconstructions | Its mage-heavy score advantage is not a draft/controller causal comparison. Applying its head to our late states still leaves only melee heroes. Old auto-cast references are historical. |
| [Richard v174](../library/docs/opponents/richard-v174/source-audit-20260923/README.md) | Small neural mode/gear selector plus ordered overrides; source and four whole-game paths reconstructed | Network labels do not prove an XP objective. Two own-policy transfer studies failed their gates. |
| [Khors v179](../library/docs/opponents/khors-v179/score-audit-20260923/README.md) | Coached 7,781-point game, income sources and structural farming opportunities; 12 additional games | Selected high score is not typical performance. Version180 invalidates universal building-avoidance claims. |
| [Khors v114](../library/docs/opponents/khors-v114/score-audit-20260923/README.md) | Historical score/opportunity analysis with evidence links | Old version/release cannot substitute for current opponents. |
| [Richard v135](../library/docs/opponents/richard-v135/source-audit-20260920/README.md) | Historical example of source-informed ordering, economy and recovery timing | Pre-new-week tactics and mechanics are not current constraints. Jordan268/Alexg002 remain hash-indexed at origin for similarly historical questions. |

## Coaching

- Portal and Druid sessions: original notes, session metadata, captured input IR/policy, transcript and synthesis are in [coaching_inputs](../coaching_inputs/manifest.json). Empty captured inputs remain empty; synthesis is unreviewed until tied to engine evidence.
- [Manual score coaching](../library/docs/coaching/2026-09-23-manual-score/README.md): consumable totals include portals, spending includes buybacks, and rejection ratios depend on command volume and old automatic casts. Diagnose accepted effects and actual income.
- [Arcanist shopping](../library/docs/coaching/2026-09-23-arcanist-shopping/README.md): exact tick3530 shopping trigger, useful purchases, 66-second XP gap and locked mana restoration. This supports a bounded shopping/resource test, not disabling returns.

The next hypotheses are separated from all these findings in [hypotheses.ir.json](hypotheses.ir.json).
