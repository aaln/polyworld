"""Side-swapped five-versus-five probes against the two user-named rivals."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from math import comb
from pathlib import Path
import shutil
import subprocess
import sys
import time

from hosted_wave import client, create, episodes, fetch, get, TERMINAL
from hosted_wave_audit import verify as audit
from policy_ir import HERE, digest, read, write
from release_workspace import verify

RIVALS = {'richard': ('richard-gods-of-the-arena:v50', '9d29b896-92ec-4a63-a152-909e40c2fa90'),
          'codex_lanes': ('gota-codex-objective-lanes-20260915:v1', '929b92b9-368e-4c7d-9275-8913703abafd')}


def prepare(study):
    verify()
    discovery = read(study / 'hosted-discovery/result.json')
    name = discovery['selected']
    if not name:
        raise ValueError('Finish discovery and qualify before rival probes')
    plan = read(study / 'hosted-discovery/plan.json')
    version = read(study / 'hosted-discovery' / name / 'uploaded-version.json')['id']
    with client() as c:
        game = get(c, '/v2/coworlds/' + plan['target']['coworld_id'])
        if game['version'] != plan['game_version'] or game['manifest']['game']['runnable']['source_url'] != plan['game_source']:
            raise ValueError('Published source changed')
    root = study / 'rival-matchups'
    root.mkdir(exist_ok=True)
    frozen = {'created_at': datetime.now(timezone.utc).isoformat(), 'candidate': name, 'policy_version': version,
        'target': plan['target'], 'game_version': plan['game_version'], 'game_source': plan['game_source'], 'config': plan['config'],
        'design': 'Five copies of our exact policy against five copies of one pinned rival;40independent games per color,80per rival. All ten slots pinned; no mixed teammates.',
        'interpretation': 'Direct team-policy probe, distinct from single-seat league contribution. Do not pool these games with confirmation.',
        'rule': 'Finish all160games and audits. To call a rival beaten:>=55%wins overall and one-sided exact binomial win-vs-loss p<.025; report draws and both colors separately. Full source/replay/VM/XP/roster checks required.',
        'discovery_sha256': digest((study / 'hosted-discovery/result.json').read_bytes())}
    if study.name == 'win-first-study':
        frozen['design'] = 'Five copies perteam;40seeded repeats percolor/rival, two fixed tactical lineups perrival. Differentseeds may reproduce identicalcommands.'
        frozen['interpretation'] = 'Direct fixed-lineup team-policy probe only; repeatedtrajectories do not establish broad significance. Mixed-roster confirmation andfieldtransfer remainseparate.'
        frozen['rule'] = 'Complete160games/allfullaudits. A fixedlineup is won if >20/40wins; require this onbothcolors tocall bothfixedlineups beaten. Nominalbinomialp is arithmetic only. No generalization claim from identicalrepeats.'
    if not (root / 'plan.json').exists():
        write(root / 'plan.json', frozen)
    else:
        prior = read(root / 'plan.json')
        if any(prior[k] != v for k, v in frozen.items() if k != 'created_at'):
            raise ValueError('Rival plan changed')
    for rival, (label, rival_id) in RIVALS.items():
        for color in ['red', 'blue']:
            out = root / rival / color
            out.mkdir(parents=True, exist_ok=True)
            slots = list(range(5)) if color == 'red' else list(range(5,10))
            roster = [version if slot in slots else rival_id for slot in range(10)]
            arm = frozen | {'rival': label, 'rival_version': rival_id, 'own_slots': slots, 'roster': roster}
            arm.pop('created_at')
            if (out / 'plan.json').exists() and read(out / 'plan.json') != arm:
                raise ValueError('Rival arm changed')
            write(out / 'plan.json', arm)
            shutil.copy2(study / 'hosted-discovery' / name / 'audit', out / 'audit')
            body = {'idempotency_key': f'gota-rival-0916-{version[:8]}-{rival}-{color}',
                'target': plan['target'], 'game_config_overrides': plan['config'], 'num_episodes': 40,
                'roster': [{'slot': s, 'player': {'policy_ref': v}} for s, v in enumerate(roster)],
                'notes': f'User-named rival probe:40games on {color}; five candidate heroes versus five {label} heroes. Other color has separate40game cohort. Not league-contribution A/B.'}
            yield out, body


def harvest(folder):
    plan = read(folder / 'plan.json')
    request = read(folder / 'batch/created.json')['id']
    def collect(ep):
        with client() as c:
            fetch(c, ep, folder / 'artifacts', plan['policy_version'], allow_repeated_subject=True)
    with client() as c, ThreadPoolExecutor(4) as pool:
        while True:
            entries = episodes(c, request)
            write(folder / 'batch/episodes.json', entries)
            done = [e for e in entries if e['status'] in TERMINAL]
            list(pool.map(collect, done))
            print(f'Collected {len(done)}/40', flush=True)
            if len(done) == 40:
                write(folder / 'collection.json', {'episodes': 40, 'request_count': 1})
                return
            time.sleep(15)


def compare(study):
    root = study / 'rival-matchups'
    plan = read(root / 'plan.json')
    seen, results = set(), {}
    for rival in RIVALS:
        rows = []
        for color in ['red', 'blue']:
            d = root / rival / color
            arm = read(d / 'plan.json')
            assert read(d / 'collection.json')['episodes'] == 40
            binary = d / 'audit'
            sha = digest(binary.read_bytes())
            folders = sorted(p.parent for p in (d / 'artifacts').glob('*/.done'))
            assert len(folders) == 40
            for f in folders:
                audit(f, binary, sha)
                ep, result, proof = [read(f / n) for n in ['episode.json', 'results.json', 'audit.json']]
                cfg = {k:v for k,v in ep['game_config'].items() if k not in {'seed','players','tokens'}}
                if (ep['policy_version_ids'] != arm['roster'] or cfg != plan['config'] or ep['coworld_version'] != plan['game_version'] or
                        ep['coworld_id'] != plan['target']['coworld_id'] or result['seed'] in seen):
                    raise ValueError('Rival roster/source/config/seed mismatch')
                seen.add(result['seed'])
                if [h['total_xp'] for h in proof['heroes']] != result['total_xp']:
                    raise ValueError('Rival XP mismatch')
                own = {result['scores'][s] for s in arm['own_slots']}
                other = {result['scores'][s] for s in range(10) if s not in arm['own_slots']}
                if len(own) != 1 or len(other) != 1 or not (own|other) <= {0,1} or sum(own|other)>1:
                    raise ValueError('Invalid team score')
                win, loss = next(iter(own)), next(iter(other))
                if win + loss > 1:
                    raise ValueError('Both teams cannot win')
                rows.append({'episode': ep['id'], 'seed': result['seed'], 'color': color, 'win': win, 'loss': loss,
                    'draw': int(not win and not loss), 'gear_heroes': sum(proof['heroes'][s]['first_gear_tick'] >= 0 for s in arm['own_slots']),
                    'replay_sha256': proof['replay_sha256']})
        wins, losses = sum(r['win'] for r in rows), sum(r['loss'] for r in rows)
        decisive = wins + losses
        p = sum(comb(decisive, k) for k in range(wins, decisive+1)) / 2**decisive if decisive else 1
        results[rival] = {'label': RIVALS[rival][0], 'games': 80, 'wins': wins, 'losses': losses,
            'draws': sum(r['draw'] for r in rows), 'one_sided_binomial_p': p, 'beaten': wins >= 44 and p < .025,
            'colors': {c: {k:sum(r[k] for r in rows if r['color']==c) for k in ['win','loss','draw']} for c in ['red','blue']}, 'rows': rows}
    if study.name == 'win-first-study':
        for result in results.values():
            result['beaten'] = all(c['win'] > 20 for c in result['colors'].values())
            result['p_value_interpretation'] = 'Arithmetic only; independent tactical diversity is not established by seeded repetitions.'
    write(root / 'result.json', {'policy_version': plan['policy_version'], 'games': 160, 'rivals': results,
        'both_beaten': all(a['beaten'] for a in results.values()), 'scope': plan['interpretation']})
    print({k:{n:v for n,v in a.items() if n!='rows'} for k,a in results.items()}, flush=True)


def run(study):
    jobs = []
    for folder, body in list(prepare(study)):
        with client() as c:
            request = create(c, body, folder / 'batch')
            print(str(folder.relative_to(study)), request, flush=True)
            for command, log_name in [([str(HERE/'rival_matchups.py'),str(folder),'harvest'],'harvest.log'),
                                       ([str(HERE/'watch_hosted_audit.py'),str(folder),'--workers','2'],'audit.log')]:
                log = (folder / log_name).open('a')
                p = subprocess.Popen([sys.executable,*command],stdout=log,stderr=log)
                jobs.append((p,log,folder,log_name))
            while True:
                entries = episodes(c, request)
                counts = dict(Counter(e['status'] for e in entries))
                write(folder / 'server-progress.json', {'request':request,'statuses':counts,'checked_at':datetime.now(timezone.utc).isoformat()})
                if any(e['status'] in {'failed','cancelled','error'} for e in entries):
                    raise ValueError('Preserve and recover the failed rival episode')
                if counts == {'completed':40}:
                    break
                time.sleep(15)
    failures = []
    for p,log,folder,name in jobs:
        code = p.wait();log.close()
        if code: failures.append(str(folder / name))
    if failures: raise ValueError(f'Recover failed collectors: {failures}')
    compare(study)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('command',choices=['run','harvest','compare'])
    args = parser.parse_args()
    {'run':run,'harvest':harvest,'compare':compare}[args.command](args.directory.resolve())
