# Patched-engine hero comparison

Engine **2026.9.22.2 / ffcedcd**. Selected research reference: **control**. This bundle itself does not deploy a league version. Read deployment receipts for live selection.

| Policy | Red score | Blue score | Aggregate change | Gate |
|---|---:|---:|---:|---|
| control | 2337.40 | 2701.97 | +0.0% | control |
| ranger | 2229.07 | 1715.95 | -21.7% | fail |
| crossbow | 2626.25 | 2382.32 | -0.6% | fail |
| warlock | 1238.45 | 722.88 | -61.1% | fail |
| arcanist | 1540.42 | 1264.67 | -44.3% | fail |

400 games, 40 per policy/color, one first-pick subject and nine frozen distinct players. All original sources are preserved. Mean integer XP score is primary; fort outcomes are diagnostics. Four-way selection and fixed rosters limit generalization. No universal hero tier, late-draft or #1 claim. Blue opposes relh; Jordan and Richard are allies there. Full picks/deaths/uncertainty and opposing-target scores: `evidence/review.json`.

Each subfolder contains editable `policy.py`, generated BASIC, and exact extracted IR. Use `python3 convert.py <variant> compile --out <new-directory>` or `extract --source <file>`; `python3 verify.py` verifies every pair and the evidence hashes offline. Captured inputs stay under the original raw study path in `evidence/raw-inputs.json`.
