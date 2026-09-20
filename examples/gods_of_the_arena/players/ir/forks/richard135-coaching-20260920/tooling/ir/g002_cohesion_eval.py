import json
import subprocess
from g002_cohesion import STUDY,VARIANTS,make
from rush_defense_eval import evaluate
from ranger_guard_hosted import freeze
from policy_ir import read,write,digest,compile_policy,extract
from release_workspace import RUN
from league_threat_review import run_native
from economy_feedback import record

if __name__=='__main__':
    freeze(STUDY/'local-prospective.json',{'cases':12,'seed':813000,'variants':VARIANTS,'scope':'Deadline contingency,60total localgames: candidate12 plus two primary andtwolegacy controls. Shortened local evidence explicitly; no60percandidate/fullfieldclaim.','gate':'No opponent/color regression versus deployedG; equipment/runtime/fullreplay and all6blue complete gameparity withH. Native quiet-release proof. Exactg00240red then40blue required beforedeadlinepromotion.'})
    evaluate('local',VARIANTS,12,813000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics'];a=m['cohesion20'];b=m['deployed'];proofs=[]
    for row in r['rows']:
        if row['name']=='cohesion20' and row['color']==1:
            root=STUDY/'local/games';proofs.append(json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(root/'cohesion20'/str(row['seed'])/'replay.bin'),str(root/'pressure_parent'/str(row['seed'])/'replay.bin')],text=True)))
    blue=len(proofs)==6 and all(all(p[k] for k in ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in proofs)
    q=a['all_gear'] and a['wins']>=b['wins'] and all(a['colors'][c]>=b['colors'][c] for c in b['colors']) and all(a['opponents'][o]>=b['opponents'][o] for o in b['opponents']) and blue
    write(STUDY/'local/blue-parity.json',{'passed':blue,'rows':proofs})
    write(STUDY/'local/comparison.json',{'qualified':['cohesion20'] if q else [],'selected':'cohesion20' if q else None,'metrics':m,'scope':'Deadline12case candidate screen only, versus deployed; not full60caseconfirmation.'})
    src=STUDY/'local/candidates/cohesion20'
    p=read(src/'policy.ir.json');assert extract(compile_policy(p),p)==p
    record(src/'policy.ir.json',src/'policy.bas',f'Deadline12case local screen: {a}, deployed{b}; qualified{q}; all6bluegameplayparity{blue}. Only shortened localvalidation, actualg002untested.',STUDY/'local/comparison.json',STUDY/'local/comparison-feedback/cohesion20')
    if q:
        rows=[]
        for case in sorted(r['rows'],key=lambda r:r['seed']):
            if case['name']!='cohesion20' or case['color']!=0:continue
            out=STUDY/'activation'/str(case['seed']);out.mkdir(parents=True,exist_ok=True)
            proof=run_native('replay-post-defense-probe',STUDY/'local/games/cohesion20'/str(case['seed'])/'replay.bin',out/'decisions.jsonl',{'PROBE_POLICY':str(src/'policy.bas'),'PROBE_SLOTS':'0,1,2,3,4'})
            rows.append({'name':'cohesion20','proof':proof,'source_sha256':digest((src/'policy.bas').read_bytes())})
            if sum(proof['release_counts']) and sum(proof['spread_counts']):break
        passed=any(sum(x['proof']['release_counts']) and sum(x['proof']['spread_counts']) and x['proof']['all_actions_consumed'] and x['proof']['all_state_hashes_equal'] for x in rows)
        write(STUDY/'activation-proof.json',{'passed':passed,'rows':rows})
        if passed:
            src=STUDY/'local/comparison-feedback/cohesion20'
            record(src/'policy.ir.json',src/'policy.bas','Source-matched complete native replay proves actual release/spread execution; deadline fullg002comparison remains required.',STUDY/'activation-proof.json',STUDY/'activation-feedback/cohesion20')
