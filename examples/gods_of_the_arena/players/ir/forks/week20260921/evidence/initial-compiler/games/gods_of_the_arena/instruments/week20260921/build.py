"""Compile the seven-layer new-week policy and verify exact reverse extraction."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pprint
import shutil
import subprocess
import contracts

contracts.register()
from policy_ir import compile_policy, extract, refresh_grounding, digest, grounded
from binding import VERSION

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT.parent / 'polyworld-gota-week-20260921'
STUDY = ROOT / 'tmp/gota-week-20260921'
PAIR = ROOT / 'examples/gods_of_the_arena/players/ir/forks/week20260921'
COMMIT = 'f776d5e55d439706a8d49878d17d7ba1f6a1f7ce'

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + '\n')

def policy(name='lane', tweaks=None):
    p = {'schema': 'gota-semantic-policy/1', 'id': 'gota_week20260921_' + name,
      'situation': {'grounded': {}, 'notes': 'Public draft choices and visible enemy objects only. Current tower aggro and nearby waves are facts, unseen opponents unknown. Shared XP rewards productive lanes; stronger towers require creep cover.'},
      'belief': {'grounded': {}, 'claims': {
        'NewWeekBundle': {'claim': 'Coordinated draft, explicit upgrades, productive lanes, permanent gear, finite defense and recovery should improve new-week outcomes. Hypothesis for the bundle, not component causality.', 'status': 'untested', 'evidence': []}}},
      'goal': {'Win': {'preference': 'Destroy the opposing god while preserving ours.', 'provenance': 'authored'},
               'Grow': {'preference': 'Earn shared XP and last-hit gold, spend legal skill points, and convert gold into durable combat strength.', 'provenance': 'authored'},
               'Survive': {'preference': 'Avoid repeated feeding, recover efficiently, and promptly return to productive play.', 'provenance': 'authored'}},
      'skill': {k: {'operator': 'week_' + k, 'parameters': v.defaults()} for k,v in contracts.SPECS.items()},
      'strategy': [{'id': 'R_' + k, 'when': 'always' if k in ('draft','lifecycle') else 'active',
          'skill': k, 'for': ['Win','Grow','Survive']} for k in contracts.SPECS],
      'execution': {'binding': VERSION, 'game_version': '2026.9.21.5', 'language': 'BASIC'},
      'update': {'revision': 1, 'parent': 'c708970db2c1be838d6d38b726cbc1b94b73c88f7c5b20c0adfd4d02666436a4',
        'change': {'origin': 'User requested new-week policy; clean Bassy binding replaces previous engine assumptions', 'upstream': COMMIT},
        'needs_review': ['belief/NewWeekBundle'], 'evidence': [{'artifact': 'games/gods_of_the_arena/experiments/2026-09-21-week-policy.md'}]}}
    for skill, values in (tweaks or {}).items(): p['skill'][skill]['parameters'].update(values)
    refresh_grounding(p)
    return p

def save(p, folder):
    if folder.exists(): raise ValueError('Preserve frozen candidate: ' + str(folder))
    source = compile_policy(p)
    recovered = extract(source, p)
    assert recovered == p
    folder.mkdir(parents=True)
    write(folder / 'policy.ir.json', p)
    write(folder / 'extracted.ir.json', recovered)
    write(folder / 'semantics.json', grounded(p))
    (folder / 'policy.py').write_text('"""New-week semantic policy; generated BASIC is derived from these skills."""\n\nPOLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (folder / 'policy.bas').write_text(source)
    engine_files=['examples/gods_of_the_arena/'+n+'.nim' for n in ('bots','content','sim','game','replays')]+['coworld/dependencies.lock']
    write(folder / 'manifest.json', {'game_version': '2026.9.21.5','upstream': COMMIT,
        'source_sha256': digest(source.encode()), 'ir_sha256': digest(p),
        'engine_files': {n:digest((ENGINE/n).read_bytes()) for n in engine_files},
        'tooling': {str(x.relative_to(ROOT)):digest(x.read_bytes()) for x in sorted(Path(__file__).parent.rglob('*.py'))},
        'artifacts': {x.name:digest(x.read_bytes()) for x in sorted(folder.iterdir()) if x.is_file()},
        'compile_extract_exact': True, 'validation': 'unvalidated: awaiting actual VM and complete-game checks'})
    print(json.dumps({'pair':str(folder),'bytes':len(source.encode()),'source_sha256':digest(source.encode()),'round_trip':True}),flush=True)

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='lane');args=parser.parse_args()
    assert subprocess.check_output(['git','-C',str(ENGINE),'rev-parse','HEAD'],text=True).strip()==COMMIT
    save(policy(args.name),STUDY/'candidates'/args.name)
