# September 21 policy development

This isolated instrument targets published **2026.9.21.5**, upstream
`f776d5e55d439706a8d49878d17d7ba1f6a1f7ce`. It preserves the previous engine,
policies, compiler, captured coaching inputs and research history. The root
checkout has divergent human-play UI changes; the clean engine lives in a
separate worktree, with every dependency fixed by its lock file.

The live league ranks heroes by `max(0, total_xp - 200 * ticks / 1440)`.
`ticks` includes the draft. Fort wins are recorded separately. The old binary
win score and inventory-based opponent identities are not carried into this
policy. New drafting means either team can receive any hero class.

`contracts.py` binds drafting, lifecycle and skill spending, bounded observation,
equipment, recovery, tower safety, combat and lane advance. `build.py` constructs
the seven-layer Python IR and generates BASIC through the existing repository
compile/extract workflow, isolated for the Bassy contract. Runtime checks use
the actual new engine, not the structural parser as an execution oracle.

Typical fresh setup from the repository root:

```sh
python3 games/gods_of_the_arena/instruments/week20260921/bootstrap.py --nim /path/to/nim-2.2.10/bin/nim
python3 games/gods_of_the_arena/instruments/week20260921/test_ir.py
python3 games/gods_of_the_arena/instruments/week20260921/build.py --name lane
WEEK_POLICY="$PWD/tmp/gota-week-20260921/candidates/lane/policy.bas" tmp/gota-week-20260921/bin/scenarios
```

Frozen candidates refuse overwrite. `local.py` consumes the captured published
game configuration and runs complete responsive matches followed by independent
action-tape replay. `episode.nim` measures all ten VMs, draft completion, skill
ranks, XP, purchases, deaths and final objectives. `command_hash.nim` measures
duplicate complete command streams independently of replay headers and seeds.

`hosted.py` registers inert versions and journals evaluation requests with the
existing campaign's global budget and creation locks. It verifies the new game
pin and preserves the old accepted campaign's engine/configuration. A temporary
pause of the previous writer precedes its hosted work. It never selects a league
champion. Requests use stable idempotency keys; restart the same script to resume
existing batches and artifacts after interruption. Raw replays and API details
stay under ignored `tmp/gota-week-20260921`; publish only sanitized evidence.

The [experiment](../../experiments/2026-09-21-week-policy.md) records prospective
thresholds and distinguishes native diagnostics, hosted comparisons and
mixed-team qualification.
