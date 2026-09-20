"""Join sampled visible base attacks to actual owned-hero orders.

Frames are post-tick samples, normally five seconds apart. Visibility/targets
at a sample are not the earlier VM snapshot. Orders in the following sample
interval establish observed responses, not internal intent or causality.
Ground truth about unseen enemies is excluded from the trigger description.
"""
import argparse
from bisect import bisect_right
from collections import defaultdict
import json,math
from pathlib import Path
from policy_ir import digest,write
from release_workspace import SOURCE,VERSION


def inspect(path,team,slots):
    if not slots or any(s//5!=team for s in slots):raise ValueError('Controlled slots must belong to the stated team')
    frames=[];actions=defaultdict(list);header=summary=None
    for line in path.open():
        r=json.loads(line)
        if r['type']=='header':header=r
        elif r['type']=='summary':summary=r
        elif r['type']=='frame':frames.append(r)
        elif r['type']=='action' and r['kind']==2 and r['slot'] in slots:
            actions[(r['slot'],r['first'])].append(r['tick'])
    if not summary or summary['hash_mismatches'] or header['source']!=SOURCE or header['version']!=VERSION:
        raise ValueError('Need a complete source-matched replay')
    cores=(1,28,29) if team==0 else (2,30,31)
    events=[]
    for n,frame in enumerate(frames):
        tick=frame['tick'];end=frames[n+1]['tick'] if n+1<len(frames) else tick
        buildings={b['id']:b for b in frame['buildings']};home=buildings[cores[0]]['position']
        alive=[h for h in frame['heroes'] if h['hp']>0]
        own=[h for h in alive if h['slot'] in slots]
        visible={o['id'] for h in own for o in h['visible_post_tick'] if o['hp']>0}
        enemies=[h for h in alive if h['team']!=team and h['id'] in visible]
        # Same home-front selection as the policy: don't credit a secondary
        # attacker that its detector would not select.
        front=min(enemies,key=lambda h:math.dist(h['position'],home),default=None)
        if front is None or math.dist(front['position'],home)>24:continue
        if front['target'] not in cores or buildings[front['target']]['hp']<=0:continue
        cluster=sum(math.dist(h['position'],front['position'])<=12 for h in enemies)
        responses=[]
        for h in own:
            orders=actions[(h['slot'],front['id'])]
            lo,hi=bisect_right(orders,tick),bisect_right(orders,end)
            responses.append({'slot':h['slot'],'position':h['position'],
                              'distance_home':math.dist(h['position'],home),'hp':h['hp'],
                              'sampled_target':h['target'],'target_orders_next_interval':hi-lo,
                              'first_order_delay_seconds':(orders[lo]-tick)/24 if hi>lo else None})
        allies=[h for h in alive if h['team']==team]
        events.append({'tick':tick,'seconds':tick/24,'interval_end_seconds':end/24,
                       'attacker_slot':front['slot'],'attacker_id':front['id'],
                       'attacker_position':front['position'],'attacked_structure':front['target'],
                       'structure_hp':buildings[front['target']]['hp'],'visible_cluster_size':cluster,
                       'all_living_allies_outside_home28':all(math.dist(h['position'],home)>28 for h in allies),
                       'no_living_allies':not allies,'owned':responses})
    isolated=[e for e in events if e['visible_cluster_size']==1]
    return {'source':SOURCE,'version':VERSION,'input_sha256':digest(path.read_bytes()),
            'team':team,'controlled_slots':slots,'ticks':summary['ticks'],'winner':summary['winner'],
            'visible_structure_attack_samples':len(events),'isolated_samples':len(isolated),
            'isolated_samples_with_owned_target_order':sum(any(h['target_orders_next_interval'] for h in e['owned']) for e in isolated),
            'isolated_samples_all_allies_away':sum(e['all_living_allies_outside_home28'] for e in isolated),
            'events':events,'interpretation':__doc__+' Sample counts are correlated time observations, not independent episodes.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('replay',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--team',type=int,choices=(0,1),required=True);p.add_argument('--slots',required=True)
    a=p.parse_args();r=inspect(a.replay,a.team,[int(x) for x in a.slots.split(',')]);write(a.output,r)
    print({k:v for k,v in r.items() if k not in ('events','interpretation')})
