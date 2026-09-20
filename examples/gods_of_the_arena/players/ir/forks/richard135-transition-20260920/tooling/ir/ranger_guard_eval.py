"""Compare arrival-qualified recall variants with the actual deployed blue repair."""
from economy_feedback import record
from policy_ir import read, write
from ranger_guard import STUDY, VARIANTS, make
from release_workspace import RUN
from rush_defense_eval import evaluate


def main():
    plan = {'hypothesis': 'Prevent the quiet timer from abandoning a remote recall before arrival.',
            'variants': VARIANTS, 'screen_cases': 12, 'screen_seed': 772000,
            'confirmation_cases': 60, 'confirmation_seed': 773000,
            'primary_control': 'deployed=exact promoted blue_repair:v1; evaluator current/blue_parent are legacy diagnostics only.',
            'screen_rule': 'All VM/replays/gear, wins>=deployed, default>=3/4, others>=2/4; top2 by wins then deaths then name.',
            'confirmation_rule': 'All VM/replays/gear, wins>=deployed, default>=18/20, others>=12/20. '
            'Require all30 red complete-game actions and state hashes equal deployed. '
            'Fresh hosted mixed and Jordan comparisons remain required; no deployment from local proxies.'}
    path = STUDY / 'prospective-plan.json'
    if path.exists() and read(path) != plan: raise ValueError('Frozen research plan changed')
    write(path, plan)
    evaluate('screen', VARIANTS, 12, 772000, make, STUDY, RUN / 'r5/fast/audit-local')
    m = read(STUDY / 'screen/result.json')['metrics']
    choices = [n for n in VARIANTS[1:] if m[n]['all_gear'] and m[n]['wins'] >= m['deployed']['wins'] and
               m[n]['opponents']['default'] >= 3 and all(m[n]['opponents'][o] >= 2 for o in ('current', 'center_proxy'))]
    choices.sort(key=lambda n: (-m[n]['wins'], m[n]['deaths'], n)); choices = choices[:2]
    write(STUDY / 'screen/selection.json', {'selected': choices, 'metrics': m})
    if not choices:
        (STUDY / 'local').mkdir(exist_ok=True)
        write(STUDY / 'local/comparison.json', {'selected': None, 'qualified': [], 'reason': 'No local screen qualifier'})
        return
    evaluate('local', ['deployed'] + choices, 60, 773000, make, STUDY, RUN / 'r5/fast/audit-local')
    result = read(STUDY / 'local/result.json'); m = result['metrics']; proofs = {}
    import json, subprocess
    for name in choices:
        rr = []
        for row in result['rows']:
            if row['name'] != name or row['color'] != 0: continue
            root = STUDY / 'local/games'
            p = json.loads(subprocess.check_output([str(RUN / 'r5/compare-gameplay'),
                str(root / name / str(row['seed']) / 'replay.bin'), str(root / 'deployed' / str(row['seed']) / 'replay.bin')], text=True))
            rr.append({'seed': row['seed'], **p})
        proofs[name] = {'games': len(rr), 'all_gameplay_equal': len(rr) == 30 and all(
            all(p[k] for k in ('all_actions_equal', 'all_state_hashes_equal', 'setup_equal', 'config_equal', 'same_seed')) for p in rr), 'rows': rr}
    write(STUDY / 'local/red-parity.json', proofs)
    qualified = [n for n in choices if proofs[n]['all_gameplay_equal'] and m[n]['all_gear'] and
                 m[n]['wins'] >= m['deployed']['wins'] and m[n]['opponents']['default'] >= 18 and
                 all(m[n]['opponents'][o] >= 12 for o in ('current', 'center_proxy'))]
    qualified.sort(key=lambda n: (-m[n]['wins'], m[n]['deaths'], n))
    comparison = {'selected': qualified[0] if qualified else None, 'qualified': qualified,
                  'metrics': m, 'verified_games': result['verified_games'], 'scope': plan['confirmation_rule'],
                  'primary_control': plan['primary_control']}
    for n in choices:
        parent = STUDY / 'local/candidates' / n
        out = STUDY / 'local/comparison-feedback' / n
        if not out.exists():
            # Record against the completed raw result; publish readiness last.
            record(parent / 'policy.ir.json', parent / 'policy.bas',
                   f'Fresh60case arrival confirmation: candidate {m[n]}, deployed blue_repair {m["deployed"]}; '
                   f'30fullredgames parity {proofs[n]["all_gameplay_equal"]}; locally qualified {n in qualified}. '
                   'Remaining current/blue_parent controls are legacy proxies. Hosted mixed/Jordan outcomes untested.',
                   STUDY / 'local/result.json', out)
    write(STUDY / 'local/comparison.json', comparison)
    print('Arrival confirmation', comparison, flush=True)


if __name__ == '__main__': main()
