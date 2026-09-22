"""Save hosted feedback in a new pair; preserve locally reviewed inputs."""
from pathlib import Path
import hashlib
import json
import pprint
import shutil
import score_binding

ROOT,HERE=score_binding.ROOT,score_binding.HERE
STUDY=ROOT.parent/'polyworld/tmp/gota-score-20260922'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    parent=ROOT/'examples/gods_of_the_arena/players/ir/forks/score-opportunities20260922'
    out=parent.with_name('score-opportunities20260922-hosted')
    assert not out.exists(),'Preserve existing reviewed pairs'
    report=read(STUDY/'hosted/report.json');result=read(STUDY/'hosted/result.json')
    assert report['complete'] and report['games']==160
    shutil.copytree(parent,out,ignore=shutil.ignore_patterns('__pycache__','captured'))
    score_binding.configure();ir=score_binding.ir
    p=read(parent/'policy.ir.json');old=ir.digest(p)
    passed=report['score_gate_passed']
    p['belief']['claims']['CompetitiveGain'].update(status='supported' if passed else 'contradicted',claim=f"The frozen160-game fresh-control comparison {'passed' if passed else 'failed'} the >=10% aggregate gain / >=95% each-color gate: {report['aggregate_gain_percent']:.3f}% gain, colors{report['per_color_gain_percent']},95% bootstrap interval{report['gain_ci95_percent']}. Fixed first-pick roster only; does not establish universal superiority or rank.",evidence=[{'artifact':'evidence/hosted/report.json'},{'artifact':'evidence/hosted/result.json'}])
    p['belief']['claims']['HostedAllocation']={'claim':'Complete replay58 XP attribution separates hero/creep/building/god rewards and elapsed time for all160 games. Per-color means and uncertainty are preserved; coordinated changes do not identify component causality.','status':'supported','evidence':[{'artifact':'evidence/hosted/report.json'}]}
    p['update']={'revision':3,'parent':old,'change':{'origin':'Completed fresh hosted comparison reflected into IR; executable unchanged','score_gate_passed':passed},'needs_review':[],'evidence':[{'artifact':'evidence/hosted/report.json'},{'artifact':'evidence/hosted/plan.json'}]}
    ir.refresh_grounding(p);source=(parent/'policy.bas').read_text()
    assert ir.compile_policy(p)==source and ir.extract(source,p)==p
    for name,value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/name,value)
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    for name in ['plan.json','result.json','report.json','draft-review.json']:
        dst=out/'evidence/hosted'/name;dst.parent.mkdir(exist_ok=True);shutil.copy2(STUDY/'hosted'/name,dst)
    for arm in read(STUDY/'hosted/plan.json')['arms']:
        folder=STUDY/'hosted'/arm['name']/str(arm['side'])
        dst=out/'evidence/hosted'/arm['name']/str(arm['side']);dst.mkdir(parents=True)
        for name in ['review.json','episodes.json','arm.json','request.json']:
            shutil.copy2(folder/name,dst/name)
        shutil.copy2(folder/'batch/created.json',dst/'created.json')
    shutil.copy2(STUDY/'budget/authorization-10000.json',out/'evidence/budget-authorization-10000.json')
    shutil.copytree(HERE,out/'evidence/hosted/instruments',ignore=shutil.ignore_patterns('__pycache__'))
    manifest=read(parent/'manifest.json')
    manifest.update(ir_sha256=ir.digest(p),hosted_complete=True,score_gate_passed=passed)
    verifier=(HERE/'verify.py').read_text()
    verifier=verifier.replace("assert p['belief']['claims']['CompetitiveGain']['status']=='requires_review'\nassert m['hosted_complete'] is False", "r=read(pair/'evidence/hosted/report.json')\nassert r['complete'] and r['score_gate_passed']==m['score_gate_passed']\nassert m['hosted_complete'] is True\nassert p['belief']['claims']['CompetitiveGain']['status']==('supported' if r['score_gate_passed'] else 'contradicted')")
    verifier=verifier.replace("'hosted_complete':False", "'hosted_complete':True,'score_gate_passed':m['score_gate_passed']")
    (out/'verify.py').write_text(verifier)
    lines=['# Hosted individual-score policy comparison','',f"Source **{manifest['source_sha256']}**, game2026.9.22.3 /1b708944.",f"Frozen score gate: **{'passed' if passed else 'failed'}**. Mean{report['baseline_score']:.2f}→{report['candidate_score']:.2f} ({report['aggregate_gain_percent']:+.2f}%).95% gain interval{report['gain_ci95_percent']}.",'','| Source | Color | Score | Hero XP | Creep XP | Building XP | God XP | Minutes | Invalid |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in report['cells']:
        m=c['means'];lines.append(f"| {c['name']} | {'Blue' if c['side'] else 'Red'} | {m['score']:.2f} | {m['hero_xp']:.2f} | {m['creep_xp']:.2f} | {m['building_xp']:.2f} | {m['god_xp']:.2f} | {m['minutes']:.2f} | {c['invalid']} |")
    lines.extend(['','All ten source identities and VM exits, every replay hash, XP attribution and integer scores audited. Duplicate streams and paired rival intervals are in report.json. Khors114/Jordan411/Richard167 oppose both sides; relh161 is a teammate. Fixed first-pick teams do not establish #1 or general strength.','', 'The controller prioritizes reachable hero finishes and creep income, checks public force/tower context, and values a near-dead exposed god for500ownXP. The combined change preserves390host fixture passes; competitive feedback applies to this exact source only.','', 'The original local pair, failed r1/r2 and original coaching captures remain unchanged in sibling score-opportunities20260922 and portal-coaching20260922-hosted. This reviewed pair does not by itself select a league champion.','', 'Use convert.py compile/extract and verify.py for exact semantic/source round-trip. Edited executables invalidate these evidence claims.'])
    (out/'README.md').write_text('\n'.join(lines)+'\n')
    write(out/'evidence/hosted/artifact-index.json',{'raw_root':str(STUDY),'artifacts':{str(f.relative_to(STUDY)):sha(f) for f in (STUDY/'hosted').rglob('*') if f.is_file() and f.suffix not in ('.log','.tmp')}})
    manifest['artifacts']={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file() and f!=out/'manifest.json' and '__pycache__' not in f.parts}
    write(out/'manifest.json',manifest)
    print(json.dumps({'pair':str(out),'ir_sha256':manifest['ir_sha256'],'source_sha256':manifest['source_sha256'],'score_gate_passed':passed}))


if __name__=='__main__':main()
