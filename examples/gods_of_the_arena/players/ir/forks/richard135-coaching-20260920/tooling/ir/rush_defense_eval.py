"""Frozen local anti-rush tests; proxy opponents are never labeled as rivals' code."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess

from economy_feedback import record
from policy_ir import HERE, ROOT, bundle, digest, read, write
from release_workspace import RUN, verify
from rush_defense import STUDY, VARIANTS, make


def evaluate(stage, variants, count, seed, factory=make, study=STUDY, auditor_override=None, opponents_override=None):
    verify()
    root = study/stage
    root.mkdir(parents=True, exist_ok=True)
    binary, auditor = RUN/'r5/fast/episode', RUN/'r5/build/audit'
    if auditor_override is not None:
        proof = read(RUN/'r5/fast/local-audit-calibration.json')
        if (digest(Path(auditor_override).read_bytes()) != proof['binary_sha256'] or
                not all(r['all_fields_equal'] for r in proof['rows'])):
            raise ValueError('Optimized local auditor lacks calibration')
        auditor = Path(auditor_override)
    if not read(RUN/'r5/fast/calibration/proof.json')['full_replay_bytes_equal']:
        raise ValueError('Fast runner lacks full-replay calibration')
    if not (root/'plan.json').exists():
        parent = RUN/'coached-lanes/r5-asymmetric/hosted/blue_damage/team-feedback'
        sources = {'current': str(HERE/'win_bounded_0916.r5.evaluated.bas'),
                   'blue_parent': str(parent/'policy.bas')}
        for name in variants:
            bundle(factory(name), root/'candidates'/name)
            sources[name] = str(root/'candidates'/name/'policy.bas')
        opponents = {'default': str(RUN/'r5/default.bas'), 'current': sources['current'],
                     'center_proxy': str(RUN/'coached-lanes/r5-convoy/screen/candidates/center/policy.bas')}
        if opponents_override is not None:
            if not opponents_override: raise ValueError('At least one diagnostic opponent is required')
            opponents = {name:str(path) for name,path in opponents_override.items()}
        if count % 6:
            raise ValueError('Balance both colors across three opponents')
        write(root/'config.json', read(RUN/'local/config.json'))
        plan = {'sources': sources, 'variants': list(variants), 'opponents': opponents,
                'cases': [{'seed': seed+i, 'color': i%2, 'opponent': list(opponents)[i//2%len(opponents)]} for i in range(count)],
                'input_sha256': {str(p): digest(p.read_bytes()) for p in [binary, auditor, root/'config.json',
                                  *map(Path, sources.values()), *map(Path, opponents.values())]},
                'interpretation': 'Local clean-release fixed-team study. center_proxy is our own '
                'previous five-hero middle-lane push, not any private rival implementation. '
                'Screen selects coordinated variants; complete60freshcases/arm before hosted. '
                'Repeated seeds may have identical tactical trajectories; no general significance claim.',
                'gates': {'default_fraction': .9, 'current_fraction': .5, 'proxy_fraction': .6,
                          'proxy_gain_over_both_controls': .2, 'all_gear': True}}
        if opponents_override is not None:
            plan['custom_opponents'] = True
            plan['gates'] = None
            plan['interpretation'] = ('Local diagnostic against the explicitly listed owned policy sources, '
                'balanced by color. Full source/runtime/replay/equipment verification. '
                'No automatic selection or hosted eligibility; preserve the original studies and gates. '
                'Fixed-lineup empirical comparison, not private rival code or independent-trial significance.')
        write(root/'plan.json', plan)
    plan = read(root/'plan.json')
    for path, sha in plan['input_sha256'].items():
        if digest(Path(path).read_bytes()) != sha:
            raise ValueError('Frozen input changed: '+path)
    if (root/'result.json').exists():
        completed = read(root/'result.json')
        if completed['verified_games'] != len(plan['cases'])*len(plan['sources']):
            raise ValueError('Cached study is incomplete')
        for row in completed['rows']:
            tape = root/'games'/row['name']/str(row['seed'])/'replay.bin'
            if digest(tape.read_bytes()) != row['replay_sha256']:
                raise ValueError('Completed replay changed')
        print('Retained completed frozen result:', root, flush=True)
        return completed['selected']

    def one(name, case):
        out = root/'games'/name/str(case['seed'])
        out.mkdir(parents=True, exist_ok=True)
        own = list(range(case['color']*5, case['color']*5+5))
        tape = out/'replay.bin'
        if not (out/'result.json').exists():
            cmd = [str(binary), '--config', str(root/'config.json'), '--seed', str(case['seed']), '--record', str(tape)]
            cmd += ['--bot:'+ (plan['sources'][name] if slot in own else plan['opponents'][case['opponent']]) for slot in range(10)]
            with (out/'stdout.log').open('w') as stdout, (out/'stderr.log').open('w') as stderr:
                subprocess.run(cmd, cwd=ROOT, stdout=stdout, stderr=stderr, check=True, timeout=900)
            write(out/'result.json', json.loads((out/'stdout.log').read_text().splitlines()[-1]))
        result = read(out/'result.json')
        if not (out/'audit.json').exists():
            audit = subprocess.run([str(auditor), '--replay', str(tape)], cwd=ROOT, capture_output=True,
                                   text=True, check=True, timeout=600)
            write(out/'audit.json', json.loads(audit.stdout.splitlines()[-1]))
        audit = read(out/'audit.json')
        if (audit['hash_mismatches'] or audit['state_hash'] != result['state_hash'] or
            audit['ticks'] != result['ticks'] or audit['actions_consumed'] != result['actions']):
            raise ValueError('Full replay validation failed')
        if any(h['max_work'] > 50000 or h['max_instructions'] > 20000 for h in result['heroes']):
            raise ValueError('VM budget failed')
        heroes = [result['heroes'][slot] for slot in own]
        return dict(name=name, **case, win=heroes[0]['score'], ticks=result['ticks'],
                    deaths=sum(h['deaths'] for h in heroes), gear_heroes=sum(h['equipment_count'] > 0 for h in heroes),
                    live_decision_ticks=sum(h['decisions'] for h in heroes),
                    replay_sha256=digest(tape.read_bytes()))

    rows = []
    with ThreadPoolExecutor(4) as pool:
        jobs = [pool.submit(one, name, case) for case in plan['cases'] for name in plan['sources']]
        for job in as_completed(jobs):
            rows.append(job.result())
            print(stage, len(rows), '/', len(jobs), flush=True)
    metrics = {}
    for name in plan['sources']:
        rr = [r for r in rows if r['name'] == name]
        metrics[name] = {'games': len(rr), 'wins': sum(r['win'] for r in rr),
                         'deaths': sum(r['deaths'] for r in rr), 'all_gear': all(r['gear_heroes'] == 5 for r in rr),
                         'deaths_per_live_decision_minute':sum(r['deaths'] for r in rr)*1440/sum(r['live_decision_ticks'] for r in rr),
                         'opponents': {o: sum(r['win'] for r in rr if r['opponent'] == o) for o in plan['opponents']},
                         'colors': {str(c): sum(r['win'] for r in rr if r['color'] == c) for c in (0, 1)}}
    n = count/3
    gates = plan['gates']
    selected = [] if plan.get('custom_opponents') else [name for name in plan['variants'] if metrics[name]['all_gear'] and
                metrics[name]['opponents']['default']/n >= gates['default_fraction'] and
                metrics[name]['opponents']['current']/n >= gates['current_fraction'] and
                metrics[name]['opponents']['center_proxy']/n >= gates['proxy_fraction'] and
                all((metrics[name]['opponents']['center_proxy']-metrics[c]['opponents']['center_proxy'])/n >=
                    gates['proxy_gain_over_both_controls'] for c in ['current', 'blue_parent'])]
    selected.sort(key=lambda n: (-metrics[n]['wins'], metrics[n]['deaths'], n))
    write(root/'result.json', dict(verified_games=len(rows), metrics=metrics, selected=selected, rows=rows,
                                  interpretation=plan['interpretation']))
    for name in plan['variants']:
        if not (root/'feedback'/name).exists():
            src = root/'candidates'/name
            record(src/'policy.ir.json', src/'policy.bas',
                   f'Frozen local rush-defense {stage}: {metrics[name]}; deployed control {metrics["current"]}; '
                   f'blue loadout parent {metrics["blue_parent"]}. Qualified={name in selected}. '
                   +plan['interpretation'], root/'result.json', root/'feedback'/name)
    print(json.dumps({'metrics': metrics, 'selected': selected}), flush=True)
    return selected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['screen-v2', 'screen-v3', 'screen-v4', 'local'])
    parser.add_argument('--screen-stage', default='screen-v4')
    args = parser.parse_args()
    from rush_persistent import make as persistent_make, VARIANTS as PERSISTENT
    from rush_lineup import make as lineup_make, VARIANTS as LINEUP
    factories = {'screen-v2': (make, VARIANTS, 758100),
                 'screen-v3': (persistent_make, PERSISTENT, 758200),
                 'screen-v4': (lineup_make, LINEUP, 758300)}
    if args.stage == 'local':
        names = read(STUDY/args.screen_stage/'result.json')['selected'][:2]
        factory = lambda name: read(STUDY/args.screen_stage/'candidates'/name/'policy.ir.json')
        seed = 759000
    else:
        factory, names, seed = factories[args.stage]
    if not names:
        raise ValueError('No local qualifier; revise from evidence before continuing')
    evaluate(args.stage, names, 60 if args.stage == 'local' else 6, seed, factory)
