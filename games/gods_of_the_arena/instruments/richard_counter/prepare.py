"""Create native Python IR candidates from the exact currently deployed source."""
from copy import deepcopy
import pprint
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CLEAN = ROOT.parent / 'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CLEAN))
from policy_ir import read, digest, refresh_grounding, bundle, compile_policy, extract
from games.gods_of_the_arena.instruments.richard_counter import contracts

STUDY = ROOT / 'tmp/gota-ir/richard-counter-20260920'
PARENT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/jordan268'


def make(name):
    frozen = STUDY / 'candidates' / name / 'policy.ir.json'
    if frozen.exists():
        return read(frozen)
    parent = read(PARENT / 'policy.ir.json')
    assert compile_policy(parent).encode() == (PARENT / 'policy.bas').read_bytes()
    if name == 'parent':
        return parent
    assert name in ('critical40', 'critical60', 'weapon')
    p = deepcopy(parent)
    p['id'] = 'gota_richard135_' + name
    if name == 'weapon':
        p['skill']['equipment']['parameters']['red_loadout'] = 1
    else:
        p['skill']['observe']['operator'] = 'lineup_critical_recall'
        p['skill']['observe']['parameters'].update(critical_radius=int(name[8:]),
            critical_group=2, critical_hold=1200)
        p['goal']['G_defense']['preference'] += (
            ' Override distant recall cancellation for a standing-anchor-qualified '
            'two-hero threat close to our god; preserve ordinary counterpressure elsewhere.')
    record = STUDY / 'prospective-snapshots' / (name + '.md')
    if not record.exists():
        record.parent.mkdir(exist_ok=True)
        record.write_text((ROOT / 'games/gods_of_the_arena/experiments/2026-09-20-richard135-counter.md').read_text())
    claim_key = 'Richard135_weapon' if name == 'weapon' else 'Richard135_critical_recall'
    p['belief']['claims'][claim_key] = {
        'claim': ('A weapon-first red frontline may improve early combat and XP versus '
        'Richard135; eight DeathKnight deaths and only12 basic hits motivate a test, '
        'not a causal conclusion.' if name == 'weapon' else
        'Richard135 losses on both colors include split threats bypassing the '
        'four-hero defense threshold and remote cancellation. A nearby two-hero '
        'critical-pressure exception may defend in time. Competitive effect untested.'),
        'status': 'untested', 'evidence': [{'artifact': str(record),
            'sha256': digest(record.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision'] + 1, parent=digest(parent),
        change={'origin': 'Complete Richard135 league replay/owned VM reconstruction',
            'experiment': '2026-09-20-richard135-counter',
            'lever': 'red frontline equipment' if name == 'weapon' else 'critical remote recall exception',
            'candidate': name}, needs_review=['belief/' + claim_key])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in sys.argv[1:]:
        p = make(name)
        folder = STUDY / 'candidates' / name
        if folder.exists():
            assert read(folder / 'policy.ir.json') == p
        else:
            folder.parent.mkdir(parents=True, exist_ok=True)
            bundle(p, folder)
        (folder / 'policy.py').write_text('"""Primary-format IR candidate; see experiment record."""\n\nPOLICY = '
            + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
        assert extract(compile_policy(p), p) == p
        print(name, digest(compile_policy(p).encode()), flush=True)
