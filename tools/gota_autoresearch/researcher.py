#!/usr/bin/env python3
"""Persistent, single-writer GotA research and evidence-gated policy lineage.

Only `accept` advances the research incumbent. It never changes a league champion.
The model supplies hypotheses; replay audits and frozen gates decide acceptance.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import uuid

DEFAULT = Path('/Users/aaln/experiments/softmax/gota-autoresearch')


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    with temp.open('w') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def require(condition, message):
    if not condition:
        raise ValueError(message)


@contextmanager
def lock(path, blocking=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        yield f


def config(root):
    c = read(root / 'config.json')
    override = c.get('daily_episode_limit_override')
    if override and now()[:10] != override['utc_day']:
        c['daily_episode_limit'] = override['normal_limit']
    if c['tooling'] not in sys.path:
        sys.path.insert(0, c['tooling'])
    return c


def verify_pair(folder):
    import policy_ir as ir
    p = ir.read(folder / 'policy.ir.json')
    source = (folder / 'policy.bas').read_text()
    require(ir.compile_policy(p) == source, 'IR does not generate exact tested BASIC')
    require(ir.extract(source, p) == p, 'IR / BASIC reverse extraction differs')
    return {'ir': sha(folder / 'policy.ir.json'), 'source': sha(folder / 'policy.bas'),
            'executable': ir.digest(ir.executable(p)), 'semantic_digest': ir.digest(p)}


def verify_snapshot(folder):
    m = read(folder / 'snapshot.json')
    require(all(sha(folder / p) == digest for p, digest in m['files'].items()),
            'An immutable snapshot was changed')
    return m


def verify_remote_source(api, metadata, version_id):
    """Some stats responses redact file hashes; metadata lookup still proves identity."""
    response = api.get('/stats/policy-versions/' + version_id)
    response.raise_for_status()
    remote = response.json()
    if remote.get('player_file_content_hash') is not None:
        require(remote['player_file_content_hash'] == metadata['content_hash'], 'Remote file hash mismatch')
        method = 'file_hash'
    else:
        # This endpoint returns an existing version for matching immutable bytes and
        # metadata. Never upload or complete a new version here; a miss is an error.
        response = api.post('/stats/policies/files/upload', json=metadata)
        response.raise_for_status()
        data = response.json()
        require((data.get('existing_policy_version') or {}).get('id') == version_id
                and not data.get('upload_url'), 'Remote metadata did not resolve to the tested version')
        method = 'existing_version_for_exact_upload_metadata'
    return {'version_id': version_id, 'source_sha256': metadata['content_hash'], 'method': method}


def snapshot(root, source, number, parent, hosted, evidence):
    c = config(root)
    hashes = verify_pair(source)
    name = f'{number:04d}-{hashes["source"][:12]}'
    dest = root / 'snapshots' / name
    if dest.exists():
        m = verify_snapshot(dest)
        require(m['parent'] == parent and m['hashes'] == hashes, 'Snapshot collision')
        return name
    staging = root / 'snapshots' / ('.staging-' + uuid.uuid4().hex)
    staging.mkdir(parents=True)
    for f in source.iterdir():
        if f.is_file() and f.suffix in ('.json', '.bas', '.md'):
            shutil.copy2(f, staging / f.name)
    # Preserve every versioned binding dependency, not just the four files in old manifests.
    with tarfile.open(staging / 'compiler.tar.gz', 'w:gz') as archive:
        for f in sorted(Path(c['tooling']).iterdir()):
            if f.is_file() and f.suffix in ('.py', '.nim'):
                archive.add(f, arcname=f.name)
    write(staging / 'evidence.json', evidence)
    files = {str(f.relative_to(staging)): sha(f) for f in staging.rglob('*') if f.is_file()}
    write(staging / 'snapshot.json', {'id': name, 'created_at': now(), 'generation': number,
          'parent': parent, 'hosted': hosted, 'hashes': hashes, 'game_version': c['game_version'],
          'engine_commit': c['engine_commit'], 'files': files})
    os.replace(staging, dest)
    for f in dest.rglob('*'):
        f.chmod(0o555 if f.is_dir() else 0o444)
    dest.chmod(0o555)
    return name


def fork(root, label):
    config(root)
    import policy_ir as ir
    with lock(root / 'state.lock'):
        s = read(root / 'state.json')
        parent = root / 'snapshots' / s['accepted']
        m = verify_snapshot(parent)
        ident = 'fork_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
        dest = root / 'forks' / ident
        p = ir.read(parent / 'policy.ir.json')
        p['id'] = ident
        p['update'].update(revision=p['update']['revision'] + 1, parent=ir.digest(ir.read(parent / 'policy.ir.json')),
                           change='Research fork: ' + label)
        ir.bundle(p, dest / 'working')
        write(dest / 'lineage.json', {'id': ident, 'parent_snapshot': s['accepted'],
              'parent_source_sha256': m['hashes']['source'], 'created_at': now(), 'hypothesis': label})
        s['working_fork'] = str(dest)
        write(root / 'state.json', s)
    return dest


def freeze(root, source):
    """Freeze a prospective holdout matrix after upload, before any holdout request."""
    c = config(root)
    plan = read(source)
    s = read(root / 'state.json')
    require(plan['parent_snapshot'] == s['accepted'], 'Stale parent')
    parent = verify_snapshot(root / 'snapshots' / s['accepted'])
    candidate = Path(plan['candidate_dir']).resolve()
    hashes = verify_pair(candidate)
    require(hashes['executable'] != parent['hashes']['executable'], 'No executable change')
    lineage = read(Path(plan['fork']) / 'lineage.json')
    require(lineage['parent_snapshot'] == s['accepted'], 'Fork lineage mismatch')
    receipt, meta = read(plan['upload_receipt']), read(plan['upload_metadata'])
    require(meta['content_hash'] == hashes['source'], 'Upload is not the frozen candidate')
    from hosted_wave import client
    with client() as api:
        remote = verify_remote_source(api, meta, receipt['id'])
    require(receipt['id'] != parent['hosted']['id'], 'Candidate is the incumbent')
    arms = plan['arms']
    require(len({a['key'] for a in arms}) == len(arms), 'Duplicate arm keys')
    require(len({str(Path(a['directory']).resolve()) for a in arms}) == len(arms), 'Duplicate arm directories')
    known = {r['id'] for r in c['field_opponents']}
    archive = {r['id'] for r in c['historical_opponents']}
    archive.update(verify_snapshot(p)['hosted']['id'] for p in (root / 'snapshots').iterdir()
                   if p.is_dir() and not p.name.startswith('.'))
    for a in arms:
        d = Path(a['directory'])
        require(not (d / 'batch/created.json').exists() and not (d / 'artifacts').exists(), 'Holdout already started')
        require(a['kind'] in ('self', 'archive', 'field', 'mixed'), 'Unknown gate kind')
        require(a['role'] in ('candidate', 'parent') and a['color'] in ('red', 'blue'), 'Invalid role/color')
        slots = list(range(5)) if a['color'] == 'red' else list(range(5, 10))
        require(a['own_slots'] and set(a['own_slots']) <= set(slots), 'Subject slots cross teams')
        own = receipt['id'] if a['role'] == 'candidate' else parent['hosted']['id']
        require(len(a['roster']) == 10 and all(a['roster'][i] == own for i in a['own_slots']), 'Subject roster mismatch')
        require(all(a['roster'][i] != receipt['id'] for i in range(10) if i not in a['own_slots']), 'Candidate leaked into opponents')
        if a['kind'] != 'mixed':
            require(a['own_slots'] == slots, 'Team-controlled match must assign all five heroes')
            other = set(a['roster'][i] for i in range(10) if i not in slots)
            require(len(other) == 1, 'Expected one opposing policy')
            if a['kind'] == 'self':
                require(a['role'] == 'candidate' and other == {parent['hosted']['id']}, 'Self test must face parent')
            if a['kind'] == 'archive':
                require(other <= archive and other != {parent['hosted']['id']}, 'Not a distinct historical opponent')
            if a['kind'] == 'field':
                require(other <= known, 'Opponent not in frozen field panel; add it prospectively to config')
        else:
            require(len(a['own_slots']) == 1, 'Mixed games test one independently controlled hero')
    require({a['color'] for a in arms if a['kind'] == 'self'} == {'red', 'blue'}, 'Missing parent test on a side')
    for kind, count in [('field', 5), ('archive', min(2, len(archive - {parent['hosted']['id']})))]:
        groups = {a['comparison'] for a in arms if a['kind'] == kind}
        require(len(groups) >= count, 'Insufficient ' + kind + ' panel')
        for group in groups:
            subset = [a for a in arms if a['kind'] == kind and a['comparison'] == group]
            require({(a['role'], a['color']) for a in subset} == {(r, col) for r in ('candidate', 'parent') for col in ('red', 'blue')},
                    'Every panel opponent needs fresh candidate and parent on both sides')
            require(len({a['roster'][5 if a['color'] == 'red' else 0] for a in subset}) == 1, 'Panel opponent changed')
        require(len({a['roster'][5 if a['color'] == 'red' else 0] for a in arms if a['kind'] == kind}) >= count,
                'Duplicate opponent disguised as multiple comparisons')
    mixed = [a for a in arms if a['kind'] == 'mixed']
    require(len({a['comparison'] for a in mixed}) >= 5, 'Need at least five mixed-team rosters')
    for group in {a['comparison'] for a in mixed}:
        pair = [a for a in mixed if a['comparison'] == group]
        require(len(pair) == 2 and {a['role'] for a in pair} == {'candidate', 'parent'}, 'Mixed roster requires paired control')
        require(pair[0]['own_slots'] == pair[1]['own_slots'], 'Mixed subject seats differ')
        require([v if i not in pair[0]['own_slots'] else '<subject>' for i,v in enumerate(pair[0]['roster'])] ==
                [v if i not in pair[1]['own_slots'] else '<subject>' for i,v in enumerate(pair[1]['roster'])], 'Mixed teammates/opponents changed')
    require({a['color'] for a in mixed} == {'red', 'blue'}, 'Mixed tests need both colors')
    for col in ('red', 'blue'):
        require(len({a['own_slots'][0] for a in mixed if a['color'] == col}) >= 2, 'Mixed tests need multiple classes per side')
    require(plan.get('local_evidence') and Path(plan['mechanism_report']).is_file(), 'Local qualification and mechanism report required')
    local = {str(Path(p).resolve()): sha(p) for p in plan['local_evidence']}
    plan.update(frozen_at=now(), candidate_hashes=hashes, candidate_version=receipt['id'],
                remote_source_verification=remote,
                parent_version=parent['hosted']['id'], game_version=c['game_version'], engine_commit=c['engine_commit'],
                target=c['target'], game_config=c['game_config'], local_evidence_hashes=local,
                thresholds={'parent_win_rate_each_color': 0.60, 'minimum_games_per_arm': 40,
                            'field_and_archive_allowed_win_rate_drop': 0, 'mixed_games_each_role': 200,
                            'mixed_minimum_each_color_role': 80, 'mixed_allowed_drop': 0},
                limitations='Seed repeats are correlated; these are empirical acceptance gates, not independent-trial significance.')
    dest = Path(plan['fork']) / 'holdout-plan.json'
    require(not dest.exists(), 'Gate is immutable; make a new study for a new candidate')
    write(dest, plan)
    write(dest.with_name('holdout-plan.sha256.json'), {'sha256': sha(dest)})
    dest.chmod(0o444)
    return dest


def audit_arm(c, plan, arm, seen):
    from hosted_wave_audit import verify
    d = Path(arm['directory'])
    request = read(d / 'batch/request.json')
    require(request['num_episodes'] >= 40, 'Use batches of at least forty games')
    require(request['target'] == plan['target'] and request['game_config_overrides'] == plan['game_config'], 'Wrong game/config')
    expected = {i: v for i, v in enumerate(arm['roster'])}
    require({r['slot']: r['player']['policy_ref'] for r in request['roster']} == expected, 'Request roster differs from frozen plan')
    folders = sorted(p.parent for p in (d / 'artifacts').glob('*/.done'))
    require(len(folders) == request['num_episodes'], 'Incomplete batch')
    binary = Path(c['auditor'])
    binary_hash = sha(binary)
    require(binary_hash == c['auditor_sha256'], 'Auditor changed')
    rows = []
    for f in folders:
        verify(f, binary, binary_hash)
        ep, result, audit = [read(f / n) for n in ('episode.json', 'results.json', 'audit.json')]
        require(ep['id'] not in seen, 'Reused episode across holdout arms')
        seen.add(ep['id'])
        require(datetime.fromisoformat(ep['created_at'].replace('Z', '+00:00')) >=
                datetime.fromisoformat(plan['frozen_at']), 'Holdout episode predates frozen plan')
        require(ep['policy_version_ids'] == arm['roster'], 'Actual roster differs')
        require(ep['coworld_id'] == plan['target']['coworld_id'] and ep['coworld_version'] == plan['game_version'], 'Game version drift')
        require({k:v for k,v in ep['game_config'].items() if k not in ('seed', 'players', 'tokens')} == plan['game_config'], 'Effective config differs')
        if arm['kind'] == 'mixed':
            require(len({p['player_id'] for p in ep['participants']}) == 10, 'Not ten distinct players')
        require(all(audit['heroes'][s]['first_gear_tick'] >= 0 for s in arm['own_slots']), 'Equipment buying regressed')
        score = {result['scores'][s] for s in arm['own_slots']}
        require(len(score) == 1 and score <= {0, 1}, 'Unexpected outcome')
        rows.append({'episode': ep['id'], 'win': score.pop(), 'seed': result['seed'],
                     'ticks': result['ticks'], 'replay_sha256': audit['replay_sha256'],
                     'audit_sha256': sha(f / 'audit.json')})
    return {'games': len(rows), 'wins': sum(r['win'] for r in rows), 'rows': rows}


def judge(plan, results):
    """Pure decision rule; draws remain zero, red and blue can never mask each other."""
    reasons = []
    for a in plan['arms']:
        r = results[a['key']]
        if r['games'] < 40:
            reasons.append(a['key'] + ': fewer than 40 complete games')
        if a['kind'] == 'self' and r['wins'] / r['games'] < 0.60:
            reasons.append(a['key'] + ': parent win rate below 60%')
        if a['kind'] in ('field', 'archive') and a['role'] == 'candidate':
            controls = [b for b in plan['arms'] if b['kind'] == a['kind'] and b['comparison'] == a['comparison']
                        and b['color'] == a['color'] and b['role'] == 'parent']
            require(len(controls) == 1, 'Missing/ambiguous comparison control')
            b = results[controls[0]['key']]
            if r['games'] != b['games']:
                reasons.append(a['key'] + ': unequal candidate/control sample counts')
            if r['wins'] * b['games'] < b['wins'] * r['games']:
                reasons.append(a['key'] + ': field/archive win-rate regression')
    mixed = [a for a in plan['arms'] if a['kind'] == 'mixed']
    for a in mixed:
        if a['role'] == 'candidate':
            controls = [b for b in mixed if b['comparison'] == a['comparison'] and b['role'] == 'parent'
                        and b['color'] == a['color']]
            require(len(controls) == 1, 'Mixed comparison control missing or ambiguous')
            if results[a['key']]['games'] != results[controls[0]['key']]['games']:
                reasons.append(a['key'] + ': unequal mixed roster weights')
    for role in ('candidate', 'parent'):
        if sum(results[a['key']]['games'] for a in mixed if a['role'] == role) < 200:
            reasons.append(role + ': fewer than 200 mixed games')
    for col in ('red', 'blue'):
        totals = {}
        for role in ('candidate', 'parent'):
            rows = [results[a['key']] for a in mixed if a['role'] == role and a['color'] == col]
            n, wins = sum(r['games'] for r in rows), sum(r['wins'] for r in rows)
            totals[role] = (n, wins)
            if n < 80:
                reasons.append(role + '/' + col + ': fewer than 80 mixed games')
        (n, w), (bn, bw) = totals['candidate'], totals['parent']
        if w * bn < bw * n:
            reasons.append('mixed/' + col + ': regression')
    return {'passed': not reasons, 'reasons': reasons}


def accept(root, path):
    c = config(root)
    from win_hosted import live
    live()
    plan = read(path)
    require(sha(path) == read(path.with_name('holdout-plan.sha256.json'))['sha256'], 'Prospective plan changed')
    s = read(root / 'state.json')
    require(plan['parent_snapshot'] == s['accepted'], 'Incumbent advanced; evaluate against new parent')
    candidate = Path(plan['candidate_dir'])
    require(verify_pair(candidate) == plan['candidate_hashes'], 'Candidate changed after freezing')
    require(all(sha(p) == h for p,h in plan['local_evidence_hashes'].items()), 'Local evidence changed')
    require(len(Path(plan['mechanism_report']).read_text()) >= 300, 'Explain observed general gameplay mechanism and limitations')
    seen = set(plan.get('discovery_episodes', []))
    results = {a['key']: audit_arm(c, plan, a, seen) for a in plan['arms']}
    verdict = judge(plan, results)
    verdict.update(checked_at=now(), plan_sha256=sha(path), arms=results)
    result_path = path.with_name('gate-result.json')
    if result_path.exists():
        previous = read(result_path)
        require({k:v for k,v in previous.items() if k != 'checked_at'} ==
                {k:v for k,v in verdict.items() if k != 'checked_at'}, 'Completed gate evidence changed')
        verdict = previous
    else:
        write(result_path, verdict)
    require(verdict['passed'], 'Rejected: ' + '; '.join(verdict['reasons']))
    # Feedback changes the semantic claims only. Its executable must remain exactly tested.
    feedback = Path(plan['fork']) / 'accepted-feedback'
    if not feedback.exists():
        import policy_ir as ir
        p = ir.read(candidate / 'policy.ir.json')
        prior = ir.digest(p)
        evidence = {'artifact': str(path.with_name('gate-result.json')),
                    'sha256': sha(path.with_name('gate-result.json'))}
        p['belief']['claims']['B_autoresearch_validation'] = {
            'claim': 'Passed the frozen empirical self-play and generalization gates. '
                     'See complete color-split results; fixed-lineup repetitions are correlated. '
                     'No guarantee of future superiority.',
            'status': 'supported', 'evidence': [evidence]}
        p['update'].update(revision=p['update']['revision'] + 1, parent=prior,
                           change='Completed empirical acceptance; tested behavior preserved.')
        p['update']['evidence'].append(evidence)
        ir.refresh_grounding(p)
        ir.bundle(p, feedback)
    verify_pair(feedback)
    require(sha(feedback / 'policy.bas') == plan['candidate_hashes']['source'], 'Feedback changed tested executable')
    with lock(root / 'state.lock'):
        state = read(root / 'state.json')
        require(state['accepted'] == plan['parent_snapshot'], 'Concurrent advancement')
        hosted = read(plan['upload_receipt'])
        name = snapshot(root, feedback, state['generation'] + 1, state['accepted'], hosted,
                        {'plan': plan, 'result': verdict, 'mechanism_report': Path(plan['mechanism_report']).read_text()})
        state.update(accepted=name, generation=state['generation'] + 1, accepted_at=now())
        write(root / 'state.json', state)
    return {'accepted': name, 'next_fork': str(fork(root, 'Improve general play beyond accepted parent ' + name))}


def reserve(root, body, output, cycle):
    c = config(root)
    require(40 <= body['num_episodes'] <= 200, 'Batch size must be 40–200')
    require(body['target'] == c['target'], 'Wrong game')
    require(body['game_config_overrides'] == c['game_config'], 'Unapproved engine/config change')
    key = body['idempotency_key']
    with lock(root / 'budget.lock'):
        p = root / 'xp-ledger.json'
        ledger = read(p) if p.exists() else {}
        if key in ledger:
            require(ledger[key]['body_sha256'] == fingerprint(body) and ledger[key]['output'] == str(output.resolve()),
                    'Idempotency key reused for a different request')
            return ledger[key]
        day = now()[:10]
        daily = sum(v['episodes'] for v in ledger.values() if v['day'] == day)
        current = sum(v['episodes'] for v in ledger.values() if v['cycle'] == cycle)
        require(daily + body['num_episodes'] <= c['daily_episode_limit'], 'Daily XP allowance reached; resume tomorrow')
        require(current + body['num_episodes'] <= c['cycle_episode_limit'], 'Cycle XP allowance reached; checkpoint and resume next cycle')
        entry = {'day': day, 'cycle': cycle, 'episodes': body['num_episodes'], 'body_sha256': fingerprint(body),
                 'output': str(output.resolve()), 'reserved_at': now()}
        ledger[key] = entry
        write(p, ledger)
        return entry


def xp_create(root, request, output):
    config(root)
    from hosted_wave import client, create
    from win_hosted import live
    live()
    body = read(request)
    cycle = os.environ.get('GOTA_RESEARCH_CYCLE')
    require(cycle, 'XP creation must run inside the supervised research cycle')
    # Held through creation: concurrent calls cannot overrun the active-request limit.
    with lock(root / 'xp-create.lock'):
        from hosted_wave import episodes
        c = config(root)
        with client() as api:
            active = 0
            ledger = read(root / 'xp-ledger.json') if (root / 'xp-ledger.json').exists() else {}
            for entry in ledger.values():
                receipt = Path(entry['output']) / 'created.json'
                if receipt.exists():
                    records = episodes(api, read(receipt)['id'])
                    active += any(e['status'] not in ('completed', 'failed', 'cancelled', 'error') for e in records)
            if not (output / 'created.json').exists():
                require(active < c['max_parallel_xp'], 'Three XP batches already active; harvest them first')
            create(api, body, output, dry_run=True)
            reserve(root, body, output, cycle)
            return create(api, body, output)


def process_table():
    rows = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,lstart='], text=True)
    return {int(parts[0]): (int(parts[1]), parts[2]) for line in rows.splitlines()
            if len(parts := line.strip().split(None, 2)) == 3}


def terminate(proc):
    if proc.poll() is None:
        table = process_table()
        owned = {proc.pid}
        while children := {p for p,(parent,_) in table.items() if parent in owned} - owned:
            owned.update(children)
        # Tool processes may create their own sessions. Track only descendants of
        # this exact agent and their birth times so an expired cycle cannot leave
        # a second policy writer behind or signal a reused PID.
        def signal_owned(sig):
            current = process_table()
            for pid in owned:
                if pid in current and pid in table and current[pid][1] == table[pid][1]:
                    try: os.kill(pid, sig)
                    except ProcessLookupError: pass
        signal_owned(signal.SIGTERM)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            signal_owned(signal.SIGKILL)
            proc.wait()
        signal_owned(signal.SIGKILL)


def run(root, once=False):
    c = config(root)
    stopping = False

    def stop(_sig, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        with lock(root / 'runner.lock', blocking=False) as held:
            failures = 0
            while not stopping and not (root / 'PAUSED').exists():
                cycle = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6]
                dest = root / 'cycles' / cycle
                dest.mkdir(parents=True)
                prompt = (root / 'PROMPT.md').read_text() + '\n\nCycle: ' + cycle + '\nCycle directory: ' + str(dest)
                (dest / 'prompt.md').write_text(prompt)
                env = dict(os.environ, GOTA_RESEARCH_ROOT=str(root), GOTA_RESEARCH_CYCLE=cycle,
                           POLYWORLD_DEPS=c['dependencies'])
                cmd = [c['codex'], 'exec', '-c', 'approval_policy="never"', '--sandbox', 'danger-full-access',
                       '-C', c['workspace'], '--json', '-o', str(dest / 'last-message.md'), '-']
                with (dest / 'events.jsonl').open('ab', buffering=0) as log:
                    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log, stderr=log,
                                            env=env, start_new_session=True, pass_fds=(held.fileno(),))
                    proc.stdin.write(prompt.encode())
                    proc.stdin.close()
                    started = time.monotonic()
                    try:
                        while proc.poll() is None:
                            write(root / 'service.json', {'state': 'running', 'supervisor_pid': os.getpid(),
                                  'agent_pid': proc.pid, 'cycle': cycle, 'cycle_directory': str(dest),
                                  'heartbeat': now(), 'elapsed_seconds': round(time.monotonic() - started)})
                            if stopping or (root / 'PAUSED').exists() or time.monotonic() - started >= c['cycle_timeout_seconds']:
                                terminate(proc)
                                break
                            time.sleep(10)
                    finally:
                        terminate(proc)
                write(dest / 'exit.json', {'finished_at': now(), 'returncode': proc.returncode,
                      'elapsed_seconds': round(time.monotonic() - started)})
                failures = failures + 1 if proc.returncode else 0
                c = config(root)
                delay = min(3600, 300 * 2 ** min(failures - 1, 4)) if failures else c['between_cycles_seconds']
                ledger = read(root / 'xp-ledger.json') if (root / 'xp-ledger.json').exists() else {}
                if sum(v['episodes'] for v in ledger.values() if v['day'] == now()[:10]) >= c['daily_episode_limit']:
                    delay = max(delay, 10800)
                write(root / 'service.json', {'state': 'paused' if (root / 'PAUSED').exists() else 'between_cycles',
                      'heartbeat': now(), 'supervisor_pid': os.getpid(), 'last_cycle': cycle,
                      'last_exit': proc.returncode, 'next_cycle_delay_seconds': delay})
                if once:
                    break
                until = time.monotonic() + delay
                while not stopping and not (root / 'PAUSED').exists() and time.monotonic() < until:
                    time.sleep(min(10, until - time.monotonic()))
    except BlockingIOError:
        print('Existing researcher owns the lock; no overlapping agent started.', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=DEFAULT)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    sub.add_parser('pause')
    sub.add_parser('resume')
    f = sub.add_parser('fork'); f.add_argument('label')
    f = sub.add_parser('freeze'); f.add_argument('plan', type=Path)
    f = sub.add_parser('accept'); f.add_argument('plan', type=Path)
    f = sub.add_parser('xp-create'); f.add_argument('request', type=Path); f.add_argument('output', type=Path)
    f = sub.add_parser('run'); f.add_argument('--once', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.command == 'run':
        return run(root, args.once)
    if args.command == 'status':
        result = {n: read(root / (n + '.json')) for n in ('state', 'service') if (root / (n + '.json')).exists()}
        result['paused'] = (root / 'PAUSED').exists()
        table = process_table()
        result['processes_alive'] = {k: result.get('service', {}).get(k) in table
                                     for k in ('supervisor_pid', 'agent_pid')}
        if 'heartbeat' in result.get('service', {}):
            result['heartbeat_age_seconds'] = round((datetime.now(timezone.utc) -
                datetime.fromisoformat(result['service']['heartbeat'])).total_seconds())
    elif args.command == 'pause':
        (root / 'PAUSED').write_text(now() + '\n')
        result = 'Pausing; current agent receives SIGTERM within ten seconds. Existing hosted XP remains harvestable.'
    elif args.command == 'resume':
        (root / 'PAUSED').unlink(missing_ok=True)
        subprocess.run(['launchctl', 'start', 'com.aaron.gota-autoresearch'], check=True)
        result = 'Research resumed.'
    elif args.command == 'fork': result = str(fork(root, args.label))
    elif args.command == 'freeze': result = str(freeze(root, args.plan))
    elif args.command == 'accept': result = accept(root, args.plan)
    else: result = xp_create(root, args.request, args.output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
