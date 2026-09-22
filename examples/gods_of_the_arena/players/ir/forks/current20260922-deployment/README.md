# Current-game policy deployed to both players

Verified 2026-09-22T08:38:01.146843+00:00. Both registrations use tested BASIC **b82c3799**, game **2026.9.21.5 / f776d5e**. Semantic IR and all gameplay evidence are in the adjacent `current20260922` bundle.

| Player | Version | Policy UUID | Active champion membership |
|---|---|---|---|
| Aaron | aaron-gota-micro0922:v1 | `f3f8baab-d02a-4f7f-8fc9-e1f050f967a7` | `lpm_e4c2be87-80db-4ef9-92eb-fe40eb4816ef` |
| Aaron's Co-play Coach | aaron-gota-micro0922-coach:v1 | `15b325b4-e9f3-487f-bd95-a059f92d20e2` | `lpm_f06eb86b-6fee-4fb3-809c-1ff1c08bcbbc` |

The user previously authorized latest-league deployment and both-player scope; the exact prior wording is recorded in `decision.json`. The new source passed 320 clean, full-audited mixed A/B and later-draft games against the deployed compat bytes. Both current XP-score gates pass. Old target gates remain frozen; Jordan356 appeared later and is untested. No #1 rank or universal matchup claim.

The manual champion endpoint returned HTTP500 twice. Readback confirmed the old champion remained active. Normal submissions with documented `auto_champion=always` succeeded. Only the unselected Aaron failed-attempt membership was retired before resubmitting identical bytes; the API represents that retirement as disqualified/inactive, not a gameplay failure. Coach and Aaron then became active competing champions. All original receipts and error logs remain in `tmp/gota-targets-20260922/deployment`.

Rollback references are saved. The manual selection endpoint was unavailable during deployment; `rollback-route-status.json` records this limitation. The prior versions remain registered, and no prior source or captured input was deleted.
