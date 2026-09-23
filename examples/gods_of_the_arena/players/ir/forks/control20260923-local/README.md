# Release61 control legality fork

Source `303eeddb9d0bb3a63d905fd3a8067d6c358cbcefac066dc68e07521a75be47a5`
inherits deployed `29f6d7e6`. The new binding guards silenced casts in combat and
Druid lane recovery while preserving legal attacks, items, movement and rooted
healing. It refreshes automatic-casting, balance and control semantics for61.

[Reviewed seven-layer IR](control-legality/policy.py),
[generated BASIC](control-legality/policy.bas),
[manifest and evidence hashes](control-legality/manifest.json).

104 paired status fixtures remove388rejected calls with otherwise identical
commands/gameplay samples. Eight complete responsive native games pass replay,
VM and integer-score checks. All four paired subject score deltas arezero.
This is a verified compatibility fork, **not a score-qualified league replacement**.
No hosted requests or league writes occurred. The existing champions remain live.

[Full release audit and tactical hypotheses](../../../../../../games/gods_of_the_arena/release-audits/2026-09-23-crowd-control/README.md).
The initial pair and complete raw traces/replays are preserved under the audit's
input manifest. The reviewed IR updates evidence without changing tested BASIC.

Run `python3 control-legality/verify.py`. Use `control-legality/convert.py compile`
or `extract --source control-legality/policy.bas` with a fresh `--out` directory.
New executable changes require fresh evidence and paired current-engine controls.
