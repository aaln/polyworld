# Build a counter to Richard v135

Handoff for the policy-building session — 2026-09-20. **Preserve the validated blue defense component and investigate red combat/coordination with the exact opponent source.** No existing tested bundle establishes wins on both colors. The source reveals concrete mechanisms to test; the new mechanisms below have not yet won full counterfactual games.

Machine-readable candidates, evidence status and rejection conditions: [counter-hypotheses.ir.json](counter-hypotheses.ir.json). Source comparison: [README](README.md). Do not replace the other session's current policy with a historical artifact without comparing their exact hashes and accepted changes.

The focused [Ranger economy and leveling audit](ranger-economy.md) adds accepted purchase times, exact XP sources and measured nine-tick attack cadence. Read it before changing item order or assuming the Ranger attacks at his nominal 18-tick period.

## Bind the opponent and starting policies

| Artifact | Identity / location |
|---|---|
| Exact opponent | Richard v135, `7c370daf-3c5f-42f8-870b-54b79c495a44` |
| Authentic executable | [v135.bas](v135.bas), SHA `f48bb0057aeaf2ff939035324340183e34f8f9544e03226edfe62e78faad5a30` |
| Source custody | [candidate.yaml](candidate.yaml), co-gas commit `93bd2aa1d79549960e88ea0f63ccf3a73273f198`, original source commit `fcdc915074115e772469c50daa61dc06b3ef8975` |
| Pinned game | `2026.9.16.5`, commit `f2ab9598d8f8001b6beae3e66404e341770c803f`, historical league configuration map 116 / seed 54 |
| Historical deployed control | BASIC SHA `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`; [retained baseline](../../../../examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/retained-baseline/) |
| Validated blue component | [IR, BASIC and evidence](../../../../examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/validated-blue-component/), BASIC SHA `d157d54aef9dc47f9d1a75a4f7216a76a3b63bb89688232b8ab6640a6b2f7140` |

The exact Richard source reproduced 915,098 commands and every state hash in all 20 original games with all five Richard VMs executing. Use this authentic source for local responsive matches. The observation-only `richard_v135.py` is a coarse forecast, not a rollout policy. Private source knowledge can inform design; our deployed policy still needs predicates computable from its actual host observations and permitted memory.

## Reuse the evidence already paid for

[Coaching results and every tested source](../../../../examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920/README.md) and the [earlier counter study](../../../../games/gods_of_the_arena/experiments/2026-09-20-richard135-counter.md) contain the experiment receipts.

| Finding | Implication for the next policy |
|---|---|
| Contemporary control lost 0/40 wins on each color | Use a fresh, explicitly bound control for a changed session; do not infer progress from a different opponent version |
| Validated blue component won 40/40 | Preserve its earlier, persistent critical-defense commitment as a blue reference; revalidate interactions when combining changes |
| Formation timing at 2400/3600/4800, weapon additions, forward discovery and several commitment variants still produced 0/40 red wins | Another gather-and-push parameter sweep needs a new measured mechanism; grouping alone has not solved red |
| Final bounded combined variant: red 0/40 (39 losses, 1 draw), blue 40/40 | Runtime repair did not establish a red counter |
| Red equipment-only screen: 0/4 | An observed gear difference did not establish that this tested loadout change was sufficient |
| Red diagnostic Death Knight: eight deaths, 12 basic hits, level 2 by tick 8517 | Investigate engagement entry, support and damage conversion before attributing the loss solely to purchases |
| Blue diagnostic: all five distant at tick 5760, `defCount=2` but `defActive=0`; core damage at 5778, defeat 5803 | Warning, travel time and persistent commitment matter; a return after damage starts can already be too late |

The 40-game cells include repeated trajectories. Report trajectory diversity and both colors separately; blue wins cannot compensate for unresolved red in a claim to beat Richard generally.

## Prioritize these experiments

### C01 — retain timely defense, improve the red engagement itself

