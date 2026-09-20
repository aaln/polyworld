# Adaptive formation3600 deployed to both league players

User authorization: “deploy the policy to latest on league”, following the full adaptive-fork result readout. The existing explicit scope is both Aaron and Coach.

Both memberships are verified competing, active and champion:

| Player | Policy version | Membership |
|---|---|---|
| Aaron | `aaron-gota-ir-formation-profile-pruned-0920:v1` (`61148477-1928-43c6-a881-8daea0e8f6c2`) | `lpm_bad3beed-50c6-4f23-ae26-58bbf064eaf5` |
| Coach | `aaron-gota-ir-formation-profile-pruned-0920-coach:v1` (`2bb94c84-fc32-4a81-9e6d-46666bc0315f`) | `lpm_b8154dc3-7185-4261-a4fb-f11e5fd112ea` |

Both registrations use byte-identical tested BASIC SHA256 `c708970db2c1be838d6d38b726cbc1b94b73c88f7c5b20c0adfd4d02666436a4`. The [frozen research pair](../formation-adaptive-20260920/README.md) and its original result snapshots remain unchanged. The conversion verifier passed immediately before deployment.

The 400-game discovery and 240-game confirmation both passed their frozen target gates: Alex 40/40 each color, Jordan 40/40 each color, Richard blue 40/40 and red 0/40. Fresh formation3600 controls lost all 160 Alex/Jordan games. The explicit deployment decision follows the disclosed limitations: correlated trajectories, Richard red losses, and no broad-field or mixed-team qualification. Formal research acceptance and failed broader gates were not changed.

`decision.json` records authorization and evidence; `deployment-verified.json` records the live readback; `rollback.json` retains the two prior formation3600 versions and exact selection calls. New league outcomes are observational and separate from the completed tests. The existing three-hour monitor remains in place; inspect `post-deployment-league-check.json` for the immediate check.
