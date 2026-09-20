"""Pinned black-kite challenge with the already planned deployed control cohort."""
from pathlib import Path
from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_wave import client, create
from jordan_lineup_guardrails import pin_auditor
from jordan_lineup_wide import ROOT as WIDE, WINNER
from policy_ir import digest, read, write
from ranger_guard_hosted import freeze
from red_pressure import STUDY
from rush_hosted import upload
from win_hosted import live


def control_path():
    row = next(h for h in read(WIDE / 'plan.json')['heads'] if h['rival']['id'] == '2b361c34-e135-4f50-bbfa-d7d9cd505c06')
    return Path(row['candidate'])


def prepare_head(folder, version, reference, label, design=None):
    old = read(reference / 'plan.json')
    fields = ('target', 'game_version', 'game_source', 'config', 'rival', 'rival_version', 'rival_key', 'episodes_per_color', 'interpretation')
    p = {k: old[k] for k in fields}
    p.update(policy_version=version['id'], policy_label=version['name'],
             design=design or 'Red attacker retention study:40episodes percolor, complete80 plus VM/fullreplay/equipment checks. '
             'Blue behavior exact locally; head counts remain fixed-lineup evidence. No deployment from this probe.',
             study_label=label)
    folder.mkdir(parents=True, exist_ok=True); freeze(folder / 'plan.json', p)
    for color in ('red', 'blue'):
        out = folder / p['rival_key'] / color; out.mkdir(parents=True, exist_ok=True)
        slots = list(range(5)) if color == 'red' else list(range(5, 10))
        roster = [version['id'] if s in slots else p['rival_version'] for s in range(10)]
        ap = p | {'color': color, 'own_slots': slots, 'roster': roster}
        freeze(out / 'plan.json', ap); pin_auditor(out)
        body = {'idempotency_key': 'gota-red-pressure-' + digest(ap)[:20], 'target': p['target'],
                'game_config_overrides': p['config'], 'num_episodes': 40,
                'roster': [{'slot': s, 'player': {'policy_ref': ref}} for s, ref in enumerate(roster)],
                'notes': p['design'] + ' ' + label + ' ' + color}
        with client() as c: create(c, body, out / 'batch', dry_run=True)


def prepare(name):
    if name not in read(STUDY / 'local/comparison.json')['qualified']:
        raise ValueError('Pressure candidate failed relative local gate')
    game = live(); wide = read(WIDE / 'plan.json')
    if game['version'] != wide['game_version'] or game['manifest']['game']['runnable']['source_url'] != wide['game_source']:
        raise ValueError('Published release changed')
    root, version = upload(name, STUDY, 'aaron-gota-ir-pressure',
        'Retain three red sentries while requiring a group to renew attacking roles; exact promoted blue branch.',
        feedback_override=STUDY / 'local/comparison-feedback' / name,
        validation_note='Fresh relative local nonregression and blue gameplay parity passed; black-kite/Jordan and field unvalidated. Inert experiment.')
    prepare_head(root / 'black-kite', version, control_path(), 'black-kite challenge')
    return root


def result(folder):
    if not (folder / 'result.json').exists(): run_prepared(folder)
    inventory(folder)
    r = next(iter(read(folder / 'result.json')['rivals'].values()))
    if r['games'] != 80 or not r['all_full_audits_passed'] or not all(x['gear_heroes'] == 5 for x in r['rows']):
        raise ValueError('Incomplete runtime/replay/equipment evidence')
    return r


def run(name):
    root = prepare(name)
    control, candidate = result(control_path()), result(root / 'black-kite')
    a, b = candidate['colors'], control['colors']
    checks = {'red_gain': a['red']['win'] >= b['red']['win'] + 20,
              'red_absolute': a['red']['win'] >= 20,
              'blue_preserved': a['blue']['win'] >= b['blue']['win'] - 2,
              'new_losses': candidate['losses'] <= control['losses'] + 2}
    report = {'checks': checks, 'passed': all(checks.values()), 'candidate': candidate, 'control': control,
              'control_reuse': str(control_path()), 'scope': 'Targeted fixed-lineup diagnostic; original wide cohort reused, never double counted.'}
    write(root / 'black-kite-result.json', report)
    feedback = STUDY / 'local/comparison-feedback' / name
    if not (root / 'black-kite-feedback').exists():
        record(feedback / 'policy.ir.json', feedback / 'policy.bas',
               f'Black-kite13 candidate{candidate["wins"]}/80 vsdeployed{control["wins"]}/80; checks{checks}. '
               'Broad field and Jordan preservation required.', root / 'black-kite-result.json', root / 'black-kite-feedback')
    print('Pressure black-kite', name, candidate['colors'], checks, flush=True)
    if report['passed']:
        prepare_head(root / 'jordan', read(root / 'uploaded-version.json'), WINNER / 'jordan', 'Jordan preservation')
        jordan = result(root / 'jordan')
        checks = {c: jordan['colors'][c]['win'] >= 38 for c in ('red', 'blue')}
        jr = {'checks': checks, 'passed': all(checks.values()), 'result': jordan, 'reused_deployed_control': '80/80'}
        write(root / 'jordan-result.json', jr)
        feedback = root / 'black-kite-feedback'
        if not (root / 'jordan-feedback').exists():
            record(feedback / 'policy.ir.json', feedback / 'policy.bas',
                   f'Jordan186 pressure preservation{jordan["wins"]}/80; checks{checks}. Field still unvalidated.',
                   root / 'jordan-result.json', root / 'jordan-feedback')
        print('Pressure Jordan', name, jordan['colors'], checks, flush=True)
    return report
