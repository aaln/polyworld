"""Both halves must execute on their real hero classes before hosted testing."""
import json
import time
from coordinated_readiness import STUDY
from economy_feedback import record
from league_threat_review import run_native
from policy_ir import read,write,digest
from ranger_guard_queue import alive


if __name__=='__main__':
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('Local study ended without verdict')
        time.sleep(10)
    candidates=read(STUDY/'local/comparison.json')['qualified']
    rows=[]
    for name in candidates:
        source=STUDY/'local/candidates'/name/'policy.bas'
        params=read(source.with_name('policy.ir.json'))['skill']['observe']['parameters']
        assisted=held=False
        for stage in ('screen','local'):
            for case in read(STUDY/stage/'result.json')['rows']:
                if case['name']!=name or case['color']!=0:continue
                seed=case['seed'];out=STUDY/'activation-review'/name/(stage+'-'+str(seed));out.mkdir(parents=True,exist_ok=True)
                trace=out/'context.jsonl';tape=STUDY/stage/'games'/name/str(seed)/'replay.bin'
                proof=run_native('replay-coordinated-probe',tape,trace,{'PROBE_POLICY':str(source),'PROBE_SLOTS':'0,1,2,3,4'})
                events=[json.loads(x) for x in trace.read_text().splitlines() if json.loads(x).get('type') in ('expanded_assist_start','supported_hold_start')]
                assert proof['all_state_hashes_equal'] and proof['all_actions_consumed']
                assert not any(proof['unsupported_hold_decisions'][1:])
                for e in events:
                    if e['type']=='supported_hold_start':
                        assert e['slot']==0 and e['class_id']==5;continue
                    assert e['slot'] in (2,3) and e['class_id'] in (7,8)
                    if params['redbranch_anchor_required']:assert e['anchor']!=0
                    if params['redbranch_frontline_only']:
                        assert any(a['class_id']==5 and a['targets_front'] and a['hp']>=120 and
                            (a['x']-e['x'])**2+(a['y']-e['y'])**2<=144 for a in e['allies'])
                rows.append({'name':name,'stage':stage,'seed':seed,'source_sha256':digest(source.read_bytes()),'proof':proof,'events':events})
                assisted=assisted or bool(sum(proof['expanded_assist_decisions']))
                held=held or bool(proof['unsupported_hold_decisions'][0])
                print(name,seed,'assist',sum(proof['expanded_assist_decisions']),'hold',proof['unsupported_hold_decisions'][0],flush=True)
                if assisted and held:break
            if assisted and held:break
        if not (assisted and held):raise RuntimeError('Both mechanisms not exercised: '+name)
    write(STUDY/'activation-proof.json',{'passed':True,'qualified':candidates,'rows':rows})
    for name in candidates:
        src=STUDY/'local/comparison-feedback'/name
        record(src/'policy.ir.json',src/'policy.bas',
            'Native complete-game reconstruction proves real DeathKnight5 waiting plus Lich7/Warlock8 expanded support on this exact source. '
            'All owned commands and hashes match. Enabled context conditions verified at expansion starts. This proves execution, not competitive improvement.',
            STUDY/'activation-proof.json',STUDY/'activation-feedback'/name)
