"""Render the completed clean-source study without pooling adaptive selection data."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import markdown

from policy_ir import read, write
from release_workspace import ROOT, SOURCE, VERSION


def report(study):
    run = study.parent
    lich_repair = read(study / 'hosted-confirmation/plan.json')['candidate'] == 'lich_nearest'
    release_bridge = read(study / 'hosted-discovery/plan.json').get('release_bridge')
    confirm = read(study / 'hosted-confirmation/result.json')
    name = read(study / 'hosted-confirmation/plan.json')['candidate']
    version = read(study / 'hosted-discovery' / name / 'uploaded-version.json')
    field_path = study / 'field/result.json'
    field = read(field_path) if field_path.exists() else None
    rivals_path = study / 'rival-matchups/result.json'
    rivals = read(rivals_path) if rivals_path.exists() else None
    rival_games = rivals['games'] if rivals else 0
    deployment_path = study / ('deployment-pair' if lich_repair else 'deployment') / 'deployment-verified.json'
    deployed = read(deployment_path) if deployment_path.exists() else None
    labels = {'v2': 'Waveguard r4:v2', 'cadence': 'Cadence-all:v1', name: 'Building targeting + class exceptions'}
    arms = confirm['arms']
    assert all(a['games'] == 400 for a in arms.values())
    vm_methods = Counter(read(p)['method'] for p in (study / 'hosted-confirmation').glob('*/*/artifacts/*/vm-validity.json'))
    assert sum(vm_methods.values()) == 1200
    decision = (('Deployed on both Aaron and Aaron’s Optimizer; exactly two active owned ladder players verified.' if lich_repair else
                 'Deployed on Aaron’s Optimizer; exactly two active owned ladder players verified.') if deployed else
                'Confirmation passed; field evaluation or deployment remains pending.' if confirm['passed'] and (field is None or field['passed']) else
                'Candidate did not pass the frozen promotion gates; deployed champions retained.')
    lines = [f'# Gods of the Arena: clean-source release study ({VERSION})', '', decision, '',
        f'Game source: `{SOURCE}`. Workspace: `{ROOT}`.', '',
        'Only policy research files were migrated from the original checkout. Game files and configuration came from origin/main, and 24 dependencies were independently pinned from its lockfile. The original workspace’s gameplay edits remain intact. The initial .2 calibration reproduced 7,269 ticks and 78,900 actions. The .3 calibration reproduced 2,388 ticks and 24,841 actions. Both had zero state mismatches.', '',
        'The original checkout still had the 240-tick spawn default and the previous hero statistics (including Death Knight heal 30 and Warlock restore 24), alongside local gameplay edits. The source mismatch is confirmed; its contribution to the previous ladder ranking is not isolated by this experiment.', '',
        'The release binding records six creeps per lane every 480 ticks, building collision and footprint-edge attack range, and the announced hero and tower statistics. Purchases and abilities use current host observations. Berserker retains baseline nearest-center selection and uninterrupted ordinary attacks. ' + ('Lich retains cadence’s nearest-center targeting and recovery; the other eight classes use building-edge targeting.' if lich_repair else 'The other nine classes use building-edge targeting.'), '',
        '## Fresh hosted confirmation', '',
        f'Each arm played 400 games against the same nine pinned incumbent versions, in four 100-episode requests with balanced hero seats. Request-derived seeds are independent cohorts. All {(1800 if lich_repair else 500) + rival_games:,} earlier hosted outcomes and seeds were excluded. All 1,200 games completed before the verdict; no interim candidate tuning or stopping.', '',
        '| Policy | Wins | Win rate | Deaths/alive-minute | Total XP | Gear purchases |',
        '|---|---:|---:|---:|---:|---:|']
    for key in ['v2', 'cadence', name]:
        a = arms[key]
        lines.append(f"| {labels[key]} | {a['wins']}/400 | {a['wins']/4:.2f}% | {a['death_rate']:.4f} | {a['xp']:,} | {a['equipment_games']}/400 |")
    lines += ['', 'The frozen gate requires at least a 5 percentage point gain and one-sided Fisher p < 0.025 against each control, no adverse class test at p < 0.005, deaths/alive-minute at most 110% of cadence, XP at least 80% of cadence, equipment in every game, and complete replay/VM validity.', '']
    for key, c in confirm['comparisons'][name].items():
        lines.append(f"- Versus {labels[key]}: {100*c['gain']:+.2f} percentage points; p = {c['p']:.6g}; adverse classes: {', '.join(c['adverse_classes']) or 'none'}. Comparison gate {'passed' if c['passed'] else 'failed'}.")
    a, b = arms[name], arms['cadence']
    lines += ['', f"Candidate death-rate ratio: {a['death_rate']/b['death_rate']:.4f}; XP ratio: {a['xp']/b['xp']:.4f}. Overall confirmation {'passed' if confirm['passed'] else 'failed'}.", '',
        'All retained tapes were checked against the exact release: every recorded action and state hash, total ticks, effective seed, configuration, roster rotation, API scores, lifetime XP, and VM completion. Missing server-log artifacts were recovered through genuine episode-specific HTTP 404 receipts and official ten-player completion statuses; no episode was dropped or replaced. VM proof counts: ' + ', '.join(f'{method}: {count}' for method, count in sorted(vm_methods.items())) + '.', '',
        '## Discovery and local screening', '',
        'Discovery chose the candidate; its results are not pooled with confirmation. The initial four behavioral variants covered building-edge targeting, heavier siege priority, shorter recovery movement, and wave spacing. Two subsequent variants isolated Berserker recovery and target selection.', '',
        '- 280 initial local games: default 8/40, waveguard 20/40, cadence 17/40, footprint 28/40, siege 28/40, short-step 18/40, wave-spacing 26/40.',
        '- 80 new class-follow-up local games: recovery exception 25/40; combined Berserker exception 27/40. Another 160 control tapes were explicitly reused for comparison.',
        '- 400 initial hosted discovery games: waveguard 44/100, cadence 41/100, footprint 49/100, siege 47/100.',
        '- 100 new class-follow-up hosted games: combined candidate 57/100. The two earlier 100-game controls were reused for selection only.',
        '- 76 complete local gameplay comparisons preserved every action and state: 72 unaffected-class games matched the footprint parent; four Berserker games matched waveguard. VM work metrics legitimately differ.', '',
        'The local screen supports debugging and mechanism checks; hosted confirmation determines competitive improvement. The sample describes these rosters and this release, and does not establish a leaderboard rank.', '']
    if release_bridge:
        lines += ['The live release advanced from .2 to .3 before this confirmation launched. Compiler dependency closure verified all 32 workspace simulation modules and external dependencies unchanged; graphics and tooling changed. Historical .2 outcomes retain their original provenance. The frozen policy BASIC is byte-identical, its IR binding is rebased, and all fresh confirmation games use .3. [Source parity proof](' + release_bridge['artifact'] + ').', '']
    if lich_repair:
        local = read(study / 'local/screen-result.json')['metrics'][name]
        discovery = read(study / 'hosted-discovery/result.json')['arms'][name]
        lines += ['The preceding Berserker-only repair completed a separate 1,200-game confirmation: 224/400 versus 172/400 and 173/400. Despite significant overall gains, its Lich result (0/40 versus cadence 10/40) failed the frozen class guard. That verdict remains failed; its data were excluded from the new confirmation.', '',
            f'The Lich repair then ran 40 new local games ({local["wins"]}/40), with 160 explicitly reused controls and 40 complete action/state identity checks. Its 100 new discovery games produced {discovery["wins"]}/100 wins. These adaptive results are also excluded from the current confirmation.', '']
    if rivals:
        lines += ['## Named-rival matchups', '',
            'Five copies of our policy faced five copies of each exact rival, in 40 games on red and 40 on blue. This measures direct team-policy behavior; the mixed-roster league-contribution comparison above remains separate.', '',
            '| Rival | Wins / losses / draws | One-sided p | Frozen win criterion |', '|---|---:|---:|---|']
        for a in rivals['rivals'].values():
            lines.append(f"| {a['label']} | {a['wins']} / {a['losses']} / {a['draws']} | {a['one_sided_binomial_p']:.6g} | {'Passed' if a['beaten'] else 'Not met'} |")
        lines += ['', 'The original arithmetic criterion required at least 44/80 wins and exact binomial p < 0.025. A subsequent full-command comparison found identical per-hero tick commands in all40repeats of each fixed lineup. Thus each rival probe contains only two distinct behavioral scenarios, one per color: the displayed p-values do not establish general competitive significance. All160games remain retained and audited; mixed-roster confirmation and sampled-field checks are separate.', '', f'[Complete rival results]({rivals_path})', '']
    if field is not None:
        lines += ['## Current-field guardrail', '',
            f"One 100-episode request sampled current division champions, excluding both owned players. Candidate: {field['wins']}/100 wins, gear in {field['equipment_games']}/100 games. The frozen minimum is 50 wins with complete equipment and artifact checks. Guardrail {'passed' if field['passed'] else 'failed'}.", '']
    lines += ['## IR and deployment', '',
        f"Candidate: `{version['name']}:v{version['version']}` (`{version['id']}`). {decision}", '',
        'Semantic feedback is recorded in the IR while preserving the exact evaluated BASIC bytes. Compilation and reverse extraction must round-trip. Historical claims remain explicitly scoped to their original release; current binary fort wins remain primary. The current local Glory diagnostic uses 200 XP/minute, separately from historical 100-rate reports.', '',
        f"New games across this release study: **{400 if lich_repair else 360} local and {(3000 if lich_repair else 1700) + rival_games + (100 if field else 0):,} hosted**. Reused controls are excluded from these counts.", '',
        'Evidence:', '',
        f'- [Release provenance]({run / "release-verification.json"})',
        f'- [Frozen confirmation plan]({study / "hosted-confirmation/plan.json"})',
        f'- [Complete confirmation result]({study / "hosted-confirmation/result.json"})',
        f'- [Artifact recovery]({run / "missing-log-inspection/README.md"})',
        f'- [Study context]({ROOT / "examples/gods_of_the_arena/players/ir/WORKING_CONTEXT.md"})', '']
    if field is not None:
        lines.append(f'- [Field result]({field_path})')
    if deployed:
        lines.append(f'- [Verified league deployment]({deployment_path})')
    text = '\n'.join(lines) + '\n'
    (run / 'REPORT.md').write_text(text)
    (run / 'REPORT.html').write_text('<!doctype html><meta charset="utf-8"><title>GotA release study</title><style>body{max-width:1000px;margin:40px auto;padding:0 24px;font:16px/1.6 system-ui;background:#f6f7f9;color:#18202a;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;background:white}th,td{padding:10px;text-align:left;border-bottom:1px solid #dde2e8}code{font-size:.9em}a{color:#1457af}</style>' + markdown.markdown(text, extensions=['tables']))
    write(run / 'report-summary.json', {'generated_at': datetime.now(timezone.utc).isoformat(),
          'version': VERSION, 'source': SOURCE, 'candidate_version': version['id'],
          'confirmation_passed': confirm['passed'], 'field_passed': field['passed'] if field else None,
          'deployed': bool(deployed), 'new_local_games': 400 if lich_repair else 360,
          'new_hosted_games': (3000 if lich_repair else 1700) + rival_games + (100 if field else 0)})
    print(run / 'REPORT.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    report(parser.parse_args().study.resolve())
