# Local microplay policy

The [evaluated semantic IR](policy.ir.json) compiles exactly to [policy.bas](policy.bas).
It adds reachable finishing and guarded ally assistance to the preserved
Jordan268 macro controller. [finish.ir.json](finish.ir.json) is the finishing-only
ablation. `policy.py` exposes both dictionaries without duplicating their source.

In 160 held-out six-second scenarios, the composite reduced allied deaths from
60 to 50 and increased enemy eliminations from 239 to 243. Its additional teamwork
benefit occurred with automatic casting disabled; explicit casts remained
possible. Ten complete normal-game checks had no refinement activations, so
field benefit is unproven. This is a qualified local skill, not a league upgrade.

The subsequent [120-game hosted verification](../../../../../../docs/microplay/2026-09-20-hosted/README.md)
also found zero refinements against nine other players. All 40 enhanced-policy
games exactly matched both controls in full same-tape counterfactuals. These
skills have **no demonstrated field benefit**. The hosted report includes new
evidence-bearing IR versions with byte-identical BASIC; the original local
qualification artifacts remain historical evidence.

Read the [research report](../../../../../../docs/microplay/2026-09-20/README.md)
and [seven-layer research IR](../../../../../../docs/microplay/2026-09-20/research.ir.json)
for failed hypotheses, corrected units, full provenance, and limitations.

```sh
python3 examples/gods_of_the_arena/players/ir/forks/microplay/verify.py
```

The [instrument](../../../../../../games/gods_of_the_arena/instruments/microplay/README.md)
loads the hash-verified original compiler and registers the versioned microplay
contract. Existing bindings are preserved. Changes to range, assistance, or
crowding parameters need new evidence.
