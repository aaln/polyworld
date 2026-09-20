# Jordan268 counter-policy forks

## aaron-gota-ir-j268-waveclear-0920:v1

- Version `bd1bb4f2-358c-4165-be2e-91ff1b757615`; UTC 2026-09-20T04:39:28.741293+00:00.
- Change: {'origin': 'Jordan268 opponent IR-guided fork', 'experiment': '2026-09-19-jordan268-waveclear', 'lever': 'defense target-kind priority', 'changed_parameters': ['observe.creep_first', 'observe.redbranch_creep_first']}.
- BASIC SHA `8a1550da9f65a5f04a8741d2de6a2a82f13a7240e5fd74ff448601fbbc4648bd`; IR SHA `2a56b6830c5068d76c333b32ad5bd9e4d161b5895143039b4ad70ea17816ecdb`. Runtime: published GOTA BASIC host .5, no container/run override.
- Initial state: unvalidated; inert upload. Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/jordan268-counter-20260920/candidates/waveclear`.

## aaron-gota-ir-j268-assembly-0920:v1

- Version `15ba2827-f589-41e0-a8f4-5af2d4093a32`; UTC 2026-09-20T04:55:15.259561+00:00.
- Change: {'origin': 'Jordan268 opponent IR and blue-loss replay', 'experiment': '2026-09-19-jordan268-assembly', 'lever': 'blue opening formation', 'parent_candidate': 'waveclear'}.
- BASIC SHA `7a5e6116819388ca0c577400bde81636209054f89a78dccfbc084f52a0449e2b`; IR SHA `557ffe1ae692971ae42aa9ec6b8ff4d06e8d94eb26b461cb6aea9aa5e30b1738`. Runtime: published GOTA BASIC host .5, no container/run override.
- Initial state: unvalidated; inert upload. Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/jordan268-counter-20260920/candidates/assembly`.

## aaron-gota-ir-j268-counterrace-0920:v1

- Version `961edad6-cad7-45e3-b155-6b5196b4ed1d`; UTC 2026-09-20T05:00:39.291248+00:00.
- Change: {'origin': 'Jordan268 IR-guided counterpressure after failed assembly', 'experiment': '2026-09-19-jordan268-counterrace', 'lever': 'blue remote recall eligibility', 'parent_candidate': 'waveclear'}.
- BASIC SHA `2e8b563d4811fef029e4dececdb5bc31803615a3700befcaff3b70a9c4e04ebd`; IR SHA `60074fa2f84c8bd34dd01e6d41a134f615ff8df84b67cae1483bd7eca8fe9db4`. Runtime: published GOTA BASIC host .5, no container/run override.
- Initial state: unvalidated; inert upload. Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/jordan268-counter-20260920/candidates/counterrace`.

## aaron-gota-ir-j268-redrace-0920:v1

- Version `00cd9483-0309-4613-bf61-89f3f4a33d01`; UTC 2026-09-20T05:14:13.010181+00:00.
- Change: {'origin': 'Audited counterrace confirmation and Jordan268 IR', 'experiment': '2026-09-19-jordan268-redrace', 'lever': 'red remote recall eligibility', 'parent_candidate': 'counterrace'}.
- BASIC SHA `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`; IR SHA `8f9888996c2a22135cae5033f3c76a8fb58aee2948b043d75bfc08bc1f2b3765`. Runtime: published GOTA BASIC host .5, no container/run override.
- Initial state: unvalidated; inert upload. Evidence: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/jordan268-counter-20260920/candidates/redrace`.

## Hosted validation — 2026-09-20 UTC

| Version | Result | Disposition |
|---|---|---|
| waveclear:v1 | Screen red3/4, blue0/4; red branch later14/40 | Insufficient as a complete counter |
| assembly:v1 | Blue0/4 | Rejected |
| counterrace:v1 | Fresh red14/40, blue40/40 | Confirmed blue component; fails both-color criterion |
| redrace:v1 | Fresh red40/40, blue40/40 | Meets fixed-lineup criterion; isolated fork, no promotion |

