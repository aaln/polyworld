"""Resume the frozen economy discovery screen; local evidence is not promotion."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import shutil
import subprocess

from economy_candidates import VARIANTS, make_policy
from motion_candidates import make_policy as motion_policy
from policy_ir import HERE, ROOT, bundle, digest, read, write


def prepare(directory, family='economy'):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'plan.json'
    if path.exists():
        plan = read(path)
        if plan.get('family', 'economy') != family:
            raise ValueError('Frozen candidate family changed')
        return plan
    variants, make, seed_start = VARIANTS, make_policy, 726000
    if family == 'cadence':
        from cadence_candidates import VARIANTS as variants, make_policy as make, parent_policy
        seed_start = 728000
    prior = ROOT / 'tmp/gota-ir/motion-campaign-20260915'
    for name in ['episode', 'audit', 'config.json', 'v2.bas', 'default.bas']:
        shutil.copy2(prior / name, directory / name)
    shutil.copy2(HERE / 'optimizer_motion_weapon.evaluated.bas', directory / 'motion.bas')
    sources = {name: directory / (name + '.bas') for name in ['v2', 'default', 'motion']}
    for name, definition in variants.items():
        # Persist the exact intermediate parent named by the successor's IR.
        parent = parent_policy() if family == 'cadence' else motion_policy(name, definition)
        bundle(parent, directory / 'parents' / name)
        bundle(make(name), directory / 'candidates' / name)
        sources[name] = directory / 'candidates' / name / 'policy.bas'
    slots = list(range(10)) * 4
    random.Random(2026091601 if family == 'economy' else 2026091602).shuffle(slots)
    instruments = ['economy_screen.py', 'economy_candidates.py', 'opportunity_contract.py',
                   'motion_candidates.py', 'motion_contract.py', 'binding.py', 'policy_ir.py']
    if family == 'cadence':
        instruments += ['cadence_candidates.py', 'cadence_contract.py', 'test_cadence.py']
    frozen = directory / 'frozen-instruments'
    frozen.mkdir()
    for name in instruments:
        shutil.copy2(HERE / name, frozen / name)
    inputs = [directory / name for name in ['episode', 'audit', 'config.json']] + list(sources.values())
    plan = {'created_at': datetime.now(timezone.utc).isoformat(), 'game_version': '2026.9.15.3',
            'game_source': 'e1279894d10a7684f303e7a9f1ea2f84c1d14253',
            'family': family, 'variants': variants, 'sources': {name: str(p) for name, p in sources.items()},
            'inputs': {str(p): digest(p.read_bytes()) for p in inputs},
            'instruments': {name: digest((frozen / name).read_bytes()) for name in instruments},
            'cases': [{'seed': seed_start + i, 'slot': slot} for i, slot in enumerate(slots)],
            'rule': f'Complete all{40 * len(sources)} games and full replay audits. Local discovery only. Eligible: at least2 more wins than BOTH v2 and default, at least as many as deployed motion; death rate <=110%v2, XP>=80%v2, zero unverified post-hit retreats, gear every game, VM budgets. Rank by wins, lower death rate, higher XP, then name. At most two enter new100-game hosted discovery against pinned incumbents and both deployed controls. No superiority claim from selected screen data. Fresh held-out hosted confirmation and broad-field validation required before league selection.',
            'stop_rule': 'No dropped seeds or optional stopping. Preserve failures. Resume identical inputs only.'}
    write(path, plan)
    return plan


def run(directory, workers, family='economy'):
    plan = prepare(directory, family)
    for path, sha in plan['inputs'].items():
        if digest(Path(path).read_bytes()) != sha:
            raise ValueError('Frozen input changed: ' + path)
    for name, sha in plan['instruments'].items():
        if digest((directory / 'frozen-instruments' / name).read_bytes()) != sha:
            raise ValueError('Frozen instrument changed')

    def episode(name, case):
        folder = directory / 'screen' / name / f"seed-{case['seed']}-slot-{case['slot']}"
        folder.mkdir(parents=True, exist_ok=True)
        source = plan['sources'][name]
        result_path = folder / 'result.json'
        if not result_path.exists():
            command = [str(directory / 'episode'), '--config', str(directory / 'config.json'),
                       '--seed', str(case['seed']), '--record', str(folder / 'episode.replay')]
            command += ['--bot:' + str(source if slot == case['slot'] else directory / 'default.bas') for slot in range(10)]
            with (folder / 'stdout.log').open('w') as out, (folder / 'stderr.log').open('w') as err:
                subprocess.run(command, cwd=ROOT, stdout=out, stderr=err, check=True, timeout=300)
            result = json.loads((folder / 'stdout.log').read_text().splitlines()[-1])
            result.update(subject_slot=case['slot'], source_sha256=plan['inputs'][source],
                          binary_sha256=plan['inputs'][str(directory / 'episode')],
                          config_sha256=plan['inputs'][str(directory / 'config.json')],
                          replay_sha256=digest((folder / 'episode.replay').read_bytes()))
            write(result_path, result)
        result = read(result_path)
        if (result['seed'] != case['seed'] or result['subject_slot'] != case['slot'] or
                result['source_sha256'] != plan['inputs'][source] or
                result['binary_sha256'] != plan['inputs'][str(directory / 'episode')] or
                result['config_sha256'] != plan['inputs'][str(directory / 'config.json')] or
                result['replay_sha256'] != digest((folder / 'episode.replay').read_bytes())):
            raise ValueError('Cached episode inputs changed')
        if not (folder / 'audit.json').exists():
            proc = subprocess.run([str(directory / 'audit'), '--replay', str(folder / 'episode.replay')],
                                  cwd=ROOT, capture_output=True, text=True, check=True, timeout=300)
            audit = json.loads(proc.stdout.splitlines()[-1])
            audit.update(replay_sha256=result['replay_sha256'], auditor_sha256=plan['inputs'][str(directory / 'audit')])
            write(folder / 'audit.json', audit)
        audit = read(folder / 'audit.json')
        if (audit['hash_mismatches'] or audit['ticks'] != result['ticks'] or
                audit['state_hash'] != result['state_hash'] or audit['actions_consumed'] != result['actions'] or
                audit['replay_sha256'] != result['replay_sha256'] or
                audit['auditor_sha256'] != plan['inputs'][str(directory / 'audit')]):
            raise ValueError('Full replay parity failed')
        hero = result['heroes'][case['slot']]
        if hero['deaths'] != audit['heroes'][case['slot']]['deaths']:
            raise ValueError('Death counters differ')
        return {'name': name, 'seed': case['seed'], 'slot': case['slot'], 'ticks': result['ticks'],
                'timeout': result['timeout'], 'alive_ticks': audit['heroes'][case['slot']]['alive_ticks'], **hero}

    rows = []
    jobs = [(name, case) for case in plan['cases'] for name in plan['sources']]
    with ThreadPoolExecutor(workers) as pool:
        for future in as_completed([pool.submit(episode, *job) for job in jobs]):
            rows.append(future.result())
            if len(rows) % 13 == 0:
                print(f'{len(rows)}/{len(jobs)} full games and replay audits complete', flush=True)
    rows.sort(key=lambda r: (r['name'], r['seed']))
    write(directory / 'screen-rows.json', rows)
    metrics = {}
    for name in plan['sources']:
        rr = [r for r in rows if r['name'] == name]
        metrics[name] = {'games': len(rr), 'wins': sum(r['score'] for r in rr),
                         'death_rate': sum(r['deaths'] for r in rr) * 1440 / sum(r['alive_ticks'] for r in rr),
                         'xp': sum(r['total_xp'] for r in rr),
                         'gear_games': sum(r['equipment_count'] > 0 for r in rr),
                         'unverified_retreats': sum(r['unverified_bursts'] for r in rr),
                         'loadout_purchases': sum(r['loadout_purchases'] or 0 for r in rr),
                         'moved_kite_ticks': sum(r['moved_kite_ticks'] for r in rr),
                         'max_work': max(r['max_work'] for r in rr),
                         'max_instructions': max(r['max_instructions'] for r in rr)}
    eligible = [n for n in plan['variants'] if
                all(metrics[n]['wins'] >= metrics[c]['wins'] + 2 for c in ['v2', 'default']) and
                metrics[n]['wins'] >= metrics['motion']['wins'] and
                metrics[n]['death_rate'] <= 1.1 * metrics['v2']['death_rate'] and
                metrics[n]['xp'] >= .8 * metrics['v2']['xp'] and
                metrics[n]['gear_games'] == 40 and not metrics[n]['unverified_retreats'] and
                metrics[n]['max_work'] <= 50000 and metrics[n]['max_instructions'] <= 20000]
    eligible.sort(key=lambda n: (-metrics[n]['wins'], metrics[n]['death_rate'], -metrics[n]['xp'], n))
    report = {'metrics': metrics, 'eligible': eligible, 'selected': eligible[:2],
              'verified_games': len(rows), 'design': 'Local discovery; no promotion or superiority claim.'}
    write(directory / 'screen-result.json', report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    p.add_argument('--workers', type=int, default=10)
    p.add_argument('--family', choices=['economy', 'cadence'], default='economy')
    args = p.parse_args()
    run(args.directory.resolve(), args.workers, args.family)
