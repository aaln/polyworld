"""Keep the successful relh alarm while restoring unrelated middle release behavior."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import sys
from binding import CONTRACTS
import relh154_research as prior
from policy_ir import read,write,digest,refresh_grounding,bundle,compile_policy,extract
from rush_hosted import upload
from economy_feedback import record
import middle_rush_parallel_checks as hosted
OLD=prior.STUDY
STUDY=OLD/'scoped-followup'
VARIANTS=('deployed','pair150','legacy','scoped')
RECORD=Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena/experiments/2026-09-18-relh154-scoped-recall.md')


def make(name):
    if name=='deployed':return read(prior.PARENT/'policy.ir.json')
    parent=read(OLD/'final-feedback/policy.ir.json')
    if name=='pair150':return parent
    assert name in ('legacy','scoped')
    p=deepcopy(parent);p['id']='gota_relh154_'+name
    o=p['skill']['observe'];o['operator']='lineup_paired_'+name
    o['parameters']['blue_hold']=1200
    o['parameters']={k:o['parameters'].get(k,v[0]) for k,v in CONTRACTS[o['operator']].parameters.items()}
    p['goal']['G_defense']['preference']+=' Restore standard middle-alarm quiet release and1200tick carryhold. '+('The new damage alarm uses the existing release logic without additional travel protection.' if name=='legacy' else 'Only the new side-alarm deadline enables1440tick carryhold and arrival-qualified quiet release; unrelated alarms preserve baseline behavior.')
    ev=[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]
    p['belief']['claims']['B_candidate']={'status':'untested','claim':'Relh-specific scoped-recall followup; prior pair150 wonrelh120/120 butJordan35wins5draws failedpromotion. New behavior has not been competitively validated.','evidence':ev}
    p['belief']['claims']['B_relh_warning']={'status':'requires_review','claim':'The prior joint package was validated againstrelh; this narrower package must repeatrelh andrestoreJordan beforepromotion.','evidence':ev}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Scope relh side-alarm persistence: '+name)
    refresh_grounding(p);return p


def local():
    prior.STUDY=STUDY;prior.VARIANTS=VARIANTS;prior.make=make
    prior.local(819100)


def remote():
    qualification=read(STUDY/'local/qualification.json')
    names=[n for n in qualification['qualified'] if n in ('legacy','scoped')]
    hosted.ROOT=STUDY/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Scopedrelh warning followup.40BLUE exactrelh154 and40BLUE exactJordan254 perlocalqualifier. Both40/40required, allfullaudits; nointerimtuning orautopromotion.'
    targets={'relh154':{'label':prior.LABEL,'id':prior.RIVAL}}
    j=read(OLD/'guards/batches/jordan254/pair150/blue/plan.json');targets['jordan254']={'label':j['rival'],'id':j['rival_version']}
    arms=[]
    for name in names:
        src=STUDY/'local/candidates'/name;feedback=STUDY/'qualified-feedback'/name
        if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas','Native middleparity/sidealarm/IR/runtime and local12case no regression passed. Hosted pending.',STUDY/'local/qualification.json',feedback)
        semantic=STUDY/'semantic-feedback'/name
        if not semantic.exists():
            q=read(feedback/'policy.ir.json');parent=deepcopy(q)
            q['goal']['G_defense']['preference']=read(prior.PARENT/'policy.ir.json')['goal']['G_defense']['preference']+' Blue: include standing outer side towers within100tiles of home. Before3600ticks, at leasttwo living visible heroes near a standing side tower missing150HP can initiate recall. '+('Use the original1200tick carryhold and quiet-release rules for every alarm; no additional arrival protection.' if name=='legacy' else 'Keep original1200tick carryhold and quiet-release behavior for ordinary alarms. When the new side alarm fires, use1440ticks for carries and count quiet only after arriving within18tiles; sentry duration remains7200. That extra arrival protection is bounded by the remembered side-alarm deadline.')
            q['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Make scoped defensive goal explicit; remove inherited universal arrival wording. Evaluated BASIC unchanged.')
            refresh_grounding(q)
            source=(src/'policy.bas').read_text();assert compile_policy(q)==source and extract(source,q)==q
            bundle(q,semantic)
        _,v=upload(name,STUDY,'aaron-gota-ir-relh154','Preserve blue damage alarm; scope added recall persistence.',feedback_override=semantic)
        hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
        for k,t in targets.items():arms.append(hosted.prepare(k,t['label'],name,'blue',t['id'])[0])
    results={}
    with ThreadPoolExecutor(4) as pool:
        for future in as_completed([pool.submit(hosted.run_arm,p) for p in arms]):
            k,r=future.result();results[k]=r;write(STUDY/'progress.json',{'arms':results})
    qualified=[n for n in names if all(results[k+'/'+n+'/blue']['wins']==40 for k in targets)]
    qualified.sort(key=lambda n:(n!='legacy',n))
    write(STUDY/'hosted-result.json',{'qualified':qualified,'selected':qualified[0] if qualified else None,'arms':results,'promotion_performed':False})
    print('HOSTED',qualified,{k:r['wins'] for k,r in results.items()},flush=True)

if __name__=='__main__':local() if sys.argv[1]=='local' else remote()
