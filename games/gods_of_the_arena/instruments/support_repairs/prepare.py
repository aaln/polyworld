"""Freeze isolated primary-IR repairs and a six-case native regression screen."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import pprint
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CLEAN))
from policy_ir import read, write, digest, refresh_grounding, bundle, compile_policy, extract
from games.gods_of_the_arena.instruments.support_repairs import contracts

STUDY = ROOT / 'tmp/gota-ir/support-repairs-20260920'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/jordan268'
CAMPAIGN = ROOT.parent / 'gota-autoresearch'
REFERENCE = CAMPAIGN / 'historical-richard-review-20260920/references/anchor'
RECORD = ROOT / 'games/gods_of_the_arena/experiments/2026-09-20-support-restoration-repairs.md'
NAMES = ('deployed', 'anchored', 'unanchored', 'historical_anchor')


def make(name):
    if (STUDY / 'candidates' / name / 'policy.ir.json').exists():
        return read(STUDY / 'candidates' / name / 'policy.ir.json')
    parent = read(PARENT / 'policy.ir.json')
    assert compile_policy(parent).encode() == (PARENT / 'policy.bas').read_bytes()
    if name == 'deployed':
        return parent
    if name == 'historical_anchor':
        reference = read(REFERENCE / 'policy.ir.json')
        assert compile_policy(reference).encode() == (REFERENCE / 'policy.bas').read_bytes()
        return reference
    assert name in ('anchored', 'unanchored')
    policy = deepcopy(parent)
    policy['id'] = 'gota_support_restore_' + name
    policy['skill']['observe']['operator'] = contracts.NAME
    policy['skill']['observe']['parameters'].update(
        assist_tiles=22, wait_support=0, idle_only=1, frontline_only=0,
        anchor_required=int(name == 'anchored'))
    policy['belief']['claims']['RestoredCasterSupport'] = {
        'claim': 'Visible healthy allied attack commitment may let idle red casters '
                 'support a defense earlier while preserving distant counterpressure. '
                 'Richard135 and Alex transfer is untested.',
        'status': 'untested', 'evidence': [{'artifact': str(STUDY / 'prospective.md')}]}
    policy['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
        change={'origin': 'Historical Richard78 support evidence and current opponent IR',
                'experiment': RECORD.stem, 'lever': 'idle red caster support restoration',
                'candidate': name}, needs_review=['belief/RestoredCasterSupport'])
    refresh_grounding(policy)
    return policy


def prepare():
    STUDY.mkdir(parents=True, exist_ok=True)
    if not (STUDY / 'prospective.md').exists():
        shutil.copy2(RECORD, STUDY / 'prospective.md')
    for name in NAMES:
        policy = make(name)
        destination = STUDY / 'candidates' / name
        if not destination.exists():
            destination.parent.mkdir(exist_ok=True)
            bundle(policy, destination)
            (destination / 'policy.py').write_text('"""Frozen primary IR repair experiment."""\n\nPOLICY = '
                + pprint.pformat(policy, width=110, sort_dicts=False) + '\n')
        assert compile_policy(policy).encode() == (destination / 'policy.bas').read_bytes()
        assert extract(compile_policy(policy), policy) == policy
    config = read(CAMPAIGN / 'config.json')
    if not (STUDY / 'plan.json').exists():
        write(STUDY / 'config.json', config['game_config'])
        sources = {n: str(STUDY / 'candidates' / n / 'policy.bas') for n in NAMES}
        opponents = {'default': str(ROOT.parent / 'gota-research-20260916/r5/default.bas'),
                     'deployed': sources['deployed'], 'historical_anchor': sources['historical_anchor']}
        inputs = [Path(p) for p in set(sources.values()) | set(opponents.values())]
        inputs += [STUDY / 'config.json', STUDY / 'prospective.md', Path(__file__),
                   Path(contracts.__file__), CLEAN / 'ally_assist_contract.py', CLEAN / 'anchored_support_contract.py']
        write(STUDY / 'plan.json', {
            'frozen_at': datetime.now(timezone.utc).isoformat(), 'sources': sources,
            'opponents': opponents, 'cases': [{'seed': 9860000 + i * 2 + side, 'opponent': name, 'side': side}
                                            for i, name in enumerate(opponents) for side in (0, 1)],
            'game_version': config['game_version'], 'engine_commit': config['engine_commit'],
            'gate': {'retain_each_deployed_win': True, 'minimum_red_win_gain': 1,
                     'max_deaths': 'max(1.15 * deployed deaths, deployed deaths + 5)',
                     'all_equipment': True, 'native_budgets_and_replay': True, 'support_activation': True},
            'inputs_sha256': {str(p): digest(p.read_bytes()) for p in inputs},
            'scope': '24 complete local mechanism/regression games; no private rival or competitive evidence.'})
    print(json.dumps({'study': str(STUDY), 'sources': {
        n: digest((STUDY / 'candidates' / n / 'policy.bas').read_bytes()) for n in NAMES}}, indent=2))


if __name__ == '__main__':
    prepare()
