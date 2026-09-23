"""Retrospective final inventory and buyback attempts, not purchase ordering."""
from pathlib import Path
from collections import Counter
import json,hashlib,statistics
ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT.parent/'polyworld/tmp/gota-score-20260922/hosted'
OUT=ROOT/'docs/reports/gota-adaptive-score-20260922/inventory-review.json'
IDS={'ours':'b65ccf7b-d7a1-4681-b57f-a55f5ace43c7','khors114':'145c01e0-0cbf-4e1e-8120-11b437175b91','richard167':'e811221e-c419-4f7b-9629-01f8722ab9f7'}
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for arm in read(OLD/'plan.json')['arms']:
    if arm['name']!='baseline':continue
    folder=OLD/'baseline'/str(arm['side'])
    for r in read(folder/'result.json')['rows']:
        assert r['valid'] and r['all_hashes_equal']
        path=folder/'artifacts'/r['episode']/'audit.json';audit=read(path)
        assert audit['hash_mismatches']==0
        for name,version in IDS.items():
            slot=arm['roster'].index(version);hero=audit['heroes'][slot]
            rows.append({'policy':name,'version':version,'own_color':hero['team'],'episode':r['episode'],'class':hero['class'],'gold':hero['gold'],'inventory':hero['inventory'],'counts':hero['item_counts'],'buyback_attempts':audit['commands'][slot][17],'audit_sha256':sha(path)})
summaries=[]
for name in IDS:
    rs=[r for r in rows if r['policy']==name];assert len(rs)==80
    summaries.append({'policy':name,'games':80,'mean_final_gold':statistics.mean(r['gold'] for r in rs),'mean_buyback_attempts':statistics.mean(r['buyback_attempts'] for r in rs),'final_equipped_counts':dict(Counter(i for r in rs for i in r['inventory'] if i!='NoItem'))})
report={'scope':'All80 prior clean 2026.9.22.3 baseline games. Final inventory is not purchase order; commands include rejected attempts. No item or buyback causal superiority inferred. ReplayAction17 is ActionBuyback in exact pinned replays.nim. Original captures preserved.','summaries':summaries,'rows':rows}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(summaries))
