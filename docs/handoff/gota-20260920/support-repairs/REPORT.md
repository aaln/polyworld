# Standalone red caster support: completed repair experiment

Neither restoration passed its pre-registered local screen. Both compiled correctly and activated in the real-VM fixture, but neither changed a single canonical game command from the deployed policy across the six complete cases.

| Source | Red wins / 3 | Blue wins / 3 | Total wins / 6 | Deaths | Decision |
|---|---:|---:|---:|---:|---|
| deployed | 0 | 3 | 3 | 25 | Control |
| anchored | 0 | 3 | 3 | 25 | Reject standalone restoration |
| unanchored | 0 | 3 | 3 | 25 | Reject standalone restoration |
| historical_anchor | 1 | 3 | 4 | 39 | Historical reference only |

All 24 games passed full replay hash/action, score, native VM budget and equipment checks. Each case pins the same seed, side and opponent across sources. The opponents were default, deployed and historical anchor; these games do not measure Richard135 or Alex directly.

All 6 complete red source reconstructions matched 108,938 own commands and every state hash. Expanded support beyond the old 10-tile range executed zero times. The observer extension is behind existing active-defense and idle-target gates; merely restoring its code did not produce the intended gameplay intervention in this sample.

The exact historical anchor won one additional local red game but had 39 deaths versus the frozen limit of 30. It was a descriptive reference and is not a qualified replacement. Its historical Alex red score is only 4/40 against the same current opponent UUID.

The useful next experiment must change when or where support becomes available—for example a separately attributed interaction with caster transit or a selective timely defense response. Do not spend another hosted batch on an unchanged standalone restoration from this screen. The existing supervised worker owns those followups and all hosted requests.

Evidence: [frozen plan](plan.json), [all results](local-results.json), [verdict and source proofs](verdict.json), [canonical command comparison](command-comparison.json), [real-VM checks](vm-proof.json). Updated Python IR records the measured failure in [anchored feedback](feedback/anchored/policy.py) and [unanchored feedback](feedback/unanchored/policy.py), with byte-identical BASIC.

Scope: local diagnosis and advancement rejection only. Six cases are not independent league trials. No hosted XP or live policy change was made by this isolated experiment.
