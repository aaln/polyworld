# Manual coaching: earn more XP during productive field time

The five screenshots support testing better resource use, creep last hits and hero kills. A full audit of **200 existing current-engine games** confirms a large productivity gap, but also exposes a major class/role confound. The resulting [seven-layer semantic suggestions](suggestions.ir.json) distinguish observations, verified mechanics and proposed interventions. They are **research IR, not an executable replacement**. [Python representation](suggestions.py), [captured inputs and hashes](input-manifest.json), and [audit evidence](evidence/current-engine-analysis.json) are preserved.

The metric remains `floor(max(0, lifetime XP − 200 × elapsed minutes))`, including draft. Another minute helps only if its additional XP exceeds 200, before accounting for any existing deficit. Raising the nonzero average alone can hide a falling productive-game rate; all three user objectives must be evaluated together.

## What the screenshots show

These are the supplied historical images, not freshly fetched leaderboard values. Their policy filters and time window are unspecified, and they contain different numbers of hero-games.

| Metric | Andre (192) | Aaron (187) | Richard (190) | Coach (188) |
|---|---:|---:|---:|---:|
| Orders rejected | 2.0% | 32.8% | 10.3% | 34.5% |
| Gold spent/game | 2,901.3 | 2,037.2 | 1,890.7 | 1,976.8 |
| Consumables/game | 17.4 | 12.8 | 3.9 | 13.0 |
| XP attributed to creep last hits/game | 2,142.2 | 1,511.4 | 1,491.5 | 1,543.7 |
| Hero kills/game | 14.2 | 10.1 | 9.9 | 9.5 |

Relative to Aaron, Andre has 42.4% more spending, 35.9% more consumables, 41.7% more last-hit XP and 40.6% more hero kills. These differences motivate hypotheses; they do not identify their causes. The unrelated relh tooltip in the consumables image is not an Andre buyback measurement.

