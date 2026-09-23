"""Write the completed study summary and current-release pointers."""
import json
from datetime import datetime, timezone
from pathlib import Path
from local import ROOT, RAW, write


def main():
    read = lambda p: json.loads(p.read_text())
    report = read(RAW / 'trial/report.json')
    entry = report['candidates'][0]
    out = ROOT / 'examples/gods_of_the_arena/players/ir/forks/weakhero20260923-hosted'
    manifest = read(out / 'explicit-sustain/manifest.json')
    snapshot = read(RAW / 'trial/field-after/snapshot.json')
    memberships = read(RAW / 'trial/field-after/memberships.json')
    versions = {'aaron': '0c766ec9-131f-45d1-a207-ad75aea9ccc5', 'coach': 'd75ff766-e78f-4aa5-b656-55eb29248208'}
    own = {}
    for name, version in versions.items():
        row = next(r for r in memberships if r['policy_version']['id'] == version)
        assert row['status'] == 'competing' and row['substatus'] == 'active' and row['is_champion']
        own[name] = {k: row[k] for k in ['id', 'status', 'substatus', 'is_champion', 'policy_version', 'player']}
    readback = {'at': snapshot['captured_at'], 'game_version': snapshot['game_version'], 'coworld_id': snapshot['coworld_id'], 'champions': own, 'standings': snapshot['standings'], 'league_writes': [], 'auth_resolution': 'Normal saved user credentials allow membership and own-version reads. Earlier selected-player token limitations are preserved historically. No credential content or elevated-header workaround is stored.'}
    write(ROOT / 'games/gods_of_the_arena/experiments/2026-09-23-weakhero60-readback.json', readback)
    lines = []
    for context in ['red-lead', 'blue-lead', 'red-late', 'blue-late']:
        b = next(c for c in report['cells'] if c['cell'] == context and c['name'] == 'baseline')
        n = next(c for c in report['cells'] if c['cell'] == context and c['name'] == 'explicit-sustain')
        lines.append(f"| {context} | {b['means']['score']:.2f} | {n['means']['score']:.2f} | {(n['means']['score']/b['means']['score']-1)*100:+.2f}% |")
    text = '''# Weak-hero survival and score on replay60

The coordinated sustain candidate **did not qualify**. Across 400 fresh games, mean individual score fell from **1,901.64 to 1,735.79 (−8.72%)**, with a stratified 95% gain interval of **−20.28% to +4.51%**. Both live champions remain source `29f6d7e6`. Fewer deaths did not translate into enough XP income.

| Context (50 games per policy) | Baseline score | Candidate score | Change |
| --- | ---: | ---: | ---: |
''' + '\n'.join(lines) + '''

Nonzero score frequency was 58% versus 56%; mean among nonzero games was 3,278.68 versus 3,099.63. Productive-game frequency (score at least 500) was 51% versus 49%. Later-draft mean score was 85.38 versus 50.37. Later-draft deaths per minute fell from 0.4235 to 0.3515 (17.0%), but XP per minute fell from 150.07 to 148.44. Both sit below the 200-XP-per-minute time charge on average; extending play without improving income is insufficient.

The overall confidence interval includes no change. These observations reject the predeclared replacement rule, not prove every component harmful. Lead contexts draft Ranger/Crossbowman, whose executable behavior is unchanged; independent seeds and draft mix differ. Their sample-score movement must not be attributed to healing changes. Later contexts naturally draft DeathKnight/Vanguard. There are **no Arcanist or Warlock hosted subjects**, so caster effects remain locally tested only. The raw by-class tables retain counts and all outcomes without selecting a favorable slice.

## What changed and what worked locally

The IR-first source `36e346c9` unlocks the resource ability from level 2 for Vanguard, DeathKnight, Arcanist and Warlock, then explicitly uses useful healing/restoration before retreat and no-target stops. Vanguard/DeathKnight gain bounded lane recovery and a short disengagement from close, unfavorable hero fights, preserving reachable creep finishes. Those four heroes avoid redundant same-decision lethal creep casts. The six other heroes retain their action behavior. Broader melee variants harmed Berserker income in local screens and were preserved as rejected exploration.

All **220 real-tick fixtures** pass: both colors, ten classes and eleven conditions. They cover healing/restoration, locked/cooling/empty skills, useful thresholds, channel protection, danger, shopping, reachable last hits and a threat outside the spacing radius. In a one-HP creep fixture, Vanguard/DeathKnight retain 15 XP while saving 70/36 mana. Sixteen complete native games pass all ten VM and replay checks; eight unchanged baseline runs are shared across exploratory versions. Six unaffected-class matches have identical commands and final states. Maximum observed fixture budgets were 6,066 instructions and 9,696 work, below 19,000/50,000 limits. These tests verify mechanics, not league superiority.

A predeclared outcome-blind sample of 32 hosted replays shows the intended healing activation. In its eight late-draft games per policy, self-healing rose from 22.5 to 1,732.5 HP per game and dead-time share fell from 17.23% to 11.51%. Yet battle time spent alive in the field after at least 30 seconds without XP rose from 33.53% to 36.57%. Sampled proximity to enemy-creep XP range improved from 13.87% to 16.88% of alive samples but remained scarce. This motivates income-preserving wave positioning and better chase/last-hit choices. It does not isolate the cause of the bundle's score result.

## Evaluation scope and decision

Exact release: `2026.9.23.2`, engine `fd315c8fa30f8923c7a7709a577c40ac071b1c2a`, replay60, Bassy `b25e0efef3fec0bd86ed3154659c0762a7158bd3`. Engine and pinned dependencies were built in an isolated worktree and verified clean. Four color/draft contexts each have 50 fresh controls and 50 candidate games, with unchanged mixed rosters containing khors180, Richard195, Jordan411 and relh169. Later contexts deliberately have two identical reference teammates; this is not a ten-distinct-policy field.

All 400 games passed ten-source identity checks, ten VM exits, complete replay hashes, XP-source reconciliation and integer score checks. Blue-lead baseline has 49 distinct command streams among 50 games; every other cell has 50. The bootstrap uses independent whole-game resampling within contexts; that disclosed duplicate limits exact independence. No games were excluded or replaced. The engine and current principal champions were unchanged throughout. Ancillary unavailable text logs remain explicit; mandatory artifacts are complete.

The frozen rule required at least 10% pooled mean improvement, a positive lower 95% gain bound, at least 95% score preservation in each context, at least 5% conditional nonzero-mean improvement, preserved nonzero frequency, increased productive frequency, and fewer/equal late deaths per minute without lower XP per minute. It fails. No league write occurred. An inert upload `opal-sable-4e91:v1` remains a research artifact. The published semantic IR reflects the supported mechanism checks and failed competitive qualification without changing tested BASIC bytes.

[Reviewed IR/policy pair](../../../examples/gods_of_the_arena/players/ir/forks/weakhero20260923-hosted/README.md), [full results](../../../examples/gods_of_the_arena/players/ir/forks/weakhero20260923-hosted/explicit-sustain/evidence/trial-report.json), [follow-up IR](../../../examples/gods_of_the_arena/players/ir/forks/weakhero20260923-hosted/explicit-sustain/evidence/follow-up.ir.json), [current champion readback](2026-09-23-weakhero60-readback.json).

## Additional Arcanist coaching

The supplied [tick 3,570 episode](../../../docs/coaching/2026-09-23-arcanist-shopping/README.md) is fully source-reconstructed. Shopping triggered at 3,530 with full HP and 590 gold, after the local enemy wave cleared. The hero walked 48 seconds to the shop and went 66 seconds without XP. It bought meaningful equipment; Mana Crystal stayed locked throughout. Three other VMs failed, so this episode diagnoses our controller but does not qualify a competitive replacement. Separate semantic coaching proposes coordinated early restoration and wave/upgrade-aware shopping timing, preserving urgent escapes and useful purchases.

## Preservation and reproduction

Raw inputs, initial IR, local rejected variants, all hosted requests and the coaching screenshot/replay remain under `polyworld/tmp/gota-weakhero60-20260923`. The sealed pair includes hashes and request/episode references. Run `python verify.py` inside its `explicit-sustain` directory; `convert.py compile` and `convert.py extract` reproduce the IR/policy pair. Study instruments live in `instruments/weakhero20260923`. The shared budget ledger records 4,320 reserved September 23 UTC episodes, including these 400, under the permanent 100,000 daily cap. No requests remain pending; the obsolete background worker stays paused.
'''
    report_path = ROOT / 'games/gods_of_the_arena/experiments/2026-09-23-weak-hero-survival.md'
    report_path.write_text(text)
    current_path = ROOT / 'games/gods_of_the_arena/current.json'
    current = read(current_path)
    current.setdefault('candidate_history', []).append({k: current[k] for k in ['candidate_pair', 'candidate_source_sha256', 'candidate_ir_sha256', 'candidate_evidence']})
    current.update(current_experiment=str(report_path.relative_to(ROOT)), candidate_pair=str(out.relative_to(ROOT)), candidate_source_sha256=manifest['source_sha256'], candidate_ir_sha256=manifest['ir_sha256'], candidate_evidence=entry)
    current.setdefault('deployment_status_history', []).append(current['deployment_status'])
    current['deployment_status'] = 'Both incumbent champions verified competing/active with normal saved user credentials at ' + snapshot['captured_at'] + '. No league writes. Research candidate failed its400game replay60 gate and remains inert; prior selected-player auth limitation resolved without changing selected credentials.'
    current['research_status'] = 'Completed400fresh replay60 games: explicit-sustain bundle mean score1901.635 to1735.790(-8.72%); late deaths/minute improve but XP/minute declines. Keep incumbent. Save income-preserving wave/chase proposals and fully reconstructed Arcanist shopping coaching; caster changes have local evidence only.'
    current['weak_hero_survival_study'] = {'status': 'complete_not_qualified', 'games': 400, 'game_version': '2026.9.23.2', 'result': entry, 'pair': str(out.relative_to(ROOT)), 'report': str(report_path.relative_to(ROOT)), 'deployment_qualified': False, 'source_sha256': manifest['source_sha256'], 'ir_sha256': manifest['ir_sha256']}
    current['arcanist_shopping_coaching'] = {'episode': 'ereq_724a8b4c-122d-407d-b988-b80cd73548e8', 'report': 'docs/coaching/2026-09-23-arcanist-shopping/README.md', 'semantic_ir': 'docs/coaching/2026-09-23-arcanist-shopping/suggestions.ir.json', 'commands_matched': 1315, 'all_state_hashes_equal': True, 'walk_to_shop_seconds': 48, 'xp_gap_seconds': 66, 'counterfactual_score_gain': None}
    current.setdefault('live_league_snapshot_history', []).append(current['live_league_snapshot'])
    current['live_league_snapshot'] = {'at': snapshot['captured_at'], 'standings': snapshot['standings'], 'scope': 'Cumulative standings, separate from controlled trial; champion identities verified through normal user-authorized membership readback.'}
    current.setdefault('current_engine_reference_control_history', []).append(current['current_engine_reference_control'])
    current['current_engine_reference_control'] = {'game_version': '2026.9.23.2', 'games': 200, 'mean_score': entry['baseline_score'], 'report': str(report_path.relative_to(ROOT)), 'scope': 'Fresh controls across four fixed color/draft contexts; not a new comparison with the pre-incumbent policy or original qualification.'}
    write(current_path, current)
    print(report_path)


if __name__ == '__main__':
    main()
