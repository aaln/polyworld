"""Prove source-bound caster activation from actual complete game tapes."""
import json
import time
from anchored_support import STUDY, VARIANTS
from economy_feedback import record
from league_threat_review import run_native
from policy_ir import read, write, digest
from ranger_guard_queue import alive


if __name__=='__main__':
    rows=[]
    for stage in ('screen','local'):
        while not (STUDY/stage/'result.json').exists():
            if not alive(read(STUDY/'local-process.json')['pid']): raise RuntimeError('No completed local evidence')
            time.sleep(10)
        result=read(STUDY/stage/'result.json')
        for name in VARIANTS[2:]:
            if any(r['name']==name and sum(r['proof']['expanded_assist_decisions']) for r in rows): continue
            source=STUDY/stage/'candidates'/name/'policy.bas'
            if not source.exists(): continue
            parameters=read(source.with_name('policy.ir.json'))['skill']['observe']['parameters']
            for case in result['rows']:
                if case['name']!=name or case['color']!=0: continue
                seed=case['seed']; out=STUDY/'activation-review'/name/(stage+'-'+str(seed)); out.mkdir(parents=True,exist_ok=True)
                tape=STUDY/stage/'games'/name/str(seed)/'replay.bin'
                trace=out/'context.jsonl'
                proof=run_native('replay-assist-context-probe',tape,trace,{'PROBE_POLICY':str(source),'PROBE_SLOTS':'0,1,2,3,4'})
                events=[json.loads(line) for line in trace.read_text().splitlines() if json.loads(line).get('type')=='expanded_assist_start']
                assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
                for e in events:
                    assert e['class_id'] in (7,8) and e['slot'] in (2,3)
                    if parameters['redbranch_anchor_required']: assert e['anchor']!=0
                    if parameters['redbranch_frontline_only']:
                        assert any(a['class_id']==5 and a['targets_front'] and a['hp']>=120 and
                            (a['x']-e['x'])**2+(a['y']-e['y'])**2<=144 for a in e['allies'])
                rows.append({'name':name,'stage':stage,'seed':seed,'source_sha256':digest(source.read_bytes()),'proof':proof,'events':events})
                print(name,seed,proof['expanded_assist_decisions'],flush=True)
                if sum(proof['expanded_assist_decisions']): break
        if all(any(r['name']==n and sum(r['proof']['expanded_assist_decisions']) for r in rows) for n in VARIANTS[2:]): break
    passed=all(any(r['name']==n and sum(r['proof']['expanded_assist_decisions']) for r in rows) for n in VARIANTS[2:])
    write(STUDY/'activation-proof.json',{'passed':passed,'rows':rows})
    if not passed: raise RuntimeError('Candidate not exercised; preserve evidence and do not upload')
    for name in VARIANTS[2:]:
        row=next(r for r in rows if r['name']==name and sum(r['proof']['expanded_assist_decisions']))
        source=STUDY/row['stage']/'candidates'/name
        record(source/'policy.ir.json',source/'policy.bas',
            'Full source-matched native reconstruction proves expanded caster assistance on actual Lich7/Warlock8. '
            'At every recorded expansion start, the enabled current-friendly-anchor and/or healthy-nearby-DK-commitment '
            'requirements hold. All owned commands and world hashes exact. This proves execution, not competitive improvement.',
            STUDY/'activation-proof.json',STUDY/'activation-feedback'/name)
