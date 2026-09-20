"""Verify post-defense behavior fires on complete source-matched game tapes."""
import json
import time
from economy_feedback import record
from g002_coordination import STUDY, VARIANTS
from league_threat_review import run_native
from policy_ir import read, write, digest
from ranger_guard_queue import alive


def activated(row):
    return sum(row['proof']['spread_counts'])>0 and (row['name']=='rally' or sum(row['proof']['release_counts'])>0)


def main():
    rows=[]
    for stage in ('screen','local'):
        while not (STUDY/stage/'result.json').exists():
            if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('Local evaluation stopped without result')
            time.sleep(10)
        result=read(STUDY/stage/'result.json')
        if stage=='local':
            while not (STUDY/'local/comparison.json').exists():
                if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('No local verdict')
                time.sleep(10)
        names=VARIANTS[2:] if stage=='screen' else read(STUDY/'local/comparison.json')['qualified']
        for name in names:
            if any(r['name']==name and activated(r) for r in rows):continue
            source=STUDY/stage/'candidates'/name/'policy.bas'
            if not source.exists():continue
            for case in sorted(result['rows'],key=lambda r:r['seed']):
                if case['name']!=name or case['color']!=0:continue
                out=STUDY/'activation-review'/name/(stage+'-'+str(case['seed']));out.mkdir(parents=True,exist_ok=True)
                tape=STUDY/stage/'games'/name/str(case['seed'])/'replay.bin';trace=out/'decisions.jsonl'
                proof=run_native('replay-post-defense-probe',tape,trace,{'PROBE_POLICY':str(source),'PROBE_SLOTS':'0,1,2,3,4'})
                assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
                decisions=[json.loads(line) for line in trace.open() if json.loads(line).get('type') in ('decision','release')]
                releases=[r for r in decisions if r['type']=='release']
                for e in releases:
                    m=e['memory']; assert m['bestId']==m['defActive']==m['pdVisibleThreat']==m['defUntil']==0
                    assert e['tick']-m['pdLastProductive']>=m['pdQuietTicks']
                # Actual subsequent movement is recorded separately from accepted walk orders.
                follow=[]
                for e in releases:
                    later=next((r for r in decisions if r['slot']==e['slot'] and r['tick']>=e['tick']+240),None)
                    if later:follow.append({'release_tick':e['tick'],'slot':e['slot'],'later_tick':later['tick'],'later_hp':later['hp'],
                        'distance_tiles':((later['x']-e['x'])**2+(later['y']-e['y'])**2)**.5/60000,
                        'later_defense':later['memory']['defActive']})
                row={'name':name,'stage':stage,'seed':case['seed'],'source_sha256':digest(source.read_bytes()),'proof':proof,'releases':releases,'movement_after_release':follow}
                rows.append(row);print(name,case['seed'],'release',sum(proof['release_counts']),'spread',sum(proof['spread_counts']),flush=True)
                if activated(row):break
        if all(any(r['name']==n and activated(r) for r in rows) for n in names):break
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('No local verdict')
        time.sleep(10)
    names=read(STUDY/'local/comparison.json')['qualified']
    passed=all(any(r['name']==n and activated(r) for r in rows) for n in names)
    write(STUDY/'activation-proof.json',{'passed':passed,'qualified':names,'rows':rows})
    if not passed:raise RuntimeError('A qualified candidate did not exercise post-defense behavior')
    for name in names:
        source=STUDY/'local/comparison-feedback'/name
        if not (STUDY/'activation-feedback'/name).exists():
            record(source/'policy.ir.json',source/'policy.bas','Complete native source-bound replay proves role-separated rally walking and, when enabled, bounded quiet release. Every owned command/state hash matches. Movement following release is reported separately; this is mechanism evidence, not a hosted win claim.',STUDY/'activation-proof.json',STUDY/'activation-feedback'/name)

if __name__=='__main__':main()
