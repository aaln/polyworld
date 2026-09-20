"""Promote an exactly evaluated coordination policy to both existing players."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import time

from economy_feedback import record
from hosted_wave import client, get
from jordan_lineup_wide import ROOT as WIDE
from policy_ir import HERE, compile_policy, digest, extract, read, write
from prepare_campaign_xp import LEAGUE
from release_deploy import AARON, champions
from release_deploy_pair import check_champions, select, verify_owned
from release_hosted import OPTIMIZER
from release_workspace import verify
from win_hosted import live


def prepare(study, name):
    verify()
    root = study / 'hosted' / name
    original = read(root / 'final-result.json')
    current = read(root / 'current-field/result.json')
    plan = read(root / 'current-field/plan.json')
    for result in (original, current):
        if not result['passed'] or not result['checks'] or not all(result['checks'].values()):
            raise ValueError('Both complete suites must pass their frozen gates')
    if original['stage'] != 'field' or set(current['arms']) != {'control', 'candidate'}:
        raise ValueError('Full ten-player comparisons required')
    if original['plan_sha256'] != digest((study / 'hosted-prospective-plan.json').read_bytes()):
        raise ValueError('Original frozen plan changed')
    if current['plan_sha256'] != digest((root / 'current-field/plan.json').read_bytes()):
        raise ValueError('Current-field frozen plan changed')
    if plan['original_result_sha256'] != digest((root / 'final-result.json').read_bytes()):
        raise ValueError('Qualification evidence changed')
    if name not in read(study / 'local/comparison.json')['qualified']:
        raise ValueError('Local qualification missing')
    if not read(study / 'activation-proof.json')['passed']:
        raise ValueError('Native activation proof missing')
    source = (study / 'local/candidates' / name / 'policy.bas').read_bytes()
    if digest(source) != plan['source_sha256']:
        raise ValueError('Evaluated source changed')
    versions = {}
    for player, folder in ((OPTIMIZER, root), (AARON, root / 'deployment-pair/aaron-upload')):
        versions[player] = read(folder / 'uploaded-version.json')
        metadata = read(folder / 'upload-request.json')
        if metadata['player_id'] != player or metadata['content_hash'] != digest(source):
            raise ValueError('Owner or source mismatch')
    ids = {p: v['id'] for p, v in versions.items()}
    if plan['candidate_versions'] != [ids[OPTIMIZER], ids[AARON]]:
        raise ValueError('Evaluated pair mismatch')
    prior_ids = read(WIDE / 'plan.json')['candidate_versions']
    if plan['control_versions'] != prior_ids:
        raise ValueError('Deployed controls mismatch')
    priors = dict(zip((OPTIMIZER, AARON), prior_ids))
    game = live()
    if (game['id'] != plan['target']['coworld_id'] or game['version'] != plan['game_version'] or
            game['manifest']['game']['runnable']['source_url'] != plan['game_source']):
        raise ValueError('Live game changed')
    out = root / 'validated-deployment'
    out.mkdir(exist_ok=True)
    note = ('User authorized promotion to both existing players when validated. This exact executable '
            'passed the frozen Richard/Jordan and other opponent gates, 200 ten-player games, '
            'and a fresh pinned current-version comparison including 200 mixed games per arm. '
            'All complete runtime/replay/equipment audits and IR round trips passed. '
            'These fixed-lineup results are directional evidence, not independent-trial significance '
            'or a guarantee of future league rank. Opponent versions are recorded in the snapshots.')
    decision = {'authorization': 'if it does well, promote it to both players in league',
                'note': note, 'versions': ids, 'rollback_versions': priors,
                'source_sha256': digest(source), 'game_version': game['version'],
                'evidence': {str(p): digest(p.read_bytes()) for p in (
                    root / 'final-result.json', root / 'current-field/result.json',
                    root / 'current-field/plan.json', study / 'activation-proof.json')}}
    decision_path = out / 'decision.json'
    if decision_path.exists() and read(decision_path) != decision:
        raise ValueError('Frozen deployment decision changed')
    write(decision_path, decision)
    feedback = out / 'policy'
    if not feedback.exists():
        parent = root / 'current-field/feedback'
        record(parent / 'policy.ir.json', parent / 'policy.bas', note, decision_path, feedback)
    ir = read(feedback / 'policy.ir.json')
    if ((feedback / 'policy.bas').read_bytes() != source or compile_policy(ir).encode() != source or
            extract(source.decode(), ir) != ir):
        raise ValueError('Final IR/executable parity failed')
    return out, versions, priors, source, ir, note


def main(study, name, apply=False):
    out, versions, priors, source, ir, note = prepare(study, name)
    ids = {p: v['id'] for p, v in versions.items()}
    with client() as c:
        before = check_champions(champions(c), ids, priors)
        for player, version in versions.items():
            verify_owned(c, version, player)
            remote = get(c, '/stats/policy-versions/' + version['id'])
            if remote.get('player_file_content_hash') not in (None, digest(source)):
                raise ValueError('Remote executable changed')
        # Retain the live snapshot even if opponents revised during the completed suite.
        pool = get(c, f'/v2/league-policy-memberships?league_id={LEAGUE}&champions_only=true&limit=100')
        write(out / 'league-readback.json', pool)
        write(out / 'preflight.json', {'checked_at': datetime.now(timezone.utc).isoformat(),
              'prior_champions': list(before.values()), 'versions': ids,
              'source_sha256': digest(source), 'semantic_ir_sha256': digest(ir), 'ready': True})
        if not apply:
            print('Exact pair and complete evidence verified. No champion selected.', flush=True)
            return
        tags = {'semantic_ir_sha256': digest(ir), 'symbolic_policy_sha256': digest(source),
                'ir_revision': str(ir['update']['revision']), 'validation': note,
                'feedback_parity': 'Exact compile and reverse extraction; tested BASIC unchanged.'}
        for player, version in versions.items():
            path = '/stats/policy-versions/' + version['id']
            remote = get(c, path)
            response = c.put(path + '/tags', json=(remote.get('tags') or {}) | tags)
            response.raise_for_status()
            saved = get(c, path)['tags']
            if any(saved.get(k) != v for k, v in tags.items()):
                raise ValueError('Evidence tags did not persist')
            current = check_champions(champions(c), ids, priors)
            if current[player]['policy_version']['id'] != version['id']:
                select(c, player, version, out / ('coach' if player == OPTIMIZER else 'aaron'), note)
            for _ in range(12):
                current = check_champions(champions(c), ids, priors)
                if current[player]['policy_version']['id'] == version['id']:
                    break
                time.sleep(5)
            else:
                raise ValueError('Selection not visible; resume existing receipt')
        after = check_champions(champions(c), ids, priors)
        if any(after[p]['policy_version']['id'] != v for p, v in ids.items()):
            raise ValueError('Both selections have not verified')
        write(out / 'deployment-verified.json', {'verified_at': datetime.now(timezone.utc).isoformat(),
              'owned_active_ladder_players': 2, 'players': list(after.values()), 'versions': ids,
              'source_sha256': digest(source), 'semantic_ir_sha256': digest(ir),
              'ir_policy_pair': str(out / 'policy'), 'decision': str(out / 'decision.json')})
        write(HERE / 'active_policy.json', {'players': [{'player': p, 'version': v['id'],
              'label': f'{v["name"]}:v{v["version"]}'} for p, v in versions.items()],
              'policy': str(out / 'policy/policy.bas'), 'semantic_ir': str(out / 'policy/policy.ir.json'),
              'deployment_receipt': str(out / 'deployment-verified.json')})
        log = HERE / 'VERSION_LOG.md'
        marker = '## Validated coordinated promotion ' + ids[OPTIMIZER]
        if marker not in log.read_text():
            with log.open('a') as f:
                f.write('\n' + marker + '\n\n' + note + '\n\nReceipt: ' +
                        str(out / 'deployment-verified.json') + '\nRollback: ' + str(priors) + '\n')
    print('Both existing league champions updated and read back.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('name')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    main(args.study.resolve(), args.name, args.apply)
