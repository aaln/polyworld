"""Save measured semantic feedback without changing evaluated executable bytes."""
from copy import deepcopy
from pathlib import Path
import pprint
import shutil
from fresh_hit import ROOT, STUDY, INITIAL, NAMES, read, write, digest
from study import bundle, compile_policy, extract, refresh_grounding, CAMPAIGN, CLEAN
from games.gods_of_the_arena.instruments.richard_transition import contracts_v3

DEST=ROOT/'examples/gods_of_the_arena/players/ir/forks/richard135-transition-20260920'
OLD=ROOT/'examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920'
VARIANTS=[(INITIAL,n) for n in ('transition','transition_armor')]+[
    (INITIAL/'cadence',n) for n in ('transition_cadence','transition_armor_cadence')]+[
    (STUDY,n) for n in NAMES[1:]]


def evidence(path):
    return {'artifact':str(path),'sha256':digest(path.read_bytes())}


def local_stats(study,name):
    v=read(study/'local-results.json');assert v['complete']
    rows=[r for r in v['rows'] if r['candidate']==name]
    assert len(rows)==12 and all(r['valid'] and r['gear_heroes']==5 for r in rows)
    return {'games':12,'wins':sum(r['win'] for r in rows),'deaths':sum(r['deaths'] for r in rows),
        'max_instructions':max(r['max_instructions'] for r in rows),'evidence':evidence(study/'local-results.json')}


def cell(folder):
    v=read(folder/'arm-result.json');correlation=read(folder/'trajectory-correlation.json')
    assert v['games']==len(v['rows'])==40 and v['all_full_audits_passed'] and v['structured_ten_vm_exits']
    return {k:v[k] for k in ('games','wins','losses','draws')}|{
        'deaths':sum(r['subject_deaths'] for r in v['rows']),
        'request':read(folder/'batch/created.json')['id'],
        'distinct_complete_command_streams':correlation['distinct_complete_all10_command_streams'],
        'evidence':evidence(folder/'arm-result.json'),'correlation_evidence':evidence(folder/'trajectory-correlation.json')}


