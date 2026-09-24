# Current research contract

This workspace is a reset of the experiment baseline, not a claim that the old policy is better. Its engine is unmodified upstream commit `2c8db6ebe1dc785ce1eea87496505d1244ee4c44` (2026.9.23.4, replay 62). The research archive remains intact.

## Objective and measurements

Maximize expected individual `floor(max(0, XP - 200 * elapsed_minutes))`. Report mean score, productive-game frequency and mean score conditional on a positive score. The latter two explain the overall mean; neither replaces it. Wins, tower damage, neutral kills and survival are diagnostics. Neutral kills do not guarantee XP credit: credit also depends on the engine's eligibility and sharing rules.

Use matched responsive counterfactuals: identical engine, seed, roster and subject seat; other policies react to the changed behavior. Preserve failures rather than converting them to zero scores. Keep each hosted request at or below 100 variations and use the shared 100,000/day journal. A local simulator or guard fixture establishes mechanics and runtime validity, not hosted score superiority.

## Evidence boundaries

- `policies/previous`: previous deployed source `29f6d7e6`; a historical reference requiring current-engine comparison.
- `policies/deployed`: current live source `2fbd789b`; the baseline for improvement claims.
- `policies/weak-neutral`: source `c2321ead`; a coordinated nearby-neutral hypothesis for heroes other than Ranger and Crossbowman. Its effect is unproven until the frozen comparison completes.
- `opponents/khors-v180`: observations tied to version and source hashes, with explicit denominators and failed-opponent caveats. It is neither authentic source nor an executable reconstruction.

Historical coaching, old win-rate targets, old hero balance, and claims from different replay versions are retained as history. They are not premises for new score claims. Frozen conversion code exists to reproduce each policy; only the current engine defines mechanics.

## What motivated the reset

The latest deployed policy had a favorable narrow pilot against a research parent, not a broad matched comparison against the preceding deployed policy. The poor league-round screenshot also mixes heroes, seeds and rosters. Neither comparison alone establishes whether the deployment regressed. The current study compares all three policy sources across every side and team seat, with prospective score rules and a separate confirmation requirement.

## Continuing from a fresh conversation

Read `manifest.json`, this file, the latest `RESULTS.md` if present, and `../AGENTS.md`. Check shared campaign ownership before writing. Do not restart the obsolete archive worker. Consult historical notes only when their engine/version and hypothesis are relevant; do not load the entire research history as current instructions.
