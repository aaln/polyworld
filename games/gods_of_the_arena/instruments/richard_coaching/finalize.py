"""Reflect measured outcomes into IR without changing any evaluated BASIC."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import pprint
import shutil
from prepare import ROOT, CLEAN, STUDY, CAMPAIGN, CRITICAL, read, write, digest, bundle, compile_policy, extract, refresh_grounding
from games.gods_of_the_arena.instruments.richard_coaching import contracts_v7

DEST=ROOT/'examples/gods_of_the_arena/players/ir/forks/richard135-coaching-20260920'
VARIANTS=[('',n) for n in ['formation2400','formation3600','formation2400_weapon']]+[
    ('refined-breach','formation2400_breach'),('visibility-complete','formation2400_discovery'),
    ('late-cohort','formation4800_cohort'),('committed-return','formation2400_commit'),
    ('armed-cohort','formation2400_armed'),('bounded-cohort','formation4800_bounded'),
    ('bounded-combat','formation4800_budget')]


def evidence(path):
    return {'artifact':str(path),'sha256':digest(path.read_bytes())}


def local_stats(study,name):
    value=read(study/'local-results.json');assert value['complete']
    rows=[r for r in value['rows'] if r['candidate']==name]
    assert len(rows)==12 and all(r['valid'] and r['gear_heroes']==5 for r in rows)
    return {'games':12,'wins':sum(r['win'] for r in rows),'deaths':sum(r['deaths'] for r in rows),
            'all_runtime_and_replay_audits_passed':True,'evidence':evidence(study/'local-results.json')}


def cell(study,name,color):
    folder=study/'hosted'/name/color
    if (folder/'arm-invalid-result.json').exists():
        v=read(folder/'arm-invalid-result.json');assert v['complete'] and v['games']==40 and v['all_replays_reconstructed']
        return {'games':40,'wins':None,'losses':None,'draws':None,'deaths':None,
            'invalid_games':v['invalid_games'],'valid_games':v['valid_games'],
            'valid_outcomes':{k:v['valid_'+k] for k in ('wins','losses','draws')},
            'cohort_eligible':False,'request':read(folder/'batch/created.json')['id'],
            'distinct_complete_command_streams':None,'evidence':evidence(folder/'arm-invalid-result.json')}
    v=read(folder/'arm-result.json')
    assert v['games']==len(v['rows'])==40 and v['all_full_audits_passed'] and v['structured_ten_vm_exits']
    correlation=read(folder/'trajectory-correlation.json')
    return {k:v[k] for k in ('games','wins','losses','draws')}|{
        'deaths':sum(r['subject_deaths'] for r in v['rows']),
        'request':read(folder/'batch/created.json')['id'],
        'distinct_complete_command_streams':correlation['distinct_complete_all10_command_streams'],
        'evidence':evidence(folder/'arm-result.json'),
        'correlation_evidence':evidence(folder/'trajectory-correlation.json')}


def save_pair(original,source,dest,claims,refs,change):
    p=deepcopy(original)
    # The inherited Jordan evaluation used a bundle-relative reference. Resolve
    # it by its recorded hash before moving the derived pair into this archive.
    inherited=ROOT/'examples/gods_of_the_arena/players/ir/forks/jordan268/evaluation.json'
    def resolve_refs(value):
        if isinstance(value,dict):
            if value.get('artifact')=='evaluation.json':
                assert value['sha256']==digest(inherited.read_bytes())
                value['artifact']=str(inherited)
            for child in value.values():resolve_refs(child)
        elif isinstance(value,list):
            for child in value:resolve_refs(child)
    resolve_refs(p)
    if 'Richard135_critical_recall' in p['belief']['claims']:
        blue_ref=CAMPAIGN/'adaptive-opponent-20260920/critical-blue-confirmation/critical60/arm-result.json'
        claims['Richard135_critical_recall']={
            'claim':'The earlier untested critical-recall hypothesis now has '
                'role-specific evidence: the exact critical60 parent won 40/40 '
                'fresh blue games against Richard v135 with full replay and '
                'VM audits. This supports retaining that blue component. It '
                'does not establish a red counter or qualify a new combined '
                'source; source-specific outcomes are recorded separately.',
            'status':'supported','evidence':[evidence(blue_ref)]}
    if 'G_group_siege' in p['goal']:
        params=p['skill']['observe']['parameters']
        p['situation']['notes']=(
            'Pinned published Gods of the Arena 2026.9.16.5. Coaching session '
            '2026-09-20t17-21-56-307zf4f7b3 is bound to historical bound_idle red '
            'versus Richard135 blue; comparison baseline is deployed be6affd3. '
            'The coach requests late-game grouping, perimeter probing and a '
            'unified assault. Numeric thresholds are authored interpretations: '
            f"red phase starts at tick {params['phase_tick']}; readiness requires "
            f"four living allies with HP >= {params['ready_hp']} within {params['group_radius']} "
            'tiles of the controller group center; distant-ally cohort trimming '
            'is used only by the operators whose captured semantics specify it. '
            'Enemy dispersion requires at least three currently visible heroes '
            'and bounding-box diagonal >= 32 tiles; unseen enemies remain unknown. '
            f"Actor tether radius={params['tether_radius']}; probe interval is "
            f"bounded by {params['probe_ticks']} ticks. The exact operator semantics "
            'define objective exposure, perimeter entry selection, home pressure, '
            'memory expiry and observation bounds. Readiness is recomputed from '
            'current public observations. No opponent policy identity or hidden '
            'enemy state is available to the executable. Native behavior proofs '
            'and validation.json delimit measured fidelity and competitive value.')
        p['goal']['G_defense']['preference']=(
            'Before the coached red phase retain the inherited observer. During '
            'the coached phase use the selected formation observer for gathered '
            'home defense; its versioned contract defines threat evidence and '
            'memory. Blue retains the critical60 defense controller.')
        p['goal']['G_fort']['preference']=(
            'Win the fort race through the selected observer, combat, equipment '
            'and navigation operators. During the coached red phase, their '
            'shared formation state coordinates target selection and movement. '
            'Equipment follows skill/equipment exactly; all-class ordered '
            'loadout variants supersede the historical red class progression.')
        claims['CoachedExecutableState']={
            'claim': 'The coaching names are implemented inside the selected '
                'observer, rather than as separate strategy-level guards. '
                'allies_concentrated(radius, min_count=4) is gaNear >= 4, '
                'with gaNear lowered to defMates; team_assault_readiness is '
                'gaReady, recomputed each decision. enemy_spread_out(32) is '
                'gaSpread, lowered to pairedRush, and requires three visible '
                'enemy heroes. near_base_perimeter(enemy_base) compares the '
                'group center to the public enemy-core coordinate within '
                '60 tiles. GroupProbeAndCircleBase is the collective observer, '
                'formation combat and formation route combination, not an '
                'independent runtime API. Its entry choice, probe timer and '
                'breach commitment persist in the aliased backdoor globals. '
                'Each hero has its own VM; coordination comes from shared '
                'public ally observations. Numeric thresholds are authored '
                'interpretations of the coaching, not spoken measurements.',
            'status':'supported','evidence':refs}
        for rule in p['strategy']:
            if rule['skill'] in ('observe','attack','fallback','equipment') and 'G_group_siege' not in rule['for']:
                rule['for'].append('G_group_siege')
    p['belief']['claims'].update(claims)
    p['update'].update(revision=p['update']['revision']+1,parent=digest(original),
        change=change,evidence=p['update']['evidence']+refs,
        needs_review=sorted(set(p['update']['needs_review'])|{'competitive_transfer_to_other_opponents'}))
    refresh_grounding(p)
    assert compile_policy(p).encode()==source
    assert extract(source.decode(),p)==p
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True);bundle(p,dest)
        (dest/'policy.py').write_text('"""Primary semantic IR with audited coaching outcomes."""\n\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    else:
        assert read(dest/'policy.ir.json')==p,'Refusing to rewrite a saved evaluated pair'
    assert (dest/'policy.bas').read_bytes()==source
    return p


def main():
    for sub,total in [('',320),('visibility-complete',80),('late-cohort',160),('committed-return',80),('armed-cohort',80),('bounded-combat',80)]:
        r=read(STUDY/sub/'hosted-result.json');assert r['complete'] and r['games']==total
    capture=read(STUDY/'captured-inputs.json')
    for relative,info in capture['files'].items():
        for root in (Path(capture['session']),STUDY/'session-inputs'):
            assert digest((root/relative).read_bytes())==info['sha256'],str(root/relative)
    DEST.mkdir(parents=True,exist_ok=True)
    initial_control={c:cell(STUDY,'deployed',c) for c in ('red','blue')}
    fresh_control={c:cell(STUDY/'late-cohort','deployed',c) for c in ('red','blue')}
    results=[]
    for sub,name in VARIANTS:
        study=STUDY/sub;candidate=study/'candidates'/name
        original=read(candidate/'policy.ir.json');source=(candidate/'policy.bas').read_bytes()
        local=local_stats(study,name);control_local=local_stats(study,'deployed')
        hosted=None if sub in ('refined-breach','bounded-cohort') else {c:cell(study,name,c) for c in ('red','blue')}
        control=fresh_control if sub in ('late-cohort','committed-return','armed-cohort','bounded-cohort','bounded-combat') else initial_control
        passed=bool(hosted and all(v.get('invalid_games',0)==0 for v in hosted.values()) and min(v['wins'] for v in hosted.values())>=30 and
                    sum(v['wins'] for v in hosted.values())>=sum(v['wins'] for v in control.values())+8)
        refs=[evidence(STUDY/'captured-inputs.json'),evidence(STUDY/'session-binding.json'),
              evidence(study/'vm-proof.json'),evidence(study/'local-results.json')]
        if hosted:refs += [v['evidence'] for v in hosted.values()]
        claim=('Native tests verified the implemented combined behavior, and all12local games '
               'passed complete runtime/replay checks. Local wins '+str(local['wins'])+'/12 versus '
               +str(control_local['wins'])+'/12 control; deaths '+str(local['deaths'])+' versus '
               +str(control_local['deaths'])+'. ')
        if hosted:
            red_result=(str(hosted['red']['wins'])+'/40' if not hosted['red'].get('invalid_games') else
                'invalid cohort: '+str(hosted['red']['invalid_games'])+'/40games failed VM validation; no valid win-rate verdict')
            claim += ('Exact Richard135: red '+red_result+', blue '
                +str(hosted['blue']['wins'])+'/40; complete all-ten-VM/replay audits. '
                'The prospective both-color target gate '+('passed.' if passed else 'failed.')+
                ' This does not establish field strength or leaderboard rank. Correlated '
                'command trajectories preclude treating40seeds as40independent trials.')
            if hosted['red'].get('invalid_games'):
                claim=claim.replace('complete all-ten-VM/replay audits.','all replays reconstructed, but the red VM gate failed; invalid episodes are neither wins nor losses.')
        else:claim += 'Not submitted: '+read(study/'hosted-disposition.json')['reason']
        claims={'CoachedFormation':{'claim':'Hypothesis: this complete coached controller clears the '
                    'prespecified both-color Richard135 gate. Observations: '+claim,
                    'status':('supported' if passed else 'contradicted') if hosted else 'requires_review','evidence':refs},
                'CoachedMechanismFidelity':{'claim':'The native VM proof validates the listed executable '
                    'scenario behaviors only. Competitive efficacy is separately reported in CoachedFormation.',
                    'status':'supported','evidence':[evidence(study/'vm-proof.json')]}}
        if hosted:
            claims['RichardBlueComponent']={'claim':'This exact combined source won '
                +str(hosted['blue']['wins'])+'/40 fresh games on blue against Richard135. '
                'The blue execution inherits critical60. This is a role-specific result; '
                'it does not imply red or field superiority.','status':'supported',
                'evidence':[hosted['blue']['evidence']]}
        if 'HomePressurePersistence' in original['belief']['claims']:
            claims['HomePressurePersistence']={'claim':'Native consecutive-decision tests confirm '
                'that observed home pressure persists through fog for1200ticks and expires '
                'without a renewed sighting. This mechanism result is distinct from the '
                'competitive result recorded in CoachedFormation.','status':'supported',
                'evidence':[evidence(study/'vm-proof.json')]}
        if 'FormationEquipmentInteraction' in original['belief']['claims']:
            claims['FormationEquipmentInteraction']={'claim':'Hypothesis: coupling all-class '
                'ordered equipment with the V5 coordinated controller clears the both-color '
                'Richard135 gate. Measured outcome: '+('passed.' if passed else 'failed.')+
                ' Native tests verify the equipment behavior; see CoachedFormation for '
                'the complete local and hosted results.','status':'supported' if passed else 'contradicted',
                'evidence':refs}
        if 'CoachingRuntimeMargin' in original['belief']['claims']:
            if (study/'runtime-margin.json').exists():
                margin=read(study/'runtime-margin.json')
                claims['CoachingRuntimeMargin']={'claim':
                    'All24local games passed the19000instruction gate; measured maximum '
                    +str(margin['max_instructions'])+', leaving'+str(margin['headroom'])+
                    ' below the hard20000limit. All80hosted games passed the required '
                    'ten-VM checks. This establishes runtime validity for these '
                    'cases, not competitive strength or a global worst-case bound.',
                    'status':'supported','evidence':refs+[evidence(study/'runtime-margin.json')]}
            else:
                claims['CoachingRuntimeMargin']={'claim':'Hypothesis: this source maintains '
                    'the required1000instruction reserve in the full local screen. '
                    'Measured19105instructions exceeds the19000gate, so the hypothesis '
                    'failed and no hosted games were requested for this source.',
                    'status':'contradicted','evidence':refs+[evidence(study/'hosted-disposition.json')]}
        dest=DEST/'evaluated'/name
        updated=save_pair(original,source,dest,claims,refs,{
            'origin':'Validated coaching feedback; exact evaluated BASIC preserved',
            'session':capture['session'],'tested_source_ir_sha256':digest(original),
            'Richard_both_color_gate_passed':passed,'league_promoted':False})
        result={'name':name,'pair':str(dest),'source_sha256':digest(source),
                'evaluated_ir_sha256':digest(updated),'tested_ir_sha256':digest(original),
                'local':local,'local_control':control_local,'Richard':hosted,
                'Richard_both_color_gate_passed':passed,'field_qualified':False,
                'captured_inputs_preserved':True,'compile_extract_exact_parity':True}
        if (candidate/'uploaded-version.json').exists():result['uploaded_version']=read(candidate/'uploaded-version.json')
        write(dest/'validation.json',result);results.append(result)
        print('SAVED',name,passed,flush=True)
    qualified=[r for r in results if r['Richard_both_color_gate_passed']]
    qualified.sort(key=lambda r:(-min(c['wins'] for c in r['Richard'].values()),
        -sum(c['wins'] for c in r['Richard'].values()),sum(c['deaths'] for c in r['Richard'].values())))
    baseline_dir=STUDY/'candidates/deployed'
    baseline_refs=[evidence(STUDY/'hosted-result.json'),evidence(STUDY/'visibility-complete/hosted-result.json'),
                   evidence(STUDY/'late-cohort/hosted-result.json'),evidence(STUDY/'committed-return/hosted-result.json'),
                   evidence(STUDY/'armed-cohort/hosted-result.json'),evidence(STUDY/'bounded-combat/hosted-result.json')]
    save_pair(read(baseline_dir/'policy.ir.json'),(baseline_dir/'policy.bas').read_bytes(),
        DEST/'retained-baseline',{'CoachingStudyOutcome':{'claim':
            'The September20 coaching study tested ten combined variants in216local '
            'games and eight hosted variants with controls in800Richard135 games. '
            +str(len(qualified))+' variants cleared the prespecified both-color '
            'Richard gate. None has completed new field qualification. Keep this '
            'existing league baseline pending a fully qualified replacement.',
            'status':'supported','evidence':baseline_refs}},baseline_refs,
        {'origin':'Coaching evidence feedback; deployed BASIC unchanged','session':capture['session']})
    blue_ref=CAMPAIGN/'adaptive-opponent-20260920/critical-blue-confirmation/critical60/arm-result.json'
    blue=read(blue_ref);assert blue['wins']==40 and blue['games']==40 and blue['all_full_audits_passed']
    save_pair(read(CRITICAL/'policy.ir.json'),(CRITICAL/'policy.bas').read_bytes(),
        DEST/'validated-blue-component',{'Richard135BlueConfirmed':{'claim':
            'This exact critical60 source won40/40 fresh blue games versus exact '
            'Richard135, with complete replay and all-ten-VM audits. Preserve it '
            'as a role-specific research improvement. Red and broad field strength '
            'are not established; the coached variants retaining this blue '
            'execution also retained its target wins.',
            'status':'supported','evidence':[evidence(blue_ref)]}},[evidence(blue_ref)],
        {'origin':'Retain independently validated blue behavior; BASIC unchanged','session':capture['session']})
    summary={'complete':True,'session':capture['session'],'captured_input_files':len(capture['files']),
        'hosted_games':800,'local_games':216,'initial_control':initial_control,'followup_control':fresh_control,
        'invalid_hosted_games':sum(c.get('invalid_games',0) for r in results if r['Richard'] for c in r['Richard'].values()),
        'candidates':results,'Richard_qualified':[r['name'] for r in qualified],
        'selected_Richard_pair':qualified[0]['pair'] if qualified else None,
        'league_changed':False,'retention':'Current deployed baseline remains the league policy. '
            'All measured IR/BASIC pairs are preserved. The independently verified critical60 '
            'blue component is retained as a role-specific research improvement; no failed red '
            'coaching variant replaces the baseline.',
        'interpretation':'Adaptive discovery on a pinned release/config/roster; generated seeds are not '
            'matched across arms and command trajectories are correlated. Qualification still '
            'requires any remaining independent target confirmation and field checks.'}
    write(DEST/'results.json',summary);write(STUDY/'results.json',summary)
    write(DEST/'session-references.json',{'session':capture['session'],
        'capture_manifest':evidence(STUDY/'captured-inputs.json'),
        'binding':evidence(STUDY/'session-binding.json'),
        'study':str(STUDY),'preservation_verified':True})
    print('COMPLETE',str(DEST),flush=True)


if __name__=='__main__':main()