def save_pair(original,source,dest,claims,refs,change):
    p=deepcopy(original)
    # Retain historical evidence, explicitly bind it to its parent rather than
    # letting prior source-specific successes or timers describe this source.
    for name,v in p['belief']['claims'].items():
        v['claim']='Inherited evidence/hypothesis from the parent IR; not validation of this saved source. '+v['claim']
    p['belief']['claims'].update(claims)
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),change=change,
        evidence=p['update']['evidence']+refs,needs_review=['competitive_transfer_to_other_opponents'])
    if 'CoachedTransition' in claims:
        params=p['skill']['observe']['parameters']
        p['situation']['notes']=(
            'Published Gods of the Arena 2026.9.16.5, immutable clean release f2ab9598. '
            'Session 2026-09-20t19-10-35-082z64deb6 analyzes exact formation4800_budget '
            'on red versus Richard v135. New red controller starts at tick4800; '
            'blue execution retains critical60. Public observations only; no opponent '
            'identity or hidden enemy positions. Readiness requires four healthy '
            'nearby allies, but a visible threatening Ranger overrides readiness '
            'for shared focus. Hostile heroes/creeps within36tiles define perimeter '
            'pressure; only a complete <=128object scan can establish observed '
            'clearance. Truncated scans remain unknown. Alarm renews on two visible '
            'heroes within28tiles, an observed nearby structure attacker, or new '
            'core HP loss. Old damage alone does not renew it. Memory lasts '
            f"{params['home_commit_ticks']}ticks and releases after {params['clear_ticks']}"
            'ticks of observed clearance. Crossbow scout needs240ticks without a '
            'visible enemy hero, no home pressure and >=60%HP; it leads the group '
            'toward center by a bounded offset. These thresholds are authored '
            'interpretations. Skills and captured operator semantics define exact '
            'target selection, recovery, equipment and navigation. Validation '
            'separates scenario fidelity from competitive performance.')
    refresh_grounding(p)
    assert compile_policy(p).encode()==source
    assert extract(source.decode(),p)==p
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True);bundle(p,dest)
        (dest/'policy.py').write_text('"""Primary semantic IR with measured session feedback."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    else:assert read(dest/'policy.ir.json')==p,'Refusing to rewrite saved evaluated IR'
    assert (dest/'policy.bas').read_bytes()==source
    return p


def main():
    completed=read(STUDY/'hosted-result.json');assert completed['complete'] and completed['games']==240
    promotion=read(INITIAL/'promotion-check/result.json')
    assert promotion['complete'] and promotion['games']==160
    plan=read(STUDY/'hosted-plan.json');arms={a['key']:Path(a['directory']) for a in plan['arms']}
    capture=read(INITIAL/'captured-inputs.json')
    for rel,info in capture['files'].items():
        for root in (Path(capture['session']),INITIAL/'session-inputs'):
            assert digest((root/rel).read_bytes())==info['sha256'],str(root/rel)
    refs=[evidence(INITIAL/f) for f in ('captured-inputs.json','session-binding.json','diagnosis.json','ranger-cadence-evidence.json')]
    baseline={c:cell(arms['coached_baseline/'+c]) for c in ('red','blue')}
    results=[]
    for study,name in VARIANTS:
        candidate=study/'candidates'/name;original=read(candidate/'policy.ir.json');source=(candidate/'policy.bas').read_bytes()
        local=local_stats(study,name);control=local_stats(study,'coached_baseline')
        hosted={c:cell(arms[name+'/'+c]) for c in ('red','blue')} if study==STUDY else None
        passed=bool(hosted and min(v['wins'] for v in hosted.values())>=30 and
            sum(v['wins'] for v in hosted.values())>=sum(v['wins'] for v in baseline.values())+8)
        scoped=refs+[evidence(study/'vm-proof.json'),local['evidence']]
        if hosted:scoped += [v['evidence'] for v in hosted.values()]
        if (study/'focus-proof.json').exists():scoped.append(evidence(study/'focus-proof.json'))
        if (study/'boundary-proof.json').exists():scoped.append(evidence(study/'boundary-proof.json'))
        outcome=f"Local {local['wins']}/12 wins and {local['deaths']} deaths versus baseline {control['wins']}/12 wins and {control['deaths']} deaths. "
        if hosted:
            outcome+=f"Exact Richard135: red {hosted['red']['wins']}/40, blue {hosted['blue']['wins']}/40. "
            outcome+='Both-color target gate '+('passed.' if passed else 'failed.')+' All80 full replay and all-ten-VM audits passed. '
        else:outcome+='No candidate hosted games requested. '+read(study/'hosted-disposition.json')['reason']+' '
        outcome+='No field or leaderboard superiority is established; repeated trajectories are correlated.'
        fidelity='Scenario tests validate the recorded controller conditions with scripted command acceptance, not combat success. '
        if study==INITIAL/'cadence':fidelity+='Later boundary tests exposed stale hit memory at cold focus entry; this intermediate version is superseded. '
        if study==STUDY:fidelity+='Fresh-hit boundary tests verify cold entry and decision gaps cannot trigger recovery from historical hits. '
        claims={
            'CoachedTransition':{'claim':'Hypothesis: the complete transition/scout/shared-focus/equipment bundle clears the both-color Richard135 gate. '+outcome,
                'status':('supported' if passed else 'contradicted') if hosted else 'requires_review','evidence':scoped},
            'CoachedMechanismFidelity':{'claim':fidelity,'status':'supported','evidence':scoped},
            'HomePressurePersistence':{'claim':'Current red observer uses360tick finite alarm memory and72tick observed-clear release. Incomplete visibility does not prove no enemies; old core damage alone does not renew defense.',
                'status':'supported','evidence':[evidence(study/'vm-proof.json')]},
            'CoachingRuntimeMargin':{'claim':f"All12local games for this source were valid; max {local['max_instructions']} instructions below the hard20000 limit. "+('All80hosted games passed all-ten-VM validation. ' if hosted else 'No hosted runtime claim. ')+ 'This is measured coverage, not a worst-case bound.',
                'status':'supported','evidence':scoped}}
        if hosted:
            claims['RichardBlueComponent']={'claim':f"This exact source won {hosted['blue']['wins']}/40 on blue against Richard135 in this study. This is a color-specific result, not proof of red strength.",'status':'supported','evidence':[hosted['blue']['evidence']]}
        conditional_pass=bool(promotion['selection']['name']==name and promotion['user_conditional_promotion_gate_passed'])
        if promotion['selection']['name']==name:
            promotion_ref=evidence(INITIAL/'promotion-check/result.json')
            claims['UserConditionalPromotion']={'claim':'Hypothesis: this unchanged source qualifies for the user-authorized promotion if it beats current Alex and Jordan, accepting unresolved Richard performance. Complete160game Alex/Jordan check '+('passed' if conditional_pass else 'failed')+' the separately frozen >=30/40-per-color-per-opponent gate. This does not change the original Richard criterion or establish broad league superiority.',
                'status':'supported' if conditional_pass else 'contradicted','evidence':[promotion_ref]}
            scoped.append(promotion_ref)
        updated=save_pair(original,source,DEST/'evaluated'/name,claims,scoped,{
            'origin':'Measured second coaching session feedback; exact tested BASIC unchanged',
            'session':capture['session'],'target_gate_passed':passed,'league_promoted':False})
        row={'name':name,'pair':str(DEST/'evaluated'/name),'source_sha256':digest(source),'tested_ir_sha256':digest(original),
            'evaluated_ir_sha256':digest(updated),'local':local,'local_control':control,'Richard':hosted,
            'Richard_both_color_gate_passed':passed,'field_qualified':False,
            'user_conditional_promotion_gate_passed':conditional_pass,'compile_extract_exact_parity':True}
        if (candidate/'uploaded-version.json').exists():row['uploaded_version']=read(candidate/'uploaded-version.json')
        write(DEST/'evaluated'/name/'validation.json',row);results.append(row)
        print('SAVED',name,passed,flush=True)
    candidate=STUDY/'candidates/coached_baseline';baseline_refs=refs+[v['evidence'] for v in baseline.values()]
    save_pair(read(candidate/'policy.ir.json'),(candidate/'policy.bas').read_bytes(),DEST/'coached-baseline',{
        'CurrentComparison':{'claim':f"Exact coached baseline fresh Richard135 results: red{baseline['red']['wins']}/40, blue{baseline['blue']['wins']}/40. This is the source in the user episode, not the currently selected league source.",'status':'supported','evidence':baseline_refs}},baseline_refs,
        {'origin':'Contemporaneous baseline feedback','session':capture['session']})
    qualified=[r['name'] for r in results if r['Richard_both_color_gate_passed']]
    summary={'complete':True,'session':capture['session'],'captured_input_files':len(capture['files']),
        'hosted_games':400,'Richard_hosted_games':240,'Alex_Jordan_hosted_games':160,
        'unique_requests':len({v['request'] for v in baseline.values()}|{v['request'] for r in results if r['Richard'] for v in r['Richard'].values()})+4,
        'local_games':108,'invalid_hosted_games':0,'baseline':baseline,'candidates':results,
        'Richard_qualified':qualified,'conditional_promotion':promotion,'league_changed':False,'existing_league_pair':str(OLD/'retained-baseline'),
        'retained_blue_component':str(OLD/'validated-blue-component'),
        'retention':('Selected unchanged source meets the user-authorized Alex/Jordan promotion gate; deployment receipt is recorded separately. ' if promotion['user_conditional_promotion_gate_passed'] else 'The Alex/Jordan condition failed; keep the current league baseline. ')+ 'Preserve the previously validated blue component, every evaluated IR/BASIC pair and failure.',
        'limits':'Adaptive discovery; generated hosted seeds differ and repeated command trajectories correlate. Local wins are not Richard proxies. Mechanism fidelity and reduced deaths do not establish better fort win rates.'}
    write(DEST/'results.json',summary);write(INITIAL/'results.json',summary)
    write(DEST/'session-references.json',{'session':capture['session'],'episode':read(INITIAL/'session-binding.json'),
        'evidence':refs,'study':str(INITIAL),'preservation_verified':True})
    write(DEST/'additional-validation.json',{'mechanisms':evidence(STUDY/'preservation-proof.json'),
        'local_mechanism_reconstruction':evidence(STUDY/'mechanism-local/comparison.json'),
        'progression_comparison':evidence(INITIAL/'progression-comparison.json'),
        'all_local_results':evidence(INITIAL/'all-local-summary.json'),
        'coaching_mapping':evidence(INITIAL/'semantic-coaching-map.json'),
        'conditional_promotion':evidence(INITIAL/'promotion-check/result.json')})
    shutil.copytree(INITIAL/'session-inputs',DEST/'session-inputs',dirs_exist_ok=True)
    shutil.copy2(INITIAL/'captured-inputs.json',DEST/'captured-inputs.json')
    shutil.copy2(INITIAL/'semantic-coaching-map.json',DEST/'semantic-coaching-map.json')
    shutil.copytree(OLD/'tooling',DEST/'tooling',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    # hero_binding resolves its pinned hero schema two parents above tooling/ir.
    # Include that engine input so the captured compiler works outside the repo.
    shutil.copy2(CLEAN/'examples/gods_of_the_arena/content.nim',DEST/'content.nim')
    tool_dest=DEST/'tooling/games/gods_of_the_arena/instruments/richard_transition';tool_dest.mkdir(parents=True,exist_ok=True)
    for name in ('contracts.py','contracts_v2.py','contracts_v3.py'):shutil.copy2(Path(__file__).parent/name,tool_dest/name)
    reproduce=(OLD/'reproduce.py').read_text().replace('richard_coaching import contracts_v7','richard_transition import contracts_v3')
    reproduce=reproduce.replace("HERE/'retained-baseline',HERE/'validated-blue-component'","HERE/'coached-baseline'")
    (DEST/'reproduce.py').write_text(reproduce)
    tool_files=[p for p in sorted((DEST/'tooling').rglob('*')) if p.is_file() and '__pycache__' not in str(p)]+[DEST/'content.nim']
    write(DEST/'tooling-manifest.json',{'files':{str(p.relative_to(DEST)):digest(p.read_bytes()) for p in tool_files}})
    print('COMPLETE',DEST,flush=True)


if __name__=='__main__':main()
