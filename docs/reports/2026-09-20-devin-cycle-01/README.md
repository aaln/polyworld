# Devin cycle 01 — Richard red mechanism (local, no hosted spend)

Sanitized copy of `.gota/CHECKPOINT.md` state for cycle `20260920T2340Z-devin-01`. Raw replays and probe output are retained privately on the Devin host under `.gota/cycles/20260920T2340Z-devin/`.

- Deployed source `c708970db2c1be838d6d38b726cbc1b94b73c88f7c5b20c0adfd4d02666436a4` vs authentic Richard v135 `f48bb0057eaf2ff939035324340183e34f8f9544e03226edfe62e78faad5a30`, pinned engine `f2ab9598`, seeds 54/101/202.
- Red: 0W 3L 0D 0 invalid, 1 distinct stream (identical action count 73,861 and termination tick 5,898). Blue: 3W 0L 0D 0 invalid.
- Reproduces the hosted 0/40 red / 40/40 blue pattern locally, so the red loss is now debuggable offline with rule-level probes.
- Mechanism evidence (red-54, `replay_structure_damage`, 0 hash mismatches): heroes 102 and 103 die alone at the centre structure at tick 1085 against three Richard heroes; 104 and 101 die at ticks 1510/1540; five deaths vs one by tick 1805; Richard heroes reach level 7 (4,650 XP vs 1,650); our fort falls at tick 5898 in a structure race.
- Hypothesis `H-RED-OPEN-SPLIT-01` (proposed): strategy/skill-layer red opening dispersal. Untested. See `summary.json`, `plan.json`.
- Ownership: observer only; account spend today 4,328 episodes, budget exhausted; zero active requests. No promotion, no membership change. Incumbent Aaron, challenger Coach, a-aron retired.
