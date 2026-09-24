"""Check published evidence integrity, identity and conditional denominators."""
from pathlib import Path
import hashlib,json

root=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
manifest=read(root/'manifest.json')
for name,digest in manifest['files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
ir=read(root/'opponent.ir.json');summary=read(root/'evidence/summary.json')
rows=[r for r in read(root/'evidence/actor-rows.json') if r['version']==ir['situation']['identity']['policy_version_id']]
assert len(rows)==28 and len({r['episode'] for r in rows})==28
assert {r['source_sha256'] for r in rows}=={ir['situation']['identity']['source_sha256_from_specs']}
assert sum(r['all_vm_clean'] for r in rows)==5 and all(r['subject_vm_clean'] for r in rows)
assert not ir['execution']['proxy_usable'] and not ir['execution']['forecast_validated']
for r in rows:
    h=r['telemetry'];assert sum(h['xp_sources'].values())==h['total_xp']
    assert max(0,h['total_xp']*1440-200*round(r['minutes']*1440))//1440==r['score']
for claim in ir['belief']['claims'][:3]:
    e=claim['evidence'];assert 0<=e['choices']<=e['opportunities']
    assert 0<=e['choice_episodes']<=e['eligible_episodes']<=28
assert sum(r['counts'].get('both_choose_2',0) for r in rows)==801
assert sum(r['counts'].get('neutral_opportunity_choose_6',0) for r in rows)==1243
print('Verified 28 version-bound appearances, source identity, XP/score accounting and non-executable evidence package.')
