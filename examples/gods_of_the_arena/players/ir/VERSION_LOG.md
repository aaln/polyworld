# Waveguard hosted versions

| Version | Immutable ID | Created UTC | Change | Validation |
| --- | --- | --- | --- | --- |
| v1 | `7b5f3065-85b0-4abf-882e-a4ab95a136fe` | 2026-09-10T19:49:18Z | Initial R4 wave following | Experimental; previous active champion |
| v2 | `6d0ff780-652f-47a8-82b3-336cb7a10a56` | 2026-09-10T20:26:41Z | E1 sustain-only purchases preserve gold for equipment | **Active champion, selected 2026-09-10T22:17:27Z at the user’s explicit request.** Runtime verified in 10 hosted episodes; 4/10 wins vs v1 2/10, one correlated seed cluster. Competitive advantage unconfirmed. |

## Selection decision

2026-09-15: uploaded **aaron-gota-ir-wave-local:v1**, immutable version
`34a06b93-fa14-457d-95ed-0d4f131344d4`, for the user's requested hosted XP.
Only R1 changes from Waveguard v2 to wave-local combat; E0/E1/E2 buying and R4
movement retain v2 behavior. BASIC SHA256
`062fe4e0c246bad9a1c0f37f7028011ce3de3294953630a44c713d9a3a134954`.
Local screen passed; confirmation remains pending. Item buying verified for all
ten classes. This upload is an experimental policy, not a league promotion.
Frozen metadata and upload/readback receipts: `tmp/gota-ir/xp-wave-local-20260915/`.

The user explicitly requested upgrading the linked v1 entry to the latest version. Select the existing v2; do not relabel unconfirmed later research as a passing promotion gate. See [the decision and readback](submission-v2-latest-20260910.json) for the exact request, evidence and rollback. Future automatic selection remains disabled.

## aaron-gota-ir-motion-weapon:v1

- Immutable ID: `6ed1efdb-d03b-4cf1-82d3-47a6e02e08cb`. Recorded UTC: 2026-09-16T02:32:00.454583+00:00.
- Change: motion_weapon; stable-destination post-hit retreat with separation feedback and ranged starting damage.
- Runtime: BASIC on 2026.9.15.3, source `e1279894d10a7684f303e7a9f1ea2f84c1d14253`; SHA256 `e845f7ff21f58466960bce6dec5fadcaf5048583934f8c28d91906c1eacb9501`.
- Validation: **hosted unvalidated**. Local win qualification failed; user-requested exploratory XP; upload is inert.
- Evidence and receipts: `tmp/gota-ir/motion-campaign-20260915/`.

## aaron-gota-ir-motion-weapon:v2 — Aaron's Optimizer copy

Immutable ID `ed2596c6-f9f7-4fe2-8b13-9383c0be7ba0`, recorded2026-09-16T03:19:31.068233+00:00.
Exact same BASIC SHA256 `e845f7ff21f58466960bce6dec5fadcaf5048583934f8c28d91906c1eacb9501` as motion-weapon:v1.
Registered for player `ply_594ec24d-d7f3-4370-a000-468354ec41c9` at the user's explicit deployment request.
No behavior change:100hosted candidate games67wins vs control59/100, all200replays verified; superiority inconclusive.
Pending league placement/selection readback.600-per-arm fresh confirmation continues on the original identical version.

Deployment verified: both Aaron (waveguard-r4:v2) and Aaron's Optimizer (motion-weapon:v2, identical v1 bytes) are active competing champions in the Competition division. Explicit user selection; automatic future-version selection remains disabled. Receipts: `tmp/gota-ir/motion-campaign-20260915/deploy-optimizer/deployment-verified.json`.

### Motion-weapon:v1/v2 independent confirmation, recovered2026-09-16 UTC

600games/arm:340wins versuswaveguard304, +6pp, Fisherp=.0213503; deathrate.38120 versus.48895 (−22%); XP936825/860675, meanGlory484.82/358.89. All1200tapes verified; frozen confirmation passed. Initial200games excluded. Old opponent roster; current-field transfer and field guardrail pending. IR updated with evidence while exactBASIC remains unchanged. No league action. Evidence: `tmp/gota-ir/motion-campaign-20260915/hosted-confirmation600/comparison.json`.

## aaron-gota-ir-farm-motion-0916:v1

- ID `f6976ce8-d2b2-4781-a1d0-14b56690045e`; UTC 2026-09-16T07:07:11.816503+00:00; player Aaron's Optimizer.
- IR configuration: `farm_motion` / {'motion': {'targeted': 0}, 'center': True, 'loadout': True, 'opportunity': {'farm_until_level': 3, 'hp_weight': 4}}; user-authorized multi-hypothesis discovery.
- BASIC SHA `b7996e592b2078eccaf9084832a28c3dfc09fcd0b5eb6729e7af91ca2a44fbbe`, game 2026.9.15.3, source `https://github.com/Metta-AI/polyworld/tree/e1279894d10a7684f303e7a9f1ea2f84c1d14253/examples/gods_of_the_arena`.
- Local discovery: 28/40 wins; selected among10cells. **Hosted unvalidated**; inert upload, no competitive-superiority claim or league selection.
- Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/economy`; receipts: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/hosted-discovery/farm_motion`.

## aaron-gota-ir-center-motion-0916:v1

