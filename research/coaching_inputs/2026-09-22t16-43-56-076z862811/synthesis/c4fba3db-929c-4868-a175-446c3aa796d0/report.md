# Context synthesis

Model-generated, unreviewed interpretation. Check the linked evidence before changing an IR or policy.

Provider: gemini · Model: gemini-3.8-flash · Prompt: coaching-evidence-v5

The coach observes a replay where the controlled hero (Ranger) walks all the way back to base before activating their town scroll (teleport). The coach instructs that the agent should activate town scroll while out in the field (in lane or river) when low on health rather than walking back to base.

This coverage review adds missing execution and goal layer specifications omitted in the first pass. While the draft identified the skill selection rule to use the town scroll in the field when low on health, it lacked the execution-level channel controller needed to prevent input cancellation during the 3.0-second cast time, as well as the explicit goal prioritization governing field retreat. It also identifies a crucial mechanic ambiguity regarding whether town scrolls function as a fixed base recall or targetable structure teleport.

## Moments

### 1.7–7.5s

Observation: The coach interacts with the replay timeline controls (clicking near the bottom-left playback scrub bar at ~6268ms and ~7110ms) to inspect the Ranger hero's recall behavior inside the allied fountain base.

Coaching intent: Locate and review the specific replay moment where the agent activated the town scroll to demonstrate the inefficiency of recalling while already inside the base.

Uncertainty: Local unreviewed ASR transcribed 'Trump squirrels' for 'town scrolls'; acoustic and context confirm discussion of town scroll usage.

Evidence: speech-0 (1.7s), input-6 (6.3s), input-14 (7.1s), input-15 (7.2s), video (0.0s)

### 8.0–13.4s

Observation: The Ranger is visible inside the allied base with a 'TELEPORTING 3s' cast indicator active, indicating the hero is channeling a town scroll teleport while already inside the base.

Coaching intent: Highlight the inefficiency of waiting until the character reaches the base before activating a town scroll.

Uncertainty: Unreviewed ASR transcribed 'Trump squirrels' and 'towns scroll'; acoustic and UI context clearly indicates 'town scroll' (portal teleport).

Evidence: speech-1 (9.4s), speech-2 (12.8s), video (0.0s)

### 13.5–20.2s

Observation: The coach navigates the camera to the river and lane areas where the hero was previously engaged.

Coaching intent: Direct the policy to trigger the town scroll to recall to base when low on health while out on the map, rather than traversing back on foot.

Uncertainty: The coach does not specify an exact numerical health percentage threshold for 'low on health' or explicit safe-channeling positioning rules (e.g., hiding in fog or under a tower).

Evidence: speech-3 (13.5s), speech-4 (15.8s), input-101 (14.3s), input-106 (14.7s), input-135 (16.4s), input-143 (17.0s), input-150 (17.5s), input-158 (18.0s), input-167 (18.6s), input-175 (18.9s), input-191 (19.9s), input-197 (20.2s), video (0.0s)

## Proposed IR changes — not applied

### situation

Define predicate `low_health_in_field(agent)`: true when agent health is below a retreat threshold (e.g., < 30% HP or threatened) AND agent is located outside the base fountain/safe area.

Rationale: The coach explicitly pointed to locations outside base ('over here', 'when they're low on health') and contrasted them with being inside base.

Test: Evaluate that `low_health_in_field` evaluates to true in lane/river when HP drops below threshold, and evaluates to false once the agent enters the base perimeter.

Evidence: speech-3 (13.5s), speech-4 (15.8s), video (0.0s)

### skill

Add guard condition to `channel_town_scroll` skill: require `NOT in_base(agent)` and `town_scroll_ready(agent)` before initiating the 3-second teleport channel. Terminate channel if interrupted or upon arrival at base.

Rationale: Currently the agent channels town scroll while already standing in base, wasting the cooldown and consumable item utility.

Test: Verify in unit tests that the agent never activates town scroll when already located in base.

Evidence: speech-1 (9.4s), speech-2 (12.8s), video (0.0s)

### strategy

WHEN `low_health_in_field(agent)` AND `town_scroll_ready(agent)` PREFER `channel_town_scroll` OVER `walk_to_base` FOR goal `survive_and_replenish`.

Rationale: Directly implements the coach's instruction: 'they should have town scrolled when they're over here when they're low on health'.

Test: In simulated matches where the hero sustains heavy damage in lane or jungle, verify that the hero attempts to channel town scroll from a secure spot rather than pathing all the way back across the map.

Evidence: speech-1 (9.4s), speech-3 (13.5s), speech-4 (15.8s), video (0.0s)

### execution

Implement a stationary channel controller for `channel_town_scroll`: upon initiating the 3.0-second teleport cast, lock movement, attack, and standard ability inputs until the 3.0-second duration completes or an explicit interrupt/evasion threshold is breached.

Rationale: The draft proposed a skill and strategy rule to trigger `channel_town_scroll` while in the field. However, in execution, continuous policy ticks issuing standard movement or auto-attack commands would immediately cancel the 3.0-second channel (evidenced by the 'TELEPORTING 3s' cast indicator in the HUD). An execution lock is necessary to make the coached skill realizable.

Test: In an offline sandbox test, trigger `channel_town_scroll` while low on health in a lane and verify that subsequent default navigation commands do not abort the channel before the 3.0-second teleport resolves.

Evidence: speech-1 (9.4s), speech-3 (13.5s), speech-4 (15.8s), video (0.0s)

### goal

Define goal `survive_and_replenish`: elevated to highest tactical priority over lane wave pushing and hero harassment when agent health is below critical retreat threshold.

Rationale: The agent in the replay delayed using the town scroll until reaching base on foot. Establishing `survive_and_replenish` as an explicit goal provides the motivational structure for the strategy proposal to prefer immediate teleportation over continued traversal or farming.

Test: Simulate low health states during wave farming; verify that the policy shifts goal arbitration from lane pressure to `survive_and_replenish`.

Evidence: speech-3 (13.5s), speech-4 (15.8s), video (0.0s)

## Missing context

- What specific health percentage or combat condition should trigger the decision to town scroll back to base?
- Can the 3-second town scroll channel be canceled by enemy hero attacks or creep damage, requiring the agent to retreat to fog of war or tower safety before channeling?
- Does the Town Scroll item in this game function strictly as an untargeted return-to-base recall, or can it target friendly towers and creeps to teleport back to lane (which could explain why the agent held the scroll until reaching the base)?

See result.json for the exact evidence text, source hashes, request hashes, model IDs and usage.
