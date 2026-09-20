# Context synthesis

Model-generated, unreviewed interpretation. Check the linked evidence before changing an IR or policy.

Provider: gemini · Model: gemini-3.8-flash · Prompt: coaching-evidence-v5

The coach reviews match replay footage between 'Aaron's Co-play Coach' and 'richard' (richard-gods-of-the-arena-v135) to diagnose why Richard's policy consistently wins. The coach observes that Richard's units group together into a 4- to 5-unit formation, hover and circle around the perimeter of the enemy base looking for openings, and exploit opponent dispersion to execute high-strength collective assaults. The coach advises adopting coordinated team grouping, avoiding splitting up during critical phases, and committing to unified team attacks.

This second-pass review identifies and develops distinct semantic components missed or left implicit in the first pass: specifically, grounding the temporal trigger to the match's late-game phase ('towards the latter part of the game'), defining the overarching objective shift in the goal layer from distributed laning to collective siege, and formalizing the update layer mechanism for evaluating and selecting an entry vector during base perimeter circling.

## Moments

### 1.2–12.2s

Observation: The coach reviews the episode scoreboard where Richard's policy defeated Aaron's policy 1-0, loads the replay, and establishes the goal of understanding Richard's strategic dominance.

Coaching intent: Direct focus toward analyzing Richard's macro-strategy and coordination patterns across the match.

Uncertainty: The coach has not yet isolated specific mechanics or conditions, presenting an initial hypothesis.

Evidence: speech-0 (1.2s), speech-1 (9.6s), input-6 (3.0s), input-211 (9.5s), video (0.0s)

### 26.4–50.6s

Observation: In the replay, Richard's units assemble into a concentrated group outside the enemy base, circling the perimeter chokepoints together to probe for an entry rather than initiating isolated dives.

Coaching intent: Encourage adopting a perimeter hovering and probing pattern where the entire team clusters and circles the base entrance together before pushing.

Uncertainty: Exact target selection and trigger thresholds for moving from probing to breaching the base perimeter are not explicitly quantified.

Evidence: speech-4 (26.4s), speech-5 (32.9s), speech-6 (37.5s), speech-7 (44.9s), input-373 (28.6s), input-431 (31.4s), input-500 (34.6s), input-605 (42.6s), input-628 (44.1s), input-655 (46.5s), video (0.0s)

### 44.9–50.6s

Observation: The coach explicitly identifies the timing of the base circling and breach probing behavior, noting that Richard's policy transitions into this 4- to 5-man perimeter grouping specifically 'towards the latter part of the game'.

Coaching intent: Restrict the collective perimeter circling and base-breach behavior to the late-game phase rather than applying it indiscriminately across early or mid-game laning.

Uncertainty: Whether 'the latter part of the game' is triggered by game clock/ticks, destroyed outer towers, or player level/item milestones is not quantified in the session.

Evidence: speech-6 (37.5s), speech-7 (44.9s), video (0.0s)

### 54.9–72.5s

Observation: Richard's 4- to 5-player deathball repeatedly overwhelms opposing units who are caught isolated or spread across different areas of the map.

Coaching intent: Advise against unit dispersion; emphasize that clustering all units concentrates combat strength and easily punishes spread-out defenders.

Uncertainty: Whether all unit roles are expected to cluster or whether vision/flanking roles exist is unstated.

Evidence: speech-8 (54.9s), speech-9 (60.5s), speech-10 (69.1s), speech-11 (71.6s), input-757 (54.3s), input-779 (55.7s), input-864 (61.4s), input-895 (63.4s), input-906 (64.5s), input-964 (69.7s), input-968 (70.1s), video (0.0s)

### 60.5–69.1s

Observation: The coach observes that when the opponent is spread across the map, Richard's clustered deathball encounters minimal resistance in initiating and executing concentrated attacks with total local numerical superiority.

