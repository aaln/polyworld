"""Fresh exact-Jordan team probes on the live guard release, including control."""
import shutil
from coached_guards import STUDY
from command_diversity import inventory
from direct_matchup import run_prepared
from hosted_wave import client,create
from policy_ir import read,write,digest
from release_workspace import RUN,VERSION
from rush_hosted import upload
from win_hosted import live


def prepare(name,study=STUDY,prefix='aaron-gota-ir-guards',change='shared lane then fort'):
    game=live()
    if name=='current':
        folder=study/'hosted/current';folder.mkdir(parents=True,exist_ok=True)
        v=read(RUN/'win-first-study/hosted-discovery/bounded/uploaded-version.json')
    else:
        folder,v=upload(name,study,prefix,change)
    old=read(RUN/'jordan-v148-probe/plan.json')
    if (study/'rival.json').exists():
        rival=read(study/'rival.json');old.update(rival=rival['label'],rival_version=rival['id'])
    config=next(v['game_config'] for v in game['manifest']['variants'] if v['id']=='competition')
    config={k:v for k,v in config.items() if k not in {'seed','players','tokens'}}
    plan={k:old[k] for k in ['target','rival','rival_version','episodes_per_color','interpretation']}
    plan.update(target={'coworld_id':game['id'],'variant_id':'competition'},game_version=VERSION,game_source=game['manifest']['game']['runnable']['source_url'],config=config,
        policy_version=v['id'],policy_label=f'{v["name"]}:v{v["version"]}',
        design='Fresh40episodes/color on live guard release. Five identical copies versus the frozen Jordan champion. Current deployed bounded control retested on same release. Full80beforeinterpretation; no interim tuning. Fixedlineups are not independent strategy samples.')
    if (folder/'plan.json').exists() and read(folder/'plan.json')!=plan:raise ValueError('Frozen probe changed')
    write(folder/'plan.json',plan)
    for color in ['red','blue']:
        out=folder/'jordan'/color;out.mkdir(parents=True,exist_ok=True)
        slots=list(range(5)) if color=='red' else list(range(5,10))
        roster=[v['id'] if s in slots else plan['rival_version'] for s in range(10)]
        arm=plan|{'own_slots':slots,'roster':roster,'color':color}
        if (out/'plan.json').exists() and read(out/'plan.json')!=arm:raise ValueError('Frozen arm changed')
        write(out/'plan.json',arm);shutil.copy2(RUN/'r5/audit',out/'audit')
        body={'idempotency_key':f'gota-coached-r5-{digest(plan)[:18]}-{color}',
              'target':plan['target'],'game_config_overrides':config,'num_episodes':40,
              'roster':[{'slot':s,'player':{'policy_ref':p}} for s,p in enumerate(roster)],
              'notes':f'Coached lane/guard chain, {name} on{color}, the frozen Jordan champion.40fixedlineup repeats; finish80bothcolors. Local gate passed for candidates; no league selection.'}
        with client() as c:create(c,body,out/'batch',dry_run=True)
    return folder


def main(study=STUDY):
    r=read(study/'local/result.json');names=r['selected'][:2]
    if not names or any(r['metrics'][n]['games']!=40 for n in names):raise ValueError('Complete local qualifiers required')
    root=study/'hosted';root.mkdir(exist_ok=True)
    plan={'candidates':names,'local_sha256':digest((study/'local/result.json').read_bytes()),
        'game_version':VERSION,'rule':'Complete80perarm including freshcurrent control. Qualify >20/40wins againstJordan on bothcolors AND totalwins greater than current. Rankwins thenwinningticks. Beforepromotion: fresh100/arm mixed pinnedroster vsdeployedbaseline, no morethan5pp regression; then100randomcurrent-fieldgames>=50wins. Allgear, VM andfullreplay/source/configvalidation. Do not interpret repeatedlineups as broad significance.'}
    if (root/'plan.json').exists() and read(root/'plan.json')!=plan:raise ValueError('Study changed')
    write(root/'plan.json',plan)
    results={}
    for n in ['current',*names]:
        folder=prepare(n,study);run_prepared(folder);inventory(folder)
        results[n]=read(folder/'result.json')['rivals']['jordan']
    qualified=[n for n in names if all(c['win']>20 for c in results[n]['colors'].values()) and results[n]['wins']>results['current']['wins'] and all(r['gear_heroes']==5 for r in results[n]['rows'])]
    qualified.sort(key=lambda n:(-results[n]['wins'],sum(r['ticks'] for r in results[n]['rows'] if r['win'])/max(1,results[n]['wins'])))
    write(root/'result.json',{'arms':results,'qualified':qualified,'selected':qualified[0] if qualified else None})
    print('Qualified:',qualified,flush=True)


if __name__=='__main__':main()
