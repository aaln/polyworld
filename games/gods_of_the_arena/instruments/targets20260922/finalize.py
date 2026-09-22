"""Freeze evidence and feed validation back to IR without changing tested BASIC."""
from datetime import datetime, timezone
from pathlib import Path
import json
import pprint
import shutil
import practiced
from panel import h, STUDY

HERE = Path(__file__).resolve().parent
PAIR = h.ROOT / 'examples/gods_of_the_arena/players/ir/forks/microplay20260922'


def copy_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main():
    result = h.read(STUDY / 'practiced/result.json')
    review = h.read(STUDY / 'review.json')
    assert result['complete'] and review['complete']
    assert not PAIR.exists(), 'Preserve frozen bundles'
    practiced.configure('potions')
    ir = practiced.ir
    source = (STUDY / 'candidates/practiced/policy.bas').read_bytes()
    p = h.read(STUDY / 'candidates/practiced/policy.ir.json')
    initial_ir = ir.digest(p)
    cells = [c for c in review['cells'] if c['label'] == 'practiced']
    scores_improved = all(c['score_delta'] > 0 for c in cells)
    forts_improved = all(c['win_delta'] >= 0 for c in cells) and sum(c['win_delta'] for c in cells) > 0
    p['belief']['claims'] = {
        'PracticeMechanics': {
            'claim': 'Controlled both-color engine drills: Ranger 20 to 39 basic hits/360 ticks; contested-wave gold 210 to 240 but XP 300 to 285; Crossbowman boundary XP 0 to 15; Ranger shop damage 47 to 61 at the same 320 HP with potion and portal slots; threatened-base portal channels complete and defense releases, while safe-base controls do not portal. These establish bounded mechanisms, not general match strength.',
            'status': 'supported',
            'evidence': [{'artifact': 'evidence/practice-baseline.json'}, {'artifact': 'evidence/practice-practiced.json'}]},
        'HostContract': {
            'claim': '126 actual-host fixtures pass across all classes/colors, including dense waves, upgrades, shopping, channels, buyback and defense release. Four responsive native games won against the parent with exact replay parity. Hosted VM and score validity is reported per game.',
            'status': 'supported',
            'evidence': [{'artifact': 'evidence/practiced-scenarios-r2.json'}, {'artifact': 'evidence/practiced-local-result.json'}, {'artifact': 'evidence/practiced/result.json'}]},
        'TargetScoreImprovement': {
            'claim': 'Mean per-hero XP score exceeds the lane:v1 baseline in every pinned target/color cell. Forts, absolute rival score and correlated trajectories are separate measurements.',
            'status': 'supported' if scores_improved else 'contradicted',
            'evidence': [{'artifact': 'evidence/review.json'}]},
        'TargetFortImprovement': {
            'claim': 'No target/color fort-win regression versus lane:v1 and positive aggregate win gain.',
            'status': 'supported' if forts_improved else 'contradicted',
            'evidence': [{'artifact': 'evidence/review.json'}]},
        'TargetQualification': {
            'claim': 'All six cells achieve >=30/40 fort wins and own score strictly above and >=1.10x rival mean. Fort gate: ' + str(result['fort_passed']) + '; score gate: ' + str(result['score_passed']) + '.',
            'status': 'supported' if result['fort_passed'] and result['score_passed'] else 'contradicted',
            'evidence': [{'artifact': 'evidence/practiced/plan.json'}, {'artifact': 'evidence/practiced/result.json'}]},
        'Generalization': {
            'claim': 'Current evidence does not establish mixed-team superiority, current successors, a #1 rank, or general per-component causality. Draft reactions are public; target identities are evaluation metadata only.',
            'status': 'requires_review', 'evidence': [{'artifact': 'evidence/review.json'}]}}
    p['update'] = {
        'revision': 4, 'parent': initial_ir,
        'change': {'origin': 'Completed user-requested micropractice and six-cell hosted target comparison; retained evaluated BASIC exactly',
                   'source': 'User: practice last hitting, optimizing XP, item upgrades and town portals'},
        'needs_review': ['belief/Generalization'] + ([] if result['score_passed'] else ['belief/TargetQualification']),
        'evidence': [{'artifact': 'evidence/experiment.md'}, {'artifact': 'evidence/review.json'}]}
    ir.refresh_grounding(p)
    assert ir.compile_policy(p).encode() == source
    assert ir.extract(source.decode(), p) == p
    PAIR.mkdir(parents=True)
    h.write(PAIR / 'policy.ir.json', p)
    h.write(PAIR / 'extracted.ir.json', p)
    h.write(PAIR / 'semantics.json', ir.grounded(p))
    (PAIR / 'policy.bas').write_bytes(source)
    (PAIR / 'policy.py').write_text('"""Practiced semantic policy; claims are scoped to preserved evidence."""\n\nPOLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    for name in ('targets20260922', 'week20260921'):
        shutil.copytree(HERE.parent / name, PAIR / 'tooling' / name,
                        ignore=shutil.ignore_patterns('__pycache__'))
    copy_file(HERE / 'verify_pair.py', PAIR / 'verify.py')
    copy_file(HERE / 'convert_pair.py', PAIR / 'convert.py')
    evidence = PAIR / 'evidence'
    for source_name, saved_name in [('build-proof.json', 'engine-build-proof.json'),
                                    ('calibration.json', 'engine-calibration.json')]:
        copy_file(practiced.PARENT / 'evidence' / source_name, evidence / saved_name)
    for name in ('local-plan.json', 'local-result.json', 'practiced-local-plan.json', 'practiced-local-result.json',
                 'practice-baseline.json', 'practice-timing.json', 'practice-growth.json', 'practice-potions.json',
                 'practice-practiced.json', 'practiced-scenarios-r2.json', 'growth-scenarios.json', 'potions-scenarios.json',
                 'confirmation-rationale.json', 'review.json', 'events-review.json', 'practice-report.md', 'build-proof.json', 'conversion-checks.json'):
        copy_file(STUDY / name, evidence / name)
    for label in ('baseline', 'practiced'):
        for name in ('plan.json', 'result.json'):
            copy_file(STUDY / label / name, evidence / label / name)
        for target in ('relh', 'jordan', 'richard'):
            for side in (0, 1):
                src = STUDY / label / target / str(side)
                dst = evidence / label / target / str(side)
                for name in ('arm.json', 'request.json', 'trajectory-correlation.json'):
                    copy_file(src / name, dst / name)
                h.write(dst / 'request-id.json', {'id': h.read(src / 'batch/created.json')['id']})
    for name in ('upload-request.json', 'uploaded-version.json'):
        copy_file(STUDY / 'uploads/practiced' / name, evidence / 'uploads/practiced' / name)
    for name in ('plan.json', 'result.json'):
        copy_file(STUDY / 'preflight' / name, evidence / 'preflight' / name)
    for name in ('baseline', 'timing', 'growth', 'potions', 'practiced'):
        shutil.copytree(STUDY / 'candidates' / name, evidence / 'initial-candidates' / name)
    shutil.copytree(STUDY / 'bindings', evidence / 'initial-bindings')
    for name in ('practice-instrument-v1.nim', 'practice-instrument-v2.nim',
                 'practice-baseline-v1.log', 'practiced-scenarios.log'):
        if (STUDY / name).exists():
            copy_file(STUDY / name, evidence / 'instrument-corrections' / name)
    copy_file(h.ROOT / 'games/gods_of_the_arena/experiments/2026-09-21-targets-microplay.md', evidence / 'experiment.md')
    table = '| Opponent | Color | Baseline W/L/D | Practiced W/L/D | Practiced / rival score | Score change | Distinct streams |\n|---|---|---|---|---:|---:|---:|\n'
    baselines = {(c['target'], c['side']): c for c in review['cells'] if c['label'] == 'baseline'}
    for c in cells:
        b = baselines[c['target'], c['side']]
        outcome = lambda x: f"{x['wins']}/{x['losses']}/{x['draws']}"
        table += f"| {c['target']} | {('red', 'blue')[c['side']]} | {outcome(b)} | {outcome(c)} | {c['own_score']:.2f} / {c['opponent_score']:.2f} | {c['score_delta']:+.2f} | {c['distinct_command_streams']} |\n"
    (PAIR / 'README.md').write_text(
        '# Practiced microplay policy\n\n'
        'Primary semantic IR: `policy.py`; generated executable: `policy.bas`. Version **aaron-gota-micro0922:v1**, UUID `f3f8baab-d02a-4f7f-8fc9-e1f050f967a7`. Engine **2026.9.21.5** / `' + h.COMMIT + '`. Inert research version; no league or formal accepted-state change.\n\n'
        'Adds a one-physics-tick post-hit movement/reacquisition skill, feasible last-hit priority, Crossbowman XP proximity before stale movement throttles, four damage/HP items with potion and portal reserves, purposeful restocking, lane-directed return portals and bounded emergency defenders. Uses public observations and draft choices; no policy-ID oracle.\n\n'
        'Practice on each color: Ranger attacks **20→39** in 360 ticks; contested-wave last-hit gold **210→240**, with shared XP **300→285**; boundary Crossbowman XP **0→15**; Ranger shop damage **47→61** with unchanged 320 HP; defensive channels complete and release, safe-base controls do not portal. The XP regression remains visible. The current host has no sell/upgrade action, so equipment improvement means purchase choice and order.\n\n'
        'Four responsive native parent matches won; all state hashes replay exactly. All 126 runtime fixtures pass, maximum 13,428 instructions / 20,377 work. The first fixture had no suitable sparse XP waypoint; its corrected ground-tile setup and the old same-tick command assertion are preserved separately. Neither instrument failure is counted as a policy runtime failure.\n\n'
        'Hosted panel: **480 games**, 40 per policy/target/color. Targets relh v161, Jordan v306 and Richard v153, with exact UUIDs in the plans. Fort qualification: **' + str(result['fort_passed']) + '**; absolute rival-score qualification: **' + str(result['score_passed']) + '**.\n\n' + table +
        '\nScore is per-hero `max(0, XP - 200 * world ticks / 1440)`, including draft time. Uniform teams, fixed map and repeated streams limit generalization; the generated seeds are not a paired or independent statistical sample. Winning forts alone does not establish leaderboard superiority. Baseline discovery closed before the revised timing/XP hypothesis was frozen; two 240-game cycles shared the existing 400/cycle, 1600/day budget.\n\n'
        'Offline verification: `python3 verify.py`. Regenerate an edited Python IR with `python3 convert.py compile --policy policy.py --out /tmp/new-micro-pair`; lift BASIC edits with `python3 convert.py extract --source edited.bas --out /tmp/lifted-micro-pair`. Changed executable bytes invalidate prior belief claims automatically. Versioned compiler and all candidate pairs are preserved under `tooling/` and `evidence/`. Raw inputs/replays remain at `tmp/gota-targets-20260922`; earlier coaching captures and baseline bundles are untouched.\n')
    h.write(PAIR / 'manifest.json', {
        'at': datetime.now(timezone.utc).isoformat(), 'game_version': h.VERSION, 'engine_commit': h.COMMIT,
        'source_sha256': h.sha(source), 'ir_sha256': ir.digest(p),
        'fort_gate_passed': result['fort_passed'], 'score_gate_passed': result['score_passed'],
        'all_cell_score_improvement': scores_improved, 'fort_improvement': forts_improved,
        'artifacts': {str(x.relative_to(PAIR)): h.sha(x.read_bytes()) for x in sorted(PAIR.rglob('*')) if x.is_file()}})
    print(PAIR)


if __name__ == '__main__':
    main()
