"""Frozen league-threat comparison using previously budgeted exact controls."""
from pathlib import Path
from economy_feedback import record
from hosted_wave import client, create
from jordan_lineup_guardrails import pin_auditor
from jordan_lineup_wide import ROOT as WIDE, WINNER
from policy_ir import digest, read, write
from ranger_guard import STUDY as RECALL
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head, result as head_result
from release_deploy_pair import clone_for_aaron
from rush_hosted import upload
from threat_coverage import STUDY
from win_hosted import live


DESIGN = ('Coordinated threat coverage: source-matched pinned roster,40episodes percolor. '
          'Complete both colors and fullruntime/replay/owned-equipment checks; no intermediate tuning. '
          'Directional tactical evidence, broad field remains necessary before deployment.')


def control(label):
    return Path(next(h['candidate'] for h in read(WIDE / 'plan.json')['heads'] if h['rival']['label'] == label))


def prepare(name):
    if name not in read(STUDY / 'local/comparison.json')['qualified']:
        raise ValueError('Candidate failed completed local qualification')
    game = live(); wide = read(WIDE / 'plan.json')
    if game['version'] != wide['game_version'] or game['manifest']['game']['runnable']['source_url'] != wide['game_source']:
        raise ValueError('Published game changed')
    root, version = upload(name, STUDY, 'aaron-gota-ir-coverage',
        'Observed three-hero rush coverage and coordinated role-specific recall; see exact IR parameters for selected color components.',
        feedback_override=STUDY / 'local/comparison-feedback' / name,
        validation_note='Fresh relative local games and full component parity passed; actual league-threat/mixed/Jordan/field outcomes unvalidated. Inert experiment.')
    source = (STUDY / 'local/candidates' / name / 'policy.bas').read_bytes()
    with client() as c:
        clone = clone_for_aaron(c, root, read(root / 'upload-request.json'), source,
                               'Local relative qualification and component parity passed; hosted unvalidated, inert registration only.')
    prepare_head(root / 'red-kite', version, control('red-kite:v27'), 'actual round377 threat', DESIGN)
    reference = RECALL / 'hosted/control-mixed'; old = read(reference / 'plan.json')
    fields = ('target','game_version','game_source','config','rival','rival_key','episodes_per_color','interpretation')
    p = {k: old[k] for k in fields}
    refs = [clone['id'], version['id']]
    p.update(policy_version=version['id'], policy_label=version['name'], owned_versions=refs, design=DESIGN)
    folder = root / 'mixed'; folder.mkdir(exist_ok=True); freeze(folder / 'plan.json', p)
    for color in ('red','blue'):
        before = read(reference / p['rival_key'] / color / 'plan.json')
        slots = [0,1] if color == 'red' else [5,6]
        roster = before['roster'].copy()
        for s, ref in zip(slots,refs): roster[s] = ref
        ap = p | {'color': color, 'own_slots': before['own_slots'], 'controlled_slots': slots,
                  'roster': roster, 'owners': before['owners']}
        out = folder / p['rival_key'] / color; out.mkdir(parents=True,exist_ok=True)
        freeze(out/'plan.json',ap); pin_auditor(out)
        body = {'idempotency_key':'gota-coverage-mixed-'+digest(ap)[:20], 'target':p['target'],
                'game_config_overrides':p['config'], 'num_episodes':40,
                'roster':[{'slot':s,'player':{'policy_ref':v}} for s,v in enumerate(roster)],
                'notes':DESIGN+' Actualtwoownedheroes in diagnosedten-playerroster. '+color}
        with client() as c: create(c,body,out/'batch',dry_run=True)
    return root


def mixed_result(folder):
    r = head_result(folder)
    p = read(folder/'plan.json')
    for color in ('red','blue'):
        arm = folder/p['rival_key']/color; plan = read(arm/'plan.json')
        for done in arm.glob('artifacts/*/.done'):
            ep, audit = read(done.parent/'episode.json'), read(done.parent/'audit.json')
            owners = {x['position']:x['player_id'] for x in ep['participants']}
            if owners != dict(enumerate(plan['owners'])) or len(set(owners.values())) != 10:
                raise ValueError('Mixed actual owner mismatch')
            if not all(audit['heroes'][s]['first_gear_tick'] >= 0 for s in plan['controlled_slots']):
                raise ValueError('Actual owned hero failed equipment check')
    return r


def run(name):
    root = prepare(name); plan = read(STUDY/'hosted-prospective-plan.json'); gates = plan['gates']
    controls = {'red_kite':head_result(control('red-kite:v27')),
                'mixed':mixed_result(RECALL/'hosted/control-mixed')}
    candidates = {'red_kite':head_result(root/'red-kite'), 'mixed':mixed_result(root/'mixed')}
    checks = {'red_kite_absolute':candidates['red_kite']['colors']['red']['win'] >= gates['red_kite_minimum_red_wins']}
    for context in candidates:
        for color in ('red','blue'):
            checks[context+'_'+color] = candidates[context]['colors'][color]['win'] >= controls[context]['colors'][color]['win'] - gates['maximum_color_loss']
    gains = {context:candidates[context]['colors'][color]['win']-controls[context]['colors'][color]['win']
             for context,color in (('red_kite','red'),('mixed','blue'))}
    checks['large_gain'] = max(gains.values()) >= gates['minimum_large_gain_either_red_kite_red_or_mixed_blue']
    report = {'candidate':name,'controls':controls,'candidates':candidates,'gains':gains,'checks':checks,'passed':all(checks.values()),
              'plan_sha256':digest((STUDY/'hosted-prospective-plan.json').read_bytes()),'scope':plan['scope']}
    write(root/'targeted-result.json',report)
    feedback = STUDY/'local/comparison-feedback'/name
    if not (root/'targeted-feedback').exists():
        record(feedback/'policy.ir.json',feedback/'policy.bas',f'Targeted league-threat and mixed tests: gains{gains}; checks{checks}. Jordan/black-kite/broad field pending.',root/'targeted-result.json',root/'targeted-feedback')
    print('Coverage targeted',name,gains,checks,flush=True)
    if report['passed']:
        preservation = {}
        for key, reference in (('jordan',WINNER/'jordan'),('black-kite',control('black-kite:v13'))):
            prepare_head(root/key,read(root/'uploaded-version.json'),reference,key+' preservation',DESIGN)
            r = head_result(root/key); before = head_result(reference)
            c = {color:r['colors'][color]['win'] >= (gates['jordan_minimum_each_color'] if key=='jordan' else
                   before['colors'][color]['win']-gates['black_kite_maximum_color_loss']) for color in ('red','blue')}
            preservation[key] = {'result':r,'checks':c,'passed':all(c.values())}
        result = {'preservation':preservation,'passed':all(x['passed'] for x in preservation.values()),'scope':'Broad field still required; no automatic deployment.'}
        write(root/'preservation-result.json',result)
        feedback = root/'targeted-feedback'
        if not (root/'preservation-feedback').exists():
            record(feedback/'policy.ir.json',feedback/'policy.bas',f'Targeted preservation passed{result["passed"]}; broad field still unvalidated.',root/'preservation-result.json',root/'preservation-feedback')
        print('Coverage preservation',name,{k:v['checks'] for k,v in preservation.items()},flush=True)
    return report


if __name__ == '__main__':
    import sys
    run(sys.argv[1])
