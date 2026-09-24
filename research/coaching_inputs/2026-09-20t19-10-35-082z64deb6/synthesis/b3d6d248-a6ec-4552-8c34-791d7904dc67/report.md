# Context synthesis

Model-generated, unreviewed interpretation. Check the linked evidence before changing an IR or policy.

Provider: gemini · Model: gemini-3.8-flash · Prompt: coaching-evidence-v5

The coach reviews a match replay where the coached team (Red) played entirely defensively against opponent Richard (Blue). Although Red defended successfully against multiple minion waves, the team failed to push outward, scout missing enemies, or convert defensive holds into offensive counter-attacks. Consequently, Blue charged late in the match, where a single high-damage Ranger eliminated Red's defending champions and base tower. The coach emphasizes transitioning from purely reactive defense to proactive scouting and offensive pushes, as well as investigating and countering the Ranger's build and combat effectiveness.

This second-pass review addresses gaps in the draft analysis by introducing the missing situation, execution, and update IR layers required to make the coached behaviors operational. Specifically, it establishes grounded situation predicates for post-wave defensive lulls, an execution-level coordinated focus-fire controller against kiting ranged carries, and an update mechanism benchmarking friendly character itemization and power scaling against high-performing opponent builds.

## Moments

### 10.2–29.0s

Observation: Red team remains huddled near base towers, clearing incoming creep waves reactively and holding defensive posture without advancing across the lane after neutralizing threats.

Coaching intent: Address excessive passivity in the team policy; defending incoming waves alone cannot win the match without transitioning into offensive pushes.

Uncertainty: It is unclear whether the passive positioning was driven by an explicit defense trigger threshold or an absence of safe-lane advance affordances.

Evidence: speech-1 (10.2s), speech-2 (14.6s), speech-3 (24.4s), video (0.0s)

### 29.0–45.0s

Observation: Red champions wait near their fortified perimeter while the enemy positions are hidden in fog of war, making no attempt to scout forward or send a champion into neutral territory.

Coaching intent: Direct the policy to proactively send a hero out to scout and locate enemy champions when enemy whereabouts are unknown, rather than idling in base.

Uncertainty: The specific hero designated for scouting duty (e.g., Crossbow, Vanguard) is not specified by the coach.

Evidence: speech-4 (29.0s), speech-5 (32.8s), speech-6 (38.1s), speech-7 (43.6s), video (0.0s)

### 43.6–57.0s

Observation: Red successfully repels multiple successive minion waves at their base gate without taking significant structure damage, but champions immediately retreat back behind the tower line after each wave rather than following the friendly minion counter-wave.

Coaching intent: Demonstrate that high defensive execution alone yields zero victory progress if the team never converts cleared waves into territory or structural counter-play.

Uncertainty: It is unverified whether the retreat is triggered by low health/mana thresholds or a hardcoded anchor point inside the base courtyard.

Evidence: speech-6 (38.1s), speech-7 (43.6s), speech-8 (51.2s), video (0.0s)

### 57.1–78.7s

Observation: Blue initiates an end-game assault. A single surviving Blue Ranger eliminates Red's remaining defenders and demolishes the final tower solo while taking minimal effective counter-damage.

Coaching intent: Highlight the catastrophic loss condition and instruct that allowing an enemy Ranger to free-fire against the tower and wipe defending heroes must be actively prevented.

Uncertainty: Whether the wipe occurred due to stat/item disparity, lack of focus fire on the Ranger, or poor range management against ranged attacks.

Evidence: speech-9 (57.1s), speech-10 (60.2s), speech-11 (65.8s), speech-12 (69.7s), speech-13 (74.0s), speech-14 (76.9s), speech-15 (79.6s), video (0.0s)

### 81.7–90.3s

Observation: The coach inspects the post-game summary and champion loadout to understand why the enemy Ranger achieved overwhelming combat performance.

Coaching intent: Identify the mechanics, items, or skills that make the Ranger character exceptionally powerful so Red's policy can either counter it or emulate comparable offensive capabilities.

Uncertainty: The coach poses this as an analytical goal without concluding on specific build modifications during the clip.

Evidence: speech-16 (81.7s), speech-17 (89.7s), video (0.0s)

### 81.7–90.3s

Observation: The coach reviews the Blue Ranger's combat stats (level 9, 123 physical attack, 410 range) and inventory loadout, noting that Red's characters fell far behind in individual combat efficacy.

Coaching intent: Benchmark friendly hero builds and progression against the opponent's build to determine why the enemy Ranger was able to solo Red's team and structures, requiring Red's heroes to match that power level.

Uncertainty: The coach does not specify whether Red's deficit stemmed from gold/XP starvation due to turtling, sub-optimal shop purchases, or hero-kit matchup differences.

Evidence: speech-16 (81.7s), speech-17 (89.7s), video (0.0s)

## Proposed IR changes — not applied

### strategy

Add an offensive transition rule: WHEN all immediate enemy lane waves at the friendly base are cleared AND no immediate structural threat is present, PREFER offensive lane pushing and objective pressure over remaining in defensive idling.

