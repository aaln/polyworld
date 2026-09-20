"""Broad 40-episode field guardrail after the frozen hosted comparison passes."""
import argparse
from collections import Counter
from pathlib import Path
import shutil
import time

from hosted_wave import client, create, episodes, fetch, TERMINAL
from hosted_wave_audit import verify
from policy_ir import digest, read, write
from prepare_campaign_xp import DIVISION, PLAYER


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('hosted', type=Path)
    parser.add_argument('command', choices=['launch', 'harvest', 'report'])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = args.hosted.resolve()
    plan, comparison = read(root / 'plan.json'), read(root / 'comparison.json')
    if not comparison['passed']:
        raise ValueError('Hosted comparison failed; field advancement is not qualified')
    directory = root / 'field'
    directory.mkdir(exist_ok=True)
    count = plan['field_guardrail']['episodes']
    version = plan['candidate_version']
    body = {'idempotency_key': 'gota-field-' + plan['run_id'] + '-' + version[:8],
            'target': {'division_id': DIVISION}, 'game_config_overrides': plan['config'],
            'excluded_players': [PLAYER], 'num_episodes': count,
            'roster': [{'slot': -1, 'player': {'policy_ref': version}}] +
                      [{'slot': -1, 'player': {'random': True}} for _ in range(9)],
            'notes': 'Preregistered40-game broad field regression guardrail after completed100-per-arm A/B. Sample current division champions, exclude Aaron from sampled seats, retain one explicit candidate. Full replay, equipment and survival audit before league selection.'}
    if args.command == 'launch':
        write(directory / 'plan.json', {'policy_version': version, 'game_version': plan['game_version'],
                                       'target': plan['target'], 'config': plan['config'],
                                       'guardrail': plan['field_guardrail']})
        shutil.copy2(root / 'candidate/audit', directory / 'audit')
        with client() as c:
            request = create(c, body, directory / 'batch', args.dry_run)
        print({'request': request, 'episodes': count})
        return
    request = read(directory / 'batch/created.json')['id']
    if args.command == 'harvest':
        with client() as c:
            while True:
                entries = episodes(c, request)
                write(directory / 'batch/episodes.json', entries)
                complete = 0
                for ep in entries:
                    if ep['status'] in TERMINAL:
                        fetch(c, ep, directory / 'artifacts', version)
                        complete += 1
                print(f'Field: {complete}/{count} complete and fetched', flush=True)
                if complete == count:
                    write(directory / 'collection.json', {'episodes': count, 'request_count': 1})
                    return
                time.sleep(15)
    binary = directory / 'audit'
    binary_hash = digest(binary.read_bytes())
    folders = sorted(p.parent for p in (directory / 'artifacts').glob('*/.done'))
    if len(folders) != count:
        raise ValueError('Field collection is incomplete')
    rows = []
    for folder in folders:
        verify(folder, binary, binary_hash)
        ep, result, audit = [read(folder / n) for n in ['episode.json', 'results.json', 'audit.json']]
        config = {k: v for k, v in ep['game_config'].items() if k not in {'seed', 'players', 'tokens'}}
        if (ep['coworld_id'] != plan['target']['coworld_id'] or
                ep['coworld_version'] != plan['game_version'] or config != plan['config'] or
                ep['policy_version_ids'].count(version) != 1):
            raise ValueError('Field game/configuration/subject changed')
        slot = ep['policy_version_ids'].index(version)
        hero = audit['heroes'][slot]
        if [h['total_xp'] for h in audit['heroes']] != result['total_xp']:
            raise ValueError('Field XP disagreement')
        rows.append({'episode': ep['id'], 'slot': slot, 'seed': result['seed'], 'class': hero['class'],
                     'win': hero['score'], 'deaths': hero['deaths'], 'alive_ticks': hero['alive_ticks'],
                     'ticks': result['ticks'], 'xp': hero['total_xp'], 'first_gear_tick': hero['first_gear_tick'],
                     'glory': hero['score'] * (hero['total_xp'] - 100 * result['ticks'] / 1440),
                     'timeout': result['outcome'] == 'time_limit', 'roster': ep['policy_version_ids']})
    if len({r['seed'] for r in rows}) != count or Counter(r['slot'] for r in rows) != Counter({s: 4 for s in range(10)}):
        raise ValueError('Field seed/seat coverage failed')
    wins = sum(r['win'] for r in rows)
    death_rate = sum(r['deaths'] for r in rows) * 1440 / sum(r['alive_ticks'] for r in rows)
    gates = plan['field_guardrail']
    checks = {'wins': wins >= gates['minimum_wins'],
              'survival': death_rate <= gates['maximum_death_rate_vs_ab_control'] * comparison['arms']['control']['death_rate'],
              'timeouts': sum(r['timeout'] for r in rows) / count <= gates['maximum_timeout_fraction'],
              'equipment': all(r['first_gear_tick'] >= 0 for r in rows)}
    write(directory / 'result.json', {'episodes': count, 'wins': wins, 'death_rate': death_rate,
                                     'mean_glory': sum(r['glory'] for r in rows) / count,
                                     'checks': checks, 'passed': all(checks.values()), 'rows': rows})
    print({'wins': wins, 'death_rate': death_rate, 'checks': checks, 'passed': all(checks.values())})


if __name__ == '__main__':
    main()
