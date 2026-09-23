# Lane recovery: practiced candidate

This snapshot records local qualification before the independent 320-game
comparison. It is not a deployment or competitive score claim. Read the
[current experiment](../../../../../../games/gods_of_the_arena/experiments/2026-09-23-lane-recovery.md)
for subsequent hosted results; preserve this initial record.

During a health-only retreat, the policy stays safely in lane while a useful
self-heal or potion works, then resumes farming at 60% HP and 20% mana. A brief
healing cooldown can be awaited; the hold is bounded at 12 seconds. An affordable
missing core item preserves the base trip for shopping. Immediate danger,
unavailable healing or exhausted waiting time retains the existing escape.
Draft, targeting, blue central route, buyback and committed portals are unchanged.

All **582 local checks** and **16 complete native games** pass. In both-color
Druid fixtures, the hero heals from 135 to 297 of 466 HP and resumes advance
without base walks, including after a three-second cooldown. Already recovered
heroes cancel the old base path; insufficient potion healing falls back after
the effect ends. The native fixtures cover runtime with responsive reference
bots, not the strength of hosted rival policies.

The previous broader field-sustain rejection is preserved separately. This
candidate starts from deployed blue-center. The initial fixture errors—an absent
baseline memory field, shopping completion resetting its flag, and an incorrect
assumption about potion capacity—are preserved in `fixture-expectations-r1`.
Correcting those expectations did not change the candidate policy bytes.

- [Semantic IR](lane-recovery/policy.ir.json), [generated BASIC](lane-recovery/policy.bas), and [manifest](lane-recovery/manifest.json).
- [Actual-tick checks](lane-recovery/evidence/practice.json), [local summary](lane-recovery/evidence/local-summary.json), and [native results](lane-recovery/evidence/native-result.json).
- [Frozen hosted plan](lane-recovery/evidence/hosted-plan.json) and [capture hashes](lane-recovery/evidence/session-input-manifest.json).

Run `python lane-recovery/verify.py`. From the pair directory, use
`python convert.py compile --out /new/path` or
`python convert.py extract --source policy.bas --out /new/path`.
The locally reviewed semantic IR regenerates the exact tested policy.

Source: `2878f3e962b9b8ac28690a939317508c6df38a55545be292b9846c91095fef45`.
Reviewed IR: `2dde8d84cac98a28eecc71bafe26837254302508fec65a3761e27ca6e16180fe`.
Binding: `gota-bassy/lane-recovery-2026-09-23-r1`.
Engine: `2026.9.22.3`, commit `1b70894436b7ffdcd0d421b6b32c2415c9c8bfde`.
Raw evidence: `polyworld/tmp/gota-lane-recovery-20260923`.
