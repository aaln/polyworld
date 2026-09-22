"""Freeze local feedback into a portable IR/source pair without qualifying it."""
from pathlib import Path
import hashlib
import json
import pprint
import shutil
import statistics
import score_binding

ROOT,HERE=score_binding.ROOT,score_binding.HERE
STUDY=ROOT.parent/'polyworld/tmp/gota-score-20260922'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    out=ROOT/'examples/gods_of_the_arena/players/ir/forks/score-opportunities20260922'
    assert not out.exists()
    original=STUDY/'candidate-r3'
    for name in ['practice-r3-v2','portals-r3']:
        assert all(r['passed'] for r in read(STUDY/(name+'.json'))['rows'])
    assert read(STUDY/'native-result.json')['passed']
    assert read(STUDY/'hosted/plan.json')['games']==160
    shutil.copytree(original,out,ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(HERE/'score_binding.py',out/'tooling/score20260922/score_binding.py')
    shutil.copy2(HERE/'verify.py',out/'verify.py')
    score_binding.configure();ir=score_binding.ir
    p=read(original/'policy.ir.json');parent=ir.digest(p)
    p['belief']['claims']['OpportunityMechanism'].update(status='supported',claim='On replay58,180 artificial host fixtures pass on all ten classes/both colors, including realized150XP hero kills and500XP god finishes. Parent differs in60 intended choices. Complete native games show changed XP allocation; hero XP falls on red and rises on blue. Mechanism scope only, no competitive score claim.',evidence=[{'artifact':'evidence/practice-r3-v2.json'},{'artifact':'evidence/practice-baseline-v2.json'},{'artifact':'evidence/native-summary.json'}])
    p['belief']['claims']['PortalPreserved'].update(status='supported',claim='All84 existing portal fixtures pass on current replay58 with the combined candidate;126 all-class/runtime checks also pass. No claim that live aggregate recall frequency is unchanged.',evidence=[{'artifact':'evidence/portals-r3.json'},{'artifact':'evidence/scenarios-r3.json'}])
    p['update']={'revision':2,'parent':parent,'change':{'origin':'Validated local behavior and current-engine calibration reflected into IR; source unchanged. Hosted comparison prepared, not run.'},'needs_review':['belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/experiment.md'},{'artifact':'evidence/calibration58.json'},{'artifact':'evidence/hosted-plan.json'}]}
    ir.refresh_grounding(p)
    assert ir.compile_policy(p)==(original/'policy.bas').read_text()
    assert ir.extract((original/'policy.bas').read_text(),p)==p
    for name,value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/name,value)
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    evidence=out/'evidence';evidence.mkdir()
    for name in ['bootstrap58.json','practice-v2-proof.json','practice-r3.json','practice-r3-v2.json','practice-baseline-v2.json','portals-r3.json','scenarios-r3.json','native-plan.json','native-result.json','calibration58.json','preflight.json','roster-template.json','roster-template-v2.json']:
        shutil.copy2(STUDY/name,evidence/name)
    shutil.copy2(STUDY/'hosted/plan.json',evidence/'hosted-plan.json')
    shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-22-score-opportunities.md',evidence/'experiment.md')
    for name in ['candidate-r1','candidate-r2','candidate-r3']:
        shutil.copytree(STUDY/name,out/'captured'/name,ignore=shutil.ignore_patterns('__pycache__'))
    rows=[]
    for r in read(STUDY/'native-result.json')['rows']:
        folder=STUDY/'native'/r['name']/str(r['side'])/str(r['seed'])
        a=read(folder/'audit.json');e=read(folder/'economy.json')['heroes'][r['side']*5]
        god=500 if a['fort_hp'][1-r['side']]<=0 else 0
        rows.append({'name':r['name'],'side':r['side'],'seed':r['seed'],'score':r['hero']['score'],'xp':e['total_xp'],'hero_xp':e['xp_sources'].get('hero',0),'creep_xp':e['xp_sources'].get('creep',0),'god_xp':god,'building_xp':e['xp_sources'].get('structure_or_other',0)-god,'kills':e['hero_kills'],'deaths':e['deaths'],'minutes':r['ticks']/1440})
        dest=evidence/'native'/r['name']/str(r['side'])/str(r['seed']);dest.mkdir(parents=True)
        for name in ['economy.json','audit.json','live.json','command.json']:shutil.copy2(folder/name,dest/name)
    summary={'rows':rows,'scope':'Eight complete native games, four source/color pairs against nine host reference bots. Not hosted rivals or competitive confirmation.'}
    summary['means']={name:{k:statistics.mean(r[k] for r in rows if r['name']==name) for k in ['score','xp','hero_xp','creep_xp','building_xp','god_xp','kills','deaths','minutes']} for name in ['baseline','candidate-r3']}
    write(evidence/'native-summary.json',summary)
    write(evidence/'provenance.json',{'raw_root':str(STUDY),'session_references':['../portal-coaching20260922-hosted/evidence/coaching/notes.md','/Users/aaln/Documents/Policy Loops/sessions/2026-09-22t16-43-56-076z862811'],'inputs':'Original coaching captures and frozen portal pair preserved unchanged; score work derives from user stats/individual-XP directions.','artifacts':{str(f.relative_to(STUDY)):sha(f) for f in STUDY.rglob('*') if f.is_file() and not f.is_symlink() and '__pycache__' not in f.parts and 'bin' not in f.parts and 'bin58' not in f.parts}})
    (out/'README.md').write_text('''# Individual XP opportunity candidate

Current game2026.9.22.3 /1b708944, replay58. **Hosted quality unvalidated; not
deployed.** Source f6a0dace is a fork of deployed portal source db71abb3.

Rank reachable finishing heroes against creep XP and routine structures, using
public health/distance/damage and final nearby force/tower context. Avoid
expensive chases; preserve critical recovery and portals. The new patch grants
500XP per teammate for god destruction, so an exposed god within basic reach
and four raw hits gets finishing priority. Utility scores are heuristics, not
calibrated expected XP; fog and armor can invalidate them. There is no hidden
opponent identity, private replay input, or invented live XP query.

The score remains max(0, XP*1440-200*world_ticks)//1440. Hero kill150XP,
shared creep pool15XP, building100XP, god500XP. Do not maximize game duration
unconditionally: every extra minute costs200XP.

All180 opportunity fixtures,84portal fixtures and126all-class/runtime checks
pass. Eight native games have exact replay/hash/XP/score checks, with four
matched score improvements: means3321→4166.75. Hero XP decreases on red and
increases on blue; the combined mean rises2325→2550. These native diagnostics
are not league evidence. Calibration matches a complete replay58 hosted game;
one other VM failed in that calibration game, so it proves decoder parity only.

A fresh160-game comparison is prepared against db71abb3, both colors, with
khors114/Jordan411/Richard167 opposing. No new games created. September22
budget1760/1760 is exhausted; additional games require user authorization or
the normal UTC reset. Promotion still requires the frozen score gate and
complete hosted audits. The deployed pair remains unchanged.

Edit policy.py and tooling/score20260922/score_binding.py, then use
`python3 convert.py compile --out <new-directory>` and
`python3 convert.py extract --source <BASIC> --out <new-directory>`.
`python3 verify.py` checks exact round-trip and evidence hashes. Changed
executable bytes invalidate inherited validation claims. Captured r1/r2 and
the initial fixture's automatic-acquisition ambiguity remain preserved.
''')
    m=read(original/'manifest.json');m.update(ir_sha256=ir.digest(p),mechanism_validated=True,hosted_complete=False,score_gate_passed=None,artifacts={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts})
    write(out/'manifest.json',m)
    print(json.dumps({'pair':str(out),'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256']}))


if __name__=='__main__':main()
