---
id: 2026-09-20-richard-growth
status: rejected
---

# Richard source-informed growth experiment

Final local screen: all 16 games were valid. Both new candidates won 2/2 blue
games and 0/2 red games, matching the critical60 control; the older deployed
control won 0/2 on each color. Neither candidate met the frozen requirement for
an extra red fort win, so neither was nominated. See the preserved
[screen verdict](2026-09-20-richard-growth/screen-verdict.json) and
[per-game results](2026-09-20-richard-growth/local-results.json). These are local
results, not hosted qualification. The original study and raw inputs remain in
`tmp/gota-ir/richard-growth-20260920`; the prospective design below is preserved.

Hypothesis: our red post-hit outward movement and low early damage purchases reduce attack conversion; group-wide remembered recall further removes income opportunities. Adopting in-place verified-hit recovery and Richard's observed damage/HP build, coupled with a current-distance limited defense assignment, can create more rewarding attacks while retaining base defense. These are coordinated variants, with a micro/economy-only arm to separate the additional recall allocation effect. Blue critical60 is held byte-equivalent by branch.

Exact source evidence f48bb0 Richardv135, source audit and 63.4% Ranger hero-kill XP. Closed levers reviewed: prior late finite-defense/scout/focus bundles and gear-only screens failed; new distinction is from-start in-place recovery versus outward movement, combined with current red recall allocation and actual responsive Richard opponent now available. No synthetic opponent model is used. No unchanged failed fusion is rerun as a candidate.

Preliminary design: first reproduce two existing exact hosted controls locally using their seeds/config and all ten responding VMs. Then native scenarios for recovery freshness, ordered equipment/host attempts, role tie/visibility/death and blue parity; dense scenes <=19,000 instructions/50,000work. Freeze exact BASIC/IR hashes before screening. Initial screen: deployed, critical60 reference, micro/economy candidate and combined growth candidate; two fresh seeds per color versus exact Richard (16games). Inspect fort outcomes, per-class hits, XP, levels, purchases and deaths at fixed 2,000/4,000ticks, plus complete terminal outcomes.

Nomination requires all native/runtime checks, at least one extra red fort win over both controls, no loss of critical60 blue wins, and a measured increase in red basic-hit/XP conversion at the fixed early horizons without increased red deaths. A faster loss cannot qualify through lower terminal deaths. If no candidate qualifies, preserve the null results and diagnose a real first engagement before a separately frozen refinement. Local calibration/diagnosis cannot alone authorize deployment.

Hosted final candidate gates retain Richard>=30/40eachcolor,+8aggregatevsfreshdeployed; Alex>=30/40each and no per-color regression; Jordan>=38/40each; pinned field8percolor candidate/control with<=2lostwins/rival/color and no aggregate regression. Fresh exact version readbacks, all10VM/fullreplay audits. Uniform5v5/repeated trajectories do not establish broad ten-player generalization. No new upload or XP before local diagnosis/runtime admission.

Adversarial critique: more forward action can feed Ranger; in-place recovery may sacrifice useful kiting; healing expenses can still starve equipment; nearest-defense roles may switch across sequential decisions and are not a strict simultaneous cap. Fixed horizons condition on survival; earlier terminated games retain terminal values and termination status rather than disappearing. Each outcome belongs to the whole bundle; do not attribute it to individual changes without ablation.
