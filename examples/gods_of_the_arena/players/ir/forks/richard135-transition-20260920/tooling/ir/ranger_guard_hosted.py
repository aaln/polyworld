"""Fresh fixed-role ten-player A/B, then Jordan preservation for qualified recall."""
from pathlib import Path

from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_wave import client, create
from jordan_lineup_guardrails import pin_auditor
from jordan_lineup_wide import WINNER as DEPLOYED
from policy_ir import digest, read, write
from ranger_guard import STUDY
from release_deploy_pair import clone_for_aaron
from rush_hosted import upload
from win_hosted import live


def diagnostic_admissibility(name, comparison, raw, parity):
    """Diagnostic admission is explicitly separate from the failed promotion gate."""
    if name != 'arrival12' or raw['verified_games'] != 300:
        raise ValueError('Only the prespecified first recall candidate has a complete local diagnostic')
    metrics = comparison['metrics']
    candidate, baseline = metrics[name], metrics['deployed']
    if not candidate['all_gear'] or not parity[name]['all_gameplay_equal']:
        raise ValueError('Local runtime/equipment or red parity failed')
    def outcomes(label):
        rows = [r for r in raw['rows'] if r['name'] == label]
        if len(rows) != 60 or any(r['gear_heroes'] != 5 for r in rows):
            raise ValueError('Incomplete local diagnostic cohort')
        return {(r['seed'], r['color'], r['opponent']): r['win'] for r in rows}
    a, b = outcomes(name), outcomes('deployed')
    if len(a) != 60 or a != b or candidate['wins'] != baseline['wins']:
        raise ValueError('Candidate did not preserve every local case outcome')
    return {'candidate': name, 'local_qualified': name in comparison['qualified'],
            'local_wins': candidate['wins'], 'control_wins': baseline['wins'],
            'default_wins': candidate['opponents']['default'], 'original_required_default_wins': 18,
            'all60_outcomes_identical': True, 'all30_red_gameplay_equal': True,
            'scope': 'Mechanism diagnostic only. Original local absolute gate remains failed; no promotion eligibility is granted.'}


