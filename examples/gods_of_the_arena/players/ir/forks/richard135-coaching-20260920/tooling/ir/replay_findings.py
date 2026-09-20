"""Aggregate descriptive replay evidence; no significance or promotion gate.

Uses the already-observed 40-case cohort, four policy arms. Events inside one
game are correlated. The output is diagnosis, not an independent strength test.
"""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys
from policy_ir import digest, read, write

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    run = Path(sys.argv[1]).resolve()
    rows = read(run / 'cohort-v2/results.json')
    if len(rows) != 160 or any(r['hash_mismatches'] for r in rows):
        raise ValueError('All 160 complete tapes must verify')
    summaries = {}
    for arm in ('v2', 'default', 'spell_short', 'long_bare'):
        rr = [r for r in rows if r['arm'] == arm]
        if len(rr) != 40 or len({r['seed'] for r in rr}) != 40:
            raise ValueError('Expected 40 distinct matched cases per arm')
        for row in rr:
            if digest(Path(row['diagnostic']).read_bytes()) != row['diagnostic_sha256']:
                raise ValueError('Diagnostic file changed')
        deaths = [d for r in rr for d in r['deaths']]
        low_hp_samples = [sum(0 < c['hp'] < .35*c['max_hp'] for c in d['preceding_6_seconds']) / 2 for d in deaths]
        long_stalls = [{'case':r['case'], 'score':r['score'], **s} for r in rr for s in r['stalls'] if s['ticks'] >= 720]
        summary = {
            'games':40, 'wins':sum(r['score'] for r in rr), 'deaths':len(deaths),
            'alive_ticks':sum(r['alive_ticks'] for r in rr),
            'stationary_no_hit_no_active_offense_ticks_in_runs_ge72':sum(r['idle_ticks_in_runs_ge72'] for r in rr),
            'long_stalls_ge30sec':long_stalls,
            'remote_target_alive_fraction':sum(r['remote_target_ticks'] for r in rr)/sum(r['alive_ticks'] for r in rr),
            'out_of_attack_range_alive_fraction':sum(r['out_of_range_ticks'] for r in rr)/sum(r['alive_ticks'] for r in rr),
            'median_low_hp_sample_seconds_in_final6sec':statistics.median(low_hp_samples),
            'deaths_without_low_hp_sample':sum(x == 0 for x in low_hp_samples),
            'deaths_with_enemy_mobile_targeting_in_final6sec':sum(any(a['kind'] in (2,3) for c in d['preceding_6_seconds'] for a in c['attackers']) for d in deaths),
            'deaths_with_tower_targeting_in_final6sec':sum(any(a['kind'] == 4 for c in d['preceding_6_seconds'] for a in c['attackers']) for d in deaths),
            'deaths_with_enemy_count_ge_allies_plus3_in_final6sec':sum(any(c['enemy_near'] >= c['ally_near']+3 for c in d['preceding_6_seconds']) for d in deaths),
        }
        if arm in ('spell_short','long_bare'):
            duration = 10 if arm == 'spell_short' else 32
            segments = [w for r in rr for w in r['walks'] if w['hit_adjacent'] and w['ticks'] == duration and w['start_separation'] <= 7]
            living = [w for w in segments if w['end_separation'] >= 0]
            summary['retreat_segments'] = {
                'definition':'Consecutive recorded walk orders immediately after a basic hit, lasting exactly the configured retreat duration; nearest initially visible enemy within 7 real tiles. A command-derived proxy, not recovered private VM state.',
                'duration_ticks':duration, 'segments':len(segments), 'living_tracked_enemy_at_end':len(living),
                'enemy_missing_or_dead_at_end':len(segments)-len(living),
                'median_turn_only_ticks':statistics.median(w['turn_only_ticks'] for w in segments),
                'median_moved_ticks':statistics.median(w['moved_ticks'] for w in segments),
                'median_displacement_tiles':statistics.median(w['displacement'] for w in segments),
                'separation_gain_gt_quarter_tile':sum(w['end_separation']-w['start_separation'] > .25 for w in living),
                'separation_loss_gt_quarter_tile':sum(w['end_separation']-w['start_separation'] < -.25 for w in living),
                'median_separation_change_tiles':statistics.median(w['end_separation']-w['start_separation'] for w in living),
            }
        summaries[arm] = summary
    full_inventory = Counter()
    for p in (ROOT/'tmp/gota-ir/hit-kite-20260915/screen/parent').glob('*/audit.json'):
        slot = int(p.parent.name.rsplit('-',1)[1])
        for event in read(p)['events']:
            if event['slot'] == slot:
                full_inventory['deaths'] += 1
                full_inventory['full_inventory'] += 'NoItem' not in event['inventory']
    probes = {name:json.loads((run/f'{name}.json').read_text().splitlines()[-1]) for name in ('escape-probe','prevention-probe','early-prevention-probe')}
    for probe in probes.values():
        assert probe['checkpoint_prefix_verified']
        assert probe['trials'][0]['post_intervention_hash_mismatches'] == 0
    evidence = {
        'created_at':datetime.now(timezone.utc).isoformat(), 'game_version':'2026.9.15.3',
        'published_source':'e1279894d10a7684f303e7a9f1ea2f84c1d14253',
        'selected_policy':'aaron-gota-ir-waveguard-r4:v2',
        'policy_sha256':digest((HERE/'waveguard_xp.evaluated.bas').read_bytes()),
        'design':'Descriptive re-analysis of 160 complete replays: the same 40 seeds/slots across four arms; adaptive discovery data, not 160 independent cases or new validation.',
        'limits':[
            'Nine default teammates/opponents; no new incumbent XP or leaderboard-strength claim.',
            'Walk segments are identified from action tapes; the nearest visible enemy is not necessarily the damaging attacker.',
            'Separation comparisons exclude enemies dead or missing at the segment end. Event samples are correlated within games.',
            'Low-HP timing is sampled every 12 ticks and totals samples in the final six seconds, not exact continuous warning time.',
            'DamageMetric is never populated by this published source; zero was NOT interpreted as zero damage. Inactivity excludes basic hits and active offensive spell effects.',
            'Native graphics could not load missing local courtyard texture. The viewer renders authoritative positions, visible objects and paths schematically.',
            'Counterfactual probes retain peers’ recorded commands and last only 96 ticks. The waypoint-changing arm is engine-only and cannot be uploaded as a policy.',
        ],
        'arms':summaries, 'inventory_at_death':dict(full_inventory), 'probes':probes,
        'inputs':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [
            run/'cohort-v2/results.json',run/'diagnostics-v2',run/'escape-probe',
            HERE/'replay_diagnostics.nim',HERE/'replay_escape_probe.nim',HERE/'replay_review.py',HERE/'replay_findings.py']},
        'next_hypotheses':[
            {'id':'H_motion_feedback','status':'untested','change':'Replace fixed ten-tick retreat completion with persistent destination and measured separation/movement, accounting for turn cost and enemy closing speed. Keep a bounded maximum, offensive spell opportunities, and a safe re-engagement condition.','validation':'Scenario checks for completed windup, turn delay, retreat displacement and failure exits; new balanced local cohort vs exact v2/default; preserve wins and reduce deaths; then one N-episode hosted request per arm.'},
            {'id':'H_tower_clearance','status':'untested','change':'Avoid standing tower clearance before crossing a collision boundary. Add target-independent progress monitoring. Do not assume terrainWalkable or accepted walkTo means a reachable route.','validation':'Reproduce the exact tower traps, confirm preventive routing before contact, then independent full-game cases. Simple nearby movement retries are already disproved in the trapped checkpoint.'},
            {'id':'H_early_survival','status':'untested','change':'Assess damage trend, multiple attackers, visible spell warnings, allied cover and escape time before HP is critical. Choose an escape corridor, not merely a vector away from the nearest object.','validation':'Compare HP/damage context and actual separation at retreat initiation; fort wins and deaths on fresh balanced cases. Do not repeat the rejected unconditional 35%-HP controller.'},
        ],
    }
    write(HERE/'replay-findings-20260915.json', evidence)
    print(json.dumps({'verified_replays':160, 'arms':summaries,'inventory_at_death':dict(full_inventory)},indent=2))


if __name__ == '__main__':
    main()
