"""Matched 40-game/color probes against the three named lane-rush policies."""
import argparse
import json
import shutil
import time
from copy import deepcopy
from pathlib import Path

from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_wave import client, create
from policy_ir import read, write, digest, HERE, bundle, refresh_grounding, compile_policy, extract
from release_workspace import RUN, VERSION
from rush_defense import STUDY
from rush_hosted import upload
from win_hosted import live

CONTROL = '810d3860-af35-4fed-9364-a4e4bd8b0c2b'


def control_root():
    ref = STUDY/'control-reference.json'
    if not ref.exists():
        return STUDY/'hosted/current'
    data = read(ref)
    path = Path(data['directory'])
    if digest((path/'result.json').read_bytes()) != data['result_sha256']:
        raise ValueError('Reused control evidence changed')
    return path


def freeze():
    game = live()
    config = next(v['game_config'] for v in game['manifest']['variants'] if v['id'] == 'competition')
    config = {k: v for k, v in config.items() if k not in {'seed', 'players', 'tokens'}}
    rivals = read(RUN/'coached-lanes/khors-defense/rush-rivals.json')
    order = ['khors:v1', 'red-kite:v20', 'gota-g001:v1']
    rivals = [next(r for r in rivals if r['label'] == label) for label in order]
    plan = {'target': {'coworld_id': game['id'], 'variant_id': 'competition'},
            'game_version': VERSION, 'game_source': game['manifest']['game']['runnable']['source_url'],
            'config': config, 'rivals': rivals, 'episodes_per_color': 40,
            'control_version': CONTROL,
            'design': 'Five identical copies of an owned policy versus five copies of each exact named '
                      'rival. One40episode request per color,80per rival,240per policy. Retest the '
                      'deployed control and each locally qualified candidate; all ten seats pinned. '
                      'Drain server, artifacts, fullVM and replay audits between arms. No interim tuning.',
            'interpretation': 'Six fixed tactical lineups per policy; count exact command diversity. '
                              'Seeded repeats are not independent strategies. A two-player-mode '
                              'defense result does not establish mixed-team improvement.',
            'gates': {'minimum_wins_per_color': 24, 'minimum_total_gain': .2,
                      'no_rival_color_regression': True, 'all_gear': True,
                      'next': 'Fresh mixed-roster paired-player comparison and field guardrail before league selection.'}}
    if (STUDY/'control-reference.json').exists():
        reference = read(STUDY/'control-reference.json')
        root = control_root()
        if read(root/'result.json')['games'] != 240:
            raise ValueError('Reused control is incomplete')
        for rival in rivals:
            key = rival['label'].split(':')[0].replace('-','_')
            old = read(root/'matchups'/key/'plan.json')
            if (old['policy_version'] != CONTROL or old['rival_version'] != rival['id'] or
                    any(old[k] != plan[k] for k in ['target','game_version','game_source','config'])):
                raise ValueError('Reused control does not match the frozen source, rival or configuration')
        plan['reused_control'] = reference
    path = STUDY/'hosted-plan.json'
    if path.exists() and read(path) != plan:
        raise ValueError('Frozen live game or rival study changed')
    write(path, plan)
    return plan


def prepare(name):
    plan = freeze()
    if name == 'current':
        if (STUDY/'control-reference.json').exists():
            raise ValueError('This study explicitly reuses a completed control; do not relaunch it')
        root = STUDY/'hosted/current'; root.mkdir(parents=True, exist_ok=True)
        version = CONTROL
        label = 'aaron-gota-ir-win-bounded-0916:v1'
    else:
        local = read(STUDY/'local/result.json')
        if name not in local['selected'] or local['metrics'][name]['games'] < 60:
            raise ValueError('Candidate needs complete local60case qualification')
        feedback = STUDY/'local/context-feedback'/name
        if not feedback.exists():
            parent = read(STUDY/'local/feedback'/name/'policy.ir.json')
            policy = deepcopy(parent)
            evidence = RUN/'coached-lanes/r5-live-league/result.json'
            mixed = read(evidence)
            a, b = mixed['arms']['candidate'], mixed['arms']['control']
            policy['belief']['claims']['B_parent_mixed_context'] = {
                'claim': f'Parent gear-only policy failed its frozen800game mixed-team gate despite '
                         f'allied wins {a["allied_wins"]}/160 versus {b["allied_wins"]}/160. '
                         f'Checks: {mixed["checks"]}. The new defense behavior has not inherited '
                         'mixed-team validation and requires its own comparison. Parent source and '
                         'known failure are retained; this is not a claim that defense fixes them.',
                'status': 'requires_review',
                'evidence': [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]}
            policy['update'].update(revision=parent['update']['revision']+1, parent=digest(parent),
                                    change='Incorporate completed parent league result without changing candidate behavior')
            policy['update']['needs_review'].append('belief/B_parent_mixed_context')
            refresh_grounding(policy)
            source = (STUDY/'local/candidates'/name/'policy.bas').read_text()
            if compile_policy(policy) != source or extract(source, policy) != policy:
                raise ValueError('Measured parent context changed executable behavior')
            bundle(policy, feedback)
        root, meta = upload(name, STUDY, 'aaron-gota-ir-rush-defense',
                            'Shared-vision coordinated lane-rush defense, bounded memory, local focus and regrouping; exact IR defines combined behavior',
                            feedback_override=feedback)
        version, label = meta['id'], f'{meta["name"]}:v{meta["version"]}'
    paths = []
    for rival in plan['rivals']:
        key = rival['label'].split(':')[0].replace('-', '_')
        path = root/'matchups'/key
        path.mkdir(parents=True, exist_ok=True)
        p = {k: plan[k] for k in ['target', 'game_version', 'game_source', 'config', 'episodes_per_color', 'design', 'interpretation']}
        p.update(policy_version=version, policy_label=label, rival=rival['label'], rival_version=rival['id'], rival_key=key)
        if (path/'plan.json').exists() and read(path/'plan.json') != p:
            raise ValueError('Frozen policy/rival comparison changed')
        write(path/'plan.json', p)
        for color in ['red', 'blue']:
            out = path/key/color
            out.mkdir(parents=True, exist_ok=True)
            slots = list(range(5)) if color == 'red' else list(range(5, 10))
            roster = [version if s in slots else rival['id'] for s in range(10)]
            arm = p | {'color': color, 'own_slots': slots, 'roster': roster}
            if (out/'plan.json').exists() and read(out/'plan.json') != arm:
                raise ValueError('Frozen color arm changed')
            write(out/'plan.json', arm)
            # Retain the auditor pinned to this arm, including a separately
            # calibrated optimized build. Never invalidate cached audit hashes.
            if not (out/'audit').exists():
                shutil.copy2(RUN/'r5/audit', out/'audit')
            body = {'idempotency_key': f'gota-rush-defense-{digest(p)[:20]}-{color}',
                    'target': p['target'], 'game_config_overrides': p['config'], 'num_episodes': 40,
                    'roster': [{'slot': s, 'player': {'policy_ref': v}} for s, v in enumerate(roster)],
                    'notes': f'Anti-rush matched team probe: {label} on{color} versus{rival["label"]}. '
                             '40seeded games/color. Bothcolors and allthree pinned rivals before verdict; no champion selection.'}
            with client() as c:
                create(c, body, out/'batch', dry_run=True)
        paths.append(path)
    return paths


