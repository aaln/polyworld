"""Freeze bounded observation/decision-frequency experiments through semantic IR."""
import argparse
import json
from pathlib import Path
import pprint
import practiced

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--think', type=int, required=True)
parser.add_argument('--scan', type=int, required=True)
a = parser.parse_args()
practiced.configure('potions')
ir = practiced.ir
current = json.loads((practiced.ROOT / 'games/gods_of_the_arena/current.json').read_text())
p = json.loads((practiced.ROOT / current['reference_pair'] / 'policy.ir.json').read_text())
assert p['execution']['game_version'] == current['game_version']
assert p['execution']['binding'] == current['binding']
assert ir.digest((practiced.ROOT / current['reference_pair'] / 'policy.bas').read_bytes()) == current['reference_source_sha256']
parent = ir.digest(p)
p['id'] = 'gota_attention_' + a.name
p['skill']['draft']['parameters']['think_ticks'] = a.think
p['skill']['observe']['parameters']['scan_limit'] = a.scan
p['belief']['claims'] = {
    'CurrentContract': {'claim': 'Use only the pinned current host/binding; historical policy content and win-only gates are not active constraints.', 'status': 'supported', 'evidence': [{'artifact': 'games/gods_of_the_arena/current.json'}]},
    'Attention': {'claim': 'More frequent current observations improve XP score versus the current microplay parent without runtime failures.', 'status': 'untested', 'evidence': []},
    'DraftAndMelee': {'claim': 'Ranged-first drafting and melee exposure require verification in the supplied episode and clean current-roster games.', 'status': 'requires_review', 'evidence': [{'artifact': 'tmp/gota-targets-20260922/user-episode'}]}
}
p['goal']['Win']['preference'] = 'Objective pressure supports XP production; fort outcomes are a diagnostic, and the current league XP score is primary.'
p['update'] = {'revision': 4, 'parent': parent,
    'change': {'origin': 'User requested continued XP/last-hit practice; test fresher creep observations under the VM margin',
               'think_ticks': a.think, 'scan_limit': a.scan},
    'needs_review': ['belief/' + k for k in p['belief']['claims']],
    'evidence': []}
ir.refresh_grounding(p)
source = ir.compile_policy(p)
assert ir.extract(source, p) == p
folder = practiced.STUDY / 'candidates' / a.name
assert not folder.exists()
folder.mkdir(parents=True)
for name, data in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
    (folder / name).write_text(json.dumps(data, indent=2) + '\n')
(folder / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
(folder / 'policy.bas').write_text(source)
(folder / 'manifest.json').write_text(json.dumps({'source_sha256': ir.digest(source.encode()),
    'ir_sha256': ir.digest(p), 'binding_sha256': ir.digest(Path(practiced.__file__).read_bytes()),
    'builder_sha256': ir.digest(Path(__file__).read_bytes()), 'exact_roundtrip': True, 'validation': 'unvalidated'}, indent=2) + '\n')
print(a.name, ir.digest(source.encode()))