Keep the blue critical-defense behavior as a regression control. For red, instrument the first losing engagement: public threat geometry, number of allies able to contribute, ordered attack/move/cast commands, basic hits, accepted spells, damage, death, and reinforcement arrival. Test one change to entry or support at a time against the reacting exact Richard source.

Candidate: a fragile or unsupported actor waits or approaches with a contributing ally, then commits to a shared visible target with a bounded release condition. Derive role and readiness from class, health, range and local ally geometry, not fixed player IDs. This is a proposed individual/teamplay repair, not a source-proven Richard weakness. Earlier gathering variants failed; require more damage converted and fewer avoidable deaths in the actual engagement before funding another full confirmation.

Reject if it merely delays the same death, gives up home defense, stalls indefinitely, loses blue performance or hurts the preservation field. Do not impose a new gathering threshold without an observed timing defect.

### C02 — test whether tower-siege retaliation can relieve pressure

Richard's added v135 branch only activates when his cached combat mode is 2 or 8, his nearest exposed objective is a **tower** within squared tile distance 300, and an enemy hero targeting him is within **his own basic attack range**. He selects the lowest-HP eligible attacker. Later home defense and post-hit movement can supersede the attack.

The paired VM test held geometry and neural mode fixed: a nearby hero targeting someone else left the tower targeted; targeting Richard switched him to that hero. Moving the hero out of range or changing the tower to a god prevented the switch. This establishes command semantics only. The branch activated **zero times** in the old 20-game corpus, so first establish a reachable activating encounter against our new policy.

Candidate: during defense of an exposed friendly tower, one healthy actor attacks a sieging Richard hero while nearby allies contribute damage. Avoid making a low-HP teammate the only eligible attacker. Our policy cannot directly observe Richard's cached mode or every private guard, so use public siege/target/range evidence and record whether Richard actually retargets. An attack order must affect the public target before Richard observes it; actor turn ordering and visibility matter.

Compare single-attractor and coordinated-support variants to the same baseline. Measure activated opportunities, time removed from tower attacks, actual tower damage prevented, bait damage/deaths, allied damage conversion and resulting match outcome. Reject if Richard simply kills the attracting actor faster, if the branch rarely activates, or if reduced tower targeting does not protect the tower. This is not a counter to god siege: that objective kind excludes this branch.

### C03 — test how home defense allocates Richard's heroes

After a home guard falls, Richard reserves a hero with no strictly closer living ally to his home. An early reservation also occurs when a nearby home guard has ≤390 HP and the candidate defender is within 30 tiles. Equal-distance ties may elect multiple heroes. The defender returns home, or attacks an intruder within 20 tiles if already nearby. Direct attacks on the fort outrank an approaching hero; an in-range one-hit enemy-fort finish suppresses reservation.

Candidate: time pressure from a second angle while a visible intruder causes the nearest defender to return. Compare the resulting defender allocation with a direct push. Use map/target geometry and remembered observations; do not assume hidden defender positions. If an existing creep wave is directly hitting the fort, observe its effect on defender target selection; our hero policy cannot issue orders to autonomous creeps.

The fixture verifies direct-creep-over-hero selection and that adding a closer ally removes self-reservation. Diversion effectiveness is untested. Measure who actually returns, arrival time, allied attackers versus available defenders, fort damage, and our own home exposure. Reject if the diversion costs more than it gains or simply consolidates Richard's defense.

### C04 — test decision timing only after measuring a real window

The neural mode updates every four living decisions, while target selection and scripted corrections run every decision. Do not treat Richard as unresponsive for four world ticks. A one-decision `walkTo(selfX,selfY)` follows a landed basic hit; this can be an attack-recovery optimization rather than weakness.

Record hit-to-hit intervals, approach/withdraw timing, accepted casts and damage before proposing timing exploitation. The Lich can attempt a midpoint ring when the nearest hero targets him at distance greater than 5 and at most 7 tiles. Entering that band while chasing may be dangerous; test lateral approach or a different attacker only if the full replay shows ring damage as the engagement cause. Synthetic command fixtures alone do not establish a safe dodge.

