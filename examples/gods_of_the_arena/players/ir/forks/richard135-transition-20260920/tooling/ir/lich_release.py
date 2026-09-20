"""Preregister and run the Lich targeting repair after the complete failed gate."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import shutil
import subprocess

from economy_feedback import record
from economy_screen import run as local_run
from hosted_queue import run as hosted_run
from hosted_wave import client, get
from policy_ir import HERE, bundle, digest, read, refresh_grounding, write
from release_hosted import upload, compare
from release_workspace import RUN, SOURCE, VERSION, verify

STUDY = RUN / 'lich-followup'
PARENT = RUN / 'class-followup'
NAME = 'lich_nearest'
DESCRIPTION = 'Restore nearest-center targeting for Lich only; keep its cadence recovery, Berserker baseline behavior, and building-edge targeting for the other eight classes.'
RULE = ('Lich repair after a completed failed confirmation, never a gate change: preserve all other nine classes action/state traces and reproduce cadence for Lich. '
        '40new local games;160paired controls explicitly reused. Need>=v2+2/default+2/cadence, within4wins of parent (only4Lich cases), '
        'death<=110%cadence, XP>=80%cadence, all gear/VM/replay checks. Then100new hosted discovery games with original frozen controls reused for selection only; '
        'need>=5pp over both and no adverse class p<.005, same guards. Then fresh400/arm confirmation, excluding all1700earlier games plus this discovery, '
        '>=5pp and p<.025 versus each control, no adverse class p<.005, same guards.100sampled field games>=50wins before promotion. No interim tuning/stopping.')


def make():
    parent = read(PARENT / 'hosted-confirmation/berserker_base/feedback/policy.ir.json')
    p = deepcopy(parent)
    p['id'] = 'gota_release_lich_nearest'
    p['skill']['observe'] = {'operator': 'class_building_two',
                            'parameters': p['skill']['observe']['parameters'] | {'extra_class': 7}}
    p['goal']['G_base']['preference'] += ' Lich and Berserker use nearest-center targeting; only Berserker is exempt from normal recovery.'
    evidence = PARENT / 'hosted-confirmation/result.json'
    refs = [{'artifact': str(evidence), 'sha256': digest(evidence.read_bytes())}]
    p['belief']['claims']['B_candidate'] = {'claim': DESCRIPTION + ' The parent won224/400 versus172/173 controls but failed its Lich guard (0/40 vs cadence10/40). '
        'This is a new candidate, requiring independent evidence; the earlier confirmation remains failed.', 'status': 'untested', 'evidence': refs}
    p['update'] = {'revision': parent['update']['revision'] + 1, 'parent': digest(parent),
        'change': DESCRIPTION, 'needs_review': ['belief/B_candidate', 'goal/G_base', 'goal/G_fort'], 'evidence': refs}
    refresh_grounding(p)
    return p


def prepare_local():
    verify()
    d = STUDY / 'local'
    d.mkdir(parents=True, exist_ok=True)
    if (d / 'plan.json').exists():
        return d
    old = read(RUN / 'local/plan.json')
    for n in ['episode', 'audit', 'config.json', 'default.bas']:
        shutil.copy2(RUN / 'local' / n, d / n)
    sources = {n: old['sources'][n] for n in ['v2', 'cadence', 'default']}
    sources['berserker_base'] = str(PARENT / 'local/candidates/berserker_base/policy.bas')
    (d / 'screen').mkdir()
    for n in sources:
        prior = PARENT if n == 'berserker_base' else RUN
        (d / 'screen' / n).symlink_to(prior / 'local/screen' / n, target_is_directory=True)
    bundle(make(), d / 'candidates' / NAME)
    sources[NAME] = str(d / 'candidates' / NAME / 'policy.bas')
    tools = d / 'frozen-instruments'
    tools.mkdir()
    for p in HERE.glob('*.py'):
        if not p.name.startswith('test_'):
            shutil.copy2(p, tools / p.name)
    inputs = [d / n for n in ['episode', 'audit', 'config.json']] + [Path(p) for p in sources.values()]
    write(d / 'plan.json', {'created_at': datetime.now(timezone.utc).isoformat(), 'family': 'release',
        'game_version': VERSION, 'game_source': SOURCE, 'variants': {NAME: DESCRIPTION}, 'sources': sources,
        'inputs': {str(p): digest(p.read_bytes()) for p in inputs},
        'instruments': {p.name: digest(p.read_bytes()) for p in tools.glob('*.py')}, 'cases': old['cases'],
        'win_thresholds': {'v2': 2, 'default': 2, 'cadence': 0, 'berserker_base': -4}, 'survival_control': 'cadence',
        'reuse': '160 completed paired control tapes;40newgames. Local regression/mechanism checks, not competitive confirmation.', 'rule': RULE})
    return d


def parity():
    rows = []
    d = STUDY / 'local'
    assert read(d / 'screen-result.json')['verified_games'] == 200
    for case in read(d / 'plan.json')['cases']:
        folder = f"seed-{case['seed']}-slot-{case['slot']}"
        candidate = d / 'screen' / NAME / folder
        result = read(candidate / 'result.json')
        hero_class = result['heroes'][result['subject_slot']]['class']
        control = 'cadence' if hero_class == 7 else 'berserker_base'
        prior = RUN if control == 'cadence' else PARENT
        old_tape = prior / 'local/screen' / control / folder / 'episode.replay'
        new_tape = candidate / 'episode.replay'
        result = subprocess.run([str(RUN / 'build/replay-parity'), str(old_tape), str(new_tape)], capture_output=True, text=True, check=True)
        rows.append({**case, 'class': hero_class, 'control': control, 'old_sha256': digest(old_tape.read_bytes()),
                     'new_sha256': digest(new_tape.read_bytes()), **json.loads(result.stdout)})
    assert sum(r['class'] == 7 for r in rows) == 4
    write(d / 'class-parity.json', {'full_action_state_identity_cases': 40, 'new_games': 40,
        'reused_control_games': 160, 'comparator_sha256': digest((RUN / 'build/replay-parity').read_bytes()),
        'meaning': '36unaffected games reproduce parent actions/states;4Lich games reproduce cadence. VM work metrics may differ.', 'cases': rows})


def hosted():
    verify()
    parity()
    local = STUDY / 'local'
    screen = read(local / 'screen-result.json')
    if NAME not in screen['selected']:
        raise ValueError('Local Lich repair did not qualify')
    feedback = local / 'screen-feedback' / NAME
    if not feedback.exists():
        record(local / 'candidates' / NAME / 'policy.ir.json', local / 'candidates' / NAME / 'policy.bas',
            f'40new local repair games: {screen["metrics"][NAME]};160controls reused. All40intended whole-game action/state identities verified. Local selection only.',
            local / 'screen-result.json', feedback)
    root = STUDY / 'hosted-discovery'
    root.mkdir(exist_ok=True)
    if not (root / 'plan.json').exists():
        plan = read(RUN / 'hosted-discovery/plan.json')
        plan.update(created_at=datetime.now(timezone.utc).isoformat(), local_plan_sha256=digest((local / 'plan.json').read_bytes()),
            confirmation_rule=RULE, discovery_reject_adverse_classes=True,
            excluded_discovery_results=[str(RUN / 'hosted-discovery/result.json'), str(PARENT / 'hosted-discovery/result.json'), str(PARENT / 'hosted-confirmation/result.json')],
            reused_controls='Original100/arm controls reused only for adaptive selection; all1700previous seeds excluded from eventual confirmation.')
        write(root / 'plan.json', plan)
        for arm in ['v2', 'cadence']:
            (root / arm).symlink_to(RUN / 'hosted-discovery' / arm, target_is_directory=True)
    with client() as c:
        league = get(c, '/v2/leagues/league_3c60897b-25cf-4b37-9d1a-8554c1198f28')
        game = get(c, '/v2/coworlds/' + league['game']['coworld_id'])
        if game['version'] != VERSION or f'/tree/{SOURCE}/' not in game['manifest']['game']['runnable']['source_url']:
            raise ValueError('Live release changed')
    upload(STUDY)
    hosted_run([root / NAME])
    compare(STUDY)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['local', 'parity', 'hosted'])
    command = parser.parse_args().command
    if command == 'local':
        local_run(prepare_local(), 8, 'release')
    elif command == 'parity':
        parity()
    else:
        hosted()
