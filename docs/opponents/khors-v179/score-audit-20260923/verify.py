"""Verify source identities, score accounting and preserved raw proof hashes."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(P/'evidence/analysis.json');v=read(P/'evidence/verified.json');ir=read(P/'opponent.ir.json')
assert len(v['rows'])==13 and len(a['all13']['rows'])==13
assert not ir['execution']['proxy_usable']
assert len({r['source_sha256'] for r in v['rows']})==1
assert v['rows'][0]['source_sha256']==ir['situation']['identity']['source_sha256_from_host_specs']
for r in v['rows']:
 assert r['all_state_hashes_equal'] and r['all_xp_scores_equal']
 assert r['score']==max(0,r['hero']['total_xp']*1440-200*r['ticks'])//1440
 assert r['slot'] not in r['failed_slots']
 assert sum(r['hero']['xp_sources'].values())==r['hero']['total_xp']
 raw=Path(a['raw_root'])/'episodes'/r['episode']
 if raw.exists():
  for n,d in r['hashes'].items():assert sha(raw/n)==d,(r['episode'],n)
assert a['coached_comparison'][0]['xp']==11892 and a['coached_comparison'][0]['score']==7781
assert a['barracks']['initial_per_team']==6 and len(a['barracks']['deaths'])==4
assert a['all13']['zero_basic_structure_damage_games']==12
print(json.dumps({'verified':True,'episodes':13,'source_sha256':a['source_sha256'],'proxy_usable':False}))
