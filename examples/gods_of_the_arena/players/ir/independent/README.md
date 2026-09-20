# Independently derived base IR

`base.ir.json` is a fresh seven-layer causal model derived from `../../base.bas` (the player source at `players/base.bas`) and the real host/simulator. It is not cloned from an existing IR, and `../independent_ir.py` does not import the existing binding or compiler. This is independent construction by the same agent/session, not a blind independent review. The syntax parser and runtime are shared and separately acknowledged.

The new model explicitly distinguishes decision-start self data, live queries, earlier inventory flags, ordered cumulative actions, engine intent, command return and realized effect. Behavioral goals are interpretations; game score comes from the game contract. Only the documented baseline family and typed ratio/waypoint parameters are editable; other changes fail closed.

Generate the fresh baseline and lift the original source without a parent:

```sh
python3 examples/gods_of_the_arena/players/ir/independent_ir.py
```

Run the saved review after building the published-runtime temporal probe:

```sh
python3 examples/gods_of_the_arena/players/ir/independent_review.py tmp/gota-ir/independent-20260910 --reconcile
```

The saved plan freezes original/regenerated inputs, two full-game seed pairs, and controlled probe scripts. Full tapes matched on seeds 65000 and 65001 (269,409 action positions and 29,407 tick states). All 34 tests passed, including 500 actual-VM scenarios and unmarked symbolic edits. Five engine probes validated timing/effect claims; they are synthetic controlled states, not competitive games.

[Report](../independent-20260910-report.html) and [machine-readable evidence](../independent-20260910-result.json). Current base, Duelist and Reserve IRs absorb the supported facts; their executable BASIC stays unchanged. Original pre-reconciliation IRs and new immutable bundles live under `tmp/gota-ir/independent-20260910/{before,reconciled}`. Historical verification hashes describe their historical versions; use those frozen bundles for reproduction.