def prepare(name, diagnostic=False):
    comparison = read(STUDY / 'local/comparison.json')
    validation = 'Local arrival-qualified recall and red gameplay parity passed; hosted mixed/Jordan unvalidated'
    feedback = STUDY / 'local/comparison-feedback' / name
    if diagnostic:
        admission = diagnostic_admissibility(name, comparison, read(STUDY / 'local/result.json'),
                                             read(STUDY / 'local/red-parity.json'))
        freeze(STUDY / 'hosted-diagnostic-admission.json', admission | {
            'comparison_sha256': digest((STUDY / 'local/comparison.json').read_bytes()),
            'raw_sha256': digest((STUDY / 'local/result.json').read_bytes()),
            'fresh_plan': '80 deployed +80 arrival12 in the diagnosed mixed roles. Conditional80 Jordan only if mixed gains pass. Existing numerical hosted thresholds retained; no automatic deployment.'})
        validation = 'Diagnostic only: original local gate failed (default15/20 vs18 required); candidate and deployed55/60 with all60 outcomes equal. Hosted unvalidated.'
        diagnostic_feedback = STUDY / 'diagnostic-feedback' / name
        if not diagnostic_feedback.exists():
            record(feedback / 'policy.ir.json', feedback / 'policy.bas', validation,
                   STUDY / 'hosted-diagnostic-admission.json', diagnostic_feedback)
        feedback = diagnostic_feedback
    elif name not in comparison['qualified']:
        raise ValueError('Not a locally qualified arrival variant')
    game = live()
    root, version = upload(name, STUDY, 'aaron-gota-ir-recall',
        'Count quiet defense only after arrival at the protected structure; preserve red policy and equipment.',
        feedback_override=feedback, validation_note=validation)
    source = (STUDY / 'local/candidates' / name / 'policy.bas').read_bytes()
    with client() as c:
        clone = clone_for_aaron(c, root, read(root / 'upload-request.json'), source,
                              validation + ' Inert registration only.')
    reference = read(STUDY / 'selected-replays.json')['selection']['candidate']
    ep = read(Path(reference['folder']) / 'episode.json')
    base = ep['policy_version_ids']
    control = [read(DEPLOYED / 'deployment-pair/aaron-upload/uploaded-version.json')['id'], read(DEPLOYED / 'uploaded-version.json')['id']]
    if base[5:7] != control or ep['coworld_version'] != game['version']:
        raise ValueError('Exact diagnosed roster/release changed')
    config = {k: v for k, v in ep['game_config'].items() if k not in ('seed', 'players', 'tokens')}
    rule = {'minimum_blue_gain': 8, 'minimum_total_gain': 8, 'minimum_blue_wins': 30, 'maximum_red_loss': 2,
            'jordan_minimum_each_color': 38, 'all_owned_equipment': True, 'all_replays_and_vms': True}
    common = {'target': {'coworld_id': ep['coworld_id'], 'variant_id': 'competition'},
              'game_version': game['version'], 'game_source': game['manifest']['game']['runnable']['source_url'],
              'config': config, 'rival_key': 'ranger_vanguard', 'rival': 'Exact diagnosed ten-player Ranger/Vanguard roster',
              'episodes_per_color': 40, 'interpretation': 'Two pinned role contexts with generated seeds; correlated trajectories, not a league-wide or formal significance estimate.',
              'local_admission': validation,
              'design': 'Fresh80/arm ten-player A/B. Blue owned Vanguard/Ranger slots5,6; mirrored red slots0,1. '
              'Only both owned versions change; all eight other players frozen. Complete both colors before verdict. '
              'If mixed gates pass,80new Jordan186 games must preserve at least38/40wins percolor. No automatic deployment.'}
    paths = []
    for arm, refs in (('control', control), ('candidate', [clone['id'], version['id']])):
        folder = STUDY / 'hosted/control-mixed' if arm == 'control' else root / 'mixed/candidate'
        folder.mkdir(parents=True, exist_ok=True)
        plan = common | {'policy_version': refs[1], 'policy_label': arm, 'owned_versions': refs}
        freeze(folder / 'plan.json', plan)
        for color in ('red', 'blue'):
            roster = base[:]; roster[5:7] = refs
            owners = [p['player_id'] for p in sorted(ep['participants'], key=lambda p: p['position'])]
            if color == 'red': roster = roster[5:] + roster[:5]; owners = owners[5:] + owners[:5]
            out = folder / plan['rival_key'] / color; out.mkdir(parents=True, exist_ok=True)
            slots = list(range(5)) if color == 'red' else list(range(5, 10))
            controlled = [0, 1] if color == 'red' else [5, 6]
            ap = plan | {'color': color, 'own_slots': slots, 'controlled_slots': controlled, 'roster': roster, 'owners': owners}
            freeze(out / 'plan.json', ap); pin_auditor(out)
            body = {'idempotency_key': 'gota-arrival-mixed-' + digest(ap)[:20], 'target': plan['target'],
                    'game_config_overrides': config, 'num_episodes': 40,
                    'roster': [{'slot': s, 'player': {'policy_ref': ref}} for s, ref in enumerate(roster)],
                    'notes': common['design'] + ' ' + arm + ' ' + color}
            with client() as c: create(c, body, out / 'batch', dry_run=True)
        paths.append(str(folder))
    freeze(root / 'mixed-plan.json', {'paths': paths, 'rules': rule, 'candidate': name,
           'control_versions': control, 'candidate_versions': [clone['id'], version['id']], 'games_per_arm': 80,
           'control_reuse': 'One fresh80game deployed control shared by any conditionally tested arrival variant; never count it as new for a second candidate.'})
    return root


def freeze(path, value):
    if path.exists() and read(path) != value: raise ValueError('Frozen hosted plan changed')
    if not path.exists(): write(path, value)


