# Town portal coaching and khors:v114 comparison

Current host: `2026.9.22.2`, commit
`ffcedcd866c4d31924361ed4baff2b7a6d3aba67`. This research branch retains
historical engine files: build instruments in the isolated current engine.
The raw study is `../polyworld/tmp/gota-portals-20260922` from the research root.

`policy.py` edits the semantic IR and current host bindings together, then
compiles the coordinated controller. The final candidate is r3,
`db71abb37180a06a432ac71c3c5d6802be2ba2c1b2d782b151336beacd8b1520`.
Failed r1/r2 and all captured coaching inputs are preserved. The portable pair
contains its own compiler/binding and supports `convert.py compile`,
`convert.py extract` and `verify.py`; changed source invalidates inherited claims.

## Instruments

- `practice.nim`: 84 actual-tick portal cases on red/blue and Ranger/Crossbowman.
  Uses `WEEK_POLICY=<absolute BASIC>` and `PORTAL_ENFORCE=1` for assertions.
  Artificial visibility isolates public threat guards; full games retain fog.
- `events.nim`: complete replay hashes, portal starts/completions/interruptions,
  keep-to-home starts and low-health field ticks. Home is the actual initial
  spawn. A landing within 15 tiles defines home-directed travel. Ready-scroll
  field time includes unsafe cases and is not a count of missed safe recalls.
- `economy.nim`: exact replay XP attribution, kills, purchases and rejections.
  Its totals reconcile to host lifetime XP. Evaluator-only hidden information
  must never become a live policy input.
- `study.py`: original 160-game plan, prepared but superseded before creation.
  Do not run it; it lacks the user's subsequently named khors:v114 target.
- `khors.py`: revised 160-game A/B, exact opposing khors:v114 and fresh controls,
  both colors with teams rotated together. `--prepare` dry-runs schema without
  spending; execution uses the existing shared reservation journal. Sequential
  hosted batches can overlap local audits only after a batch drains.
- `report.py --watch`: streams complete portal reconstruction and then computes
  prespecified score gates, rival comparisons and whole-game bootstrap intervals.
- `dashboard.py`: read-only progress at `http://127.0.0.1:8851`.
- `finalize.py --name <new-pair> --hosted-dir hosted-khors114`: saves exact bytes
  with reviewed result feedback. Refuses to overwrite previous bundles.

Use the existing `balance20260922/bootstrap.py` to restore the exact engine and
locked dependencies. Copy these Nim sources into that engine's
`examples/gods_of_the_arena/tools/`. Build with Nim 2.2.10, the locked
`POLYWORLD_DEPS`, `-d:headless -d:release -d:replayEvents --hints:off`.
Keep new binaries and provenance separate from earlier captured builds. Replays
use `--replay <file>`; the full-match auditor is the existing `episode-v2`.

## Evidence boundaries

All 84 portal cases, 126 broader class/runtime checks and eight complete native
games pass. The native score outcomes are mixed; those games validate behavior
and runtime, not competitive improvement. Original session recordings and the
user's supplied episode have different visible rosters and remain separate
evidence. All 33 captured inputs are unchanged at original and copied paths.

The user authorized exactly 160 additional games for September 22, increasing
that UTC day's effective cap from 1600 to 1760. Normal cap remains 1600 on other
days. The cap record and previous configuration are preserved in raw `budget/`.
No script here selects a league champion. Keep the incumbent until measured
improvement passes the frozen score gate; report khors superiority separately.
