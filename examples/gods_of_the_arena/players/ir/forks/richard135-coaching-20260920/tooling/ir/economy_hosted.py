"""Upload screened IR candidates, read fixed discovery, prepare held-out XP."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import shutil

import httpx

from campaign_hosted_compare import cohort, fisher_greater
from economy_feedback import record
from hosted_wave import client, get
from policy_ir import HERE, compile_policy, digest, extract, read, write

OPTIMIZER = 'ply_594ec24d-d7f3-4370-a000-468354ec41c9'


def upload(directory):
    local = directory / 'economy'
    screen = read(local / 'screen-result.json')
    frozen = read(local / 'plan.json')
    hosted = directory / 'hosted-discovery'
    plan = read(hosted / 'plan.json')
    for name in screen['selected']:
        source = Path(frozen['sources'][name]).read_bytes()
        policy = read(local / 'screen-feedback' / name / 'policy.ir.json')
        if (digest(source) != frozen['inputs'][frozen['sources'][name]] or
                compile_policy(policy).encode() != source or extract(source.decode(), policy) != policy):
            raise ValueError('IR and frozen executable disagree')
        out = hosted / name
        out.mkdir(exist_ok=True)
        metadata = {'name': 'aaron-gota-ir-' + name.replace('_', '-') + '-0916',
                    'content_hash': digest(source), 'size_bytes': len(source), 'player_id': OPTIMIZER,
                    'attributes': {}, 'tags': {'game': 'gods_of_the_arena', 'change': name,
                        'semantic_ir_sha256': digest(policy), 'game_version': plan['game_version'],
                        'validation': 'Local discovery qualifier; hosted unvalidated; no league selection'}}
        request = out / 'upload-request.json'
        if request.exists() and read(request) != metadata:
            raise ValueError('Upload metadata changed')
        write(request, metadata)
        receipt = out / 'uploaded-version.json'
        with client() as c:
            if not receipt.exists():
                response = c.post('/stats/policies/files/upload', json=metadata)
                version = None
                if response.status_code == 409:
                    # Stored content is reusable; completing registers its player/version.
                    response = c.post('/stats/policies/files/complete', json=metadata)
                    response.raise_for_status()
                    version = response.json()
                else:
                    response.raise_for_status()
                    payload = response.json()
                    version = payload.get('existing_policy_version')
                    if version is None:
                        stored = httpx.put(payload['upload_url'], content=source,
                                           headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                        stored.raise_for_status()
                        response = c.post('/stats/policies/files/complete', json=metadata)
                        response.raise_for_status()
                        version = response.json()
                write(receipt, version)
            version = read(receipt)
            log = HERE / 'VERSION_LOG.md'
            text = log.read_text()
            if version['id'] not in text:
                text += (f"\n## {version['name']}:v{version['version']}\n\n"
                         f"- ID `{version['id']}`; UTC {datetime.now(timezone.utc).isoformat()}; player Aaron's Optimizer.\n"
                         f"- IR configuration: `{name}` / {frozen['variants'][name]}; user-authorized multi-hypothesis discovery.\n"
                         f"- BASIC SHA `{digest(source)}`, game {plan['game_version']}, source `{plan['game_source']}`.\n"
                         f"- Local discovery: {screen['metrics'][name]['wins']}/40 wins; selected among {len(frozen['variants'])} cells. "
                         '**Hosted unvalidated**; inert upload, no competitive-superiority claim or league selection.\n'
                         f"- Evidence: `{local}`; receipts: `{out}`.\n")
                log.write_text(text)
            owned = get(c, '/v2/policy-versions?mine=true&limit=100&q=' + metadata['name'])
            write(out / 'owned-readback.json', owned)
            entries = owned if isinstance(owned, list) else owned.get('entries', owned.get('policy_versions', []))
            matches = [r for r in entries if r.get('policy_version_id', r.get('id')) == version['id']]
            if len(matches) != 1 or matches[0].get('player_id') != OPTIMIZER:
                raise ValueError('Ownership/player binding did not verify')
        arm_plan = {k: plan[k] for k in ['target', 'game_version', 'game_source', 'config', 'opponents']}
        arm_plan.update(run_id='gota-economy-20260916-' + name, policy_version=version['id'],
                        notes='100episode frozen current-field discovery; locally selected IR candidate, hosted unvalidated. Same pinned opponents as both deployed controls; fresh confirmation required.')
        arm_plan['run_id'] += '-' + digest(plan)[:10]
        if (out / 'plan.json').exists():
            # A previously launched request keeps its exact idempotency key.
            arm_plan['run_id'] = read(out / 'plan.json')['run_id']
        if (out / 'plan.json').exists() and read(out / 'plan.json') != arm_plan:
            raise ValueError('Arm plan changed')
        write(out / 'plan.json', arm_plan)
        shutil.copy2(hosted / 'v2/audit', out / 'audit')
        print(f"{name}: {version['name']}:v{version['version']} ({version['id']}); no league change", flush=True)


def summarize(parts):
    rows = [r for p in parts for r in p['rows']]
    count = len(rows)
    if len({r['seed'] for r in rows}) != count or Counter(r['slot'] for r in rows) != Counter({s: count // 10 for s in range(10)}):
        raise ValueError('Repeated seeds or unbalanced seats')
    return {'games': count, 'wins': sum(r['win'] for r in rows),
            'death_rate': sum(r['deaths'] for r in rows) * 1440 / sum(r['alive_ticks'] for r in rows),
            'xp': sum(r['xp'] for r in rows), 'mean_glory': sum(r['glory'] for r in rows) / count,
            'equipment_games': sum(r['first_gear_tick'] >= 0 for r in rows),
            'class_wins': {cls: {'games': len(rr := [r for r in rows if r['class'] == cls]),
                                  'wins': sum(r['win'] for r in rr)} for cls in sorted({r['class'] for r in rows})},
            'rows': rows}


def compare(directory, confirmation=False):
    root = directory / ('hosted-confirmation' if confirmation else 'hosted-discovery')
    plan = read(root / 'plan.json')
    selected = [plan['candidate']] if confirmation else read(directory / 'economy/screen-result.json')['selected']
    names = ['v2', 'motion', *selected]
    arms = {}
    seeds = set()
    if confirmation:
        discovery = read(directory / 'hosted-discovery/result.json')
        seeds = {r['seed'] for a in discovery['arms'].values() for r in a['rows']}
    for name in names:
        folders = [root / name / f'part-{i}' for i in range(4)] if confirmation else [root / name]
        for folder in folders:
            arm = read(folder / 'plan.json')
            for key in ['target', 'game_version', 'game_source', 'config', 'opponents']:
                if arm[key] != plan[key]:
                    raise ValueError('Frozen arm mismatch: ' + key)
        arms[name] = summarize([cohort(folder, 2) for folder in folders])
        new = {r['seed'] for r in arms[name]['rows']}
        if new & seeds:
            raise ValueError('Non-independent or previously observed effective seed')
        seeds |= new
    eligible = []
    comparisons = {}
    for name in selected:
        a = arms[name]
        comparisons[name] = {}
        for control in ['v2', 'motion']:
            b = arms[control]
            gain = (a['wins'] - b['wins']) / a['games']
            p = fisher_greater(a['wins'], a['games'], b['wins'], b['games'])
            adverse = [cls for cls, group in a['class_wins'].items() if
                       fisher_greater(b['class_wins'][cls]['wins'], b['class_wins'][cls]['games'],
                                      group['wins'], group['games']) < .005]
            comparisons[name][control] = {'gain': gain, 'p': p, 'adverse_classes': adverse,
                                          'passed': gain >= .05 and (not confirmation or (p < .025 and not adverse))}
        guards = a['death_rate'] <= 1.1 * arms['v2']['death_rate'] and a['xp'] >= .8 * arms['v2']['xp'] and a['equipment_games'] == a['games']
        if all(c['passed'] for c in comparisons[name].values()) and guards:
            eligible.append(name)
    eligible.sort(key=lambda name: (-arms[name]['wins'], arms[name]['death_rate'], -arms[name]['xp'], name))
    result = {'stage': 'confirmation' if confirmation else 'discovery', 'arms': arms,
              'comparisons': comparisons, 'eligible': eligible, 'selected': eligible[0] if eligible else None,
              'passed': bool(eligible) if confirmation else False,
              'meaning': 'Fresh400/arm held-out verdict' if confirmation else 'Candidate selection only; no superiority claim'}
    path = root / 'result.json'
    write(path, result)
    for name in selected:
        parent = directory / ('hosted-discovery' if confirmation else 'economy/screen-feedback') / name
        if confirmation:
            parent = parent / 'feedback'
        a = arms[name]
        claim = (f"Completed hosted {result['stage']} against fixed current top-nine incumbents on {plan['game_version']}: "
                 f"{a['wins']}/{a['games']} wins, v2 {arms['v2']['wins']}/{arms['v2']['games']}, motion {arms['motion']['wins']}/{arms['motion']['games']}. "
                 f"Comparisons {comparisons[name]}; death rate {a['death_rate']:.6f}; XP {a['xp']}; meanGlory {a['mean_glory']:.3f}; "
                 f"class wins {a['class_wins']}. All artifacts and replay state sequences verified. "
                 f"{'Passed' if name in eligible else 'Failed'} frozen stage gates. {result['meaning']}. "
                 + ('Broad-field guardrail still required before deployment.' if confirmation and name in eligible else 'No league promotion from this result.'))
        record(parent / 'policy.ir.json', directory / 'economy/candidates' / name / 'policy.bas', claim,
               path, root / name / 'feedback')
    print({k: v for k, v in result.items() if k != 'arms'}, flush=True)


def prepare_confirmation(directory):
    discovery = directory / 'hosted-discovery'
    result = read(discovery / 'result.json')
    name = result['selected']
    if name is None:
        raise ValueError('No hosted discovery qualifier')
    old = read(discovery / 'plan.json')
    study_tag = digest(old)[:10]
    root = directory / 'hosted-confirmation'
    root.mkdir(exist_ok=True)
    plan = {k: old[k] for k in ['target', 'game_version', 'game_source', 'config', 'opponents', 'confirmation_rule']}
    plan.update(candidate=name, discovery_sha256=digest((discovery / 'result.json').read_bytes()),
                sample_size=400, previous_outcomes_excluded=True)
    if (root / 'plan.json').exists() and read(root / 'plan.json') != plan:
        raise ValueError('Confirmation selection changed')
    write(root / 'plan.json', plan)
    for arm in ['v2', 'motion', name]:
        prior = read(discovery / arm / 'plan.json')
        for index in range(4):
            folder = root / arm / f'part-{index}'
            folder.mkdir(parents=True, exist_ok=True)
            write(folder / 'plan.json', prior | {'run_id': f'gota-economy-confirm-20260916-{study_tag}-{arm}-{index}',
                  'notes': f'Fresh fixed400-per-arm confirmation {arm},part{index+1}/4. Previous discovery excluded; no interim tuning or stopping. Complete1200games and all replay audits before verdict.'})
            shutil.copy2(discovery / arm / 'audit', folder / 'audit')
    print('Prepared fresh400games/arm; no XP launched.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    p.add_argument('command', choices=['upload', 'compare', 'prepare-confirmation', 'confirm'])
    a = p.parse_args()
    {'upload': upload, 'compare': compare, 'prepare-confirmation': prepare_confirmation,
     'confirm': lambda d: compare(d, True)}[a.command](a.directory.resolve())