def run(name, diagnostic=False):
    root = prepare(name, diagnostic=diagnostic); plan = read(root / 'mixed-plan.json'); arms = {}; equipment = True
    for folder in map(Path, plan['paths']):
        if not (folder / 'result.json').exists(): run_prepared(folder)
        inventory(folder)
        label = 'control' if folder.name == 'control-mixed' else 'candidate'
        arms[label] = read(folder / 'result.json')['rivals']['ranger_vanguard']
        for color in ('red', 'blue'):
            arm = folder / 'ranger_vanguard' / color; p = read(arm / 'plan.json')
            for done in arm.glob('artifacts/*/.done'):
                ep, audit = read(done.parent / 'episode.json'), read(done.parent / 'audit.json')
                owners = {r['position']: r['player_id'] for r in ep['participants']}
                if owners != dict(enumerate(p['owners'])) or len(set(owners.values())) != 10:
                    raise ValueError('Actual ten-player ownership differs')
                equipment &= all(audit['heroes'][s]['first_gear_tick'] >= 0 for s in p['controlled_slots'])
    a, b, g = arms['candidate'], arms['control'], plan['rules']
    checks = {'blue_gain': a['colors']['blue']['win'] >= b['colors']['blue']['win'] + g['minimum_blue_gain'],
              'blue_absolute': a['colors']['blue']['win'] >= g['minimum_blue_wins'],
              'total_gain': a['wins'] >= b['wins'] + g['minimum_total_gain'],
              'red': a['colors']['red']['win'] >= b['colors']['red']['win'] - g['maximum_red_loss'],
              'both_gear': equipment}
    result = {'games': 160, 'arms': arms, 'checks': checks, 'passed': all(checks.values())}
    write(root / 'mixed-result.json', result)
    src = STUDY / ('diagnostic-feedback' if diagnostic else 'local/comparison-feedback') / name
    if not (root / 'mixed-feedback').exists():
        record(src / 'policy.ir.json', src / 'policy.bas',
               f'Fresh160game targeted mixed test: candidate{a["wins"]}/80, deployed{b["wins"]}/80. Checks{checks}. '
               'Twofixedrosters; Jordan and broad guardrails remain required before another deployment.',
               root / 'mixed-result.json', root / 'mixed-feedback')
    print('Arrival mixed result', {k: v for k, v in result.items() if k != 'arms'}, flush=True)
    if result['passed']: jordan(root, name)
    return result


def jordan(root, name):
    version = read(root / 'uploaded-version.json')
    old = read(DEPLOYED / 'jordan/plan.json'); key = old['rival_key']
    plan = {k: old[k] for k in ('target', 'game_version', 'game_source', 'config', 'rival', 'rival_version',
                              'rival_key', 'episodes_per_color', 'interpretation')}
    plan.update(policy_version=version['id'], policy_label=version['name'],
                design='After the frozen mixed recall test passes, require38/40wins percolor against Jordan186. '
                'Exact current blue_repair80/80 is a reused control; new candidate80 fully audited. Broad field still required.')
    folder = root / 'jordan'; folder.mkdir(exist_ok=True); freeze(folder / 'plan.json', plan)
    for color in ('red', 'blue'):
        out = folder / key / color; out.mkdir(parents=True, exist_ok=True)
        slots = list(range(5)) if color == 'red' else list(range(5, 10))
        roster = [version['id'] if s in slots else plan['rival_version'] for s in range(10)]
        p = plan | {'color': color, 'own_slots': slots, 'roster': roster}
        freeze(out / 'plan.json', p); pin_auditor(out)
        body = {'idempotency_key': 'gota-arrival-jordan-' + digest(p)[:20], 'target': p['target'],
                'game_config_overrides': p['config'], 'num_episodes': 40,
                'roster': [{'slot': s, 'player': {'policy_ref': v}} for s, v in enumerate(roster)],
                'notes': p['design'] + ' ' + color}
        with client() as c: create(c, body, out / 'batch', dry_run=True)
    if not (folder / 'result.json').exists(): run_prepared(folder)
    inventory(folder); r = read(folder / 'result.json')['rivals'][key]
    checks = {c: r['colors'][c]['win'] >= 38 for c in ('red', 'blue')}
    checks['equipment'] = all(x['gear_heroes'] == 5 for x in r['rows'])
    result = {'wins': r['wins'], 'games': 80, 'colors': r['colors'], 'checks': checks, 'passed': all(checks.values())}
    write(root / 'jordan-result.json', result)
    if not (root / 'jordan-feedback').exists():
        src = root / 'mixed-feedback'
        record(src / 'policy.ir.json', src / 'policy.bas',
               f'Arrival candidate Jordan80 preservation result {result}. Broad mixed field remains required.',
               root / 'jordan-result.json', root / 'jordan-feedback')
    print('Arrival Jordan result', result, flush=True)


if __name__ == '__main__':
    import sys
    run(sys.argv[1])
