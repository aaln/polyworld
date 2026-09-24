# Richard v174: source-informed semantic IR

Richard uses a small neural selector followed by ordered tactical overrides. His source repeatedly chooses exposed objectives, counterattacks reachable heroes during tower assaults, and reserves a nearby defender for an exposed friendly god. Those are useful transfer hypotheses; their presence alone does not establish why he scores well.

The exact v174 source is [preserved here](richard-v174.bas). Its SHA256 is `c6429ea4ee202edc456de71c5ee7ad896ec423b11bbf2717c0dd4dd76c58b766`, bound to hosted version `5b854825-446a-4864-8dfc-bb3404d4fe81` by the co-gas [candidate record](source-candidate.yaml), [repository provenance](provenance.json), and hosted source hashes. The co-gas source commit is `767c552febdd79f132f933ccbfa9fa4f6babe970`. No changes were made to that repository or Richard's deployment.

## Model and verification

[Seven-layer semantic IR](richard_v174.source.ir.json) describes situation, belief, goal, skill, strategy, execution and update. [Recovered neural weights](neural-controller.json) preserve all 25 effective inputs, 16 ReLU hidden units and 18 output scores. Source lines support every skill. Explanatory goal labels are analyst interpretations, not an explicit XP objective in Richard's program.

Four complete hosted replays reconstruct Richard's actual private VM from tick zero, with all other players' authentic recorded commands. All **82,818 submitted commands** and every full world-state hash match. This verifies source identity and execution, including override ordering. All four observed Richard heroes are Warlocks, two on each color; this is not a validated semantic surrogate for every class. See [frozen selection and commands](source-audit-plan.json) and [per-episode evidence](evidence/).

| Behavior | Observed evidence | Transfer decision |
| --- | --- | --- |
| Structure-first combat mode | 45,490 of 71,954 living decisions | Test guarded nearby tower pressure when allied creeps cover it, health is adequate and no hero fight or last hit has already been selected. |
| Counterattack an in-range hero targeting self during siege | Guard true on 141 decisions | Test together with pressure; synchronize every target field so existing spells and movement follow the same target. Counts are guards, not landed hits. |
| Reserve nearby defender for an exposed god | Guard true on 101 decisions | Preserve as a separate hypothesis. Equal-distance allies can both defend; unseen allies are excluded. Current defense already has finite release. |
| Move after a landed basic attack | 1,033 observed recovery guards | Already present in our controller; retain our current implementation. |
| Legal skill spending | R > W > E > Q, at most four attempts | Already present; no redundant change. |
| Draft and equipment | Crossbowman +25, Warlock +10, Druid/DeathKnight −20; objective dagger → sword → armor → axe → book | Do not copy globally from four Warlock games. Our current draft and economy have independent evidence. |
| Immediate buyback whenever affordable | No item reserve or remaining-respawn threshold | Retain our validated core-aware buyback. |

## Ordering matters

Draft and death handling terminate early. Living decisions spend skills, scan public observations and evaluate the neural selector every fourth invocation. The main attack/navigation decision comes before Lich casting, consumables and shopping; mode corrections, siege retaliation, home defense and post-hit movement follow. A later movement/attack command can replace earlier intent. Merely counting the first selected mode would misdescribe the final policy.

Decisions 0–8 select generic equipment and decisions 9–17 select objective equipment, with nine shared combat modes. The computed early-clock and remembered enemy-offset features are not connected to the network. A mode-18 perimeter branch is unreachable. The source still checks a 50-gold vitality threshold while the current item costs 75, so a shopping attempt need not succeed. The faction term is a policy draft tie-break; the host no longer supplies faction bonuses. No opponent-name detector or explicit XP-minus-time optimizer exists.

## Our coordinated transfer

Four exact replays of our deployed Druid-lane source contain **109 decisions** selecting a nonlethal creep while the broader diagnostic finds a nearby exposed tower, allied creep cover, adequate health and no local disadvantage. The new candidate adds the stricter requirement that the tower already targets someone else. This is an opportunity count, not predicted score gain.

The candidate is generated through our IR conversion workflow, with changes in observation, skill, strategy, belief and execution. It retains available last hits, already-selected heroes and gods, recovery, portals, and current safety priorities. It can then switch a tower assault to the lowest-HP in-range hero targeting self. Both behaviors are evaluated together against fresh controls; neither is assumed to improve alone.

[Experiment protocol and result](../../../../games/gods_of_the_arena/experiments/2026-09-23-richard174-transfer.md) records 662 local checks, 16 native matches and the frozen 400-game hosted comparison. The broad transfer failed its400-game gate (+7.58%,95%interval−8.65% to+27.05%; red later-draft−53.15%) and was not deployed. [Transfer review](transfer-review.json) records that result and an eight-game diagnostic finding no redundant home navigation. A separate blue-Druid-only source completed its own 400 fresh games: own score 722.445 → 721.890 (−0.08%, 95% interval −17.43% to +21.10%). It outscored Richard in 119/200 games (59.5%), versus 86/200 baseline, but worsened its mean gap to khors by 718.49 points. It also failed qualification. [Scoped transfer review](scoped-transfer-review.json) and the [saved specialist fork](../../../../examples/gods_of_the_arena/players/ir/forks/blue-druid-siege20260923-hosted/README.md) preserve the result. Current Druid-lane champions remain live. Uploaded candidate names are opaque; the hosting API has no private-policy flag.

## Limits and preserved evidence

The previous [observation-only admission IR](../admission-20260923/richard_v174.ir.json) remains untouched. Source-reveal truth is only retrospective audit evidence; our runtime reads public observations, never Richard's private memory. No causal claims are assigned to the neural weights. The additional matches mentioned by the co-gas candidate YAML are not claimed as independently reverified: its `.runtime` directory is absent on this machine.

Both required Buff pages were visited and captured in [buff-visits.json](buff-visits.json). Their cohorts predate current replay58/v174, so they provide historical context only. Raw inputs and failed local revisions are preserved under `/Users/aaln/experiments/softmax/polyworld/tmp/gota-richard174-source-20260923`. Run `python verify.py` in this directory to recheck the source, recovered network and recorded reconstruction evidence.

## What explains the specialization

In the independent scoped study, our own XP was nearly unchanged (3215.86 → 3196.13), while Richard earned less hero and creep XP (total 3507.52 → 2843.64). Andre earned more (4551.12 → 5235.65). The relative improvement against Richard therefore did not translate into more individual points or better performance against the entire roster. This is a descriptive full-policy/context comparison; it does not establish that XP was directly transferred between opponents or isolate either edited component.

The 16-game mechanism subset verified 114 covered-tower selections and 77 submitted attacks, with no siege-attacker branch activation. The broader source study observed both transferred guards. Keep the distinction between source capability, executed actions and competitive benefit. [Current class mapping](class-mapping.json) comes directly from the pinned engine: class3 is DruidWarden, class4 is DemonHunter, class8 is Warlock. All hosted policy guards used the correct DruidWarden constant.
