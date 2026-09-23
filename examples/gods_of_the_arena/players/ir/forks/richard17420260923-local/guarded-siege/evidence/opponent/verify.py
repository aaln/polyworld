"""Verify the source snapshot, recovered neural weights and exact replay proofs."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
s=(P/'richard-v174.bas').read_text();provenance=read(P/'provenance.json');model=read(P/'richard_v174.source.ir.json');network=read(P/'neural-controller.json')
assert hashlib.sha256(s.encode()).hexdigest()==provenance['source_sha256']==network['source_sha256']==model['situation']['identity']['source_sha256']
assert hashlib.sha256((P/'source-candidate.yaml').read_bytes()).hexdigest()==provenance['manifest_sha256']
assert all(k in model for k in ['situation','belief','goal','skill','strategy','execution','update'])
assert not model['execution']['proxy_usable'] and model['execution']['authentic_source_replay_verified']
hidden=[]
for m in re.finditer(r'^h\((\d+)\) = (\d+)(.*)$',s,re.M):
 c={int(i):int(w) for i,w in re.findall(r'f\((\d+)\) \* \((-?\d+)\)',m[3])};assert len(c)==25
 hidden.append({'index':int(m[1]),'bias':int(m[2]),'weights':[c[i] for i in range(25)]})
outputs=[]
for m in re.finditer(r'^score = (\d+)(.*)\nif score > bestScore then\n  bestScore = score\n  decision = (\d+)',s,re.M):
 c={int(i):int(w) for i,w in re.findall(r'h\((\d+)\) \* \((-?\d+)\)',m[2])};assert len(c)==16
 outputs.append({'decision':int(m[3]),'bias':int(m[1]),'weights':[c[i] for i in range(16)]})
assert hidden==network['hidden'] and outputs==network['outputs']
rows=[read(p) for p in (P/'evidence').glob('*.json')]
assert len(rows)==4 and all(r['all_state_hashes_equal'] and r['all_actions_consumed'] for r in rows)
assert sum(r['commands_matched'] for r in rows)==82818
assert sum(r['counts'].get('combat_8',0) for r in rows)==45490
for r in rows:assert r['max_instructions']<=19000 and r['max_work']<=50000
print(json.dumps({'verified':True,'source_sha256':provenance['source_sha256'],'reconstructed_commands':82818,'episodes':4,'semantic_surrogate_validated':False}))
