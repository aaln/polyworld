"""Full local comparison of coordinated coverage and its two color components."""
import json
import subprocess
from economy_feedback import record
from policy_ir import read, write
from ranger_guard_hosted import freeze
from red_pressure_eval import qualifies
from release_workspace import RUN
from rush_defense_eval import evaluate
from threat_coverage import STUDY, VARIANTS, make


def main():
    plan = {'variants': VARIANTS, 'fresh_cases_per_variant': 60, 'seed': 776000,
            'local_games': 360, 'primary_control': 'exactpromotedblue_repair; otherlegacycontrolsdiagnosticonly',
            'rule': 'All four variants plus two legacy controls run60cases each without intermediate selection. '
            'Require no opponent/color win regression versus actual deployed, all gear/runtime/replay audits. '
            'Verify every unchanged color and combined component across30full games. Rank qualifies by wins/deaths/name. '
            'Actual red-kite27 threat, mixed weak roster, Jordan186 and broad field still required; no local-only promotion.',
            'combined_effect': 'Individual components need not qualify for the coordinated candidate to qualify.'}
    freeze(STUDY / 'prospective-plan.json', plan)
    evaluate('local', VARIANTS, 60, 776000, make, STUDY, RUN / 'r5/fast/audit-local')
    result = read(STUDY / 'local/result.json'); m = result['metrics']; proofs = {}
    comparisons = [('blue_coverage','deployed',0), ('red_coverage','deployed',1),
                   ('both_coverage','red_coverage',0), ('both_coverage','blue_coverage',1)]
    for candidate, parent, color in comparisons:
        rr = []
        for row in result['rows']:
            if row['name'] != candidate or row['color'] != color: continue
            root = STUDY / 'local/games'
            p = json.loads(subprocess.check_output([str(RUN / 'r5/compare-gameplay'),
                str(root / candidate / str(row['seed']) / 'replay.bin'), str(root / parent / str(row['seed']) / 'replay.bin')], text=True))
            rr.append({'seed': row['seed'], **p})
        key = candidate + '-' + str(color)
        proofs[key] = {'parent': parent, 'games': len(rr), 'all_gameplay_equal': len(rr) == 30 and all(
            all(p[k] for k in ('all_actions_equal', 'all_state_hashes_equal', 'setup_equal', 'config_equal', 'same_seed')) for p in rr), 'rows': rr}
    write(STUDY / 'local/component-parity.json', proofs)
    if not all(p['all_gameplay_equal'] for p in proofs.values()): raise ValueError('Full-game composition parity failed')
    qualified = [n for n in VARIANTS[1:] if qualifies(m, n)]
    qualified.sort(key=lambda n: (-m[n]['wins'], m[n]['deaths'], n))
    comparison = {'selected': qualified[0] if qualified else None, 'qualified': qualified, 'metrics': m,
                  'verified_games': result['verified_games'], 'scope': plan['rule']}
    for n in VARIANTS[1:]:
        parent = STUDY / 'local/candidates' / n; out = STUDY / 'local/comparison-feedback' / n
        if not out.exists():
            record(parent / 'policy.ir.json', parent / 'policy.bas',
                   f'Fresh60case threat coverage: candidate{m[n]}, deployed{m["deployed"]}; '
                   f'all120fullcomponentparitycomparisons passed; localqualification{n in qualified}. '
                   'Actual red-kite27/mixed/Jordan/field untested.', STUDY / 'local/result.json', out)
    write(STUDY / 'local/comparison.json', comparison)
    print('Threat coverage confirmation', comparison, flush=True)


if __name__ == '__main__': main()
