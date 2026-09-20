# Sampled field — population opponent IR

Native Python prior: [`population_20260919.py`](../../../examples/gods_of_the_arena/players/ir/opponents/population_20260919.py). This prior supports the Jordan comparison; it is not a validated league-wide strategy.

## 1. Header

Level population. 21 games, 15 policy versions, all before Jordan heldout cutoff. One earliest eligible episode per opponent-version × our observer side. Our policy is the same frozen relh154 IR. 198,677/1,076,818 living opponent hero-ticks visible (18.5%). Exact IDs and dates: [study-plan.json](study-plan.json).

## 2. Skills

Same seven observation motifs, definitions and local estimated affordances as the individual model. 6489 sustained starts, 4660 eligible choices; residual 6.2%. Population segmentation is recorded per episode; complete blocks are [population-observations.jsonl.gz](population-observations.jsonl.gz).

## 3. Preferences

The Python prior retains count-backed context distributions with stable `GotaField20260919_P_Oxx` IDs. They are provisional: no independent population validation split was reserved. The comparison baseline is Laplace-smoothed context frequency, masked by available motifs; contexts with n<8 back off globally.

| Context | Most frequent motif | Selected / n |
|---|---|---:|
| `mask_0_low_0` | `advance` | 4/4 |
| `mask_1_low_0` | `target_hero` | 345/456 |
| `mask_1_low_1` | `target_hero` | 17/49 |
| `mask_2_low_0` | `target_creep` | 1107/1115 |
| `mask_2_low_1` | `target_creep` | 17/17 |
| `mask_3_low_0` | `target_creep` | 970/1524 |
| `mask_3_low_1` | `target_creep` | 35/69 |
| `mask_4_low_0` | `target_structure` | 137/184 |
| `mask_5_low_0` | `target_hero` | 263/338 |
| `mask_5_low_1` | `target_hero` | 9/26 |
| `mask_6_low_0` | `target_creep` | 435/556 |
| `mask_6_low_1` | `target_creep` | 1/1 |
| `mask_7_low_0` | `target_creep` | 171/287 |
| `mask_7_low_1` | `target_creep` | 13/34 |

## 4. Goals — hypotheses

No population goal ordering is accepted. Contact/pressure labels inherit descriptive motif names only; goal validation n=0, confidence unestimated.

## 5. Beliefs (theirs)

No second-order beliefs inferred; distinguishable tests n=0, predictions=0, confidence unestimated.

## 6. Adaptation and deception

Different player versions and sides must not be read as adaptation by one agent. No population deception or causal adaptation claim; tests n=0.

## 7. Validation

As a frozen baseline on Jordan heldout choices: 690/1466 (47.1%); this is not a population-generalization test. All 21 tapes pass every original state hash. No proxy rollouts (n=0); usable=False; divergence unmeasured.

## 8. Unglossed

Uses the same five observer-binding extensions documented in the individual IR; no primary-glossary changes. Tagged blocks n=6,489.

## 9. Counter-strategy candidates

None: this is a comparison prior without an independently validated exploit. Candidate tests=0.

## 10. Provenance

Same pinned game, host view, own policy, guide and instrument as [individual IR](opponent.ir.md). Selection preceded behavior inspection and ignored outcomes. Policy-version composition:

- `relh-gods-of-the-arena:v154`: 2 episode(s).
- `gota-g002:v1`: 2 episode(s).
- `nancy-goa:v2`: 2 episode(s).
- `macromackie-gota:v4`: 1 episode(s).
- `black-kite:v16`: 2 episode(s).
- `gota-codex-side-aware-team-secondary-20260917:v1`: 1 episode(s).
- `khors:v1`: 1 episode(s).
- `richard-gods-of-the-arena:v93`: 1 episode(s).
- `red-kite:v34`: 2 episode(s).
- `richard-gods-of-the-arena:v99`: 1 episode(s).
- `gota-g003:v2`: 2 episode(s).
- `Polyworld GOTA base.bas:v1`: 1 episode(s).
- `gota-vanguard-rally-hold:v1`: 1 episode(s).
- `richard-gods-of-the-arena:v113`: 1 episode(s).
- `richard-gods-of-the-arena:v115`: 1 episode(s).

Episode IDs, creation dates, observation slots and versions are in the frozen study plan.
