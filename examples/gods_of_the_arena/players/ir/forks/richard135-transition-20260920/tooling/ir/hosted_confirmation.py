"""Fixed fresh 600-per-arm confirmation in serial 100-episode XP requests.

The preceding100-per-arm result remains an unsuccessful preliminary test.
Never pool it into this confirmation or inspect intermediate outcomes to stop.
Uses Metta's virtualenv. No uploads or league mutations.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
import time

from campaign_hosted_compare import cohort, fisher_greater
from hosted_batch import batch_body
from hosted_wave import client, create, episodes
from policy_ir import HERE, digest, read, write


def prepare(previous):
    old = read(previous / 'plan.json')
    result = read(previous / 'comparison.json')
    if result['arms']['control']['games'] != 100 or result['arms']['candidate']['games'] != 100:
        raise ValueError('Requires the complete preceding 100-per-arm study')
    out = previous.parent / 'hosted-confirmation600'
    out.mkdir(exist_ok=True)
    path = out / 'plan.json'
    if path.exists():
        return out, read(path)
    plan = {'created_at': datetime.now(timezone.utc).isoformat(),
            'previous_result': str(previous / 'comparison.json'),
            'previous_result_sha256': digest((previous / 'comparison.json').read_bytes()),
            'previous_win_gate_passed': result['passed'],
            'reason': 'New independent confirmation of a fixed candidate after the user-requested exploratory hosted test:67/100 vs59/100, lower deaths and higher Glory, but the preliminary win gate failed. That failure is retained. Fresh outcomes alone decide this study; no pooling, optional stopping, tuning or candidate selection.',
            'sample_size': {'episodes_per_arm': 600, 'episodes_per_request': 100, 'requests_per_arm': 6,
                            'calculation': 'For an expected8pp gain near pooled win probability.63, one-sided alpha.025 and80%power, normal approximation gives about572episodes/arm; round to600. A5pp minimum observed gain is the practical-effect guard, not an80%-power claim at5pp.'},
            'gates': {'minimum_win_gain': .05, 'maximum_win_p': .025,
                      'maximum_death_rate_ratio': 1.10, 'minimum_xp_ratio': .80},
            'field_guardrail': old['field_guardrail'],
            'candidate_version': old['candidate_version'], 'control_version': old['control_version'],
            'game_version': old['game_version'], 'game_source': old['game_source'],
            'target': old['target'], 'config': old['config'], 'opponents': old['opponents'],
            'auditor_sha256': digest((previous / 'control/audit').read_bytes()),
            'runner_sha256': digest(Path(__file__).read_bytes()),
            'stop_rule': 'Finish all1200games and all replay audits; infrastructure failures block the verdict and retain artifacts. Each100-game request drains before the next. All600control games drain before candidate launch. Reject/inconclusive if any prespecified gate fails.'}
    write(path, plan)
    shutil.copy2(Path(__file__), out / 'frozen-runner.py')
    for arm in ['control', 'candidate']:
        for index in range(6):
            folder = out / arm / f'part-{index}'
            folder.mkdir(parents=True, exist_ok=True)
            write(folder / 'plan.json', {
                'run_id': f'gota-motion-confirm600-{arm}-{index}',
                'policy_version': plan[arm + '_version'], 'game_version': plan['game_version'],
                'game_source': plan['game_source'], 'target': plan['target'],
                'config': plan['config'], 'opponents': plan['opponents'],
                'notes': f'Fixed600-per-arm fresh confirmation, {arm} part{index+1}/6,100episodes. Same pinned roster/game, independent platform seeds and balanced seats. No interim outcome decision; complete all1200 and audit every tape. Previous200games excluded.'})
            shutil.copy2(previous / 'control/audit', folder / 'audit')
    return out, plan


def run(out, plan):
    jobs = []
    with client() as c:
        for arm in ['control', 'candidate']:
            for index in range(6):
                folder = out / arm / f'part-{index}'
                if digest((folder / 'audit').read_bytes()) != plan['auditor_sha256']:
                    raise ValueError('Auditor changed')
                arm_plan = read(folder / 'plan.json')
                body = batch_body(arm_plan, 100)
                # create performs live schema validation before every idempotent POST.
                request = create(c, body, folder / 'batch')
                print(f'{arm} part{index+1}/6: {request}', flush=True)
                for script, args, log in [
                    ('hosted_batch.py', [str(folder), 'harvest', '--watch'], 'harvest.log'),
                    ('watch_hosted_audit.py', [str(folder), '--workers', '4'], 'audit.log')]:
                    stream = (folder / log).open('a')
                    proc = subprocess.Popen([sys.executable, str(HERE / script), *args], stdout=stream, stderr=stream)
                    jobs.append((proc, stream, folder, script))
                while True:
                    rows = episodes(c, request)
                    statuses = dict(Counter(ep['status'] for ep in rows))
                    write(out / 'progress.json', {'arm': arm, 'part': index + 1, 'request': request,
                                                 'statuses': statuses, 'checked_at': datetime.now(timezone.utc).isoformat()})
                    if any(ep['status'] in {'failed', 'cancelled', 'error'} for ep in rows):
                        raise ValueError('Failed hosted game; exact-request recovery required: ' + request)
                    if len(rows) == 100 and statuses == {'completed': 100}:
                        write(folder / 'drained.json', {'request': request, 'episodes': 100,
                                                       'checked_at': datetime.now(timezone.utc).isoformat()})
                        print(f'{arm} part{index+1}/6:100games complete; artifacts/audits streaming', flush=True)
                        break
                    time.sleep(15)
    for proc, stream, folder, script in jobs:
        code = proc.wait()
        stream.close()
        if code:
            raise ValueError(f'{script} failed for {folder}; inspect its log and recover before verdict')
    compare(out, plan)


def compare(out, plan):
    arms = {}
    all_seeds = set()
    previous = read(Path(plan['previous_result']))
    old_seeds = {row['seed'] for arm in previous['arms'].values() for row in arm['rows']}
    for arm in ['control', 'candidate']:
        parts = [cohort(out / arm / f'part-{index}', 4) for index in range(6)]
        rows = [row for part in parts for row in part['rows']]
        seeds = {row['seed'] for row in rows}
        if len(rows) != 600 or len(seeds) != 600 or seeds & all_seeds or seeds & old_seeds:
            raise ValueError('Missing/repeated/nonfresh effective seeds; cannot use this confirmation')
        all_seeds |= seeds
        if Counter(row['slot'] for row in rows) != Counter({slot: 60 for slot in range(10)}):
            raise ValueError('Confirmation seat coverage changed')
        arms[arm] = {'games': 600, 'wins': sum(r['win'] for r in rows),
                     'death_rate': sum(r['deaths'] for r in rows) * 1440 / sum(r['alive_ticks'] for r in rows),
                     'deaths': sum(r['deaths'] for r in rows), 'xp': sum(r['xp'] for r in rows),
                     'mean_glory': sum(r['glory'] for r in rows) / 600,
                     'timeouts': sum(r['timeout'] for r in rows),
                     'bought_equipment': sum(r['first_gear_tick'] >= 0 for r in rows),
                     'policy_version': plan[arm + '_version'], 'rows': rows}
    c, v = arms['control'], arms['candidate']
    gain = (v['wins'] - c['wins']) / 600
    p = fisher_greater(v['wins'], 600, c['wins'], 600)
    g = plan['gates']
    checks = {'win_gain': gain >= g['minimum_win_gain'], 'win_p': p < g['maximum_win_p'],
              'survival': v['death_rate'] <= g['maximum_death_rate_ratio'] * c['death_rate'],
              'xp': v['xp'] >= g['minimum_xp_ratio'] * c['xp'], 'equipment': v['bought_equipment'] == 600}
    result = {'design': 'Fresh fixed600-per-arm confirmation; preliminary200excluded', 'arms': arms,
              'win_gain': gain, 'one_sided_fisher_p': p, 'checks': checks, 'passed': all(checks.values()),
              'field_guardrail': 'pending' if all(checks.values()) else 'not qualified'}
    write(out / 'comparison.json', result)
    print({k: v for k, v in result.items() if k != 'arms'}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('previous', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    directory, frozen = prepare(args.previous.resolve())
    print(directory, flush=True)
    if not args.prepare_only:
        run(directory, frozen)