def run(name, wait_for_mixed=False, wait_for_control=False):
    paths = prepare(name)
    if wait_for_mixed:
        done = RUN/'coached-lanes/r5-live-league/result.json'
        print('Prepared exact-rival probes; waiting for existing mixed league experiment to drain.', flush=True)
        while not done.exists():
            time.sleep(15)
    if wait_for_control:
        print('Prepared candidate probes; waiting for the240game control benchmark to drain.', flush=True)
        while not (control_root()/'result.json').exists():
            time.sleep(15)
    for path in paths:
        if not (path/'result.json').exists():
            run_prepared(path)
        inventory(path)
    result = {'games': 240, 'rivals': {read(p/'plan.json')['rival_key']:
              next(iter(read(p/'result.json')['rivals'].values())) for p in paths}}
    result['wins'] = sum(r['wins'] for r in result['rivals'].values())
    result['all_gear'] = all(row['gear_heroes'] == 5 for r in result['rivals'].values() for row in r['rows'])
    result['interpretation'] = freeze()['interpretation']
    out = STUDY/'hosted'/name
    write(out/'result.json', result)
    if not (out/'feedback').exists():
        parent = HERE if name == 'current' else STUDY/'local/context-feedback'/name
        ir = parent/'win_bounded_0916.r5.evaluated.ir.json' if name == 'current' else parent/'policy.ir.json'
        bas = parent/'win_bounded_0916.r5.evaluated.bas' if name == 'current' else parent/'policy.bas'
        record(ir, bas, f'Exact named-rival rush benchmark: {result["wins"]}/240 wins; '
               +json.dumps({k: v['colors'] for k, v in result['rivals'].items()})+'. '+result['interpretation'],
               out/'result.json', out/'feedback')
    print(name, result['wins'], '/240', flush=True)
    if name != 'current':
        control = read(control_root()/'result.json')
        gates = freeze()['gates']
        checks = {
            'wins_each_color': all(c['win'] >= gates['minimum_wins_per_color'] for r in result['rivals'].values() for c in r['colors'].values()),
            'total_gain': (result['wins']-control['wins'])/240 >= gates['minimum_total_gain'],
            'no_rival_color_regression': all(result['rivals'][k]['colors'][c]['win'] >= control['rivals'][k]['colors'][c]['win'] for k in result['rivals'] for c in ['red','blue']),
            'equipment': result['all_gear']}
        write(out/'gate.json', {'checks': checks, 'passed': all(checks.values()),
                               'candidate_wins': result['wins'], 'control_wins': control['wins'],
                               'candidate_result_sha256': digest((out/'result.json').read_bytes()),
                               'control_result_sha256': digest((control_root()/'result.json').read_bytes()),
                               'next': gates['next'], 'interpretation': result['interpretation']})
        print('Rush gate:', checks, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    parser.add_argument('--study', type=Path)
    parser.add_argument('--reuse-control', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--wait-for-mixed', action='store_true')
    parser.add_argument('--wait-for-control', action='store_true')
    args = parser.parse_args()
    if args.study:
        STUDY = args.study.resolve()
        STUDY.mkdir(parents=True, exist_ok=True)
    if args.reuse_control:
        ref = args.reuse_control.resolve()
        reference = {'directory':str(ref), 'result_sha256':digest((ref/'result.json').read_bytes()),
                     'reason':'Reuse the completed exact same baseline, rivals, coworld release and config; no new result is claimed for these controls.'}
        path = STUDY/'control-reference.json'
        if path.exists() and read(path) != reference:
            raise ValueError('Frozen control reference changed')
        write(path,reference)
    prepare(args.name) if args.prepare_only else run(args.name, args.wait_for_mixed, args.wait_for_control)
