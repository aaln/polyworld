# Context synthesis

Model-generated, unreviewed interpretation. Check the linked evidence before changing an IR or policy.

Provider: gemini · Model: gemini-3.8-flash · Prompt: coaching-evidence-v5

Reviewing a match replay of a Druid hero ('Aaron'), the coach observes the agent repeatedly executing a full retreat to base after taking damage and dropping to low HP. Because the Druid possesses self-healing capabilities that restore health in the field, the coach notes that retreating all the way to base wastes valuable time and sacrifices lane pressure and experience/point accumulation. The coach advises modifying the retreat policy to sustain and continue pushing in lane when self-healing is available.

While the initial draft correctly recognized the coach's desire to use self-healing to sustain in lane instead of retreating to base, it overlooked a critical execution defect visible in the match replay: the agent's retreat skill lacked an early abort/termination condition. At 00:10–00:13, after casting its healing spell at low HP, the Druid's health restored almost completely (reaching 388/390 HP), yet the hero continued navigating all the way into the friendly base fountain before turning back to lane. This second pass develops the missing skill termination, interruptible execution controller, and dynamic belief revision required to stop premature full-base journeys when health has already recovered in the field.

## Moments

### 2.2–35.0s

Observation: The coached Druid takes minion/tower damage, casts an area self-heal (green circle), but proceeds to retreat all the way back into the friendly base fountain before walking all the way back out to the lane.

Coaching intent: The coach wants the agent to sustain in lane using its healing ability rather than retreating to base when low on HP, allowing it to maintain lane pressure, stay on the map, and farm experience and points.

Uncertainty: The coach's transcribed phrasing contains minor ASR noise ('OHB' for low HP, 'still themselves' for heal themselves), but visual feedback of the green healing aura confirms self-healing mechanics.

Evidence: speech-0 (2.2s), speech-1 (11.0s), speech-2 (13.9s), speech-3 (16.9s), speech-4 (19.3s), speech-5 (21.1s), speech-8 (25.8s), speech-9 (27.8s), speech-10 (30.0s), speech-11 (32.0s), video (0.0s)

### 10.7–32.0s

Observation: After dropping to low HP (~112/390) and casting self-heal at 00:08, the Druid's health bar recovers to near maximum (388/390 HP) by ~00:12.5. However, rather than stopping or turning around, the hero continues walking all the way through the jungle back to the home base fountain (arriving at ~00:24), lingers briefly, and then paths all the way back out to lane.

Coaching intent: The coach emphasizes that because the hero healed itself, walking all the way back to base was completely unnecessary ('he'll actually move to run back to base' / 'didn't have to be that') and wasted substantial lane uptime and point/XP earning opportunity ('so he can keep playing and keep pushing... could have earned more points all before').

Uncertainty: ASR transcript noise ('still themselves' for 'healed themselves', 'put on time in the revenues' for 'prevent that from happening'), but visual health indicators and the coach's direct verbal commentary clearly establish the intended behavior.

Evidence: speech-1 (11.0s), speech-2 (13.9s), speech-3 (16.9s), speech-4 (19.3s), speech-5 (21.1s), speech-8 (25.8s), speech-9 (27.8s), speech-10 (30.0s), speech-11 (32.0s), video (0.0s)

### 39.9–52.0s

Observation: In a subsequent push, the Druid pushes forward into enemy territory, takes damage down to low HP, and again begins running all the way back to base.

Coaching intent: The coach explicitly requests preventing this repetitive full-base retreat behavior when sustaining in the field is viable.

Uncertainty: Exact mana cost or cooldown limitations on the Druid's heal ability are not fully readable from the low-resolution HUD.

Evidence: speech-12 (39.9s), speech-13 (45.9s), speech-14 (46.9s), speech-15 (50.0s), video (0.0s)

## Proposed IR changes — not applied

### situation

Define a predicate `can_sustain_in_lane` that evaluates whether the agent has a ready or active self-heal ability, sufficient mana/resources to cast it, and is not facing imminent lethal burst damage from overwhelming enemy units.

Rationale: The coach points out that running back to base was unnecessary because the Druid could heal itself and remain active in lane.

Test: Check in replay state whether the Druid triggers `can_sustain_in_lane` when HP drops below retreat thresholds while the healing spell is off cooldown.

Evidence: speech-0 (2.2s), speech-1 (11.0s), speech-2 (13.9s), video (0.0s)

### strategy

