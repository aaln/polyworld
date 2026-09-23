"""Replay59 full mandatory-artifact audit; missing ancillary text logs retained explicitly."""
import gzip,json,subprocess,httpx
h=STUDY=VERSION=None
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
    for kind, name in [('results', 'results.json'), ('replay', 'replay.bin'),
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
    # Text logs are ancillary: preserve a missing-log receipt without fabricating
    # a file. Replay, spec, results and all ten player exits remain mandatory.
    if not (out/'game.log').exists() and not (out/'logs-unavailable.json').exists():
        with httpx.Client(base_url=c.base_url,headers=c.headers,timeout=20,follow_redirects=True) as logs_client:
            try:
                response=logs_client.get('/v2/episode-requests/'+ep['id']+'/artifacts/logs')
                if response.status_code==200:(out/'game.log').write_bytes(response.content)
                else:h.write(out/'logs-unavailable.json',{'status':response.status_code,'body':response.text,'checked_at':h.research.now()})
            except httpx.TransportError as error:
                h.write(out/'logs-unavailable.json',{'error':type(error).__name__,'checked_at':h.research.now()})
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
           'logs_available': (out/'game.log').exists(), 'score': actual['scores'][slot], 'scores': actual['scores'], 'class': hero['class'],
           'xp': hero['xp'], 'deaths': hero['deaths'], 'hits': hero['hits'], 'level': hero['level'],
           'inventory': hero['inventory'], 'commands': audit['commands'][slot],
           'win': int(winner == arm['side']), 'loss': int(winner == 1-arm['side']),
           'draw': int(winner == -1), 'ticks': audit['ticks'], 'seed': actual['seed'],
           'all_hashes_equal': True, 'replay_sha256': h.sha((out / 'replay.bin').read_bytes()), **command_hash}
    h.write(out / 'result.json', row)
    return row
