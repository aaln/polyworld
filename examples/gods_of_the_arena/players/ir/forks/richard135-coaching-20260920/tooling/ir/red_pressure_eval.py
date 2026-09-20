"""Fresh relative-control local gate; actual black-kite/Jordan tests still needed."""
import json
import subprocess
from economy_feedback import record
from policy_ir import read, write
from red_pressure import STUDY, VARIANTS, make
from release_workspace import RUN
from rush_defense_eval import evaluate


def qualifies(metrics, name):
    a, b = metrics[name], metrics['deployed']
    return a['all_gear'] and a['wins'] >= b['wins'] and all(
        a['opponents'][o] >= b['opponents'][o] for o in b['opponents']) and all(
        a['colors'][c] >= b['colors'][c] for c in b['colors'])


def main():
    plan = {'hypothesis': 'Stop isolated survivors from indefinitely retaining both red attacking roles; keep three sentries.',
            'variants': VARIANTS, 'screen_cases': 12, 'screen_seed': 774000,
            'confirmation_cases': 60, 'confirmation_seed': 775000,
            'primary_control': 'deployed=exact promoted blue_repair:v1; current/blue_parent are legacy diagnostics.',
            'rule': 'Complete all VM/replay/equipment checks. Require no win regression relative to actual deployed in any opponent or color. '
            'Screen top2 by wins then deaths/name; fresh60cases each plus deployed. Require all30 blue games exact actions/hashes/config/seed. '
            'This is local admissibility only; fresh hosted black-kite13,Jordan186 and field guardrails required. No automatic deployment.'}
    path = STUDY / 'prospective-plan.json'
    if path.exists() and read(path) != plan: raise ValueError('Frozen plan changed')
    write(path, plan)
    evaluate('screen', list(VARIANTS), 12, 774000, make, STUDY, RUN / 'r5/fast/audit-local')
    m = read(STUDY / 'screen/result.json')['metrics']
    choices = [n for n in VARIANTS if n != 'deployed' and qualifies(m, n)]
    choices.sort(key=lambda n: (-m[n]['wins'], m[n]['deaths'], n)); choices = choices[:2]
    write(STUDY / 'screen/selection.json', {'selected': choices, 'metrics': m})
    if not choices:
        (STUDY / 'local').mkdir(exist_ok=True)
        write(STUDY / 'local/comparison.json', {'selected': None, 'qualified': [], 'reason': 'No relative local screen qualifier'})
        return
    evaluate('local', ['deployed'] + choices, 60, 775000, make, STUDY, RUN / 'r5/fast/audit-local')
    result = read(STUDY / 'local/result.json'); m = result['metrics']; proofs = {}
    for name in choices:
        rr = []
        for row in result['rows']:
            if row['name'] != name or row['color'] != 1: continue
            root = STUDY / 'local/games'
            p = json.loads(subprocess.check_output([str(RUN / 'r5/compare-gameplay'),
                str(root / name / str(row['seed']) / 'replay.bin'), str(root / 'deployed' / str(row['seed']) / 'replay.bin')], text=True))
            rr.append({'seed': row['seed'], **p})
        proofs[name] = {'games': len(rr), 'all_gameplay_equal': len(rr) == 30 and all(
            all(p[k] for k in ('all_actions_equal', 'all_state_hashes_equal', 'setup_equal', 'config_equal', 'same_seed')) for p in rr), 'rows': rr}
    write(STUDY / 'local/blue-parity.json', proofs)
    qualified = [n for n in choices if qualifies(m, n) and proofs[n]['all_gameplay_equal']]
    qualified.sort(key=lambda n: (-m[n]['wins'], m[n]['deaths'], n))
    comparison = {'selected': qualified[0] if qualified else None, 'qualified': qualified, 'metrics': m,
                  'verified_games': result['verified_games'], 'scope': plan['rule']}
    for n in choices:
        parent = STUDY / 'local/candidates' / n; out = STUDY / 'local/comparison-feedback' / n
        if not out.exists():
            record(parent / 'policy.ir.json', parent / 'policy.bas',
                   f'Fresh60case pressure confirmation: candidate{m[n]}, deployed{m["deployed"]}; '
                   f'30bluegame exact parity{proofs[n]["all_gameplay_equal"]}; localadmissibility{n in qualified}. '
                   'Actual black-kite/Jordan and broad field untested.', STUDY / 'local/result.json', out)
    write(STUDY / 'local/comparison.json', comparison)
    print('Pressure confirmation', comparison, flush=True)


if __name__ == '__main__': main()