Update retreat strategy: WHEN `low_hp` AND `can_sustain_in_lane` PREFER `skill_field_sustain_and_push` over `skill_base_retreat` FOR lane presence and XP farming.

Rationale: Currently the agent defaults to running back to base upon reaching low HP, wasting transit time. Supplying an alternative sustain-in-field skill keeps the hero active.

Test: Expose the agent to lane combat where its HP drops to low levels with heal available; verify it casts self-heal and remains in lane rather than pathing to base.

Evidence: speech-3 (16.9s), speech-4 (19.3s), speech-10 (30.0s), speech-11 (32.0s), speech-15 (50.0s)

### skill

Create or refine `skill_field_sustain_and_push`: step back to a safe position behind allied creeps/towers, activate self-healing ability, and resume pushing/farming once HP is above safe threshold.

Rationale: The coach stresses that after healing, the hero should 'keep playing and keep pushing' instead of navigating to the fountain.

Test: Verify pathing trajectories do not generate waypoints toward the spawn fountain when executing field sustain.

Evidence: speech-3 (16.9s), speech-4 (19.3s), speech-11 (32.0s), video (0.0s)

### goal

Increase the relative priority of map uptime and lane pushing/XP gathering compared to base retreat safety when sustaining mechanics are available.

Rationale: The agent was overly conservative, prioritizing a complete base return at the cost of losing significant lane points and time.

Test: Compare average time spent in lane vs time in transit to base over simulated match episodes.

Evidence: speech-5 (21.1s), speech-10 (30.0s), speech-11 (32.0s), speech-15 (50.0s)

### skill

Add an early termination/abort condition to `skill_base_retreat`: terminate immediately if `current_hp >= hp_safe_threshold` or if self-healing restores health to operational levels while in transit.

Rationale: The first pass proposed preventing retreat initiation when heal is available, but failed to address in-progress retreats. In the replay, the agent initiated a retreat while low, healed to 388/390 HP en route, but stayed locked into running to the base fountain for over 15 seconds because the retreat skill only terminates upon reaching the fountain.

Test: Induce low HP on the agent, trigger retreat toward base, apply a heal that brings HP above the safe threshold en route, and verify `skill_base_retreat` terminates immediately rather than navigating to the fountain.

Evidence: speech-1 (11.0s), speech-2 (13.9s), speech-3 (16.9s), speech-4 (19.3s), speech-5 (21.1s), speech-9 (27.8s), speech-10 (30.0s), speech-11 (32.0s), video (0.0s)

### execution

Implement an interruptible pathing controller for base retreats that clears waypoints and halts fountain navigation as soon as higher-level retreat skills are aborted or superseded by field sustain/push goals.

Rationale: Even if strategic priorities switch, if the underlying movement controller treats navigation to base fountain as an uninterruptible waypoint queue, the agent will walk all the way to base despite having full health. Dynamic pathing cancellation is necessary to realize field re-engagement.

Test: Issue a base retreat pathing command, inject an interrupt event when HP is restored, and verify that motor commands toward base cease within one tick and orient toward the lane objective.

Evidence: speech-1 (11.0s), speech-2 (13.9s), speech-5 (21.1s), speech-9 (27.8s), video (0.0s)

### belief

Update the belief layer to maintain a continuously revised hypothesis `base_fountain_required`, which evaluates to false whenever current HP and field regeneration capacity are sufficient to survive the active lane threat.

Rationale: The coach explicitly notes that the player 'didn't actually need to run back to base' because the hero was already healed. The current policy appears to treat reaching low HP as a latched state requiring fountain replenishment regardless of field health status.

Test: Monitor `base_fountain_required` during a heal-in-transit episode; verify the belief shifts to false upon HP reaching the safe threshold and triggers strategy re-evaluation prior to arriving at base.

Evidence: speech-0 (2.2s), speech-1 (11.0s), speech-2 (13.9s), speech-10 (30.0s), speech-11 (32.0s), video (0.0s)

## Missing context

- What are the precise mana and cooldown constraints on the Druid's self-healing skill that dictate whether staying in lane is safe versus requiring a fountain refill?
- Under what specific threat levels (e.g., enemy hero presence, tower dive risk) should the agent override lane sustain and commit to a full retreat to base?
- What specific HP percentage threshold (e.g., 70% vs 90%) should trigger an immediate abort of an in-progress base retreat when no enemy heroes are actively pursuing?

See result.json for the exact evidence text, source hashes, request hashes, model IDs and usage.
