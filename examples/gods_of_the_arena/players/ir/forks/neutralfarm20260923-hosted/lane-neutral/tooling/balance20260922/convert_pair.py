"""Compile or extract a captured current-engine semantic policy."""
import argparse
import json
from pathlib import Path
import pprint
import runpy
import sys

pair = Path(__file__).resolve().parent
sys.path.insert(0, str(pair / 'tooling/balance20260922'))
import build

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('variant', choices=('control', 'ranger', 'crossbow', 'warlock', 'arcanist'))
parser.add_argument('mode', choices=('compile', 'extract'))
parser.add_argument('--policy', type=Path)
parser.add_argument('--source', type=Path)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
assert not args.out.exists(), 'Preserve captured inputs; choose a new output folder'
build.configure_control() if args.variant == 'control' else build.configure()
ir = build.ir
p = runpy.run_path(str(args.policy or pair / args.variant / 'policy.py'))['POLICY']
if args.mode == 'extract':
    assert args.source
    source = args.source.read_text()
    p = ir.extract(source, p)
else:
    ir.refresh_grounding(p)
    source = ir.compile_policy(p)
if source.encode() != (pair / args.variant / 'policy.bas').read_bytes():
    for claim in p['belief']['claims'].values():
        claim['status'] = 'requires_review'
    p['update']['needs_review'] = ['belief/' + k for k in p['belief']['claims']]
    p['update']['change'] = {'origin': 'Edited executable; prior results do not validate these bytes'}
    ir.refresh_grounding(p)
assert ir.extract(source, p) == p
args.out.mkdir(parents=True)
for name, obj in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
    (args.out / name).write_text(json.dumps(obj, indent=2) + '\n')
(args.out / 'policy.bas').write_text(source)
(args.out / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
print(json.dumps({'source_sha256': ir.digest(source.encode()), 'ir_sha256': ir.digest(p)}))
