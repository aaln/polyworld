"""Check the descriptive model, saved reconstruction proofs and evidence hashes."""
from pathlib import Path
from collections import Counter
import hashlib,json,runpy
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'opponent.ir.json');rows=read(P/'evidence/actor-rows.json');a=read(P/'evidence/analysis.json');v=read(P/'evidence/verified.json')
assert runpy.run_path(str(P/'opponent.py'))['MODEL']==m
assert all(k in m for k in ['situation','belief','goal','skill','strategy','execution','update'])
assert not m['execution']['source_available'] and not m['execution']['proxy_usable'] and not m['execution']['forecast_validated'] and not m['execution']['compile_to_basic']
assert len(v['rows'])==72 and sum(r['valid'] for r in v['rows'])==9
assert all(r['all_replay_hashes_equal'] for r in v['rows'])
assert len({r['canonical_commands_sha1'] for r in v['rows']})==72
assert Counter(r['policy'] for r in rows)=={'aaron':38,'coach':37,'khors':39}
ours=[r for r in rows if r['policy']!='khors'];khors=[r for r in rows if r['policy']=='khors'];melee=[r for r in ours if r['class'] in ['DeathKnight','DemonHunter','VanguardKnight','Berserker']]
assert sum(r['score']==0 for r in ours)==14 and sum(r['score']==0 for r in khors)==8
assert len(melee)==13 and sum(r['score']==0 for r in melee)==9
for r in rows:
    assert r['dead_seconds']>=0
    assert r['xp']==sum(r[k] for k in ['hero_xp','creep_xp','building_xp','god_xp'])
    assert r['score']==max(0,r['xp']*1440-200*round(r['minutes']*1440))//1440
    assert abs(r['unclamped_score_margin']-(r['xp']-200*r['minutes']))<1e-9
    assert abs(r['net_xp_per_minute']-(r['xp']/r['minutes']-200))<1e-9
    assert r['xp_deficit_to_break_even']==max(0,-r['unclamped_score_margin'])
for cl,needed in [('Crossbowman',12),('Ranger',6)]:
    z=[r for r in khors if cl in r['draft']['available_before'] and (cl=='Crossbowman' or 'Crossbowman' not in r['draft']['available_before'])]
    assert len(z)==needed and all(r['class']==cl for r in z)
x=read(P/'evidence/own-source-summary.json')['rows'];assert len(x)==4 and sum(r['commands_matched'] for r in x)==5826
assert all(r['all_state_hashes_equal'] and r['all_actions_consumed'] and r['max_instructions']<20000 and r['max_work']<50000 for r in x)
for name,digest in read(P/'evidence/preserved-prior-models.json')['unchanged'].items():assert sha(ROOT/name)==digest
idx=read(P/'evidence/artifact-index.json');raw=Path(idx['raw_root']);checked=0
instrument=ROOT/'games/gods_of_the_arena/instruments/khors11420260923'
for name,source,provenance in [('stalls','stalls.nim','stalls-provenance.json'),('own-source-probe','own_source_probe.nim','own-source-provenance.json')]:
    proof=read(P/'evidence'/provenance)
    assert sha(instrument/source)==proof['source_sha256']
    if (raw/name).exists():assert sha(raw/name)==proof['binary_sha256']
if raw.exists():
    for name,digest in idx['files'].items():assert sha(raw/name)==digest,name;checked+=1
for name,digest in read(P/'package-manifest.json')['files'].items():assert sha(P/name)==digest,name
print(json.dumps({'verified':True,'league_games':72,'all_vm_clean_games':9,'other_vm_failure_games':63,'subject_appearances':114,'own_source_commands_matched':5826,'raw_hashes_checked':checked,'opponent_source_available':False,'proxy_usable':False}))
