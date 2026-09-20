"""Close completed coaching experiments into immutable IR feedback and a report."""
from datetime import datetime, timezone
from html import escape

from economy_feedback import record
from policy_ir import HERE, ROOT, read, write, digest
from release_workspace import RUN, VERSION, SOURCE

STUDY = RUN / 'coached-lanes'


def main():
    studies = []
    for path in sorted(STUDY.glob('r5-*/*/result.json')):
        result = read(path)
        if 'metrics' not in result or not (path.parent / 'plan.json').exists():
            continue
        plan = read(path.parent / 'plan.json')
        for name in plan['variants']:
            source = path.parent / 'candidates' / name
            feedback = path.parent / 'measured-feedback' / name
            if not feedback.exists():
                claim = (
                    f'Completed {path.parent.parent.name}/{path.parent.name} on {VERSION}, '
                    f'source {SOURCE}. Candidate {name}: {result["metrics"][name]}. '
                    f'Matched deployed control: {result["metrics"]["current"]}. '
                    f'Frozen local gate: {plan.get("rule", plan.get("gates"))} '
                    f'Gate passed: {name in result["selected"]}. '
                    'Local evidence only; repeated team lineups do not establish broad superiority. '
                    'A small-screen qualifier requires fresh larger local and hosted comparison. '
                    'No league selection follows from this result. Coaching source: '
                    '/Users/aaln/Documents/Policy Loops/sessions/2026-09-16t21-57-06-471ze12176; '
                    'original captures preserved under coached-lanes/captured-inputs. '
                    'Input policy belongs to another game; applied coaching to the actual GotA baseline.')
                record(source / 'policy.ir.json', source / 'policy.bas', claim, path, feedback)
        studies.append({'study': str(path.parent.relative_to(STUDY)),
                        'result': str(path), 'result_sha256': digest(path.read_bytes()),
                        'games': result['verified_games'], 'selected': result['selected'],
                        'metrics': result['metrics']})
    deployment = read(STUDY / 'deployment-r5/deployment-verified.json')
    jordan = read(STUDY / 'r5-convoy/hosted/current/result.json')['rivals']['jordan']
    field = read(STUDY / 'r5-current-field/result.json')
    mixed_path = STUDY / 'r5-live-league/result.json'
    mixed = read(mixed_path) if mixed_path.exists() else None
    rush_results = {p.parent.name: read(p) for p in (STUDY/'r5-rush-defense/hosted').glob('*/result.json')}
    candidate_team_path = STUDY/'r5-asymmetric/hosted/blue_damage/result.json'
    candidate_team_games = 80 if candidate_team_path.exists() else 0
    summary = {'updated_at': datetime.now(timezone.utc).isoformat(), 'game_version': VERSION,
               'source': SOURCE, 'workspace': str(ROOT), 'deployment': deployment,
               'completed_r5_local_games': sum(s['games'] for s in studies), 'studies': studies,
               'valid_hosted_games': 180 + candidate_team_games + (800 if mixed else 0) + sum(r['games'] for r in rush_results.values()),
               'jordan175_wins': jordan['wins'],
               'mixed_league_comparison': str(mixed_path) if mixed else None,
               'rush_benchmark_results': {k: {'games': v['games'], 'wins': v['wins']} for k,v in rush_results.items()},
               'field_wins': field['wins'], 'quarantined_hosted_games': 80,
               'new_behavior_promoted': False,
               'captures': str(STUDY / 'capture-manifest.json')}
    write(STUDY / 'research-index.json', summary)
    lines = [
        '# GotA coaching research and deployment', '',
        f'Updated {summary["updated_at"]}. Game {VERSION}; exact source `{SOURCE}`.', '',
        'Both existing league players are active on the bounded-pursuit BASIC. '
        'Their current-release IR and evaluation metadata were updated and read back. '
        'The executable was already selected; no replacement or third player was created.', '',
        '- Aaron’s Optimizer: `aaron-gota-ir-win-bounded-0916:v1`.',
        '- Aaron: `aaron-gota-ir-win-bounded-0916-aaron:v1`.',
        f'- [Deployment receipt]({STUDY}/deployment-r5/deployment-verified.json).',
        f'- [Canonical semantic IR]({HERE}/win_bounded_0916.r5.evaluated.ir.json); '
        f'[generated BASIC]({HERE}/win_bounded_0916.r5.evaluated.bas).', '',
        'The current executable won **80/80** against Jordan v175 (40 per color), with all ten VMs '
        'and every full replay verified. These are **two distinct full command tapes**, so the result '
        'supports this fixed team matchup, not 80 independent strategies or a #1 ranking. '
        'A separate sampled current-field request won **75/100**; red 35/50, blue 40/50. '
        'That field request is diagnostic, not an A/B comparison. All 100 games bought equipment.', '',
        f'[Jordan results]({STUDY}/r5-convoy/hosted/current/result.json); '
        f'[field results]({STUDY}/r5-current-field/result.json).', '',
        'The user identified a current-release counterexample: khors:v1 won at125.33seconds '
        'with zero hero deaths, while all five attackers were visible in the middle lane by40seconds '
        'and our heroes stayed split across the outer lanes. This limits the Jordan result. '
        'The new rush-defense study also pins red-kite:v20 and gota-g001:v1. '
        f'[Replay breakdown]({STUDY}/khors-defense/rush-breakdown.png); '
        f'[counterexample IR feedback]({STUDY}/khors-defense/deployed-feedback/policy.ir.json).', '',
        'Coaching evidence suggests sustained lane pressure with creeps. The new release requires '
        'one breached lane, then **both god guards**, then the exposed god. Replays show that '
        'creeps can remain occupied by lane barracks while heroes reach the guards. '
        'Stricter shared routes often reduced practical siege participation or lost the race. '
        'The baseline already follows an outer wave in the inspected Lich losses; forcing a new '
        'route was harmful in the tested cases. Terminal-priority changes alone also failed to '
        'improve the initial screen. These are scoped observations, not universal causal findings.', '',
        '## Completed local experiments on the current release', '',
        '| Study | Audited games | Control wins | Local qualifiers |',
        '|---|---:|---:|---|',
    ]
    if mixed:
        a, b = mixed['arms']['candidate'], mixed['arms']['control']
        lines[lines.index('## Completed local experiments on the current release'):lines.index('## Completed local experiments on the current release')] = [
            '## Both-player league simulation', '',
            f'Completed800games with both owned players and thirteen pinned other players across four '
            f'rosters. Allied gear-candidate wins {a["allied_wins"]}/160 versus control {b["allied_wins"]}/160. '
            f'Complete frozen gate passed: {mixed["passed"]}. Checks: {mixed["checks"]}. '
            f'Opposed draws {a["opposed_draws"]} versus {b["opposed_draws"]}; opposing-owned-player '
            'outcomes are kept separate from allied gains. No gear-only deployment follows. '
            f'[Full comparison]({mixed_path}).', '']
    if rush_results:
        lines += ['', 'Completed exact-rival rush benchmarks: '+str(summary['rush_benchmark_results'])+'. '
                  'Every policy is tested in40episode requests on both colors against all three pinned rivals. '
                  'Fixed repeated lineups are not broad statistical proof.', '']
    for study in studies:
        control = study['metrics']['current']
        lines.append(f'| [{study["study"]}]({study["result"]}) | {study["games"]} | '
                     f'{control["wins"]}/{control["games"]} | '
                     f'{", ".join(study["selected"]) or "None"} |')
    lines += ['', f'{summary["completed_r5_local_games"]} current-release local games completed in '
              'these studies. Each tested candidate has an immutable measured-feedback IR, '
              'regenerated byte-identical BASIC, and reverse extraction under its study directory. '
              'Small-screen qualifiers are not deployment approvals.', '',
              '## Preserved evidence and exclusions', '',
              'The coaching video shows GotA, but session.json and input.policy.py identify Pudge Wars; '
              'input.ir.md is inactive. Captured inputs were preserved without edits, and the coaching '
              'was applied to the actual GotA IR. '
              f'[Capture manifest]({STUDY}/capture-manifest.json).', '',
              'An accidental old-coworld request (40 games) was fully audited against its actual old '
              'release and excluded here. Another 40-game request against historical Jordan v148 '
              'on the new release disabled all five rival VMs; those games were also excluded. '
              'Neither set supports a competitive win claim. The 736 earlier valid local games '
              'remain scoped to release .3 and are not counted as current-release evidence.', '',
              'All original workspace edits and coaching captures remain preserved. Research uses '
              f'the clean release worktree `{ROOT}`.']
    (STUDY / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    # A standalone readable artifact; Markdown remains the detailed linked source.
    html = '<!doctype html><meta charset="utf-8"><title>GotA coaching research</title>'
    html += '<style>body{max-width:1100px;margin:40px auto;padding:0 24px;font:16px/1.6 system-ui;background:#101822;color:#e7edf4}pre{white-space:pre-wrap}a{color:#8cceff}</style>'
    html += '<a href="REPORT.md">Detailed report with evidence links</a><pre>' + escape('\n'.join(lines)) + '</pre>'
    (STUDY / 'REPORT.html').write_text(html)
    print({'completed_r5_local_games': summary['completed_r5_local_games'],
           'studies': len(studies), 'report': str(STUDY / 'REPORT.md')})


if __name__ == '__main__':
    main()