The [player-statistics documentation](https://github.com/Metta-AI/polyworld-buff/blob/main/tools/PLAYERS.md) describes hero-game means and version filters. The [metric extractor](https://raw.githubusercontent.com/Metta-AI/polyworld-buff/main/tools/players/extract.nim) counts all consumed item types and includes buybacks in spending. Creep last-hit XP is a reward total, not a last-hit accuracy percentage; nearby shared XP is tracked separately.

## What we verified against the current engine

We reused **all 200 baseline controls** from the completed unit-farming trial, without choosing episodes by score or resource use. Each game includes our deployed source `29f6d7e6`, exact khors v180 and Richard v195. All ten VMs were healthy, with source identities, full replay hashes, XP and integer scores checked. The resource instrument was independently calibrated against the coached khors v179 episode. No additional hosted games were needed for this diagnosis.

These are matched episodes, not matched heroes, teams or opportunities. Pooled figures must be read with the class breakdown below.

| Current 200-game diagnostic | Ours | Andre khors v180 |
|---|---:|---:|
| Mean score | 1,714.83 | 3,774.72 |
| Field time/game, minutes | 10.66 | 10.86 |
| Hero kills/game | 10.51 | 23.59 |
| Hero kills/field minute | 0.99 | 2.17 |
| Creep last hits/game | 155.56 | 234.57 |
| Total creep XP/field minute | 213.19 | 307.40 |
| Health potions used/game | 10.63 | 17.04 |
| Actual potion healing/game | 921.03 | 1,464.95 |
| Portal scrolls used/game | 6.32 | 9.05 |
| Gold spent/game | 2,920.35 | 4,422.05 |
| Of which buybacks | 1,235.50 | 2,245.00 |
| Gold remaining at end | 804.43 | 1,608.75 |
| Mean per-game rejected-order share | 37.07% | 2.43% |

Andre's extra spending is not simply more health. **1,009.50 of the 1,501.70 gold gap is buybacks.** He also ends with more unspent gold. Our field time is nearly equal, so more time outside base alone cannot explain the observed gap. We still need to distinguish useful wave exposure, target selection and kill conversion.

Class composition is especially important:

| Hero | Ours: games / mean score | Andre: games / mean score |
|---|---:|---:|
| Crossbowman | 49 / 4,041.22 | 104 / 4,096.08 |
| Ranger | 51 / 2,610.24 | 96 / 3,426.58 |
| Death Knight | 86 / 137.48 | 0 / — |
| Vanguard | 14 / 0 | 0 / — |

The ranged comparison remains confounded by side, draft and teammates; it is not a causal hero ranking. Nevertheless, the weak melee cases are a concrete low-tail problem. Our Crossbowman already averages **more** spending than Andre's Crossbowman, so globally increasing spending is an inadequate policy rule. Exact engine class enums determine these labels; the inherited policy name “Druid lane” does not describe every hero it drafts.

The current engine is **2026.9.23.1**, commit `d6827a4`, replay 59. Its content confirms Ranger HP growth 29, Crossbowman base damage 58, Chalice healing 45 and Gale Slash damage 65. The research checkout's older gameplay files were not used to decode these games. [Source hashes](engine-source-proof.json) bind the mechanics below.

## Semantic suggestions and decisive tests

| Proposed skill | Situation and strategy | Verify/practice first | Competitive measure |
|---|---|---|---|
| `effective_spell_selection` | When a useful spell is affordable and its target satisfies current class/rank geometry, choose an actionable target, potentially different from the basic target. | Diagnose missed effective casts with **automatic casting included**; practice range boundaries, visibility, cooldowns, mana and all spell shapes without losing basics. | Additional effective damage/healing and XP per field minute; fewer rejections alone does not pass. |
| `productive_consumable_reserve` | During an already-required keep visit, buy a bounded useful health stack after protecting core items and buyback reserve. Use regeneration behind safe cover when it enables productive lane presence. | Find actual stockouts followed by avoidable lost lane time; measure interruptions, unused inventory, actual HP restored and core timing. Practice full inventory and shared cooldowns. | Score and productive frequency, supported by effective recovery, time regained and death risk. |
| `last_hit_opportunity_and_timing` | When a visible creep can die to the next basic, preserve the appropriate windup and be within XP range. Recover toward a productive wave after a measured drought. | Separate eligible creep opportunities from conversion using predecision public visibility and HP history. Practice competing last hits, target death, retarget starvation, floor/range boundaries and dense waves. | Last hits per eligible opportunity, creep XP and gold per field minute, with hero XP and survival preserved. |
| `bounded_hero_engagement` | Prefer a reachable short hero finish when its expected return exceeds local farming and the public threat estimate allows escape. | Measure activation before spending. Practice weak hero versus lethal creep, tower cover, lost vision, outnumbering and chase deadline. | Hero XP gained against creep XP displaced, deaths, travel and final score. |
| `selective_structure_finish` | Restrict deliberate structure attacks to nearby plausible finishes; barracks require a stricter cutoff because they stop future waves. | Passed 802 checks and 16 native games; all 400 hosted games audited. Only three short tower commands activated in the 16 candidate diagnostic games. | **Did not qualify:** overall mean −1.82%; productive frequency 53% → 44.5%. Incumbent retained. |

These skills span **situation** predicates, **belief** estimates, the score **goal**, **skill** guards, **strategy** priorities, **execution** bindings and evidence-driven **updates**. Proposed live features use only public observations. Raw XP, hidden replay truth, opponent policy UUIDs and typed rejection reasons are evaluation-only information.

Important constraints change the test design:

- **Automatic spells already operate.** None of the 200 complete replays toggles manual-only casting. Of our 738 rejected orders/game, about 733 are out-of-range casts, but failed range checks do not consume mana/charges/cooldown and the engine can still cast automatically. A range guard is not yet a demonstrated lost-DPS fix. [Evidence](evidence/autocast-proof.json).
- **Health stock already exists.** Our policy stocks up to two potions, with a safe-use guard. A health potion costs 30 gold and restores up to 120 HP over ten seconds; incoming damage interrupts it. The 75-gold instant elixir restores 90 HP and shares the health-family cooldown. Buying both is not an independent two-heal burst.
- **Inventory has six slots.** Four core items, health potions and portal scrolls fill it. Extra quantities stack; adding mana/instant-heal types needs an explicit slot tradeoff. Shopping requires our keep, and no sell operation exists.
- **Basic last-hit timing is not projectile forecasting.** Current basics apply damage at windup. A lethal-creep ranking bonus and Crossbowman movement into the six-tile XP radius already exist. New timing or routing work needs evidence beyond reimplementing these skills.
- **Hero aggression needs boundaries.** Our prior close-hero diagnostic found no activating opportunities in four productive examples. Do not repeat that exact inactive rule or discard the melee tail after seeing results.

In the selected 7,781-point khors v179 game, Andre used 26 health potions and 11 portals; Coach used 15 health potions and 11 portals. Both bought back five times. The 1,170-gold spending difference consists of **1,000 more buyback gold, 270 more health purchases, and 100 less scroll purchasing**. This corroborates separating resource types; it does not prove that buying 11 more potions would reproduce the score. [Accepted-event comparison](evidence/coached-resource-comparison.json).

## Admission and acceptance

First use existing replays to establish activation and lost opportunity. Then update the executable semantic IR and current host binding together, regenerate BASIC through the repository converter, prove round-trip equality and practice the coordinated behavior. Local matches establish mechanism/runtime, not superiority over hosted rivals.

Before each new competitive trial, freeze source, IR, exact published engine, rival versions, roster and decision rule. The proposed shared rule uses 400 fresh games: 50 per source in each color/lead-or-later-draft context. Require at least 10% higher overall mean with a positive lower 95% bootstrap gain bound, each context retaining 95% of control, nonzero mean at least 5% higher with nonzero frequency preserved, and a strictly higher fraction scoring at least 500. Audit every game and disclose class mixtures. No sample extension or favorable class filtering after outcomes.

Keep earlier failures visible: ignoring all buildings lost 27.58% mean score across 400 clean games despite more creep XP. Broad retreat/healing bundles and instant-elixir attempts also did not qualify. The selective-finish trial has a separate [experiment record](../../../games/gods_of_the_arena/experiments/2026-09-23-selective-finish.md): mean score 1,540.30 → 1,512.315, 95% gain interval [−16.53%, +14.35%]. Its productive-game mean rose 2,877.67 → 3,351.92 while productive frequency fell. This supports the need for a joint rule, not a claim of a certain population decline. New suggestions did not modify its frozen source or thresholds.

Run `python verify.py` to check captured hashes, representations, diagnostic arithmetic, engine/source bindings and rejection by the executable-policy compiler. This verifies the coaching package, not its untested gameplay benefits.
