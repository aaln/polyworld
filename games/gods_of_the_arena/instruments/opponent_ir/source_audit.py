"""Reconstruct pinned Richard v135 source on every original target replay.

This source-reveal evidence is deliberately separate from the frozen,
observation-only model and its held-out prediction score.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'docs/opponents/richard-v135/source-audit-20260920'
STUDY = ROOT / 'tmp/gota-ir/opponent-richard-v135-20260920'
RUN = ROOT / 'tmp/gota-ir/richard-v135-source-audit-20260920'
SOURCE_SHA = 'f48bb0057aeaf2ff939035324340183e34f8f9544e03226edfe62e78faad5a30'
VERSION = '7c370daf-3c5f-42f8-870b-54b79c495a44'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(row):
    folder = STUDY / 'artifacts' / row['id']
    episode = read(folder / 'episode.json')
    result = read(folder / 'results.json')
    slots = [p['position'] for p in episode['participants'] if p['policy_version_id'] == VERSION]
    assert len(slots) == 5 and episode['coworld_version'] == '2026.9.16.5'
    source, binary, tape = OUT / 'v135.bas', RUN / 'source-probe', folder / 'replay.bin'
    identity = {'episode': row['id'], 'split': row['split'], 'source_sha256': sha(source),
                'probe_sha256': sha(binary), 'replay_sha256': sha(tape)}
    assert identity['source_sha256'] == SOURCE_SHA
    receipt = RUN / 'episodes' / (row['id'] + '.json')
    if receipt.exists():
        audit = read(receipt)
        assert all(audit[k] == v for k, v in identity.items())
        return audit
    process = subprocess.run([str(binary), '--replay', str(tape)],
        env=dict(os.environ, AUDIT_POLICY=str(source), AUDIT_SLOTS=','.join(map(str, slots))),
        text=True, capture_output=True, timeout=900)
    if process.returncode:
        raise ValueError(f'{row["id"]}: {process.stderr} {process.stdout[-3000:]}')
    audit = json.loads(process.stdout.splitlines()[-1]) | identity
    assert audit['all_state_hashes_equal'] and audit['all_actions_consumed']
    assert audit['ticks'] == result['ticks']
    write(receipt, audit)
    print(row['id'], audit['ticks'], audit['commands_matched'], flush=True)
    return audit


def main():
    plan = read(STUDY / 'study-plan.json')
    rows = [r for r in plan['episodes'] if r['split'] != 'population']
    assert len(rows) == 20
    with ThreadPoolExecutor(max_workers=3) as pool:
        audits = list(pool.map(one, rows))
    counts = Counter()
    for a in audits:
        counts.update(a['counts'])
    write(OUT / 'runtime-audit.ir.json', {
        'schema': 'gota-source-reveal-replay-audit/1', 'source_sha256': SOURCE_SHA,
        'game_version': '2026.9.16.5', 'game_commit': 'f2ab9598d8f8001b6beae3e66404e341770c803f',
        'episodes': len(audits), 'ticks': sum(a['ticks'] for a in audits),
        'commands_matched': sum(a['commands_matched'] for a in audits),
        'decisions': sum(a['decisions'] for a in audits),
        'all_complete_state_sequences_equal': True, 'all_five_opponent_vms_reconstructed': True,
        'max_instructions': max(a['max_instructions'] for a in audits),
        'max_work': max(a['max_work'] for a in audits), 'counts': dict(counts),
        'interpretation': 'Retrospective source-reveal audit, not new held-out evidence. Guard counts overlap; final actions can override earlier requests.',
        'probe_source_sha256': sha(Path(__file__).with_name('source_audit_probe.nim')),
        'rows': audits})
    print(json.dumps({'episodes': len(audits), 'counts': dict(counts)}, indent=2), flush=True)


if __name__ == '__main__':
    main()
