"""Seal completed replay60 results and reflect them into the tested semantic pair."""
import hashlib
import json
from pathlib import Path
import pprint
import shutil
import subprocess
import sys
import weak_binding as b

ROOT = b.ROOT
RAW = ROOT.parent / 'polyworld/tmp/gota-weakhero60-20260923'
OUT = ROOT / 'examples/gods_of_the_arena/players/ir/forks/weakhero20260923-hosted'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    report = read(RAW / 'trial/report.json')
    assert report['complete'] and report['games'] == 400
    assert not OUT.exists(), 'Do not overwrite a sealed study'
    entry = report['candidates'][0]
    pair = OUT / 'explicit-sustain'
    shutil.copytree(RAW / 'explicit-sustain', pair, ignore=shutil.ignore_patterns('__pycache__'))
    evidence = pair / 'evidence'
    for name in ['local-summary.json', 'native-result.json', 'native-provenance-amendment.json', 'runtime-provenance.json', 'source-pin-verification.json', 'skill-difference.json', 'preflight.json', 'request.json', 'explicit-sustain-practice.json', 'baseline-practice.json', 'diagnostic-plan.json', 'diagnostic-selection.json', 'diagnostic-summary.json', 'follow-up.ir.json', 'follow-up-preliminary.ir.json']:
        shutil.copyfile(RAW / name, evidence / name)
    write(evidence / 'arcanist-coaching-reference.json', {'report': 'docs/coaching/2026-09-23-arcanist-shopping/README.md', 'episode': 'ereq_724a8b4c-122d-407d-b988-b80cd73548e8', 'scope': 'Separate retrospective diagnosis; not a candidate score evaluation.'})
    shutil.copyfile(RAW / 'survival-steering.txt', evidence / 'survival-steering.txt')
    shutil.copyfile(RAW / 'trial/report.json', evidence / 'trial-report.json')
    shutil.copyfile(RAW / 'trial/plan.json', evidence / 'trial-plan.json')
    write(evidence / 'practice.json', {'baseline': read(RAW / 'baseline-practice.json'), 'candidate': read(RAW / 'explicit-sustain-practice.json'), 'scope': read(RAW / 'local-summary.json')['scope']})
    for stage in ['before', 'submit', 'after']:
        shutil.copyfile(RAW / 'trial' / ('field-' + stage) / 'snapshot.json', evidence / ('field-' + stage + '.json'))
    plan = read(RAW / 'trial/plan.json')
    receipts = []
    for arm in plan['arms']:
        folder = RAW / 'trial' / arm['name'] / arm['cell']
        result = read(folder / 'result.json')
        receipts.append({'arm': arm, 'request_id': read(folder / 'batch/created.json')['id'], 'episodes': [r['episode'] for r in result['rows']]})
        write(evidence / 'cells' / arm['name'] / (arm['cell'] + '.json'), read(folder / 'review.json'))
    write(evidence / 'requests.json', receipts)
    # Preserve local rejections and the exploratory selection history explicitly.
    exploratory = []
    for revision in sorted((RAW / 'local-revisions').iterdir()):
        if not revision.is_dir():
            continue
        info = {'revision': revision.name, 'raw_path': str(revision)}
        manifest = revision / 'explicit-sustain/manifest.json'
        if manifest.exists():
            info['manifest'] = read(manifest)
        native = revision / 'native-result.json'
        if native.exists():
            info['native'] = read(native)
        exploratory.append(info)
    write(evidence / 'local-exploration.json', {'revisions': exploratory, 'selection_scope': 'Exploratory fixed local seeds informed source selection. Hosted400games are fresh held-out outcomes; local observations are not an independent score confirmation. Final native16 includes8reused unchanged baseline games; all exploratory raw files remain.'})
    b.configure()
    p = read(pair / 'policy.ir.json')
    initial = b.ir.digest(p)
    p['belief']['claims']['ExplicitSustainMechanism'].update(status='supported', claim='On exact replay60,220real-tick fixtures validate useful no-target healing/restoration, level2resource unlock, no casts at full resources or empty/cooling slots, portal lock, short threat disengagement and retained creep XP. Vanguard/DeathKnight retain15XP while saving70/36mana in the one-HP creep fixture. Six complete matches for unaffected classes have identical commands/terminal state; final16native games pass replay hashes and all10VM limits. Local checks do not prove a league gain.')
    p['belief']['claims']['CompetitiveGain'].update(status='supported' if report['deployment_qualified'] else 'contradicted' if not entry['score_gate_passed'] else 'requires_review', claim=f"Fresh400game replay60 gate passed={report['deployment_qualified']}. Mean score{entry['baseline_score']:.3f} to{entry['candidate_score']:.3f},gain{entry['aggregate_gain_percent']:.3f}percent,95percent interval{entry['gain_ci95_percent']}. Late-draft survival/XP gate={entry['late_survival_gate_passed']}. See all class/context/frequency results; no claim of universal rank, isolated-component causality or superiority on every hero.")
    p['update'] = {'revision': 2, 'parent': initial, 'change': {'origin': 'Completed local and fresh hosted evidence reflected into semantic IR; exact tested BASIC bytes retained.', 'deployment_qualified': report['deployment_qualified']}, 'needs_review': ['belief/CompetitiveGain'] if entry['score_gate_passed'] and not report['deployment_qualified'] else [], 'evidence': [{'artifact': 'evidence/trial-report.json'}, {'artifact': 'evidence/local-summary.json'}, {'artifact': 'evidence/local-exploration.json'}]}
    b.ir.refresh_grounding(p)
    source = (pair / 'policy.bas').read_text()
    assert b.ir.compile_policy(p) == source and b.ir.extract(source, p) == p
    for name, value in [('policy.ir.json', p), ('extracted.ir.json', p), ('semantics.json', b.ir.grounded(p))]:
        write(pair / name, value)
    (pair / 'policy.py').write_text('POLICY = ' + pprint.pformat(p, width=110, sort_dicts=False) + '\n')
    (pair / 'verify.py').write_text('''from pathlib import Path
import json, hashlib, sys
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / 'tooling/weakhero20260923'))
import weak_binding as b
b.configure()
read = lambda p: json.loads(p.read_text())
m, p = read(P/'manifest.json'), read(P/'policy.ir.json')
s = (P/'policy.bas').read_text()
assert b.ir.compile_policy(p) == s and b.ir.extract(s, p) == p
assert b.ir.digest(p) == m['ir_sha256']
for name, digest in m['artifacts'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest() == digest, name
assert read(P/'evidence/local-summary.json')['passed']
assert read(P/'evidence/trial-report.json')['complete']
print(json.dumps({'verified': True, 'source_sha256': m['source_sha256'], 'ir_sha256': m['ir_sha256'], 'deployment_qualified': m['deployment_qualified']}))
''')
    (pair / 'README.md').write_text('''# Explicit sustain and cautious melee farming on replay60

The frozen source changes Vanguard/DeathKnight recovery and close-threat spacing, plus Arcanist/Warlock mana restoration. These four classes unlock their resource ability from level2 and avoid redundant same-decision lethal creep casts. Other classes retain their behavior. Broad melee variants were rejected in local exploration; see evidence/local-exploration.json.

Run `python verify.py`. Recompile with `python convert.py compile --out /new/path`; extract with `python convert.py extract --source policy.bas --out /new/path`. Evidence in `evidence/trial-report.json` controls competitive qualification. Captured inputs and initial IR remain unchanged in the raw study.
''')
    manifest = read(pair / 'manifest.json')
    manifest.update(ir_sha256=b.ir.digest(p), initial_ir_sha256=initial, hosted_complete=True, score_gate_passed=entry['score_gate_passed'], deployment_qualified=report['deployment_qualified'])
    manifest['artifacts'] = {str(f.relative_to(pair)): sha(f) for f in pair.rglob('*') if f.is_file() and f.name != 'manifest.json' and '__pycache__' not in f.parts}
    write(pair / 'manifest.json', manifest)
    write(OUT / 'summary.json', {'trial': entry, 'deployment_qualified': report['deployment_qualified'], 'source_sha256': manifest['source_sha256'], 'ir_sha256': manifest['ir_sha256']})
    (OUT / 'README.md').write_text(f"# Weak-hero score and survival study\n\nFresh400game replay60 comparison: mean score{entry['baseline_score']:.2f} to{entry['candidate_score']:.2f} ({entry['aggregate_gain_percent']:+.2f}percent). Deployment qualified: {report['deployment_qualified']}.\n\n[Reviewed IR/policy pair](explicit-sustain/README.md), [complete score, survival and XP results](explicit-sustain/evidence/trial-report.json), [local exploration](explicit-sustain/evidence/local-exploration.json). Baseline source29f6d7e6; exact gamefd315c8.\n")
    write(OUT / 'raw-input-manifest.json', {'raw_root': str(RAW), 'artifacts': {str(f.relative_to(RAW)): sha(f) for f in RAW.rglob('*') if f.is_file() and '__pycache__' not in f.parts and 'bin' not in f.relative_to(RAW).parts}})
    subprocess.run([sys.executable, str(pair / 'verify.py')], check=True)
    print(OUT)


if __name__ == '__main__':
    main()