Rationale: The coach noted that the current policy plays defensively all the time ('we're just defending wave after wave and that's our policy... but then never ends up attacking and that's a problem'). Pure defense guarantees attrition and eventual defeat without pushing.

Test: In self-play or scripted matches, verify that champions initiate lane advances toward enemy towers once incoming waves are cleared rather than pacing behind friendly perimeter towers.

Evidence: speech-1 (10.2s), speech-2 (14.6s), speech-3 (24.4s), speech-6 (38.1s), speech-7 (43.6s)

### skill

Introduce a proactive scouting skill for high-mobility or ranged units: WHEN enemy champion positions are unobserved in the fog of war, dispatch a designated scout to check lane chokepoints and neutral areas while maintaining safe escape vectors.

Rationale: The coach explicitly criticized the team for idling when enemy positions are unknown ('we don't know where the enemy is but we're not proactively going at or sending a player out. We need to do so').

Test: Evaluate vision coverage in test episodes; confirm that at least one hero advances beyond base sightlines during lulls between enemy wave encounters.

Evidence: speech-4 (29.0s), speech-5 (32.8s), video (0.0s)

### belief

Update threat appraisal to assign top target priority to high-DPS ranged carries (such as the enemy Ranger) during base defenses, flagging them as primary targets for crowd control and coordinated focus fire.

Rationale: The match ended in defeat because a single enemy Ranger wiped out Red's heroes and the tower unhindered ('this character single-handedly takes down us the tower and all of our other characters. And so we have to avoid this happening').

Test: Present simulated defensive scenarios with mixed enemy units including an enemy Ranger; verify that defensive targeting prioritizes the Ranger over frontline minions or tank units.

Evidence: speech-10 (60.2s), speech-11 (65.8s), speech-12 (69.7s), speech-13 (74.0s), speech-14 (76.9s), speech-15 (79.6s)

### goal

Rebalance global objective utilities to weight enemy structure destruction higher relative to zero-risk personal preservation, preventing endless defensive turtling.

Rationale: The team repeatedly defended waves successfully but failed to win because defense does not satisfy the victory condition of destroying the enemy core/towers ('even though we defend very well not attacking so we're not winning').

Test: Compare policy evaluation metrics across episodes to verify that offensive objective damage increases without an unforced surge in catastrophic team wipes.

Evidence: speech-6 (38.1s), speech-7 (43.6s), speech-15 (79.6s)

### situation

Define grounded predicates `PerimeterCleared` (true when no hostile units or minions remain within friendly base turret attack range) and `HostilesUnobserved` (true when all enemy champions are hidden in the fog of war for more than a set time window).

Rationale: The draft proposed a strategy transition rule and scouting skill, but lacked the formal situation predicates required to trigger them. The coach noted that Red idles defenseless in base while unaware of enemy positions ('defending not really doing anything that much... we don't know where the enemy is'). Grounded predicates are needed to evaluate when the base is safe enough to dispatch scouts or push.

Test: In headless replay parsing, verify that `PerimeterCleared` evaluates to true within 500 ms of the last lane minion dying at the tower, and `HostilesUnobserved` flags true during fog-of-war lulls.

Evidence: speech-2 (14.6s), speech-3 (24.4s), speech-4 (29.0s), speech-5 (32.8s)

### execution

Implement a synchronized gap-closing and focus-fire execution controller for defending champions: WHEN engaging a single dominant ranged carry (e.g., Ranger), initiate gap-closing abilities and attacks simultaneously rather than approaching sequentially in single-file pathing.

Rationale: During the end-game breach (01:05–01:25), the surviving Blue Ranger eliminated Red's champions one by one as they trickled toward it while it fired from range 410. The coach stressed: 'this character single-handedly takes down us the tower and all of our other characters. And so we have to avoid this happening.' High-threat ranged units require synchronized engagement to prevent kiting.

Test: Test against an isolated ranged carry bot; confirm defending melee and ranged units synchronize initiation commands within a tight timing window, preventing individual unit attrition.

Evidence: speech-10 (60.2s), speech-11 (65.8s), speech-12 (69.7s), speech-13 (74.0s), speech-14 (76.9s), video (0.0s)

### update

Add an offline policy/itemization update rule: compare friendly champion net worth, item paths, and damage scaling against opponent carries across match replays, updating shop priorities and resource-harvesting weights to ensure friendly damage dealers match enemy power curves.

Rationale: The coach concluded the review by emphasizing: 'we need to figure out why this Ranger is so good and how they were able to defeat us and we need our characters to get as good.' Turtling inside base starved Red of map resources, creating an insurmountable stat deficit against Blue's carry.

Test: Compare end-game gold, XP, and inventory tier of Red's primary carries against enemy benchmarks across 20 evaluation matches; verify the power gap shrinks when offensive farming and updated item builds are active.

Evidence: speech-16 (81.7s), speech-17 (89.7s), video (0.0s)

## Missing context

- Which hero archetype on the coached team is intended to lead proactive scouting when enemies are off the map?
- Did the enemy Ranger gain a dominant level or item advantage during the extended turtling phase, or was the loss purely caused by target prioritization and positioning errors during the final fight?
- Does the game engine support vision wards or deployable sensors, or does scouting require risking physical champion presence in unrevealed areas?
- Did the Blue Ranger's dominant damage output result primarily from a level/item advantage accumulated while Red was turtling, or from inherently superior base class attributes?

See result.json for the exact evidence text, source hashes, request hashes, model IDs and usage.