Coaching intent: Incorporate an asymmetric dispersion assessment that triggers aggressive engagement when friendly units are clustered and enemy units are detected as dispersed.

Uncertainty: Visibility requirements (fog of war vs global vision) for assessing enemy dispersion are unstated.

Evidence: speech-8 (54.9s), speech-9 (60.5s), video (0.0s)

### 73.0–80.0s

Observation: The coach summarizes the primary tactical rule: units must not split up when executing late-game objectives, but instead gather together to deliver a decisive collective attack.

Coaching intent: Formulate a policy rule disallowing splitting up during late-game attack timing and enforcing a synchronized team assault.

Uncertainty: The exact timing window ('when it's time') relies on game phase or tower/health criteria that must be verified in the game engine.

Evidence: speech-12 (73.0s), speech-13 (75.8s), speech-14 (77.6s), input-999 (72.0s), input-1008 (72.6s), input-1030 (73.9s), input-1074 (81.2s), video (0.0s)

## Proposed IR changes — not applied

### situation

Define spatial predicates 'allies_concentrated(radius, min_count=4)', 'enemy_spread_out(dispersion_threshold)', and 'near_base_perimeter(target_base)'.

Rationale: The coach identifies that Richard's strategy succeeds because 4 to 5 units group up together and exploit the opponent's dispersion while circling the base perimeter.

Test: Compute mutual Euclidean distances between all surviving friendly agents; verify 'allies_concentrated' evaluates to true when at least 4 units remain within the clustering radius.

Evidence: speech-4 (26.4s), speech-6 (37.5s), speech-8 (54.9s), speech-9 (60.5s), video (0.0s)

### belief

Maintain a belief state 'team_assault_readiness' that tracks whether the allied unit cluster is sufficiently gathered and ready for objective engagement versus currently scattered.

Rationale: Units should not commit to dangerous base approaches alone; they require a belief estimate indicating whether the full squad has assembled.

Test: In replay simulations, check that 'team_assault_readiness' transitions to true only once 4-5 units converge near the staging area.

Evidence: speech-8 (54.9s), speech-12 (73.0s), speech-13 (75.8s), speech-14 (77.6s), video (0.0s)

### skill

Implement a collective skill 'GroupProbeAndCircleBase' that moves allied units around the exterior boundary of the enemy base in mutual proximity without penetrating defensive choke points alone.

Rationale: Richard's units do not immediately dive towers; they circle outside the base looking for entries while maintaining cohesive group formation.

Test: Evaluate agent pathing when outside the enemy base; ensure agents navigate along waypoint rings around the base perimeter while maintaining inter-unit distances below the scatter threshold.

Evidence: speech-4 (26.4s), speech-5 (32.9s), speech-6 (37.5s), speech-7 (44.9s), video (0.0s)

### skill

Implement 'SynchronizedTeamAssault' skill initiating simultaneous advance into the enemy base toward towers and core structures once gathered.

Rationale: The coach specifies that when it is time to attack, all units must come together to make a unified final attack rather than attacking sequentially.

Test: Verify that attack commands are dispatched synchronously to all grouped agents when entering the base, terminating only upon target destruction, retreat trigger, or unit loss.

Evidence: speech-12 (73.0s), speech-13 (75.8s), speech-14 (77.6s), video (0.0s)

### strategy

Add strategy rule: WHEN near_base_perimeter AND NOT allies_concentrated PREFER RallyToTeam; WHEN near_base_perimeter AND allies_concentrated AND NOT ready_for_breach PREFER GroupProbeAndCircleBase; WHEN near_base_perimeter AND allies_concentrated AND ready_for_breach PREFER SynchronizedTeamAssault.

Rationale: Prevents individual agents from splitting off or diving solo, enforcing the team-wide grouping and coordinated assault behavior observed in Richard's policy.

Test: Run ablation experiments comparing the policy with and without the grouping constraint; verify zero solo base breaches occur when allies are dispersed.

Evidence: speech-8 (54.9s), speech-9 (60.5s), speech-12 (73.0s), speech-13 (75.8s), speech-14 (77.6s), video (0.0s)

### execution

Enforce a formation tether in the low-level movement controller that restricts agent departure velocities if distance to the team centroid exceeds the allowable grouping radius.

Rationale: Ensures agents do not wander off or split up during navigation and perimeter circling.

Test: Measure inter-agent distance variance during transit; confirm agents slow or redirect toward the group centroid if separation exceeds threshold.

Evidence: speech-4 (26.4s), speech-13 (75.8s), video (0.0s)

### situation

Define the temporal/state predicate 'is_late_game' based on match progression indicators (e.g., match tick threshold or destruction of outer defensive structures).

Rationale: The first pass proposed base-circling and rally rules without conditioning them on game progression. The coach specifically qualifies that this base encirclement and entry probing happens 'towards the latter part of the game' (speech-7).

Test: Evaluate game state transitions; confirm 'is_late_game' evaluates to false during initial laning and transitions to true once configured match thresholds (or outer tower destructions) are reached.

Evidence: speech-6 (37.5s), speech-7 (44.9s), video (0.0s)

### goal

Define a late-game macro goal 'GroupSiegeAndCoreAssault' that overrides individual split-pushing, farming, and separate lane defense priorities in favor of unified 5-man team fighting and base destruction.

Rationale: The draft analysis introduced skills and strategies but omitted the top-level goal shift. The coach notes 'there's a lot to be said by forming up as a team' and 'no splitting up when it's time, they all come together in order to make a final attack' (speech-12, speech-13, speech-14), signifying an explicit goal hierarchy change.

Test: Log utility values across policy goals; ensure individual lane maintenance and split-push utilities drop below 'GroupSiegeAndCoreAssault' when 'is_late_game' is active.

Evidence: speech-12 (73.0s), speech-13 (75.8s), speech-14 (77.6s), video (0.0s)

### update

Implement an update rule 'UpdateBreachPathVector' that dynamically revises the chosen base entry choke point as agents execute 'GroupProbeAndCircleBase' around the base exterior.

Rationale: The coach notes that while circling around the base, the team 'tries to find like ways in' (speech-7). The draft skill described moving around the perimeter but lacked the mechanism by which sensory observations during circling update the intended breach path.

Test: In replay testing, verify that the target breach waypoint shifts along the perimeter as defenders reposition or as minion waves create favorable entry paths, rather than committing rigidly to a single predefined entry point.

Evidence: speech-6 (37.5s), speech-7 (44.9s), video (0.0s)

### strategy

Augment strategy rules with condition: WHEN is_late_game AND enemy_spread_out AND allies_concentrated PREFER SynchronizedTeamAssault FOR GroupSiegeAndCoreAssault.

Rationale: The coach notes that Richard's team has 'a much easier time to form up and attack' specifically 'when we're spread out' (speech-9), indicating that enemy dispersion should directly accelerate the decision to commit the concentrated strike.

Test: Simulate late-game scenarios comparing clustered vs dispersed defender configurations; confirm the policy initiates breach and assault significantly faster when enemy units are scattered across lanes.

Evidence: speech-8 (54.9s), speech-9 (60.5s), speech-11 (71.6s), speech-14 (77.6s), video (0.0s)

## Missing context

- What specific radius or distance metric defines whether 4 to 5 units are considered sufficiently grouped in this arena environment?
- What specific trigger indicates that 'it's time' for the probing behavior to convert into the final base attack (e.g., enemy unit pick-off, minion wave arrival, or health advantage)?
- What specific criteria in the 'Gods of the Arena' engine define the transition to 'the latter part of the game' (e.g., elapsed match time/ticks, tier-1/tier-2 tower destruction, or team level thresholds)?

See result.json for the exact evidence text, source hashes, request hashes, model IDs and usage.
