"""Five-arm, two-color patched-engine comparison through the shared journal."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import gzip
import json
import subprocess
import time
import httpx
import jsonschema
from environment import h, panel, ROOT, STUDY, VERSION, COMMIT

OUT = STUDY / 'hosted'


def upload(c, label):
    source = (STUDY / 'candidates' / label / 'policy.bas').read_bytes()
    out = STUDY / 'uploads' / label
    meta = {'name': 'aaron-gota-balance0922-' + label, 'content_hash': h.sha(source),
            'size_bytes': len(source), 'player_id': h.PLAYER, 'attributes': {},
            'tags': {'game': 'gods_of_the_arena', 'game_version': VERSION,
                     'engine_commit': COMMIT, 'validation': 'Native checked; hosted unvalidated; inert'}}
    h.freeze(out / 'upload-request.json', meta)
    jsonschema.validate(meta, h.read(STUDY / 'openapi.json')['components']['schemas']['PlayerFilePolicyUploadRequest'])
    path = out / 'uploaded-version.json'
    if not path.exists():
        r = c.post('/stats/policies/files/upload', json=meta)
        if r.status_code == 409:
            r = c.post('/stats/policies/files/complete', json=meta)
            r.raise_for_status()
            version = r.json()
        else:
            r.raise_for_status()
            payload = r.json()
            version = payload.get('existing_policy_version')
            if version is None:
                r = httpx.put(payload['upload_url'], content=source,
                              headers={'Content-Type': 'application/octet-stream'}, timeout=120)
                r.raise_for_status()
                r = c.post('/stats/policies/files/complete', json=meta)
                r.raise_for_status()
                version = r.json()
        h.write(path, version)
    version = h.read(path)
    assert h.get(c, '/stats/policy-versions/' + version['id'])['name'] == meta['name']
    log = ROOT / 'games/gods_of_the_arena/players/balance20260922/VERSION_LOG.md'
    text = log.read_text() if log.exists() else '# Patch-aware hero experiments\n'
    if version['id'] not in text:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(text + f"\n- {h.research.now()}: {meta['name']}:v{version['version']}, `{version['id']}`, `{meta['content_hash']}`. Team-relative controller with {label} first preference, public fallback; engine {VERSION}/{COMMIT}. Native checked; hosted unvalidated; inert upload.\n")
    return version['id'], meta['content_hash']


def collect(c, arm, folder, ep):
    out = folder / 'artifacts' / ep['id']
    if (out / 'result.json').exists():
        row = h.read(out / 'result.json')
        if 'score' in row:
            outcome = h.read(out / 'results.json')['outcome']
            winner = {'RedTeam': 0, 'BlueTeam': 1}.get(outcome, -1)
            row.update(win=int(winner == arm['side']), loss=int(winner == 1-arm['side']), draw=int(winner == -1))
        return row
    out.mkdir(parents=True, exist_ok=True)
    full = h.get(c, '/v2/episode-requests/' + ep['id'])
    h.write(out / 'episode.json', full)
    assert full['coworld_id'] == h.GAME and full['coworld_version'] == VERSION
    assert full['policy_version_ids'] == arm['roster']
    if ep['status'] != 'completed':
        row = {'episode': ep['id'], 'valid': False, 'status': ep['status']}
        h.write(out / 'result.json', row)
        return row
    for kind, name in [('results', 'results.json'), ('logs', 'game.log'), ('replay', 'replay.bin'),
                       ('player-status', 'player-status.json'), ('spec', 'spec.json')]:
        path = out / name
        if path.exists():
            continue
        r = c.get('/v2/episode-requests/' + ep['id'] + '/artifacts/' + kind)
        r.raise_for_status()
        data = r.content
        if kind == 'replay' and data.startswith(b'\x1f\x8b'):
            data = gzip.decompress(data)
        path.write_bytes(data)
    if not (out / 'audit.json').exists():
        p = subprocess.run([str(STUDY / 'bin/episode-v2'), '--replay', str(out / 'replay.bin')],
                           capture_output=True, text=True, timeout=900)
        (out / 'audit-stderr.log').write_text(p.stderr)
        assert p.returncode == 0, p.stderr[-2000:]
        h.write(out / 'audit.json', json.loads(p.stdout.splitlines()[-1]))
    audit, actual, status = [h.read(out / name) for name in ('audit.json', 'results.json', 'player-status.json')]
    assert audit['hash_mismatches'] == 0
    assert audit['ticks'] == actual['ticks']
    assert [x['xp'] for x in audit['heroes']] == actual['total_xp']
    assert [max(0, x['xp'] * 1440 - 200 * audit['ticks']) // 1440 for x in audit['heroes']] == actual['scores']
    slot = arm['own_slots'][0]
    if arm.get('source_sha256'):
        assert h.read(out / 'spec.json')['players'][slot]['content_hash'] == arm['source_sha256']
    hero = audit['heroes'][slot]
    winner = {'RedTeam': 0, 'BlueTeam': 1}.get(actual['outcome'], -1)
    assert winner == (-1 if max(audit['fort_hp']) <= 0 else audit['winner'])
    failed = [p['slot'] for p in status['players'] if p.get('exit_code') != 0]
    cmd = subprocess.check_output([str(STUDY / 'bin/command-hash'), str(out / 'replay.bin')], text=True)
    command_hash = json.loads(cmd.splitlines()[-1])
    row = {'episode': ep['id'], 'valid': not failed, 'failed_slots': failed,
           'score': actual['scores'][slot], 'scores': actual['scores'], 'class': hero['class'],
           'xp': hero['xp'], 'deaths': hero['deaths'], 'hits': hero['hits'], 'level': hero['level'],
           'inventory': hero['inventory'], 'commands': audit['commands'][slot],
           'win': int(winner == arm['side']), 'loss': int(winner == 1-arm['side']),
           'draw': int(winner == -1), 'ticks': audit['ticks'], 'seed': actual['seed'],
           'all_hashes_equal': True, 'replay_sha256': h.sha((out / 'replay.bin').read_bytes()), **command_hash}
    h.write(out / 'result.json', row)
    return row


def prepare(c):
    path = OUT / 'plan.json'
    if path.exists():
        return h.read(path)
    h.live(c)
    assert h.read(STUDY / 'fixtures.json')['passed']
    assert h.read(STUDY / 'roster-preflight-pooled.json')['passed']
    assert h.read(STUDY / 'calibration-hosted-clean.json')['valid']
    assert h.read(STUDY / 'native-admission.json')['passed']
    versions = {'control': (h.INCUMBENT, 'b82c379953831b719776ba4faf3ab21a5ac2d1d383ed7f93c5f70df26fc81098')}
    versions.update({name: upload(c, name) for name in ('ranger', 'crossbow', 'warlock', 'arcanist')})
    members = h.read(STUDY / 'roster.json')
    cfg = {k: v for k, v in h.read(STUDY / 'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed', 'players', 'tokens')}
    arms = []
    for label, (version, source_hash) in versions.items():
        for side in (0, 1):
            subject = side * 5
            pool = iter(m['policy_version']['id'] for m in members)
            roster = [version if i == subject else next(pool) for i in range(10)]
            background = h.sha(json.dumps([None if i == subject else v for i, v in enumerate(roster)]).encode())
            arm = {'name': label, 'side': side, 'version': version, 'source_sha256': source_hash,
                   'own_slots': [subject], 'roster': roster, 'background': background, 'games': 40}
            body = {'idempotency_key': 'gota-balance0922-' + label + '-' + str(side) + '-' + source_hash[:10] + '-' + background[:8],
                    'target': {'coworld_id': h.GAME, 'variant_id': 'competition'}, 'game_config_overrides': cfg,
                    'num_episodes': 40, 'roster': [{'slot': i, 'player': {'policy_ref': v}} for i, v in enumerate(roster)],
                    'notes': 'Patched 2026.9.22.2 hero-preference A/B; exact mixed roster, one first-pick subject, both colors. All VMs/replay hashes/integer XP scores/source specs audited. Full prospective rule in frozen study; no automatic league selection.'}
            folder = OUT / label / str(side)
            h.freeze(folder / 'arm.json', arm)
            h.freeze(folder / 'request.json', body)
            h.create(c, body, folder / 'batch', dry_run=True)
            arms.append(arm)
    plan = {'engine_commit': COMMIT, 'game_version': VERSION, 'cycle': h.CYCLE, 'games': 400, 'arms': arms,
            'rule': 'All compared games clean; >=95% control score each color and strict >=10% aggregate improvement. Choose highest aggregate qualifying arm. Report all arms, correlated streams and realized draft. First-pick roster evidence only.'}
    h.freeze(path, plan)
    return plan


def run(plan):
    with h.research.lock(STUDY / 'hosted.lock', blocking=False), h.client() as c:
        for arm_index, arm in enumerate(plan['arms']):
            folder = OUT / arm['name'] / str(arm['side'])
            if (folder / 'result.json').exists():
                continue
            receipt = folder / 'batch/created.json'
            ident = h.read(receipt)['id'] if receipt.exists() else panel.reserve(c, h.read(folder / 'request.json'), folder / 'batch')
            print(json.dumps({'name': arm['name'], 'side': arm['side'], 'request': ident}), flush=True)
            while True:
                eps = h.episodes(c, ident)
                h.write(folder / 'episodes.json', eps)
                done = [ep for ep in eps if ep['status'] in ('completed', 'failed', 'cancelled', 'error')]
                # Drain hosted play before the next request; local replay audits
                # can overlap the next arm without competing for hosted slots.
                if len(done) == arm['games'] and arm_index + 1 < len(plan['arms']):
                    following = plan['arms'][arm_index + 1]
                    next_folder = OUT / following['name'] / str(following['side'])
                    if not (next_folder / 'batch/created.json').exists():
                        next_id = panel.reserve(c, h.read(next_folder / 'request.json'), next_folder / 'batch')
                        print(json.dumps({'queued_after_drain': following['name'], 'side': following['side'], 'request': next_id}), flush=True)
                with ThreadPoolExecutor(8) as pool:
                    rows = list(pool.map(lambda ep: collect(c, arm, folder, ep), done))
                h.write(folder / 'progress.json', {'audited': len(rows), 'total': len(eps), 'rows': rows})
                if len(rows) == 40:
                    break
                print(json.dumps({'name': arm['name'], 'side': arm['side'], 'audited': len(rows)}), flush=True)
                time.sleep(10)
            cell = {'name': arm['name'], 'side': arm['side'], 'games': len(rows),
                    'invalid': sum(not r['valid'] for r in rows),
                    'score': sum(r.get('score', 0) for r in rows) / len(rows),
                    'xp': sum(r.get('xp', 0) for r in rows) / len(rows),
                    'deaths': sum(r.get('deaths', 0) for r in rows) / len(rows),
                    'picks': dict(Counter(r.get('class') for r in rows)),
                    'distinct_streams': len({r.get('canonical_commands_sha1') for r in rows}), 'rows': rows}
            h.write(folder / 'result.json', cell)
            print(json.dumps({k: v for k, v in cell.items() if k != 'rows'}), flush=True)
        cells = [h.read(OUT / a['name'] / str(a['side']) / 'result.json') for a in plan['arms']]
        controls = cells[:2]
        comparisons = []
        for name in ('ranger', 'crossbow', 'warlock', 'arcanist'):
            selected = [c for c in cells if c['name'] == name]
            score, reference = sum(c['score'] for c in selected), sum(c['score'] for c in controls)
            passed = all(c['invalid'] == 0 for c in selected + controls) and all(c['score'] >= .95 * b['score'] for c, b in zip(selected, controls)) and score > reference and score >= 1.10 * reference
            comparisons.append({'name': name, 'passed': passed, 'score': score / 2, 'control_score': reference / 2})
        eligible = [c for c in comparisons if c['passed']]
        verdict = {'complete': True, 'comparisons': comparisons,
                   'selected': max(eligible, key=lambda c: c['score'])['name'] if eligible else 'control', 'cells': cells}
        h.write(OUT / 'result.json', verdict)
        print(json.dumps({k: v for k, v in verdict.items() if k != 'cells'}), flush=True)


if __name__ == '__main__':
    with h.client() as client:
        plan = prepare(client)
    run(plan)