### C05 — interrupt Ranger's combat snowball, with measured economy and cadence

In the repeated Ranger trajectory, he has 0 XP at tick 1000, 100 at 2000 and 400 at 4000, but finishes level 10 with 4025 XP; 63.4% comes from hero kills. His accepted equipment order is dagger→sword→armor→axe→book, with the sword only at 3824. He already lands repeated nine-tick basics through post-hit recovery. See the [full ledger analysis](ranger-economy.md).

Test whether a bounded, coordinated early engagement and fewer isolated repeat deaths prevent the later hero-kill income without losing our own farm or core. Measure levels/items on both teams, deaths, damage conversion, accepted healing purchases and actual hit intervals. Earlier opening-farm and axe-before-armor ideas did not establish a sustained advantage. Reject an early XP gain that becomes a worse later fight or match result. C05 is proposed, with source/replay diagnosis supporting the question but no new counter-policy win evidence.

## Encode each change as IR before evaluating it

For each candidate, persist a stable ID, source parent/hash, public `when` predicate, individual `skill`, team assignment/commitment rule, goal hypothesis, precedence relative to attack/spell/defense/recovery, memory/reset rule, compute bound, paired control, mechanism metrics, competitive outcome and rejection rule. Link the Richard source mechanism ID from [source-model.ir.json](source-model.ir.json), but keep our policy's observed features separate from Richard's private state.

Use the existing primary policy IR compiler and verify regenerated BASIC bytes. Do not insert source-audit JSON directly into that compiler. Store proposals in the belief/update layers until an experiment supports adoption. A macro win improvement without the predicted skill change should trigger diagnosis rather than an invented explanation.

## Validate with a responding opponent and preserve the field

Start with local discriminators and complete matches using the pinned authentic source, all ten policy VMs responding. Same-tape reconstruction validates provenance; it is not a changed-action competitive experiment. Freeze candidate/control and expected effects before XP requests. Use hosted exact Richard v135 for confirmation, with both teams containing five copies of the intended policy when matching league conditions.

The previous prospective gate was ≥30/40 Richard wins **on each color**, at least eight additional combined wins over a fresh control, Jordan v268 ≥38/40 on each color, and a candidate/control field screen of eight per color against pinned relh154, g002v1, black-kite16, macro4, red-kite34 and vanguard1, with no more than two lost wins per rival/color and no aggregate regression. Keep the other session's already frozen gates if it has a stronger or newer plan; record any prospective revision before inspecting outcomes. If also claiming the joint Richard/Alex repair, carry the exact Alex gates from that study.

Small screens nominate candidates; they do not establish the promotion claim. Report both actual microplay changes and full-game results. Audit game/build/roster, all ten VM exits, complete replay hashes/actions and terminal outcome. Distinguish duplicate trajectories, draws, invalid execution and losses. Test other teammates/lineups before claiming general cooperative skill beyond uniform teams.

## Keep the counter within runtime limits

Pinned limits are 20,000 instructions and 50,000 work units per decision. Richard's observed maximum in this audit was 14,255 / 23,076; it is not a universal worst-case bound. Our earlier `formation4800_cohort` failed the instruction limit in all 40 red hosted games. The inspected first failure was reproduced at tick 5274 after 24,936 matching owned commands. Those games are quarantined, not ordinary losses.

The attempted bounded observer peaked at 19,105 and failed the local 19,000 margin gate before upload. The final coordinated observer/combat budget peaked at 17,982 in its recorded local suite. Preserve that margin discipline: combine shared observation scans, bound candidate/target loops, and test dense encounters and late game. Adding a sophisticated selector without paying its runtime cost recreates a known failure.

This handoff spent no new XP, changed no policy and makes no claim that the proposed source-informed counters win. Its usable result is an authenticated responding opponent, tested decision mechanisms, preserved blue evidence, and a narrower set of red experiments.
