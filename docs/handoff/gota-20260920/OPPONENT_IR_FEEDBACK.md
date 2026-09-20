# Completed Richard135 and Alex g002:v1 opponent IR

The interactive read-only analysis is complete. Use OPPONENT_MODELS.json for exact paths, UUIDs and hashes. Both model manifests and Python compatibility receipts exist. Full summary: polyworld/docs/opponents/richard-alex-20260920/analysis.md. All 1,210 heldout forecasts reproduce, all episode rosters and native replay hashes match, and all game logs have 10 active VMs. Merging both belief patches into a COPY of the deployed primary IR preserves exact BASIC. Models are forecasting observations, not live rollout proxies (usable=False).

## Counted findings

- Richard won 20/20 selected games. Forecast 75.2% versus population 54.4%; novel-stream subset 76.3% versus 50.2%. Main preference Richard135_I_O13: structure over creep contact when both available, training338/583, heldout140/226 correct versus83/226 population. Only18.3% of living opponent ticks are visible. Do not infer a universal structure-first objective.
- Alex won 20/20, with losses at107.6s on our red and130.3s on our blue. Forecast73.2% versus67.9%; EVERY heldout stream repeats training, so new-trajectory generalization is unresolved. In all12distinct training observer streams the first visible pair within24tiles of our god arrives while all5friendly heroes are alive farther than28tiles away. Contextual structure-versus-hero preference is25/33training and4/6heldout, but with creeps also available Alex often selects heroes. Never reduce this to a universal hero-ignoring rule.

## Own decision evidence and next tests

Exact source reproduced93,288owned commands in4representative red/blue replays. Against Alex red, t2520 ALL5own VMs have defCount5, defAnchor1, defActive0, defUntil0 and attack remote structures. First god damage2533, defeat2583. Blue t3000 samples defCount4 and inactive defense; first damage3108, defeat3126. Our28-tile cancellation suppresses a detected push. Richard blue t5760 sees2enemies with defenseinactive; first damage5778, defeat5803. The normal group alarm also misses that pair. Richard red shows actual late defender return and still loses; a recall-only explanation is insufficient.

These are actual120-tick own-memory samples, never interpolated at the damage tick. Macro counts are POST-FIT DESCRIPTIVE TRAINING analysis and must not be called heldout macro prediction.

Use PROPOSED_RULES C01/C02 as hypotheses: bounded critical-defense override, earlier inner-structure interception based on visible pressure and travel time, plus separate red combat/economy diagnosis. Existing critical60blue4/4 is directional; red0/4, critical40blue2/4 andred0/4, equipmentred0/4 remain failures. Do not promote any of them from this evidence.

Continue your currently owned middle-coverage screen to its ORIGINAL conclusion; this analysis is not a reason to modify it mid-run or duplicate XP. No other interactive policy editor or collector was launched. Retain one final executable that meets all prospective Richard/Alex/Jordan both-color thresholds, fresh controls and broad-field gates in FOCUS.md. Preserve budgets, accepted snapshot lineage and active Aaron+Coach. Consume exact model identities; update future target versions prospectively. The #1 objective remains unresolved.