- ID `572b9013-7205-4475-8158-ac99b447a013`; UTC 2026-09-16T07:07:13.952309+00:00; player Aaron's Optimizer.
- IR configuration: `center_motion` / {'motion': {'targeted': 0}, 'weapon': True, 'center': True}; user-authorized multi-hypothesis discovery.
- BASIC SHA `93a9f2f5cd15c934218c5fd08f541719546896d077d0f0d167adccd27b5169f9`, game 2026.9.15.3, source `https://github.com/Metta-AI/polyworld/tree/e1279894d10a7684f303e7a9f1ea2f84c1d14253/examples/gods_of_the_arena`.
- Local discovery: 24/40 wins; selected among10cells. **Hosted unvalidated**; inert upload, no competitive-superiority claim or league selection.
- Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/economy`; receipts: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/hosted-discovery/center_motion`.

## aaron-gota-ir-cadence4-guard-0916:v1

- ID `1a152668-4985-4273-98d8-cba900ff94dc`; UTC 2026-09-16T07:31:12.244624+00:00; player Aaron's Optimizer.
- IR configuration: `cadence4_guard` / {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 7, 'all_classes': 1, 'risk_hp': 55, 'recovery_ticks': 4}}; user-authorized multi-hypothesis discovery.
- BASIC SHA `d882a1e65ecb77372c739ce623abc4e24c271bfd0f97b3a6ae845f7fbfda2289`, game 2026.9.15.3, source `https://github.com/Metta-AI/polyworld/tree/e1279894d10a7684f303e7a9f1ea2f84c1d14253/examples/gods_of_the_arena`.
- Local discovery: 26/40 wins; selected among 6 cells. **Hosted unvalidated**; inert upload, no competitive-superiority claim or league selection.
- Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/cadence-cycle/economy`; receipts: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/cadence-cycle/hosted-discovery/cadence4_guard`.

## aaron-gota-ir-cadence-all-0916:v1

- ID `c5711f9d-6248-4843-ae39-bc13a4911b79`; UTC 2026-09-16T07:31:13.971343+00:00; player Aaron's Optimizer.
- IR configuration: `cadence_all` / {'operator': 'cadence_motion', 'parameters': {'threat_tiles': 7, 'all_classes': 1}}; user-authorized multi-hypothesis discovery.
- BASIC SHA `d44442652129be56516e6ef675bd338d05a0a7863e2372958d2da8fece348c8e`, game 2026.9.15.3, source `https://github.com/Metta-AI/polyworld/tree/e1279894d10a7684f303e7a9f1ea2f84c1d14253/examples/gods_of_the_arena`.
- Local discovery: 25/40 wins; selected among 6 cells. **Hosted unvalidated**; inert upload, no competitive-superiority claim or league selection.
- Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/cadence-cycle/economy`; receipts: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/autoresearch-20260916/cadence-cycle/hosted-discovery/cadence_all`.

### Cadence hosted discovery completed,2026-09-16 UTC

Cadence-all-0916:v1 won54/100 versus waveguard46 and motion37, qualifying
for fresh400/arm confirmation only. Deathrate.42640; XP203875; all100gear.
Cadence4-guard-0916:v1 won36/100 and failed advancement; do not select it.
All400artifacts and full replay/VM audits passed. Both IRs updated with
byte-identical executable parity. League champions remain unchanged.
Evidence: `tmp/gota-ir/autoresearch-20260916/cadence-cycle/hosted-discovery/result.json`.

### Cadence-all-0916:v1 independent confirmation PASSED

Fresh400games/arm: cadence215/400 (53.75%), waveguard175/400 (43.75%),
motion176/400 (44.00%). Gains+10.00pp/+9.75pp; one-sided Fisherp=.002886/.003579.
All1200games, replays, roster rotations, scores, XP and VM proofs verified.
No adverse class flag. Deathrate.39800 versus.65400/.48925; XP891200 versus
526650/512475; meanGlory989.37 versus389.51/365.32; gearall400candidate games.
One pod log capture failure used the game's equivalent structured VM status;
original marker retained. No case dropped, replaced or pooled with discovery.

Candidate IR now merges measured confirmation and the corrected recovery
goals/strategy rationale, with identical BASIC and exact reverse extraction.
Canonical candidate: cadence_all.evaluated.ir.json/.bas. League still unchanged.
The required100episode sampled-current-champion field check is running:
`xreq_98443e6b-3124-4449-84ba-4af4e06aa594`; excludes both owned players.
Evidence: `tmp/gota-ir/autoresearch-20260916/cadence-cycle/hosted-confirmation/result.json`.

### Cadence-all-0916:v1 DEPLOYED on Aaron's Optimizer

Field guardrail PASSED:58/100 wins, gearall100,13 opponent versions and59
distinct opponent sets; both owned players excluded. All full replay/VM checks
passed. User-authorized submission used auto_champion=never followed by explicit
champion selection. Membership`lpm_365995fe-5793-4098-959a-c211f850b8c0`.
APIreadback verifies exactlytwo owned active competing champions, Optimizer on
cadence and Aaron on waveguard-r4:v2. Rank improvement is not yet measured.
Canonical cadence IRrevision22 contains confirmation, field and deployment
feedback with exact evaluated BASIC parity. See experiments/2026-09-16-autoresearch-result.md
and `tmp/gota-ir/autoresearch-20260916/cadence-cycle/deployment/deployment-verified.json`.
