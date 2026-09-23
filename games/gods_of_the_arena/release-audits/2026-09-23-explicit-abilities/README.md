# Explicit abilities: release60 contract and policy impact

The creator's change removes **all automatic ability casting**, not only casts
against creeps. Healing, restoration, slot0 and ultimates now require explicit
`castTarget` or `castPoint` commands. Items already required explicit use.
Basic attacks remain automatic; idle acquisition also expands from creeps to
visible attackable heroes and exposed structures. Walking still suppresses it.

Verified against the [published release](release.json),
[upstream source](https://github.com/Metta-AI/polyworld/commit/fd315c8fa30f8923c7a7709a577c40ac071b1c2a)
and [live league manifest readback](live-readback.json) at
**2026-09-23T18:37:29 UTC**:

- Game `2026.9.23.2`, coworld `cow_f2dcdbcd-f984-445b-af5b-ee9481a7f362`.
- Engine `fd315c8fa30f8923c7a7709a577c40ac071b1c2a`; replay60/format6/outer2.
- Bassy `b25e0efef3fec0bd86ed3154659c0762a7158bd3`; other locked dependencies
  are unchanged. The earlier Bassy checkout is preserved separately.
- `Hero.manualSpells`, replay action14 and automatic spell helpers are removed.
  The score, balance stats, draft, portals and skill-point rules are unchanged.

## What it changes for our policy

The incumbent already casts explicitly; it does not become a basic-only bot.
Its generic combat rule attempts abilities0–3 when a target is selected and no
earlier rule stops processing. However, retreat and no-target situations can
bypass that rule. The old engine could supply healing independently.

Twenty controlled fixtures run the unchanged incumbent, all ten classes on both
colors, using **normal engine vision**, 29%HP, full mana, learned rank1 abilities,
four core items and no consumables. They assert that no enemy target is selected
throughout180real ticks. [Full fixture results](healing-probe.json).

| Hero | Explicit heals released | Self-healing | Behavior, both colors |
| --- | ---: | ---: | --- |
| Vanguard | 0 | 0HP | Walks home despite healing abilities |
| Death Knight | 0 | 0HP | Walks home despite available Chalice |
| Druid | 3 | 212HP | Dedicated lane recovery heals and exits retreat |

Source inspection also finds that our generic casting loop handles healing and
damage but **never mana restoration**. Arcanist and Warlock's restoration abilities
therefore need explicit handling. This is a source finding; the full-mana fixtures
above do not measure low-mana recovery or its score impact.

These are mechanism fixtures, not league score measurements. Preliminary probes
with forced visibility are retained in the raw input manifest but excluded from
these findings: full visibility exposed distant structures, while zero visibility
incorrectly hid the caster's own target. The accepted fixture uses ordinary vision.

The [seven-layer mechanics/coaching IR](mechanics-and-coaching.ir.json) records
the verified contract separately from proposed executable changes:

1. Evaluate safe self/ally healing and useful mana restoration before retreat and no-target stops, while
   retaining the portal channel lock and useful shopping returns.
2. Cast with correct ability range, shape and target type. The upstream baseline
   now fixes ally healing, tracking projectiles and damaging-ring placement.
3. Reserve scarce mana and charges for useful opportunities. Efficient creep
   last hits or wave clearing can still justify spells; a blanket ban is not
   established by the patch.

Failed explicit casts still do not spend mana/charges/cooldowns, but there is
**no automatic ability fallback** to compensate for omitted or invalid calls.
Count accepted spell releases, damage/healing and eventual XP-minus-time.

## Validation and evidence scope

- Upstream `test_gota_spells`, `test_gota_attacks` and `test_gota_base` pass on
  the pinned new engine. Checks cover no automatic abilities/items, explicit
  resource consumption for all40abilities, basic acquisition and updated baseline
  spell behavior. [Recorded outputs](tests/).
- All20incumbent healing fixtures pass runtime/scene checks; the healing gaps
  above are findings, not assertions that those behaviors are desirable.
- Four complete native games with one incumbent and nine updated upstream bots
  pass all ten VM checks, full replay hashes and all40integer score checks.
  Both colors and two subject seats are exercised. This is runtime evidence,
  not a comparison against current relh/khors/Richard or a promotion gate.
  [Native results](smoke.json), [frozen plan](smoke-plan.json).
- The exact incumbent remains
  `29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36`.
  No policy was uploaded or deployed, and no hosted games were requested.

The earlier relh169/Richard174 source identities remain valid, but their score
and activation cohorts used older engines with automatic spells. In particular,
relh's frequent combat modes0/8 did not issue general explicit combat spells in
the prior eight traces; only separate special-case code such as the Lich cast
could do so. New trajectories may activate different modes. Re-evaluate these
opponents before treating their historical strength as current.

All earlier replay59 reports, IR, captures and failed transfers are preserved.
This amendment supersedes their “current engine” and fallback assumptions for
new work; it does not rewrite their outcomes. The next competitive comparison
requires fresh replay60 controls and a frozen explicit-casting candidate.

## Reproduce

Use the isolated engine checkout and dependency tree recorded in
[checks.json](checks.json). The three instrument scripts are at
[`instruments/explicit20260923`](../../instruments/explicit20260923/).

```sh
python3 games/gods_of_the_arena/instruments/explicit20260923/check.py
python3 games/gods_of_the_arena/instruments/explicit20260923/smoke.py
python3 games/gods_of_the_arena/release-audits/2026-09-23-explicit-abilities/verify.py
```

Preserve prior runtime captures before rerunning instruments.
[Input hashes](input-manifest.json) retain the original request, live readback,
fixtures, corrected attempts and native replay files. [Scope](scope.json) records
the distinction between game readback, old membership readback and qualification.
