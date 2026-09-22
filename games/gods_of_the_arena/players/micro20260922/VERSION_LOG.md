# Microplay versions

## aaron-gota-micro0922:v1

- Version `f3f8baab-d02a-4f7f-8fc9-e1f050f967a7`; registered 2026-09-22T05:51:50.860967+00:00.
- BASIC SHA256 `b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098`; game 2026.9.21.5, engine `f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`.
- Coordinated user-requested microplay: one-tick recovery, feasible last hits, six-tile XP positioning, damage equipment and purposeful portals. Individual contributions are not inferred from full matches.
- Runtime: uploaded BASIC file, no container/argv. Native practice and responsive match validation completed; hosted quality unvalidated at upload. Inert version, no league selection.


## Current-release mixed validation 2026-09-22

- Validation: validated against deployed compatibility bytes in 320 clean hosted games, both colors from first and third draft positions. All ten VMs, full replay hashes, official XP/score and actual source identity pass.
- First-pick scores: candidate red 4081.61 / blue 2511.85 versus control 0 / 0. Third-pick scores: 1719.68 / 1938.65 versus 0 / 581.30. Both preregistered current-score gates pass.
- Blue first-pick deaths 8.85 → 2.62 and level 4.92 → 10.53. Red absolute deaths do not decrease. No independent-trial significance or universal rank claim. relh161 is outscored in all four tested mixed cells; Jordan317/Richard153 only count as opponents in red cells. Jordan356 appeared later and is untested.
- Exact BASIC remains b82c3799; current IR e9243120 and all evidence saved in `examples/gods_of_the_arena/players/ir/forks/current20260922`. Existing source registration remains f3f8baab-d02a-4f7f-8fc9-e1f050f967a7.


## Coach practiced registration 15b325b4-e9f3-487f-bd95-a059f92d20e2

- aaron-gota-micro0922-coach:v1; registered 2026-09-22T08:30:59.052944+00:00; BASIC `b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098`.
- Runtime: BASIC file, no container or argv. Byte-identical to tested Aaron source; separate player binding, not independent evidence.
- Validation: validated executable via completed 320-game current mixed A/B and guardrail; registration inert until selection.
- Current-game practiced policy: ranged-first public drafting, explicit skill points, actual-tick attack recovery, last-hit/XP positioning, equipment and purposeful portals. Exact BASIC passed current-engine both-color mixed A/B against deployed compat and later-draft guardrail, all VMs/replay/XP/score audited. Original target panel and its limitations remain preserved. Fixed rosters/correlated trajectories; no universal opponent, class or rank guarantee. Prior user league/latest and two-player authorization continues; this is not a new user approval or old-v135 qualification claim.


## Current-release submission decision 2026-09-22

- Earlier user authorization: deploy the policy to latest on league; deploy the policy to league that can beat richard's v135 even half the time to both players. it's important even while we work that we start beating him
- Current-game practiced policy: ranged-first public drafting, explicit skill points, actual-tick attack recovery, last-hit/XP positioning, equipment and purposeful portals. Exact BASIC passed current-engine both-color mixed A/B against deployed compat and later-draft guardrail, all VMs/replay/XP/score audited. Original target panel and its limitations remain preserved. Fixed rosters/correlated trajectories; no universal opponent, class or rank guarantee. Prior user league/latest and two-player authorization continues; this is not a new user approval or old-v135 qualification claim.
- Decision, exact version IDs, evidence deltas and rollback: `tmp/gota-targets-20260922/deployment/decision.json`.
- Validation: validated on 320 mixed A/B and later-draft games; submitting. No independence/significance claim from correlated streams.


## Current-release deployment verified 2026-09-22

- Both Aaron and Coach active, competing champions with exact BASIC `b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098`. Validation: submitted.
- Manual selection returned HTTP500 twice; readback confirmed unchanged old champion. The documented automatic selection route succeeded. Only the unselected failed-attempt membership was retired; receipts preserved.
- Receipt: `tmp/gota-targets-20260922/deployment/deployment-verified.json`.
