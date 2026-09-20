"""Fresh 40-per-color repair probes against fixed Richard/relh/rush versions.

Prepare is an inert upload and dry-run; run must be paced with the existing
league sweep. Neither operation selects league champions.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil

from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_wave import client,create
from policy_ir import bundle,compile_policy,digest,extract,read,refresh_grounding,write
from release_workspace import RUN
from rush_hosted import upload
from rush_sentries import STUDY as DEPLOYED
from rush_unblock import STUDY
LOCAL=STUDY/'local-safe'
from win_hosted import live


def controls():
    return [DEPLOYED/'league-sweep/head-to-head'/key for key in
            ('rival_bdc35084','rival_833f94fd')] + [
            DEPLOYED/'hosted/long_three/matchups'/key for key in ('red_kite','khors')]


def prepare(name):
    live()
    local=read(LOCAL/'comparison.json')
    if name not in local['qualified']:
        raise ValueError('Repair needs fresh local qualification against actual deployed parent')
    feedback=LOCAL/'replay-feedback'/name
    if not feedback.exists():
        parent=LOCAL/'deployed-comparison-feedback'/name
        intent=LOCAL/'intent-feedback'/name
        if not intent.exists():
            prior=read(parent/'policy.ir.json');ir=deepcopy(prior)
            ir['goal']['G_defense']['preference']=(
                'Respond together to a visible concentrated rush near friendly structures. '
                'Separate hero rally destinations by class. Keep the configured three sentries '
                'through repeated attacks while other heroes restore wave pressure. '
                +('During active defense, nearby defenders must intercept visible god attackers or enemies within6tiles '
                  'of the god; distant offensive heroes keep their mission.' if name=='fused_core' else
                  'Retain the deployed enemy targeting and defensive commitment rules.'))
            ir['belief']['claims']['B_release_rejected']={
                'claim':'Quiet-time releases and broad all-team core recalls regressed the local '
                        'screen and were not retained in this candidate. The candidate keeps '
                        'the deployed sentry memory. Rally separation is implemented; its hosted '
                        'effect and the scoped core response still require validation.',
                'status':'supported','evidence':[{'artifact':str(STUDY/'screen-refine/result.json'),
                    'sha256':digest((STUDY/'screen-refine/result.json').read_bytes())}]}
            ir['update'].update(revision=prior['update']['revision']+1,parent=digest(prior),
                                change='Reflect rejected release hypotheses back into semantic goals; executable unchanged')
            refresh_grounding(ir);source=(parent/'policy.bas').read_text()
            if compile_policy(ir)!=source or extract(source,ir)!=ir:raise ValueError('Semantic feedback changed behavior')
            bundle(ir,intent)
        record(intent/'policy.ir.json',intent/'policy.bas',
               'Repair selected for hosted comparison after local checks against the actual '
               'deployed sentry. '+str(local['metrics'][name])+'. Replay diagnosis: shared '
               'rally stalls occur in losses and wins; bounded duty and narrow emergencies '
               'remain hypotheses. No claim yet of beating Richard69 or relh133.',
               STUDY/'diagnosis.json',feedback)
    root,v=upload(name,STUDY,'aaron-gota-ir-unblock',
                  'Replay-guided defense release, rally separation and scoped core response; exact IR defines tested combination',
                  feedback_override=feedback,candidate_override=LOCAL/'candidates'/name)
    paths=[]
    for prior in controls():
        old=read(prior/'plan.json');key=old['rival_key']
        p={k:old[k] for k in ('target','game_version','game_source','config','rival','rival_version','rival_key','episodes_per_color','interpretation')}
        p.update(policy_version=v['id'],policy_label=f'{v["name"]}:v{v["version"]}',
                 design='Fresh40seeded games/color, five copies of repair versus five copies of exact rival. '
                        'Compare completed same-source deployed-sentry80games. Seeds need not be matched. '
                        'No interim tuning; all320games and fullreplay/VM/item checks before final verdict.',
                 control_result=str(prior/'result.json'),
                 control_result_sha256=digest((prior/'result.json').read_bytes()))
        path=root/'matchups'/key;path.mkdir(parents=True,exist_ok=True)
        if (path/'plan.json').exists() and read(path/'plan.json')!=p:raise ValueError('Frozen repair plan changed')
        write(path/'plan.json',p)
        for color in ('red','blue'):
            out=path/key/color;out.mkdir(parents=True,exist_ok=True)
            slots=list(range(5)) if color=='red' else list(range(5,10))
            roster=[v['id'] if s in slots else p['rival_version'] for s in range(10)]
            arm=p|{'color':color,'own_slots':slots,'roster':roster}
            if (out/'plan.json').exists() and read(out/'plan.json')!=arm:raise ValueError('Frozen arm changed')
            write(out/'plan.json',arm)
            binary=RUN/'r5/fast/audit-hosted';cal=RUN/'r5/fast/audit-calibration/proof.json'
            proof=read(cal)
            if digest(binary.read_bytes())!=proof['optimized_binary_sha256'] or not all(r['all_audit_fields_identical'] for r in proof['rows']):
                raise ValueError('Auditor calibration changed')
            if not (out/'audit').exists():shutil.copy2(binary,out/'audit')
            write(out/'audit-build.json',{'binary_sha256':digest(binary.read_bytes()),'calibration':str(cal),'calibration_sha256':digest(cal.read_bytes())})
            body={'idempotency_key':'gota-unblock-'+digest(p)[:20]+'-'+color,
                  'target':p['target'],'game_config_overrides':p['config'],'num_episodes':40,
                  'roster':[{'slot':s,'player':{'policy_ref':ref}} for s,ref in enumerate(roster)],
                  'notes':p['design']+' Rival '+p['rival']+'; own '+color+'.'}
            with client() as c:create(c,body,out/'batch',dry_run=True)
        paths.append(str(path))
    decision={'paths':paths,'games':320,'rule':{
        'richard_and_relh_red_minimum_wins':30,'richard_and_relh_blue_minimum_wins':38,
        'khors_minimum_per_color':38,'redkite_minimum_total':70,'redkite_minimum_per_color':32,
        'all_gear_and_replays':True},
        'interpretation':'Targeted fixed-copy comparison with completed same-release baseline; '
                         'repeated command trajectories limit statistical independence. '
                         'This alone does not establish mixed-team improvement.'}
    if (root/'repair-plan.json').exists() and read(root/'repair-plan.json')!=decision:raise ValueError('Study changed')
    write(root/'repair-plan.json',decision)
    return root


def run(name):
    root=prepare(name);plan=read(root/'repair-plan.json')
    rivals={}
    for path in map(Path,plan['paths']):
        if not (path/'result.json').exists():run_prepared(path)
        inventory(path)
        rivals.update(read(path/'result.json')['rivals'])
    checks={}
    for key in ('rival_bdc35084','rival_833f94fd'):
        checks[key+'_red']=rivals[key]['colors']['red']['win']>=30
        checks[key+'_blue']=rivals[key]['colors']['blue']['win']>=38
    checks['khors']=all(v['win']>=38 for v in rivals['khors']['colors'].values())
    checks['redkite']=rivals['red_kite']['wins']>=70 and all(v['win']>=32 for v in rivals['red_kite']['colors'].values())
    checks['gear']=all(r['gear_heroes']==5 for v in rivals.values() for r in v['rows'])
    result={'games':sum(r['games'] for r in rivals.values()),'wins':sum(r['wins'] for r in rivals.values()),
            'rivals':rivals,'checks':checks,'passed':all(checks.values()),'scope':plan['interpretation']}
    write(root/'result.json',result)
    if not (root/'feedback').exists():
        parent=LOCAL/'replay-feedback'/name
        record(parent/'policy.ir.json',parent/'policy.bas',
               f'Complete320game repair comparison: {result["wins"]} wins. Checks {checks}. '
               +plan['interpretation'],root/'result.json',root/'feedback')
    print('Repair hosted verdict:',{k:v for k,v in result.items() if k!='rivals'},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('name');p.add_argument('--prepare-only',action='store_true')
    a=p.parse_args();(prepare if a.prepare_only else run)(a.name)
