"""Required preservation of previously winning blue matchups before promotion."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from relh154_research import STUDY,RUN
import middle_rush_parallel_checks as hosted
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze

ROOT=STUDY/'guards'
PREVIOUS=RUN/'coached-lanes/r5-jordan254/warning-followup'


def main():
    confirm=read(STUDY/'confirmation/result.json');assert confirm['passed']
    name=confirm['name'];ROOT.mkdir(exist_ok=True)
    refs={}
    for k in ('g002','black16','macro4'):
        plan=read(PREVIOUS/'guards/batches'/k/'candidate/blue/plan.json')
        control=read(PREVIOUS/'guards/result.json')['arms'][k+'/candidate/blue']
        refs[k]={'label':plan['rival'],'id':plan['rival_version'],'control_wins':control['wins'],'evidence':str(PREVIOUS/'guards/result.json')}
    p=read(PREVIOUS/'batches/jordan254/warning100/blue/plan.json')
    refs['jordan254']={'label':p['rival'],'id':p['rival_version'],'control_wins':40,'evidence':str(PREVIOUS/'hosted-result.json')}
    freeze(ROOT/'prospective.json',{'candidate':name,'refs':refs,'episodes_per_arm':40,'source_sha256':digest((STUDY/'local/candidates'/name/'policy.bas').read_bytes()),
        'gate':'EachchangedBLUE matchup>=prior40/40. REDunchanged source and6fullgameparities, freshrelh40red40blue. Exactuserrequestedpreservation beforepromotion; no broadfield or10playerclaim. Historicalcontrols reused/differentseeds; no independenttrialstatistic.',
        'authorization':'User previously requested promotion if better after checking g002,blackkite,macromackie,relh and Jordan. Exact relh improvement completed first.'})
    hosted.ROOT=ROOT/'batches';hosted.ROOT.mkdir(exist_ok=True)
    hosted.DESIGN='Preservation required before promoting relh154 repair.40BLUE perexactrival; RED executable unchanged. Allfullaudits; match prior40/40 each; historicalcontrols reused.'
    v=read(STUDY/'hosted'/name/'uploaded-version.json');hosted.VERSIONS[name]={'id':v['id'],'name':v['name']+':v'+str(v['version'])}
    arms=[hosted.prepare(k,t['label'],name,'blue',t['id'])[0] for k,t in refs.items()]
    results={}
    with ThreadPoolExecutor(4) as pool:
        for future in as_completed([pool.submit(hosted.run_arm,p) for p in arms]):
            k,r=future.result();results[k]=r;write(ROOT/'progress.json',{'arms':results})
    checks={k:results[k+'/'+name+'/blue']['wins']>=t['control_wins'] for k,t in refs.items()}
    write(ROOT/'result.json',{'passed':all(checks.values()),'checks':checks,'arms':results,'promotion_performed':False})
    print('GUARDS',checks,{k:v['wins'] for k,v in results.items()},flush=True)

if __name__=='__main__':main()
