---
id: 2026-09-23-unit-farming
policy: unit-farming
baseline: druid-lane 29f6d7e6
candidate: 1238ec73cfd85d2f157b7ea9c639679c9c24110f54bb49e684515f3999ffa10d
status: refuted
hypothesis: Excluding buildings from deliberate target selection redirects attacks toward recurring hero and creep XP, improving score after time cost.
decision_rule: Fresh400 games,50 per source/context; overall mean at least10% higher with positive lower95% bootstrap gain, each context at least95% of control, nonzero mean at least5% higher, nonzero frequency no lower, productive(score>=500) frequency strictly higher, all audits pass and current field stable.
evals: ["xreq_77a1d248-182c-441e-96c8-642ef9f1f2fa", "xreq_a25e4992-fe72-4310-8f05-a39434489175", "xreq_01e5c8c2-0a17-4ebc-8eaf-c278e29915f3", "xreq_eac410fe-ad7d-4863-8247-93363d34837f", "xreq_59253e1a-f655-4a95-b23a-ab67c5e4c414", "xreq_e42b2b58-c62c-406f-beca-df88467a0f93", "xreq_9874b519-8636-4326-ac57-cae728c85d4e", "xreq_8aa8c596-7531-4575-983c-8eef20f9496c"]
---

# Hypothesis

User supplied episode ereq_e3471c64-b38e-4bfc-927e-e0e3f3076d9d and the aggregate building-target screenshot. khors179 scored7781 from11892XP:6342creep and5550hero. Coach scored1660 from5771XP, including500structureXP after18321structure damage. The direct comparison is confounded by classes, teams, positions and one failed opposing VM. The screenshot's0.0% versus39.3%/39.8% motivates a test; it does not establish causality or mean buildings have no reward.

The current engine awards150XP per hero kill,100XP to a hero killing a building, and500XP to each teammate when the enemy god falls. Score is floor(max(0,XP-200*elapsed minutes)) including draft. Creeps also share proximity XP. The proposed gain is opportunity cost, not zero building rewards.

# Design and critique

Closed levers reviewed: prior all-target score changes and guarded siege failed their own rules. This is a distinct single intervention: only visible living enemy heroes(kind2) and creeps(kind3) may enter best-target ranking. Retain all structural observations for safety, routes, keep defense and portal anchors. Current host attack-move automatically acquires creeps only. Incidental spell damage to structures is allowed; no claim of exactly zero damage.

The previously prepared single-scroll outbound candidate is preserved and deferred before upload or hosted spending. It is not combined here. Only the observe executable changes; every other Druid-parent skill is byte-identical. Regenerate via semantic IR and the versioned binding, then compile/extract equality.

Use current published d6827a4/replay59, source29f6d7e6 controls, natural drafts and fixed mixed rosters. First run actual-host mixed-target, building-only, lethal-hero/creep and both-color/all-class scenarios, inherited safety fixtures and complete responsive native games. They establish runtime/mechanism, not competitiveness.

Then400fresh games,50 per source/context:redlead,bluelead,redlate,bluelate. Freeze rival UUIDs and sources; freshly resolved khors180/Richard195/Jordan411 (v179 is the coached episode; the opponent upgraded before this comparison). One subject per game, rotate whole teams, no reused score controls or outcome-dependent class filters. Independent seeds; bootstrap whole games within context10000times. Nonzero mean alone is selection-sensitive, so qualify it jointly with overall mean and frequencies. Report all VMs; any invalid game fails qualification and is retained, not silently replaced. Duplicate streams and class mixtures are disclosed. Sample size can be inconclusive; no extension after outcomes.

Risks include walking into towers after skipping a target, reduced gold, losing valuable structure last hits and the500god reward, and longer games whose extraXP fails to cover time. Native checks and hosted decomposition must expose these. A long game is not itself a success. The current controller's out-of-range casts remain a separate hypothesis.

# Predictions and decision rule

If true: deliberate building attacks disappear, hero/creep XP rises enough to compensate lost structure/objective XP, and overall mean, nonzero mean and productive-game frequency pass the frontmatter rule. If false: work shifts into travel, danger or idle periods; retained structure value dominates; or scores fail preservation/gain thresholds.

Metrics: overall mean, nonzero conditional mean and frequency, score>=500 mean and frequency, per-color/draft contexts, hero/creep/building/godXP, elapsedminutes, deaths, kills, class, and rejected casts. Competitive score gate uses the exact frontmatter rule, with source/VM/full-replay/XP/integer-score verification for every game. Mechanism subset: first four lexical episode IDs per arm,32 games, chosen before detailed decoding; compare actual structure-target commands and basic damage. Preserve all outcomes. No posthoc threshold changes or source edits after freeze.

# Result

All400 fresh games passed ten-source/VM, full replay-state, totalXP, XP-source and integer-score checks. Every50-game cell has50distinct command streams. The game and all fixed champions stayed unchanged.

| Context | Baseline mean | Unit-only mean | Change |
|---|---:|---:|---:|
| Red lead |2725.00|1668.00|−38.79%|
| Blue lead |3897.84|3256.72|−16.45%|
| Red late |39.30|11.64|−70.38%|
| Blue late |197.16|30.82|−84.37%|

Overall mean1714.825→1241.795: **−27.58%**,95% gain interval[−38.30%,−16.07%]. Nonzero mean2834.42→2459.00; nonzero rate60.5%→50.5%; productive(score>=500) rate54.5%→38.0%. Productive-only mean3127.80→3201.14 rises, but its95% difference interval[−341.20,+476.55] includes zero and many more games fall below the threshold. This does not satisfy the joint objective.

In the32-game preregistered diagnostic subset, deliberate building attack commands fall1813→0 while unit attack commands fall4481→4366. Eliminating structure actions alone does not redirect that effort into more unit attacks. Incidental spells and changed movement remain distinct mechanisms.

662candidate checks,164baseline checks and16native games passed before spending. Two completed baseline blue-lead games returned404 for ancillary text logs; their error receipts are preserved. Both had exact replay/spec/results and ten clean exit codes; neither was omitted or replaced. The collector amendment changed only text-log availability, not mandatory audits or policy/decision rules.

The user permanently raised the shared daily allowance to100000 during the trial. Its400-game sample and prospective thresholds stayed unchanged. The first report had an inherited outbound-return narrative label; its numeric-identical corrected report and original are both preserved.


# Verdict

Refuted for this exact unit-only targeting intervention and fixed current-release roster. Every context fails preservation and both primary/productivity gates fail. Do not deploy or rerun unchanged; retain the Druid incumbent. This does not refute selective short building finishes or coordinated farming navigation. The user proposed a distinct selective-finish candidate before the full trial ended; it requires its own fresh controls.

Portable evidence: examples/gods_of_the_arena/players/ir/forks/unit-farming20260923-hosted. Original raw captures remain in tmp/gota-unit-farming59-20260923.
