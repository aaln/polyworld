"""Pinned ten-player episode roster A/B,40episodes/color/arm, both owned players."""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil

from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_wave import client,create
from policy_ir import bundle,compile_policy,digest,extract,read,refresh_grounding,write
from release_deploy_pair import clone_for_aaron
from release_workspace import RUN
from rush_hosted import upload
from mixed_backdoor import STUDY
from win_hosted import live

OPT='fb8454da-1657-40fe-ad1b-bcf185d0bcaa'
AARON='3a1c17a7-6f8f-4aa0-a297-c3f2bf14b2d0'


def intent_feedback(name,study=STUDY):
    """Narrow semantic intent to the measured behavior; preserve captured inputs."""
    prior=study/'local/comparison-feedback'/name
    corrected=study/'local/corrected-comparison-feedback'/name
    if corrected.exists():prior=corrected
    out=study/'local/intent-feedback'/name
    if out.exists():return out
    parent=read(prior/'policy.ir.json');p=deepcopy(parent)
    if name.startswith('isolated_') or name=='blue_assigned':
        source=(prior/'policy.bas').read_text()
        if compile_policy(parent)!=source or extract(source,parent)!=parent:raise ValueError('IR parity changed')
        evidence=RUN/'coached-lanes/r5-mixed-backdoor/response-audit.json'
        claim=('Command-level correction to the selected replay diagnosis: Ranger issued '
               '22attack-target orders toward Jordan in the sample interval after200seconds '
               'and48after220seconds. It did not remain a sustained defender. At265and280seconds '
               'all living allies were outside28tiles of home and neither surviving owned '
               'hero ordered an interception. The failure is loss of sustained coverage and '
               'backup, not a total absence of Ranger targeting. These are post-tick samples '
               'joined to next-interval orders, not a reconstruction of historical VM beliefs. '
               'Local qualification does not establish hosted mixed-team benefit.')
        p['belief']['claims']['B_lone_base_attacker']={
            'claim':claim,'status':'supported','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
        p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                           change='Correct replay belief from actual target orders; retain exact locally tested behavior')
        refresh_grounding(p)
        if compile_policy(p)!=source or extract(source,p)!=p:raise ValueError('Replay correction changed behavior')
        bundle(p,out);write(out/'parent.ir.json',parent)
        return out
    if name!='protected_near':raise ValueError('Review semantic scope for the selected operator')
    p['goal']['G_defense']['preference']=(
        'Respond to visible concentrated rushes using the existing group commitment and '
        'three-sentry assignment. Separate hero rally destinations by class. During active '
        'defense, heroes within24tiles of home prioritize visible god attackers or enemies '
        'within6tiles of the god. Independently, heroes already within28tiles of home '
        'intercept a visible lone hero within24tiles targeting a standing own god or final '
        'guard, even beyond the ordinary local intercept radius. Keep isolated duty for '
        '20seconds after the last qualifying attack; never shorten an established group '
        'deadline. Remote heroes do not gain a new solo-threat recall in this candidate.')
    p['belief']['claims']['B_remote_recall_rejected']={
        'claim':'Broad and staggered remote solo recalls regressed local screens, including '
                'versions preserving existing group deadlines. The selected nearby-only '
                'candidate addresses a defender ignoring and abandoning a visible base '
                'attacker. It cannot protect a fully unattended base by recalling a distant '
                'hero. Hosted mixed-roster benefit is still untested; whole-team local '
                'proxy results do not establish ten-player improvement.',
        'status':'supported','evidence':[{'artifact':str(study/'screen-protected/result.json'),
          'sha256':digest((study/'screen-protected/result.json').read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Align semantic goals with qualified nearby-only scope; preserve tested executable')
    refresh_grounding(p);source=(prior/'policy.bas').read_text()
    if compile_policy(p)!=source or extract(source,p)!=p:raise ValueError('Semantic feedback changed tested behavior')
    bundle(p,out);write(out/'parent.ir.json',parent)
    return out


def prepare(study=STUDY):
    game=live();local=read(study/'local/comparison.json');name=local['selected']
    if not name:raise ValueError('No qualified mixed-backdoor candidate')
    feedback=intent_feedback(name,study)
    root,v=upload(name,study,'aaron-gota-ir-backdoor',
                  'Intercept observed base attackers under the exact IR isolation and response rules; preserve group duty, rally separation and one-pass core defense. Mixed comparison pending.',
                  feedback_override=feedback)
    metadata=read(root/'upload-request.json');source=(study/'local/candidates'/name/'policy.bas').read_bytes()
    with client() as c:
        clone=clone_for_aaron(c,root,metadata,source,'Locally confirmed combined defense; exact mixed-roster comparison pending. Inert upload.')
    ep=read(study/'episode.json')
    if ep['coworld_version']!=game['version'] or ep['policy_version_ids'][6:8]!=[AARON,OPT]:
        raise ValueError('Reported episode or source changed')
    base=ep['policy_version_ids'];config={k:v for k,v in ep['game_config'].items() if k not in ('seed','players','tokens')}
    common={'target':{'coworld_id':ep['coworld_id'],'variant_id':'competition'},
            'game_version':game['version'],'game_source':game['manifest']['game']['runnable']['source_url'],
            'config':config,'rival_key':'mixed_roster','rival':'Pinned user episode ten-player roster',
            'episodes_per_color':40,'design':'40seededgames/color/arm. Pin the same ten-player roster '
            'from reported episode, replacing only bothowned versions. Mirror entire teams for othercolor. '
            'own_slots names the scoring team; controlled_slots identifies the two owned heroes.',
            'interpretation':'Twofixed role/rostercontexts,80games/arm. Seeds are independently derived '
            'byplatform, not paired. Command diversity retained; no broadleague significance claim.'}
    paths=[]
    for arm,refs in [('control',[AARON,OPT]),('candidate',[clone['id'],v['id']])]:
        path=root/'mixed'/arm;path.mkdir(parents=True,exist_ok=True)
        plan=common|{'policy_version':refs[1],'policy_label':arm,'owned_versions':refs}
        if (path/'plan.json').exists() and read(path/'plan.json')!=plan:raise ValueError('Frozen mixed plan changed')
        write(path/'plan.json',plan)
        for color in ('red','blue'):
            out=path/'mixed_roster'/color;out.mkdir(parents=True,exist_ok=True)
            roster=base[:];roster[6:8]=refs
            if color=='red':roster=roster[5:]+roster[:5]
            slots=list(range(5)) if color=='red' else list(range(5,10))
            controlled=[1,2] if color=='red' else [6,7]
            armplan=plan|{'color':color,'own_slots':slots,'controlled_slots':controlled,'roster':roster}
            if (out/'plan.json').exists() and read(out/'plan.json')!=armplan:raise ValueError('Frozen mixed arm changed')
            write(out/'plan.json',armplan)
            binary=RUN/'r5/fast/audit-hosted';cal=RUN/'r5/fast/audit-calibration/proof.json'
            proof=read(cal)
            if digest(binary.read_bytes())!=proof['optimized_binary_sha256'] or not all(r['all_audit_fields_identical'] for r in proof['rows']):
                raise ValueError('Auditor calibration changed')
            if not (out/'audit').exists():shutil.copy2(binary,out/'audit')
            if digest((out/'audit').read_bytes())!=digest(binary.read_bytes()):raise ValueError('Pinned auditor changed')
            write(out/'audit-build.json',{'binary_sha256':digest(binary.read_bytes()),'calibration':str(cal),'calibration_sha256':digest(cal.read_bytes())})
            body={'idempotency_key':'gota-backdoor-mixed-'+digest(armplan)[:20],
                  'target':plan['target'],'game_config_overrides':config,'num_episodes':40,
                  'roster':[{'slot':s,'player':{'policy_ref':x}} for s,x in enumerate(roster)],
                  'notes':common['design']+' '+arm+' '+color+'. No league selection.'}
            with client() as c:create(c,body,out/'batch',dry_run=True)
        paths.append(str(path))
    p={'paths':paths,'games':160,'candidate':name,'versions':{'optimizer':v['id'],'aaron':clone['id']},
       'rule':read(study/'prospective-plan.json')['hosted_rule']}
    if (root/'mixed-plan.json').exists() and read(root/'mixed-plan.json')!=p:raise ValueError('Mixed study changed')
    write(root/'mixed-plan.json',p);return root


def run(study=STUDY):
    root=prepare(study);plan=read(root/'mixed-plan.json');results={};gear=True
    for path in map(Path,plan['paths']):
        if not (path/'result.json').exists():run_prepared(path)
        inventory(path);results[path.name]=read(path/'result.json')['rivals']['mixed_roster']
        for color in ('red','blue'):
            folder=path/'mixed_roster'/color;p=read(folder/'plan.json')
            for done in folder.glob('artifacts/*/.done'):
                ep=read(done.parent/'episode.json');audit=read(done.parent/'audit.json')
                owners=[r['player_id'] for r in ep['participants']]
                if len(owners)!=10 or len(set(owners))!=10:raise ValueError('Roster must have ten distinct players')
                for slot in p['controlled_slots']:
                    if ep['policy_version_ids'][slot] not in p['owned_versions']:raise ValueError('Owned slot mismatch')
                    gear=gear and audit['heroes'][slot]['first_gear_tick']>=0
    a,b=results['candidate'],results['control']
    checks={'blue_gain':a['colors']['blue']['win']>=b['colors']['blue']['win']+8,
            'total_gain':a['wins']>=b['wins']+16,'red_no_regression':a['colors']['red']['win']>=b['colors']['red']['win'],
            'both_owned_gear':gear}
    result={'games':160,'arms':results,'checks':checks,'passed':all(checks.values()),'rule':plan['rule']}
    write(root/'mixed-result.json',result)
    from review_mixed_replays import review
    review(root)
    feedback=root/'mixed-feedback';name=plan['candidate'];src=study/'local/intent-feedback'/name
    if not feedback.exists():record(src/'policy.ir.json',src/'policy.bas',
        f'Completepinnedmixed160gameA/B: candidate{a["wins"]}/80 vscontrol{b["wins"]}/80. Checks{checks}. '
        'Twofixedrolecontexts; adaptive discovery, not broadleague proof.',root/'mixed-result.json',feedback)
    print('Mixed backdoor comparison:',{k:v for k,v in result.items() if k!='arms'},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare-only',action='store_true')
    a=p.parse_args();(prepare if a.prepare_only else run)()
