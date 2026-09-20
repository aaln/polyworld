# Research starting point — 2026-09-18

The user's active task is continuous GotA self-improvement, immutable accepted
snapshots, IR lineage, broad generalization tests, and a three-hour restart.
Both existing live champions use relh154-legacy (same BASIC SHA
`b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9`).
The bootstrap snapshot is that validated incumbent. Current known weaknesses:
red defense can remain committed too long; red g002 is variable (~20–24/40),
red black-kite v16 was 0/40. Blue performance was strong. No guaranteed wins.

Source is the CLEAN release 2026.9.16.5 at commit
f2ab9598d8f8001b6beae3e66404e341770c803f. The user's original main has gameplay
changes; never use it to claim hosted parity. Verify current live source each run.

Recent coaching source, preserved:
`/Users/aaln/Documents/Policy Loops/sessions/2026-09-18t23-13-38-249zf154ac`.
Study: `RUN/coached-lanes/r5-coach-split-0918`, where RUN is
`/Users/aaln/experiments/softmax/gota-research-20260916`.

The coaching asked for at most two defenders after clearing an intrusion and a
three-hero center counterpush. Full own-policy replay reconstruction found accepted
wait orders with a five-minute deadline refreshed by a survivor. No physical
collision deadlock or coordinate-side bug was proven. Examples are repetitive
defensive decisions, not arbitrary engine failure. Game source says walkTo cancels
attack; accepted movement is not proof of arrival. Enemy unseen is not dead;
structure objectAlive means exposed, HP means standing.

Six coordinated coaching variants completed 180 local games and 120 hosted games:
- fixed support/tank-healer rear groups: local10/12 and9/12 vs11/12; rejected.
- require assembled team and quiet5/15sec: local9/12 and10/12 vs12/12; rejected.
- mobile supports30/45: local10/12 each vs10/12 but gains on default traded for
  center-proxy draws. Full traces show supports actually join attack; mere release
  is insufficient to secure a fort win.
- HOSTED final RED g002: incumbent24W16L; mobile30 13W0L27D; mobile45 0W0L40D,
  all40 games per arm, every replay/runtime audit complete. Neither qualifies.
  Do NOT adopt these as parent or say they beat the incumbent.

Mobile results: `RUN/coached-lanes/r5-coach-split-0918/mobile-followup/discovery-result.json`.
The old WORKING_CONTEXT header may say running; completed artifacts supersede it.
No followup flank experiment has started. A possible new hypothesis is preserving
wave support and choosing an outer lane after safe defensive release, rather than
forcing three/five heroes through the contested middle. This is only a proposal;
read failures and choose scientifically. There are many older failed red release,
guard/watch and fallback variants in lab closed_levers.md: do not repeat blindly.

Tools: policy_ir.py / binding.py implement compile/extract seven layers. New
contracts must be new names; old policies remain reproducible. Snapshot compiler
archives include all imported local modules, unlike the old minimal bundle manifest.
Native replay probe: RUN/r5/replay-coach-split-probe with PROBE_POLICY, PROBE_SLOTS,
PROBE_SAMPLE_EVERY; compare all commands and state hashes. Macro decoder and
structure-damage decoder also exist. Do not fabricate private opponent source.

Hosted API helper hosted_wave.client uses existing auth. Never expose tokens.
middle_rush_parallel_checks.prepare with an EXACT rival UUID only dry-runs;
without UUID it creates an XP request to resolve the name, so don't use that mode.
Create via the campaign xp-create command, then collectors may reuse the receipt.
The ten-player collector needs single-subject roster support; the five-hero
middle_rush summarize assumes five gear heroes and cannot be used unchanged.

Predecessor policies and tests remain useful, but most historical evaluators have
hardcoded assumptions, old CURRENT IDs, or target-specific gates. Inspect before
reuse. Always record actual pinned sources, release, roster, side and hashes.
