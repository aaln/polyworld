# gota_waveguard_v0 — advance with the wave

Status: full Waveguard design draft. Its isolated **R4 movement experiment** is now implemented in [waveguard_r4.ir.json](waveguard_r4.ir.json) and [waveguard_r4.generated.bas](waveguard_r4.generated.bas). The complete retreat, obstruction and supported-siege strategy below remains unimplemented. See [README.md](README.md) for the implemented contract and evidence.
Origin: a first coaching change to [gota_base_v0](base.policy.md).
Intent: “Help our footmen open a lane to the fort. Do not abandon them to chase a hero.”
Domain: Gods of the Arena `2026.9.10.1`, source-compatible with `2026.9.9.4`; [verified mechanics and evaluation plan](README.md).

## 1. Situation — what exists and what it affords

**Entities.** Hero, Footman, Tower, Fort, Item, WaveEscort and CombatTarget. A WaveEscort is one selected allied footman, used as an observable anchor for a moving wave; it is not a hidden engine object or an inference that every nearby footman belongs to the same lane.

**Grounding.** Self and object fields come only from the BASIC host. Coordinates are integer tiles 0–127. Equipment and class definitions come from the versioned static catalog. Movement requests are destinations, not guaranteed traversable paths.

| Predicate | Grounded meaning | Affordance |
| --- | --- | --- |
| enemy(o) | Observed `objectTeam(o) != selfTeam` | Consider as threat or target |
| living_unit(o) | Kind hero/footman, HP >0, `objectAlive(o)` | Pursue or escort |
| standing_structure(o) | Kind tower/fort, HP >0 | Landmark; a tower remains a possible threat |
| attackable_structure(o) | Standing enemy structure and `objectAlive(o)` | Normal combat can damage it |
| critical_health | `100*selfHp < 35*selfMaxHp` | Consume healing and disengage |
| recovered_health | `100*selfHp >= 65*selfMaxHp` | End health-based retreat |
| near(a,b,r) | Squared observed tile distance ≤ r² | Local decision region; not path reachability |
| screen_present(t) | Living allied footman within 3 observed tiles of standing enemy tower t | Candidate siege opportunity, subject to uncertainty |
| screen_ahead(t) | At least one such footman closer to t than self | Join an existing approach instead of initiating tower contact |
| tower_danger | Self within 8 observed tiles of any standing enemy tower | Conservative exposure region, including protected towers |

The 3- and 8-tile regions are proposed margins, not learned constants. Actual tower attack radii are 5, 5.5 and 6 tiles. Tile observations lose sub-tile positions; static ranges do not eliminate that uncertainty.

## 2. Belief — what we infer and remember

Maintain per-hero memory: escort ID, last confirmed escort location, selected target ID, retreat mode, last HP/tick/position and progress-monitor timestamps. Reset it for a new episode. Revalidate commitments after respawn.

Distinguish three records:

- **Observed:** ally footman at `(x,y)` at tick t; tower HP h and exposed flag e.
- **Inferred:** that footman may absorb tower attacks on approach. Evidence is its position, survival and earlier arrival; the tower's current target remains unknown.
- **Preferred:** keeping the wave alive is worth passing up a distant hero chase. This is a goal/strategy choice, not a belief about the world.

Do not invent numerical probabilities. A later opponent model needs defined evidence and calibration. A vanished enemy becomes unobserved, not dead. A vanished/dead escort ends its commitment; select from currently observed allies. Retain an observed, living escort to avoid switching lanes merely because another becomes slightly closer.

The statement “footmen always protect me” is false: towers can retain hero aggro. Unexpected HP loss while near a tower lowers confidence in a safe siege, without identifying the tower as the damage source. Update the estimate from observations; reconsider the concept if it systematically mispredicts outcomes.

## 3. Goal — explicit preferences and reasons

**G1 Fort victory.** Destroy the enemy fort before timeout; team success determines the official score.

**G2 Productive presence.** Stay alive and equipped so we can keep helping a push. Prefer escape over a speculative fight when critical. Survival alone is not success; a retreat must make progress or trigger replanning.

**G3 Wave progress.** Remove enemies that obstruct our escort and attack exposed structures with support. Prefer this over opportunistic hero pursuit away from the wave.

**G4 Efficient capacity.** Buy useful sustain and class-appropriate equipment. Preserve existing baseline spending for the first movement experiment; revise its budget and inventory habits in a separately evaluated change.

These are conditional preferences, not one weighted reward. G1 is the evaluation objective. G2 overrides local combat while critical; otherwise G3 governs movement and targeting. The fort-win rate and timeout rate will reveal whether this survival preference is too conservative.

## 4. Skill — reusable, bounded competences

Every skill has an initiation condition, action contract and termination condition. The names below specify proposed behavior; they do not reference an implemented skill library.

**observe_and_reconcile.** Begin each decision. Read the bounded visible object list; classify standing/exposed structures separately; update memories and progress observations. Finish before action selection. Use stable object IDs for memory, never temporary enumeration indices.