The selected version is `00cd9483-0309-4613-bf61-89f3f4a33d01`, BASIC SHA `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. All completed cohorts passed full replay/VM/roster/build/config/score/XP audits. Repeated trajectory signatures and unmatched generated seeds limit generalization. Native artifact and evidence: `examples/gods_of_the_arena/players/ir/forks/jordan268`.

## Submission decision records

### 2026-09-20T05:42:13.761130+00:00 — Jordan268 fork promotion

- User go-ahead, verbatim: "let's promote". Refers to the immediately preceding `aaron-gota-ir-j268-redrace-0920:v1` result.
- Target: Gods of the Arena `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`, Aaron's Co-play Coach `ply_594ec24d-d7f3-4370-a000-468354ec41c9`; version `00cd9483-0309-4613-bf61-89f3f4a33d01`.
- Validation state: **validated for the exact Jordan268 matchup; submitted**. Experiment `2026-09-19-jordan268-redrace` is confirmed: 40/40 red and 40/40 blue, against the precommitted >=30/40 per-color rule. All 80 replay/VM/roster/build/config/score/XP audits passed; Python/BASIC parity verified again before submission.
- Scope: repeated trajectories; no inferential p-value, broad-field check, or A/B against the intervening live champion. The user explicitly requested this promotion after the scoped 80/80 readout. No broader superiority claim.
- Submission `sub_e4ddcd00-3329-41bf-808d-66ad846a2449`; status pending at creation. Qualification and champion flag are being monitored without an active-only membership filter.
- Actual preflight rollback: `aaron-gota-autoresearch-suppress_toward-0916:v1` (`a1661ebb-7c77-4b7d-94ee-f5dbb27064ba`), membership `lpm_28225237-335e-415f-840c-a40254622094`. Restore with `POST /v2/league-policy-memberships/lpm_28225237-335e-415f-840c-a40254622094/champion`, followed by readback; one authenticated request, no rebuild.
- BASIC SHA `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. Decision and API receipts: `tmp/gota-ir/jordan268-counter-20260920/promotion`.

- Promotion verified at 2026-09-20T05:43:03.140815+00:00: **active, competing champion**; membership `lpm_52e65ea2-e7c6-430a-8dd2-a323776acf1f`. Version `00cd9483-0309-4613-bf61-89f3f4a33d01` and source hash match the approved fork. Other owned players’ champion versions were unchanged. Durable receipt: `examples/gods_of_the_arena/players/ir/forks/jordan268/promotion.json`.

## aaron-gota-ir-j268-redrace-0920-aaron:v1

- Version `4cdbbf36-3d70-4ea3-8aed-c92ee0e024be`; player Aaron `ply_630a768f-d623-44b2-80fa-36968d6fa75a`; UTC 2026-09-20T06:14:08.747299+00:00.
- BASIC SHA `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`; byte-identical to evaluated version `00cd9483-0309-4613-bf61-89f3f4a33d01`.
- Byte-identical registration of the Jordan268 counter just promoted for Aaron’s Co-play Coach. Original executable confirmed 40/40 red and 40/40 blue with full replay/VM/roster/score/XP audits. Fixed lineups and repeated trajectories; broad-field superiority untested. This duplicate registration adds no independent evaluation evidence. Runtime: published GOTA BASIC host 2026.9.16.5.
- Initial state: registered; inert until submission and champion selection. Receipts: `/Users/aaln/experiments/softmax/polyworld/tmp/gota-ir/jordan268-counter-20260920/promotion-aaron`.

### 2026-09-20T06:14:08.918814+00:00 — Aaron player upgrade

- User go-ahead, verbatim:

> upgrade this playre
> Aaron aaron-gota-ir-relh154-legacy-0916-aaron:v1

- Target player `ply_630a768f-d623-44b2-80fa-36968d6fa75a` in league `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; new version `4cdbbf36-3d70-4ea3-8aed-c92ee0e024be`.
- Byte-identical registration of the Jordan268 counter just promoted for Aaron’s Co-play Coach. Original executable confirmed 40/40 red and 40/40 blue with full replay/VM/roster/score/XP audits. Fixed lineups and repeated trajectories; broad-field superiority untested. This duplicate registration adds no independent evaluation evidence.
- Submission `sub_c7b9769d-62c0-4046-b9a0-d0ca8a0d027b`; pending at creation, `auto_champion=never`. Exact membership and active champion status are being monitored.
- Rollback: `aaron-gota-ir-relh154-legacy-0916-aaron:v1` (`eae99cdd-b2a9-4426-aa20-289d8637fa54`), membership `lpm_e7bd9f1d-6a9a-4ee3-a3c0-e9b387d2666b`. Restore with `POST /v2/league-policy-memberships/lpm_e7bd9f1d-6a9a-4ee3-a3c0-e9b387d2666b/champion` followed by readback; no rebuild.
- BASIC SHA `be6affd3b3b9516a15dc8b32687c29b728adc4aa367fc651ba5c0fcefb9cbf73`. Decision and API receipts: `tmp/gota-ir/jordan268-counter-20260920/promotion-aaron`.

- Aaron upgrade verified at 2026-09-20T06:15:03.297298+00:00: **active, competing champion**, `aaron-gota-ir-j268-redrace-0920-aaron:v1` (`4cdbbf36-3d70-4ea3-8aed-c92ee0e024be`), membership `lpm_d9ccbafb-edec-4af8-9704-17856b726f74`. The Coach champion remained unchanged. Durable receipt: `examples/gods_of_the_arena/players/ir/forks/jordan268/promotion-aaron.json`.
