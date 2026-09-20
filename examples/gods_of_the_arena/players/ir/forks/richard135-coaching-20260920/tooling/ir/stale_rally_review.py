"""Join a full native replay, owned BASIC decisions, and structure damage."""
import json
from jordan254_research import STUDY
from policy_ir import read,write,digest

ROOT=STUDY/'user-stall-77d700dd'
EPISODE='ereq_77d700dd-de3c-4ee6-ab43-965fedf66b7d'


def main():
    folder=ROOT/'artifacts'/EPISODE
    events=[json.loads(l) for l in (ROOT/'structure-damage.jsonl').open()]
    assert events[-1]['hash_mismatches']==0 and events[-1]['ticks']==13872
    proof=read(ROOT/'owned-proof.json')
    assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
    deaths={}
    core=[]
    for e in events:
        if e['type']!='damage':continue
        for b in e['structures']:
            if b['before']>0 and b['after']<=0:deaths[str(b['id'])]=e['tick']
            if b['id']==1:
                hits=[f for f in e['creep_swings_landed'] if f['team']==1 and f['attacking_fort']]
                assert min(b['before'],12*len(hits))==b['before']-b['after']
                assert all((h['position'][0]-105.09375)**2+(h['position'][1]-10.90625)**2>20**2
                           for h in e['heroes'] if h['team']==1 and h['hp']>0)
                core.append({'tick':e['tick'],'hp_before':b['before'],'hp_after':b['after'],
                             'creep_ids':[f['id'] for f in hits]})
    snapshots=[];last_refresh={}
    for line in (folder/'decisions.jsonl').open():
        r=json.loads(line)
        if r['type']!='decision' or r['slot'] not in [0,2,3]:continue
        m=r['memory']
        if m['defUntil']==r['tick']+7200:last_refresh[r['slot']]=r
        if r['tick']==13081:snapshots.append(r)
    assert len(snapshots)==3
    assert all(r['memory']['defUntil']==17672 and r['memory']['bestId']==0 and
               r['memory']['defActive']==1 and r['memory']['defMoveAccepted']==1 and
               [r['memory']['defPointX'],r['memory']['defPointY']]==[73,11] for r in snapshots)
    assert all(r['tick']==10472 and r['memory']['defAnchor']==11 for r in last_refresh.values())
    result={'episode':EPISODE,'opponent':'Polyworld GOTA base.bas:v1','game_version':'2026.9.16.5',
            'own_source_sha256':'455ac9dd6ec8bc52db5e6547ba3894391fce9f38cf20ddd279e176c87b379ba5',
            'owned_proof':proof,'native_damage_proof':events[-1],'structure_death_ticks':deaths,
            'last_sentry_refresh':list(last_refresh.values()),'screenshot_tick_decisions':snapshots,
            'fort_damage':core,'all_fort_damage_accounted_for_by_enemy_creeps':True,
            'mechanism':'At10472 a visible enemy refreshes7200tick sentry duty at standing tower11. Tower11 dies during that same tick. Its absence is not used to retire the saved rally. DK/Lich/Warlock keep rally73,11 with no combat target until after the match ends. Hero-group detection also fails to react to the independent core-creep attack.',
            'collision_claim':'The inspected wait is caused by stale accepted walk orders. This evidence does not establish a physical collision deadlock.',
            'warning100_fixes_this':False,
            'inputs':{str(p):digest(p.read_bytes()) for p in [ROOT/'structure-damage.jsonl',ROOT/'owned-proof.json',ROOT/'episode-request.json']}}
    write(ROOT/'diagnosis.json',result)
    (ROOT/'REPORT.md').write_text('''# Red-side stale rally: confirmed decision bug

In [the reported match](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:ereq_77d700dd-de3c-4ee6-ab43-965fedf66b7d), our deployed middle-rush policy lost to **Polyworld GOTA base.bas:v1**, not Jordan.

At tick **10,472**, the three sentries renewed their defensive commitment for **7,200 ticks (five minutes)** around our inner tower11. The tower was destroyed during that same tick. The policy never invalidated the saved rally when the tower disappeared.

At the screenshot's tick **13,081**, Death Knight, Lich, and Warlock each had `defActive=1`, `bestId=0`, `defUntil=17672`, and an accepted `walkTo(73,11)`. That destination is roughly32tiles from our god. Their order would have expired after the game ended at13872. This is stale decision state; accepted movement alone cannot prove that heroes never collide, but a collision is unnecessary to explain this wait.

The last god guard fell at **13,499**. Enemy creeps started hitting our400HP god at **13,551** and destroyed it at **13,872**. Every god HP loss is accounted for by native creep swings (12damage each, clamped on the final hit); all living enemy heroes were over20tiles away at each damage event. Meanwhile our three healthy defenders kept waiting. The remaining two heroes were pushing across the map.

The root problems are an objective that outlives its tower and a hero-group alarm that does not cover a creep-only base attack. A repair needs to revalidate the actual saved friendly anchor and independently respond to visible creeps threatening the god. Simply spreading the same stale rally would retain the strategic failure.

**Evidence:** full13872tick replay reconstruction, zero hash mismatches, all137344actions consumed, all70399ownedcommands reproduced from the exact deployed BASIC. `diagnosis.json` contains the joined decisions, structure deaths, and exact fort-damage sequence. `positions.png` is a source-verified schematic, not a recording of the native3D viewer.

**Release boundary:** the newly validated warning100 candidate improves the early Jordan response. It does not repair this stale-rally bug; repair experiments are separate from its promotion.
''')
    print('Confirmed stale tower11 duty and all400 god HP lost to enemy creeps;',len(core),'damage ticks.')


if __name__=='__main__':main()