**baseline_economy.** Apply the inventory-use and ordered purchase contracts from `gota_base_v0`. Keep their snapshot semantics for the initial movement comparison. Poison requires the target selected this decision; it is therefore resolved after the movement/combat choice. A retreat decision suppresses poison so it cannot use a stale attack order. Log that explicit exception as part of the retreat rule.

**recover.** Initiate at critical health or when a siege loses its screen while health is falling. Clear the attack order and request movement toward a living allied tower away from immediate observed enemy pressure; use the allied fort as fallback. Healing comes from items or class abilities, not an assumed healing aura at home. Keep retreat state until recovered, or replan if movement/healing stalls. A bounded stall timeout and fallback must be specified and tested in the binding before this skill is executable; never wait indefinitely for HP to regenerate.

**select_escort.** Keep the current observed living allied footman. Otherwise select the nearest living allied footman by squared tile distance, stable ID breaking ties. If none exists, return unavailable. This first version does not allocate a team-wide lane formation; record that as a separate future coaching change.

**join_wave.** With an escort, move toward a point two tiles behind it along the line toward our fort. Keep a class-conditioned offset as a future parameter; two tiles is the initial draft. Recompute when the escort changes position. End when near that point, an actionable local target appears, or the escort is lost. The binding must define integer rounding and check acceptance/progress instead of repeatedly issuing an ineffective destination.

**clear_wave_obstruction.** With an escort, consider visible living enemies within six tiles of both self and escort. Prefer a footman over a hero; choose nearest to the escort within a kind, then stable ID. Request attack. Reconsider next decision and stop chasing once the target leaves that region, disappears or dies. This is a bounded proxy for protecting the wave; the host does not expose who attacks the escort.

**siege_with_wave.** Consider exposed enemy structures within eight tiles of self and escort. For a tower require `screen_present` and `screen_ahead`. Prefer fort over tower, then nearest to self, then stable ID. All nearby standing enemy towers still count as danger. Request attack only while the support conditions hold; loss of support or critical health terminates the skill. Neither screen presence nor attack acceptance is a promise of safe damage.

**regroup.** When there is no escort, move toward a living allied defensive structure using current observations, then recheck for new footmen. Wave spawns are periodic; do not assume a command can summon them. This replaces the baseline's unconditional walk to `(64,64)`.

## 5. Strategy — the text a coach edits

```text
POLICY gota_waveguard_v0
STATUS design_draft
GOAL fort_victory

R0 ALWAYS observe_and_reconcile
   FOR faithful_context

R1 WHEN critical_health OR losing_screen_while_health_falls
   PREFER recover OVER siege_with_wave, clear_wave_obstruction
   FOR productive_presence

R2 WHEN escort_available AND supported_exposed_structure_available
   PREFER siege_with_wave OVER opportunistic_hero_chase
   FOR wave_progress

R3 WHEN escort_available AND local_obstruction_available
   PREFER clear_wave_obstruction OVER leaving_the_wave
   FOR wave_progress

R4 WHEN escort_available AND no_combat_skill_selected
   PREFER join_wave OVER walk_to_center
   FOR wave_progress

R5 WHEN no_escort_available
   PREFER regroup OVER blind_enemy_pursuit
   FOR productive_presence

E0 AFTER tactical_selection DO baseline_economy
   EXCEPT suppress_poison_during_recovery
```

R1 has priority; then R2, R3, R4, R5. Retained recovery is subject to its termination and stall rules. Exactly one tactical skill owns movement/attack for a decision. Economy composes afterward. This prevents a later walk from cancelling an attack selected by an earlier skill.

The first experiment should implement **R4 only** against the faithful baseline; add retreat and siege changes separately. The complete draft is a destination for discussion, not one indivisible mutation to benchmark.

## 6. Execution — lower the meaning into BASIC

Generate bounded BASIC with explicit guards, deterministic tie breaking, persistent ID-based memory and calls to the four exported commands. Emit sparse private reason records containing tick, rule ID, target/escort ID, relevant observed predicates and command acceptance. Validate outputs against later observations.

The binding still needs exact recovery/stall logic, integer waypoint rounding and work-budget bounds. Reject generation until those contracts are complete. Do not hide missing semantics in an unversioned helper, arbitrary code block or a copied whole policy. Pin the game, IR, skill definitions and compiler with each generated artifact.

## 7. Update — coaching and research

“Stay closer to our footmen” changes the join-wave distance or the local engagement region. “Stop chasing kills” strengthens the requirement that a hero target remain near the escort. “You keep tanking the tower” first checks traces for retained tower targeting; it may require revising the screening belief and recover skill, not merely reordering target preferences.

“Good job” attaches positive feedback to the recent observed episode segment and selected rules. It does not automatically rewrite goals or increase every rule weight. Show the coach the event and proposed interpretation before treating it as a durable preference.

For every edit: save the named layer/rule change and intended observable effect → generate BASIC → extract its actual supported behavior back to IR → check fidelity in scenarios → run matched complete games → record improvement or failure. Keep goal edits explicit. Future ontology revisions must explain what the old representation failed to distinguish and add an observable test for the new distinction.
