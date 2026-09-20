"""Sixty full games must match the intended parent on every action/state hash."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,subprocess
from economy_feedback import record
from policy_ir import ROOT,read,write,digest
from release_workspace import RUN,verify
from jordan_lineup import STUDY,PRIOR


def main():
    verify();old=read(PRIOR/'local/plan.json');out=STUDY/'local';out.mkdir(parents=True,exist_ok=True)
    source=STUDY/'candidate/policy.bas';binary=RUN/'r5/fast/episode';audit=RUN/'r5/fast/audit-local';compare=RUN/'r5/compare-gameplay'
    plan={'cases':old['cases'],'opponents':old['opponents'],'config':str(PRIOR/'local/config.json'),
          'source':str(source),'source_sha256':digest(source.read_bytes()),
          'reference':'Each red game must equal deployed_parent; each blue game must equal release20 on ALL actions, ALL state hashes, config/setup. VMmetric differences expected. Existing reference games are reused, not freshcontrols. This is behavior-parity validation, not evidence of incrementalwin improvement.',
          'binaries':{str(p):digest(p.read_bytes()) for p in (binary,audit,compare)}}
    if (out/'plan.json').exists() and read(out/'plan.json')!=plan:raise ValueError('Frozen plan changed')
    write(out/'plan.json',plan)
    def one(case):
        folder=out/'games'/str(case['seed']);folder.mkdir(parents=True,exist_ok=True);tape=folder/'replay.bin'
        team=case['color'];reference_name='deployed_parent' if team==0 else 'release20'
        reference=PRIOR/'local/games'/reference_name/str(case['seed'])/'replay.bin'
        if not (folder/'result.json').exists():
            cmd=[str(binary),'--config',plan['config'],'--seed',str(case['seed']),'--record',str(tape)]
            cmd+=['--bot:'+str(source if slot//5==team else plan['opponents'][case['opponent']]) for slot in range(10)]
            with (folder/'stdout.log').open('w') as stdout,(folder/'stderr.log').open('w') as stderr:subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr,check=True,timeout=900)
            write(folder/'result.json',json.loads((folder/'stdout.log').read_text().splitlines()[-1]))
        result=read(folder/'result.json')
        if not (folder/'audit.json').exists():write(folder/'audit.json',json.loads(subprocess.check_output([str(audit),'--replay',str(tape)],cwd=ROOT,text=True).splitlines()[-1]))
        proof=read(folder/'audit.json')
        if proof['hash_mismatches'] or proof['state_hash']!=result['state_hash'] or proof['ticks']!=result['ticks'] or proof['actions_consumed']!=result['actions']:raise ValueError('Fullreplay mismatch')
        if any(h['max_work']>50000 or h['max_instructions']>20000 for h in result['heroes']):raise ValueError('VM budget')
        parity=json.loads(subprocess.check_output([str(compare),str(reference),str(tape)],text=True))
        write(folder/'parity.json',parity)
        if not all(parity[k] for k in ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')):raise ValueError('Unexpected gameplay divergence')
        heroes=result['heroes'][team*5:team*5+5]
        if any(h['equipment_count']==0 for h in heroes):raise ValueError('Missing equipment')
        return case|{'win':heroes[0]['score'],'reference':reference_name,'full_gameplay_equal':True,
                     'max_instructions':max(h['max_instructions'] for h in heroes),'max_work':max(h['max_work'] for h in heroes),
                     'replay_sha256':digest(tape.read_bytes()),'reference_sha256':digest(reference.read_bytes())}
    rows=[]
    with ThreadPoolExecutor(4) as pool:
        for job in as_completed([pool.submit(one,c) for c in plan['cases']]):rows.append(job.result());print('Lineup parity',len(rows),'/60',flush=True)
    result={'games':60,'wins':sum(r['win'] for r in rows),'all_gameplay_equal':True,'all_full_audits_passed':True,
            'colors':{str(c):sum(r['win'] for r in rows if r['color']==c) for c in (0,1)},'rows':rows,'scope':plan['reference']}
    write(out/'result.json',result)
    dest=out/'comparison-feedback/blue_repair'
    if not dest.exists():record(STUDY/'candidate/policy.ir.json',source,f'All60fullgames match the corresponding parent in every action and statehash. Wins{result["wins"]}; colors{result["colors"]}. '+plan['reference'],out/'result.json',dest)
    # Ready marker only after immutable feedback bundle is complete.
    write(out/'comparison.json',{'selected':'blue_repair','qualified':['blue_repair'],'games':60,'all_gameplay_equal':True,'scope':plan['reference']})
    print('Lineup60 fullgame parity passed',flush=True)

if __name__=='__main__':main()
