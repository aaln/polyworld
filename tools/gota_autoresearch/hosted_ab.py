"""Durable, idempotent hosted A/B: candidate (and optional control) vs one pinned rival, fixed seats per colour.

usage:
  hosted_ab.py STUDY_DIR plan   PLAN_IN.json          freeze plan.json (refuses to change a frozen plan)
  hosted_ab.py STUDY_DIR upload                       inert upload of the candidate source (tagged unvalidated)
  hosted_ab.py STUDY_DIR create [--post]             write bodies + live-schema dry-run; POST only with --post
  hosted_ab.py STUDY_DIR harvest [--watch]           fetch episodes, tally W/L/D/INVALID per arm/colour

Every request body is frozen under STUDY_DIR/requests/<arm>-<colour>/request.json with a deterministic
idempotency key derived from the frozen plan. Budget is journaled in .gota/xp-ledger.json before any POST:
per-cycle <= 400, per UTC day <= 1,600, active requests <= 3 (account-wide, read live). Nothing here changes
league memberships or tags a version as validated.
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / '.gota'
sys.path.insert(0, str(Path(json.loads((ROOT/'config.json').read_text())['tooling'])))
os.environ.setdefault('GOTA_EVAL_HELPER', str(REPO/'tools/gota_autoresearch/portable/eval_request.py'))
from hosted_wave import client, get, helper  # noqa: E402

sha = lambda b: hashlib.sha256(b).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat(timespec='seconds')
read = lambda p: json.loads(Path(p).read_text())


def write(p, v):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(v, indent=1, sort_keys=True))


def freeze(path, value):
    if path.exists():
        if read(path) != value:
            raise ValueError(f'Refusing to change frozen {path}')
        return read(path)
    write(path, value); return value


def plan_cmd(study, args):
    p = read(args.plan_in)
    src = Path(p['candidate_source'])
    p['candidate_sha256'] = sha(src.read_bytes())
    for k in ('rival_version', 'coworld_id', 'episodes_per_color', 'arms', 'decision_rule'):
        assert k in p, k
    p['frozen_at'] = p.get('frozen_at') or now()
    freeze(study/'plan.json', p); print(json.dumps(p, indent=1))


def upload_cmd(study, args):
    p = read(study/'plan.json'); src = Path(p['candidate_source']).read_bytes()
    assert sha(src) == p['candidate_sha256']
    metadata = {'name': p['candidate_name'], 'content_hash': sha(src), 'size_bytes': len(src),
                'player_id': p['upload_player_id'], 'attributes': {},
                'tags': {'game': 'gods_of_the_arena', 'game_version': p['game_version'],
                         'semantic_ir_sha256': p['candidate_ir_sha256'], 'parent_source_sha256': p['parent_sha256'],
                         'hypothesis': p['hypothesis'],
                         'validation': 'Local gates only (no regression vs Richard v135, 0 invalid); hosted unvalidated; inert upload, no league selection'}}
    freeze(study/'upload-request.json', metadata)
    receipt = study/'uploaded-version.json'
    import httpx
    with client() as c:
        if not receipt.exists():
            r = c.post('/stats/policies/files/upload', json=metadata)
            if r.status_code == 409:
                r = c.post('/stats/policies/files/complete', json=metadata); r.raise_for_status(); version = r.json()
            else:
                r.raise_for_status(); payload = r.json(); version = payload.get('existing_policy_version')
                if version is None:
                    put = httpx.put(payload['upload_url'], content=src, headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                    put.raise_for_status()
                    r = c.post('/stats/policies/files/complete', json=metadata); r.raise_for_status(); version = r.json()
            write(receipt, {k: v for k, v in version.items() if 'url' not in k})
        v = read(receipt)
        remote = get(c, '/stats/policy-versions/' + v['id'])
        assert remote.get('content_hash', sha(src)) == sha(src), 'uploaded content hash mismatch'
        print(json.dumps({'candidate_version': v['id'], 'name': remote.get('name'), 'player_id': remote.get('player_id')}))


def bodies(study):
    p = read(study/'plan.json')
    cand = read(study/'uploaded-version.json')['id'] if (study/'uploaded-version.json').exists() else None
    out = {}
    for arm, ver in p['arms'].items():
        ver = cand if ver == 'CANDIDATE' else ver
        if ver is None:
            raise ValueError('upload the candidate first')
        for color in p.get('colors', ('red', 'blue')):
            own = range(5) if color == 'red' else range(5, 10)
            roster = [ver if s in own else p['rival_version'] for s in range(10)]
            key = 'gota-ab-' + sha(json.dumps([p['frozen_at'], arm, color, roster, p['episodes_per_color'], p['coworld_id']]).encode())[:20]
            out[f'{arm}-{color}'] = {
                'idempotency_key': key, 'target': {'coworld_id': p['coworld_id'], 'variant_id': 'competition'},
                'game_config_overrides': p.get('config', {}), 'num_episodes': p['episodes_per_color'],
                'roster': [{'slot': s, 'player': {'policy_ref': r}} for s, r in enumerate(roster)],
                'notes': f"{p['study_id']} {arm} {color}: fixed seats, {p['episodes_per_color']} platform-seeded episodes vs {p['rival_label']}. {p['hypothesis']}. Inert experiment; no promotion from this request."}
    return p, out


def ledger_reserve(p, total):
    led = read(ROOT/'xp-ledger.json'); day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    d = led['days'].setdefault(day, {'purchased_by_this_host': 0, 'requests': []})
    if d['purchased_by_this_host'] + total > led['limits']['per_utc_day']:
        raise ValueError('UTC-day budget exceeded')
    if total > led['limits']['per_cycle']:
        raise ValueError('per-cycle budget exceeded')
    return led


def create_cmd(study, args):
    p, bs = bodies(study); total = sum(b['num_episodes'] for b in bs.values())
    led = ledger_reserve(p, total)
    with client() as c:
        active = {st: len(get(c, f'/v2/experience-requests?mine=true&event=status&status={st}&limit=30').get('entries', []))
                  for st in ('pending', 'submitted', 'running')}
        slots = led['limits']['max_active'] - sum(active.values())
        if slots <= 0:
            raise ValueError(f'active request cap: {active}')
        for name, body in bs.items():
            folder = study/'requests'/name
            freeze(folder/'request.json', body)
            issues = helper().validate_body(c, body)
            write(folder/'dry-run.json', {'checked_at': now(), 'valid_live_schema': not issues, 'issues': issues, 'body_sha256': sha(json.dumps(body, sort_keys=True).encode())})
            if issues:
                raise ValueError(issues)
            print(name, body['idempotency_key'], 'dry-run OK', flush=True)
        if not args.post:
            print('dry-run only; no POST'); return
        day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        for name, body in bs.items():
            folder = study/'requests'/name; receipt = folder/'created.json'
            if receipt.exists():
                print(name, 'already created', read(receipt)['id']); continue
            if slots <= 0:
                print(name, 'deferred: active-request cap; rerun create --post after a request completes'); continue
            slots -= 1
            entry = {'study': p['study_id'], 'arm': name, 'idempotency_key': body['idempotency_key'], 'episodes': body['num_episodes'], 'reserved_at': now(), 'status': 'reserved'}
            led['days'][day]['requests'].append(entry); write(ROOT/'xp-ledger.json', led)   # journal before POST
            r = c.post('/v2/experience-requests', json=body); r.raise_for_status(); write(receipt, r.json())
            entry.update(status='created', request_id=r.json()['id'], created_at=now())
            led['days'][day]['purchased_by_this_host'] += body['num_episodes']
            led['episodes_purchased_by_this_host'] = led.get('episodes_purchased_by_this_host', 0) + body['num_episodes']
            led['requests_created_by_this_host'].append(r.json()['id']); write(ROOT/'xp-ledger.json', led)
            print(name, 'created', r.json()['id'], flush=True)


def harvest_cmd(study, args):
    import time
    from hosted_wave import TERMINAL, episodes
    p, bs = bodies(study)
    while True:
        summary = {}; done = True
        with client() as c:
            for name, body in bs.items():
                receipt = study/'requests'/name/'created.json'
                if not receipt.exists():
                    continue
                xreq = read(receipt)['id']; rows = episodes(c, xreq); write(study/'requests'/name/'episodes.json', rows)
                own = body['roster'][0]['player']['policy_ref'] if name.endswith('red') else body['roster'][5]['player']['policy_ref']
                t = {'W': 0, 'L': 0, 'D': 0, 'INVALID': 0, 'pending': 0}
                for ep in rows:
                    if ep['status'] not in TERMINAL:
                        t['pending'] += 1; done = False; continue
                    if ep['status'] != 'completed' or ep.get('error'):
                        t['INVALID'] += 1; continue
                    if ep['coworld_id'] != p['coworld_id'] or sorted(ep['policy_version_ids']) != sorted(r['player']['policy_ref'] for r in body['roster']):
                        raise ValueError(f'frozen roster/game changed in {ep["id"]}')
                    sc = {s['policy_version_id']: s['score'] for s in ep['scores']}
                    ours = sc.get(own, 0); theirs = sum(v for k, v in sc.items() if k != own)
                    t['W' if ours > theirs else 'L' if ours < theirs else 'D'] += 1
                summary[name] = {'request': xreq, **t}
        write(study/'summary.json', {'checked_at': now(), 'arms': summary})
        print(json.dumps(summary, indent=1), flush=True)
        if done or not args.watch:
            return
        time.sleep(30)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('study'); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('plan'); s.add_argument('plan_in')
    sub.add_parser('upload')
    s = sub.add_parser('create'); s.add_argument('--post', action='store_true')
    s = sub.add_parser('harvest'); s.add_argument('--watch', action='store_true')
    a = ap.parse_args(); study = Path(a.study); study.mkdir(parents=True, exist_ok=True)
    {'plan': plan_cmd, 'upload': upload_cmd, 'create': create_cmd, 'harvest': harvest_cmd}[a.cmd](study, a)


if __name__ == '__main__':
    main()
