"""Reflect the complete hosted result into the exact tested Druid lane recovery pair."""
import json
import pprint
import shutil
import subprocess
import sys

import publish_local as local
from publish_local import ROOT, STUDY, read, sha, write

OUT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted'


def main():
    report = read(STUDY / 'trial/report.json')
    assert report['complete'] and report['games'] == 400
    assert len(read(STUDY / 'trial/effects-summary.json')['rows']) == 16
    assert not OUT.exists(), 'Preserve sealed result capsules'
    prior = local.OUT / 'druid-lane'
    pair = OUT / 'druid-lane'
    shutil.copytree(prior, pair, ignore=shutil.ignore_patterns('__pycache__'))
    evidence = OUT / 'evidence'
    evidence.mkdir()
    for name in ['plan.json', 'result.json', 'report.json', 'field-changes.json',
                 'effects-plan.json', 'effects-summary.json', 'score-breakdown.png']:
        shutil.copy2(STUDY / 'trial' / name, evidence / name)
    for label in ['field-before', 'field-after', 'field-submit']:
        (evidence / label).mkdir()
        for name in ['snapshot.json', 'game.json', 'leaderboard.json']:
            shutil.copy2(STUDY / 'trial' / label / name, evidence / label / name)
    for arm in read(STUDY / 'trial/plan.json')['arms']:
        src = STUDY / 'trial' / arm['name'] / arm['cell']
        dst = evidence / arm['name'] / arm['cell']
        dst.mkdir(parents=True)
        for name in ['arm.json', 'request.json', 'episodes.json', 'review.json']:
            shutil.copy2(src / name, dst / name)
        shutil.copy2(src / 'batch/created.json', dst / 'created.json')
    shutil.copy2(STUDY / 'budget/authorization.json', evidence / 'budget-authorization.json')
    inherited = ROOT.parent / 'polyworld/tmp/gota-lane-recovery-20260923'
    write(evidence / 'effect-audit-provenance.json', {
        'source_sha256': sha(ROOT / 'games/gods_of_the_arena/instruments/druidlane20260923/effect_audit.nim'),
        'binary_sha256': sha(STUDY / 'sustain-effect-audit'),
        'inherited_from': str(inherited),
        'inherited_source_sha256': sha(ROOT / 'games/gods_of_the_arena/instruments/lane20260923/effect_audit.nim'),
        'inherited_binary_sha256': sha(inherited / 'sustain-effect-audit'),
        'scope': 'Auditor and affordability metric inherited unchanged before the Druid-only trial; diagnostic subset only.'})
    assert sha(STUDY / 'sustain-effect-audit') == sha(inherited / 'sustain-effect-audit')
    shutil.copy2(STUDY / 'trial/report.json', pair / 'evidence/trial-report.json')
    shutil.copy2(STUDY / 'trial/effects-summary.json', pair / 'evidence/effects-summary.json')
    b = local.b
    b.configure()
    ir = b.ir
    p = read(prior / 'policy.ir.json')
    parent = ir.digest(p)
    entry = report['candidates'][0]
    p['belief']['claims']['CompetitiveGain'].update(
        status='supported' if report['deployment_qualified'] else 'contradicted',
        claim=f"The frozen 400-game qualification rule was met: {report['deployment_qualified']}. "
              f"Aggregate mean score change {entry['aggregate_gain_percent']:.3f}%, "
              f"95% gain interval {entry['gain_ci95_percent']}; context changes "
              f"{entry['per_context_gain_percent']}. Druid exposure {entry['druid_exposure']}. "
              'This decision applies to the frozen two-color later-draft roster and complete candidate; '
              'it does not establish universal ranking, certain population harm on rejection, '
              'or the causal value of a single component.',
        evidence=[{'artifact': 'evidence/trial-report.json'}, {'artifact': 'evidence/effects-summary.json'}])
    p['update'] = {
        'revision': 3, 'parent': parent,
        'change': {'origin': 'Complete hosted score and effect evidence reflected into IR; tested BASIC unchanged.',
                   'deployment_qualified': report['deployment_qualified']},
        'needs_review': [], 'evidence': [{'artifact': 'evidence/trial-report.json'}]}
    ir.refresh_grounding(p)
    source = (prior / 'policy.bas').read_text()
    assert ir.compile_policy(p) == source and ir.extract(source, p) == p
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', ir.grounded(p))]:
        write(pair / name, value)
    (pair / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    verifier = (pair / 'verify.py').read_text().replace("'competitive_validation':'pending'", "'deployment_qualified':m['deployment_qualified']")
    (pair / 'verify.py').write_text(verifier)
    manifest = read(prior / 'manifest.json')
    manifest.update(ir_sha256=ir.digest(p), hosted_complete=True,
                    deployment_qualified=report['deployment_qualified'], score_gate_passed=entry['score_gate_passed'])
    manifest['artifacts'] = {str(f.relative_to(pair)): sha(f) for f in pair.rglob('*')
                             if f.is_file() and f.name != 'manifest.json' and '__pycache__' not in f.parts}
    write(pair / 'manifest.json', manifest)
    subprocess.run([sys.executable, str(pair / 'verify.py')], check=True)
    write(evidence / 'artifact-index.json', {'raw_root': str(STUDY), 'artifacts': {
        str(f.relative_to(STUDY)): sha(f) for f in (STUDY / 'trial').rglob('*')
        if f.is_file() and f.suffix not in ['.log', '.tmp']}})
    write(OUT / 'summary.json', {
        'trial': entry, 'deployment_qualified': report['deployment_qualified'],
        'source_sha256': manifest['source_sha256'], 'ir_sha256': manifest['ir_sha256']})
    print(OUT)


if __name__ == '__main__':
    main()
