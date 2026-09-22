"""Freeze reviewed semantic feedback without modifying captured candidate bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import pprint
import shutil
import policy

ROOT,STUDY,HERE=policy.ROOT,policy.STUDY,policy.HERE
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2)+'\n')


def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='portal-coaching20260922')
    parser.add_argument('--hosted-dir',default='hosted');a=parser.parse_args()
    out=ROOT/'examples/gods_of_the_arena/players/ir/forks'/a.name
    assert not out.exists(),'Preserve earlier reviewed bundles'
    fixtures=read(STUDY/'candidate-r3-practice-v4.json')
    assert all(r['passed'] for r in fixtures['rows'])
    native=read(STUDY/'native-result.json');assert native['passed']
    hosted_folder=STUDY/a.hosted_dir
    hosted_path=hosted_folder/'result.json'
    hosted=read(hosted_path) if hosted_path.exists() else None
    if hosted:assert hosted['complete']
    report=read(hosted_folder/'report.json') if (hosted_folder/'report.json').exists() else None
    if hosted and a.hosted_dir=='hosted-khors114':assert report and report['complete']
    policy.configure();ir=policy.ir
    p=read(STUDY/'candidate-r3/policy.ir.json');parent=ir.digest(p)
    source=(STUDY/'candidate-r3/policy.bas').read_bytes()
    p['belief']['claims']['CoachingFidelity'].update(status='supported',evidence=[{'artifact':'evidence/candidate-r3-practice-v4.json'},{'artifact':'evidence/native-result.json'},{'artifact':'evidence/review.json'}])
    p['belief']['claims']['CoachingFidelity']['claim']='The combined controller passes84 actual-tick portal fixtures on both colors plus126 all-class checks. Four complete candidate games eliminate six matched-control keep-to-home portals and complete all12 channels. These are mechanism/runtime observations, not proof of competitive gain.'
    p['belief']['claims']['CompetitiveGain'].update(status=('supported' if hosted['passed'] else 'contradicted') if hosted else 'requires_review',evidence=[{'artifact':'evidence/hosted/result.json'}] if hosted else [{'artifact':'evidence/hosted/plan.json'}])
    if report:
        p['belief']['claims']['KhorsSuperiority']={
            'claim':'On the fixed first-pick mixed roster, the candidate exceeds khors:v114 mean individual XP score by at least10% on both colors with a positive95% bootstrap lower bound. This is separate from team wins or a leaderboard-rank guarantee.',
            'status':'supported' if report['khors_superiority_passed'] else 'contradicted',
            'evidence':[{'artifact':'evidence/hosted/report.json'}]}
    p['update']={'revision':2,'parent':parent,'change':{'origin':'Validated portal coaching feedback; preserve exact candidate source','hosted_complete':hosted is not None},'needs_review':[] if hosted else ['belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/experiment.md'},{'artifact':'evidence/review.json'}]}
    ir.refresh_grounding(p);assert ir.compile_policy(p).encode()==source;assert ir.extract(source.decode(),p)==p
    out.mkdir()
    for name,value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/name,value)
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (out/'policy.bas').write_bytes(source)
    shutil.copytree(policy.PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'))
    copy(HERE/'policy.py',out/'tooling/portals20260922/portal_binding.py')
    for name in ('candidate-r3-practice-v4.json','candidate-r3-scenarios.json','baseline-practice-v2.json','native-result.json','native-plan.json','native-proof.json','diagnosis-result.json','diagnostic-plan.json','review.json','captured-inputs.json'):
        copy(STUDY/name,out/'evidence'/name)
    copy(ROOT/'games/gods_of_the_arena/experiments/2026-09-22-portal-coaching.md',out/'evidence/experiment.md')
    copy(hosted_folder/'plan.json',out/'evidence/hosted/plan.json')
    if hosted:copy(hosted_path,out/'evidence/hosted/result.json')
    if report:copy(hosted_folder/'report.json',out/'evidence/hosted/report.json')
    if a.hosted_dir=='hosted-khors114':
        copy(STUDY/'hosted/plan.json',out/'evidence/hosted/superseded-unlaunched-plan.json')
        copy(STUDY/'budget/authorization.json',out/'evidence/budget-authorization.json')
        copy(STUDY/'khors-discovery/preflight.json',out/'evidence/khors-preflight.json')
    for name in ('notes.md','session.json'):
        copy(STUDY/'captured-session'/name,out/'evidence/coaching'/name)
    synthesis=STUDY/'captured-session/synthesis/c4fba3db-929c-4868-a175-446c3aa796d0'
    copy(synthesis/'result.json',out/'evidence/coaching/synthesis.json')
    copy(synthesis/'report.md',out/'evidence/coaching/synthesis.md')
    for f in HERE.glob('*'):
        if f.is_file():copy(f,out/'evidence/instruments'/f.name)
    for name in ('candidate-r1','candidate-r2','candidate-r3'):
        shutil.copytree(STUDY/name,out/'captured'/name)
    write(out/'evidence/raw-inputs.json',{'root':str(STUDY),'files':{str(f.relative_to(STUDY)):sha(f) for f in sorted(STUDY.rglob('*')) if f.is_file() and not f.is_symlink() and 'bin' not in f.parts and f.suffix not in ('.log','.tmp')}})
    converter=(ROOT/'games/gods_of_the_arena/instruments/balance20260922/convert_followup.py').read_text()
    converter=converter.replace("'tooling/balance20260922'","'tooling/portals20260922'").replace('import draft_only\ndraft_only.configure()\nir = draft_only.build.ir','import portal_binding\nportal_binding.configure()\nir = portal_binding.ir')
    (out/'convert.py').write_text(converter)
    copy(HERE/'verify.py',out/'verify.py')
    status=('passed' if hosted['passed'] else 'failed') if hosted else 'pending: prepared160-game fresh comparison awaits completion'
    (out/'README.md').write_text(f'''# Portal coaching policy

Source **{ir.digest(source)}**, engine **2026.9.22.2 / ffcedcd**.
Hosted verdict: **{status}**. This bundle does not select a champion.

The policy commits to recovery below30% field health, gives safe home channels
priority over walking, walks to the fountain once inside the keep, and preserves
useful base-to-lane travel only when another scroll remains. Scroll buying and
live inventory accounting support this behavior. A persistent channel lock
covers the final zero-ticks boundary until host cooldown confirms completion or
interruption. Missing anchors, roots, cooldowns, recent damage and public threats
fall back to walking. It does not access replay truth or hidden opponent state.

All84 actual-tick portal cases and126 broader all-class host checks pass. Eight
matched native baseline/candidate games have exact replays: keep-to-home uses
fall6→0 across four candidate cases; all12 candidate channels complete. Native
scores are mixed and are not a competitive verdict. Diagnosis found the pattern
in all16 prespecified baseline replays (24keep-origin home trips out of124total).
The separately supplied episode has one failed rival VM and is diagnostic only.

Coaching session: `/Users/aaln/Documents/Policy Loops/sessions/2026-09-22t16-43-56-076z862811`.
Supplied episode: `ereq_2d958e27-210e-461d-b6af-b2e26dfa3a81`. The recording's
visible roster differs; they remain separate evidence. Gemini's suggestions are
reviewed interpretations. Ordinary movement does not cancel a channel in this
engine, and healthy outbound portals should not be banned. Captured originals,
including video/audio/frames, remain hash-indexed at their original and copied
raw-study paths. No captured source has been overwritten.

Edit `policy.py` and, for new executable skills, the frozen binding in
`tooling/portals20260922/portal_binding.py`. Run `python3 convert.py compile --out
<new-directory>`, reverse with `extract --source <BASIC> --out <new-directory>`,
then `python3 verify.py`. New executable bytes invalidate inherited claims.
''')
    write(out/'manifest.json',{'source_sha256':ir.digest(source),'ir_sha256':ir.digest(p),'binding':policy.BINDING,'engine_commit':policy.draft_only.build.COMMIT,'game_version':'2026.9.22.2','mechanism_validated':True,'hosted_complete':hosted is not None,'score_gate_passed':hosted['passed'] if hosted else None,'artifacts':{str(f.relative_to(out)):sha(f) for f in sorted(out.rglob('*')) if f.is_file()}})
    print(out)


if __name__=='__main__':main()
