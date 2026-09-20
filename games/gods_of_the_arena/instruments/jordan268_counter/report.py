"""Summarize complete audited arms; do not score pending requests."""
from collections import Counter
import json

from campaign import STUDY, digest, read, write


def summarize():
    arms = []
    evidence = []
    for path in sorted((STUDY / 'hosted').glob('*/*/*/result.json')):
        result = read(path)
        plan = read(path.parent / 'plan.json')
        signatures = Counter()
        for row in result['rows']:
            folder = path.parent / 'artifacts' / row['episode']
            audit, reported = read(folder / 'audit.json'), read(folder / 'results.json')
            assert audit['hash_mismatches'] == 0
            assert audit['recorded_ticks'] == audit['ticks'] == reported['ticks']
            assert audit['recorded_actions'] == audit['actions_consumed']
            assert [h['total_xp'] for h in audit['heroes']] == reported['total_xp']
            assert [h['score'] for h in audit['heroes']] == reported['scores']
            assert (folder / 'vm-validity.json').exists()
            # Signature includes sampled frames and full event/hero summaries.
            # Distinct signatures are not a claim of independent trajectories.
            signature = digest({k: audit[k] for k in
                                ('frames', 'events', 'heroes', 'recorded_actions', 'ticks')})
            signatures[signature] += 1
            evidence.append(row | {'candidate': result['name'], 'color': result['color'],
                                   'stage': plan['stage'], 'request': result['request'],
                                   'policy_version': plan['policy_version'],
                                   'opponent_version': plan['rival_version'],
                                   'audit_signature': signature,
                                   'checks': {'all_state_hashes_equal': True,
                                              'all_actions_consumed': True,
                                              'xp_and_scores_equal': True,
                                              'vm_validity': read(folder / 'vm-validity.json')},
                                   'sha256': {name: digest((folder / name).read_bytes()) for name in
                                              ('episode.json', 'results.json', 'audit.json', 'replay.bin', 'vm-validity.json')}})
        arm = {k: v for k, v in result.items() if k != 'rows'}
        arm.update(stage=plan['stage'], own_slots=plan['own_slots'],
                   policy_version=plan['policy_version'],
                   distinct_audit_signatures=len(signatures),
                   signature_multiplicities=sorted(signatures.values(), reverse=True),
                   replay_ticks=sum(r['ticks'] for r in result['rows']),
                   result_sha256=digest(path.read_bytes()), result_path=str(path))
        arms.append(arm)
    requests = read(STUDY / 'requests.json')
    completed = {a['request'] for a in arms}
    pending = [r for r in requests if r['request'] not in completed]
    output = {'opponent_version': '207ffaf9-0d1e-4d92-a15d-4352f1bddec2',
              'game_version': '2026.9.16.5', 'arms': arms, 'pending': pending,
              'scope': 'Fixed five-versus-five lineups, both colors. Generated seeds are '
              'not matched A/B; repeated trajectories limit independence. Directional '
              'evidence only; no field or league promotion claim.',
              'audited_episodes': sum(a['n'] for a in arms),
              'audited_ticks': sum(a['replay_ticks'] for a in arms)}
    write(STUDY / 'evidence-index.json', evidence)
    output['evidence_index_sha256'] = digest((STUDY / 'evidence-index.json').read_bytes())
    write(STUDY / 'campaign-summary.json', output)
    print(json.dumps(output, indent=2))
    return output


if __name__ == '__main__':
    summarize()
