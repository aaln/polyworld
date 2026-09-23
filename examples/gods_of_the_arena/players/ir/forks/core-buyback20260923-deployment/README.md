# Core buyback deployment

Both authorized players were verified **competing, active and champion** at
**2026-09-23T01:35:32.222011+00:00**, with source **67fdcd5d0e8692138655c5f5ca93c98ec723690665eb1ca0fe412cb630a99024** and reviewed
IR **c1a5839bcfe2c4a155f6ee76de78fb6a86d59601e1e051dafe62bac5bb7b5b20**.

- Aaron: `aaron-gota-buyback0923-core-buyback:v1`, `30a0e469-8c2f-450c-b3bc-4a687a6c74e3`.
- Coach: `aaron-gota-buyback0923-coach:v1`, `2013aad3-a754-4e31-8cea-727aa6c3a6b1`.

The [validated pair and full comparison](../core-buyback20260923/README.md)
passed400fresh held-out games: +30.18% individual score, red+22.97%,blue+39.79%,
95%aggregate gain interval[+16.10%,+46.54%]. All400all-ten source/VM/replay/XP
and integer-score audits pass. Richard174 was outscored160/200; khors114 was
outscored100/200, with the blue mean still below khors. No#1rank guarantee.

Normal `auto_champion=always` submissions selected both replacements without
retiring either incumbent first. Fresh game/principal-version stability and
ownership checks passed. [After readback](after.json) verifies both memberships;
[decision](decision.json) records the existing user authorization and rollback.
The nullable API content-hash field is not used as invented source proof;
the exact hosted specifications, source digest and Coach upload request bind it.

Rollback: Aaron `b65ccf7b-d7a1-4681-b57f-a55f5ace43c7`, Coach
`088c0fed-b536-4777-9f7a-14abee21e5b8`, source db71abb3 in the preserved
[portal pair](../portal-coaching20260922-hosted/README.md).

Before deployment, round51 ranked Andre#1(1721.37), Aaron#2(1666.26),
Richard#3(1623.73). These are old-policy results. Placement has been verified;
new league-round performance remains unmeasured. Raw receipts remain under
`polyworld/tmp/gota-core-buyback-20260923/deployment`.
