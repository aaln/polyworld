import json,collections,sys
d=sys.argv[1]
ours={'61148477-1928-43c6-a881-8daea0e8f6c2':'Aaron','2bb94c84-fc32-4a81-9e6d-46666bc0315f':'Coach'}
eps=json.load(open(d+'/episodes.json'))
rec=collections.defaultdict(collections.Counter); seen=set(); tot=collections.defaultdict(collections.Counter)
for e in eps:
    if e['id'] in seen: continue
    seen.add(e['id'])
    ps=e['participants']; rv={p['policy_version_id'] for p in ps if p['position']<5}; bv={p['policy_version_id'] for p in ps if p['position']>=5}
    if len(rv)!=1 or len(bv)!=1: continue
    rv,bv=rv.pop(),bv.pop()
    for mine,col,opp in ((rv,'red',bv),(bv,'blue',rv)):
        if mine not in ours: continue
        if e['status']!='completed': r='INVALID'
        else:
            sc={s['policy_version_id']:s['score'] for s in e['scores']}
            r='W' if sc[mine]>sc[opp] else 'L' if sc[mine]<sc[opp] else 'D'
        oppn=[p['player_name']+' '+p['policy_name'][-20:]+':v'+str(p['version']) for p in ps if p['policy_version_id']==opp][0]
        rec[(ours[mine],oppn,col)][r]+=1; tot[ours[mine]][r]+=1
for k,v in sorted(rec.items()): print(k,dict(v))
print(dict(tot))
