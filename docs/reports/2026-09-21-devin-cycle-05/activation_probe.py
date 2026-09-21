import json,sys,collections
f=sys.argv[1]; lo,hi=int(sys.argv[2]),int(sys.argv[3]); ourteam=int(sys.argv[4])
act=collections.Counter(); ally_attacked=collections.Counter(); firsts={}
with open(f) as fh:
    next(fh)
    for line in fh:
        r=json.loads(line); t=r.get('tick')
        if t is None: continue
        if t<lo or t>hi: continue
        objs={o[0]:o for o in r['objects']}
        heroes=[o for o in objs.values() if o[1]==2]
        for s in heroes:
            if s[2]!=ourteam or s[6]<=0: continue
            tgt=objs.get(s[8]); tgt_kind=tgt[1] if tgt else 0
            for e in heroes:
                if e[2]==ourteam or e[6]<=0: continue
                a=objs.get(e[8])
                if not a or a[1]!=2 or a[2]!=ourteam or a[0]==s[0] or a[6]<=0: continue
                ally_attacked[s[0]]+=1
                de=(s[4]-e[4])**2+(s[5]-e[5])**2; da=(s[4]-a[4])**2+(s[5]-a[5])**2
                if de<=36 and da<=36 and tgt_kind in (0,3):
                    act[s[0]]+=1; firsts.setdefault(s[0],(t,e[0],a[0],tgt_kind,de,da))
                    break
print('ticks any ally-hero-attacked visible per self:',dict(ally_attacked))
print('v2 predicate fires (ticks) per self:',dict(act)); print('first fire:',firsts)
