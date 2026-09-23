"""Generate a fresh semantic IR/BASIC pair without altering its qualified parent."""
from pathlib import Path
import json,pprint,shutil,re
import return_binding as b
ROOT,STUDY=b.ROOT,b.ROOT.parent/'polyworld/tmp/gota-productive-return59-20260923'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    out=STUDY/'productive-return';assert not out.exists(),'Preserve frozen source'
    specs=b.configure();ir=b.ir;p=json.loads((b.PARENT/'policy.ir.json').read_text());parent=ir.digest(p)
    p['id']='gota_productive_return59_20260923';p['execution']['binding']=b.VERSION
    p['execution']['game_version']='2026.9.23.1'
    p['belief']['claims']['CurrentPatch']={'status':'supported','claim':'Published d6827a4: Ranger HP growth29, Crossbowman damage58, Gale Slash65, Sanguine Chalice45. Score formula unchanged. Parent hosted gains belong to replay58; this source requires fresh replay59 controls.','evidence':[{'artifact':'evidence/release.json'}]}
    rules={r['skill']:r for r in p['strategy']}
    p['skill']={k:{'operator':'productive_'+k,'parameters':v.defaults()} for k,v in specs.items()}
    p['strategy']=[rules[k] if k in rules else {'id':'R_'+k,'when':'active','skill':k,'for':['Score']} for k in specs]
    p['situation']['notes']+=' Ready outbound scroll and lane-aligned friendly anchor support faster productive reentry; public current observations only, no raw XP or opponent identity.'
    p['goal']['Score']['preference']='Maximize final individual floor(max(0, lifetime XP - 200 * elapsed minutes)). Evaluate whole-sample mean, nonzero mean and productive frequency jointly; do not optimize conditional mean by increasing zeroes. Productive is score>=500 in evaluation, not a live hidden-state input.'
    p['belief']['claims']['ProductiveReturn']={'status':'requires_review','claim':'Khors uses more outbound portals per appearance. Our source requires two scrolls despite a ready single scroll, and blue opening anchor selection differs from its central route. Earlier safe lane reentry may increase XP after time cost, but can lose a future recall reserve. Actual-host practice and fresh score comparison must decide this coordinated change.','evidence':[{'artifact':'evidence/diagnosis.json'},{'artifact':'evidence/local-summary.json'}]}
    p['belief']['claims']['CompetitiveGain']={'status':'requires_review','claim':'The new source must independently pass the frozen400game score, nonzero-average and productive-frequency rule against current Druid controls; inherited gains do not qualify it.','evidence':[{'artifact':'evidence/trial-report.json'}]}
    p['update']={'revision':1,'parent':parent,'change':{'origin':'User prioritizes productive-game score, nonzero average and productive frequency. One productive outbound-return behavior: spend a ready single scroll and align its anchor with the active lane. Preserve all other inherited skills.'},'needs_review':['belief/ProductiveReturn','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/experiment.md'}]}
    ir.refresh_grounding(p);source=ir.compile_policy(p);assert ir.extract(source,p)==p
    out.mkdir()
    for n,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/n,v)
    (out/'policy.bas').write_text(source);(out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    shutil.copytree(b.PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'));(out/'tooling/productive20260923').mkdir();shutil.copy2(b.HERE/'return_binding.py',out/'tooling/productive20260923/return_binding.py')
    converter=(b.PARENT/'convert.py').read_text().replace('tooling/druidlane20260923','tooling/productive20260923').replace('import druid_binding\ndruid_binding.configure()\nir = druid_binding.ir','import return_binding\nreturn_binding.configure()\nir = return_binding.ir');(out/'convert.py').write_text(converter)
    (out/'evidence').mkdir();shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-23-productive-return.md',out/'evidence/experiment.md')
    shutil.copy2(b.PARENT/'evidence/coaching-review.json',out/'evidence/coaching-review.json')
    manifest={'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'binding':b.VERSION,'parent_source_sha256':ir.digest((b.PARENT/'policy.bas').read_bytes()),'engine_commit':'d6827a4bd3a55a46cf86f88e921f147137709c64','game_version':'2026.9.23.1','hosted_complete':False,'score_gate_passed':None};write(out/'manifest.json',manifest)
    split=lambda s:dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)",s,re.S))
    old,new=split((b.PARENT/'policy.bas').read_text()),split(source);write(STUDY/'skill-difference.json',{'changed':[k for k in old if old[k]!=new[k]],'added':[k for k in new if k not in old],'unchanged':[k for k in old if old[k]==new[k]],'source_sha256':manifest['source_sha256']});print(json.dumps(manifest))
if __name__=='__main__':main()
