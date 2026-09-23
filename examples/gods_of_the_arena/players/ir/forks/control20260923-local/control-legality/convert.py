"""Convert the crowd-control legality semantic policy through its frozen binding."""
import argparse
import json
from pathlib import Path
import pprint
import runpy
import sys

pair = Path(__file__).resolve().parent
sys.path.insert(0, str(pair / 'tooling/control20260923'))
import control_binding
control_binding.configure()
ir = control_binding.ir
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode', choices=('compile', 'extract'))
parser.add_argument('--policy', type=Path, default=pair / 'policy.py')
parser.add_argument('--source', type=Path)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
assert not args.out.exists()
p = runpy.run_path(str(args.policy))['POLICY']
if args.mode == 'extract':
    assert args.source
    source = args.source.read_text()
    p = ir.extract(source, p)
else:
    ir.refresh_grounding(p)
    source = ir.compile_policy(p)
if source.encode() != (pair / 'policy.bas').read_bytes():
    for claim in p['belief']['claims'].values():
        claim['status'] = 'requires_review'
    p['update']['needs_review'] = ['belief/' + k for k in p['belief']['claims']]
    p['update']['change'] = {'origin': 'Edited executable; prior results no longer validate it'}
    ir.refresh_grounding(p)
assert ir.extract(source, p) == p
args.out.mkdir(parents=True)
for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
    (args.out / name).write_text(json.dumps(value, indent=2) + '\n')
(args.out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
(args.out / 'policy.bas').write_text(source)
print(json.dumps({'source_sha256': ir.digest(source.encode()), 'ir_sha256': ir.digest(p)}))
