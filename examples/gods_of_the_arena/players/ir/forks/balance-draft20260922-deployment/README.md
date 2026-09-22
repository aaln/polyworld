# Crossbowman-first policy deployed to both players

Verified 2026-09-22T17:14:35Z and read back again after placement. Both registrations use tested BASIC **7631fa32**, game **2026.9.22.2 / ffcedcd**. The semantic IR, compiler and complete evaluation are in the adjacent [policy bundle](../balance-draft20260922/README.md).

| Player | Version | Policy UUID | Active champion membership |
|---|---|---|---|
| Aaron | aaron-gota-balance0922-crossbow_draft:v1 | `0dc85085-cb5b-4de6-8d50-e8fd043d0b5f` | `lpm_e389bf69-ec4e-4b2a-9600-f1ded7db9c3b` |
| Aaron's Co-play Coach | aaron-gota-balance0922-coach:v1 | `35c85505-1977-4bad-b4ea-f1473aaa79dc` | `lpm_b4cbe4a1-76a2-4c3d-8829-05b49bddb02d` |

The user's existing authorization covers deployment of the latest validated policy to both players. After the 400-game screen rejected the coordinated mirrored controllers, an 80-game Crossbowman draft-only follow-up scored 2888.975 red / 3273.5 blue versus reused current-engine controls 2337.4 / 2701.975: **+22.3% overall**. Both prospective score conditions passed; all 480 games passed source, VM, full replay, lifetime XP and integer score checks. This fixed first-pick-roster result is not independent confirmation, a universal hero ranking or proof of #1.

Normal league submissions with `auto_champion=always` selected Coach, then Aaron. Both were verified competing, active and champion. Upload content hashes and exact version identities match the tested source; all 80 hosted episode specs verify Aaron's runnable hash. Coach is a byte-identical separate-player registration, not independent performance evidence. Fresh readback still found relh161, Jordan411 and Richard153 as champions.

Rollback versions are Aaron `f3f8baab-d02a-4f7f-8fc9-e1f050f967a7` and Coach `15b325b4-e9f3-487f-bd95-a059f92d20e2`; exact b82c3799 source remains in `../balance20260922/control/policy.bas`. Prior manual champion selection returned HTTP500; normal automatic placement succeeded. Prior registrations and all captured inputs are preserved. This records placement, not later league-round results.

Curated receipts omit signed URLs. `raw-input-index.json` hashes the original private captures at their existing paths.
