"""Generate the unit-target fork and portable semantic conversion toolchain."""
from pathlib import Path
import json,pprint,shutil,re
import finish_binding as b
ROOT=b.ROOT;STUDY=ROOT.parent/'polyworld/tmp/gota-selective-finish59-20260923'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 out=STUDY/'selective-finish';assert not out.exists(),'Preserve frozen candidate'
 specs=b.configure();ir=b.ir;p=json.loads((b.PARENT/'policy.ir.json').read_text());parent=ir.digest(p)
 p['id']='gota_selective_finish59_20260923';p['execution']['binding']=b.VERSION;p['execution']['game_version']='2026.9.23.1'
 p['skill']={k:{'operator':'finish_'+k,'parameters':v.defaults()} for k,v in specs.items()}
 p['situation']['notes']+=' SelectiveFinish: visible living enemy heroes/creeps remain eligible; exposed nearby towers/god require <=two current basic hits of HP, barracks <=one; one-hit tower/barracks gets +300 target score. Buildings remain observations for safety and navigation; hidden XP and opponent identity are never live inputs.'
 p['goal']['Win']['preference']='Enemy god destruction gives500XP per teammate; permit a nearby two-hit finish. Buildings give100last-hitXP; barracks require a one-hit finish because their loss removes recurring waves.'
 p['goal']['Score']['preference']='Maximize final individual floor(max(0,lifetime XP-200*elapsed minutes)). Evaluate overall and nonzero averages together with nonzero/productive frequency; longer matches alone are not gains.'
 p['belief']['claims']['CurrentPatch']={'status':'supported','claim':'Published d6827a4/replay59: Ranger HP growth29, Crossbowman damage58, Gale Slash65, Sanguine Chalice45. Hero kills150XP, buildings100XP to killer, god500XP per teammate. Prior hosted gains belong to replay58.','evidence':[{'artifact':'evidence/release.json'}]}
 p['belief']['claims']['SelectiveFinish']={'status':'requires_review','claim':'In the coached khors179 game, all11892XP came from heroes and creeps. Coach spent18321damage on structures for500XP and then lost margin late. Restricting buildings to plausible short finishes may retain immediate rewards without prolonged siege. Barracks loss can still reduce future XP. The one selected high-score example is not causal or representative.','evidence':[{'artifact':'evidence/coaching-analysis.json'}]}
 p['belief']['claims']['CompetitiveGain']={'status':'requires_review','claim':'Requires fresh400-game comparison against exact incumbent, with improved overall score, nonzero average and productive frequency. No claim that the khors source is known or replicated.','evidence':[{'artifact':'evidence/trial-report.json'}]}
 p['update']={'revision':1,'parent':parent,'change':{'origin':'User coaching: damage alone earns no building XP; rank nearby short finishes while retaining unit farming. Only observe executable changes; all other skills retained.'},'needs_review':['belief/SelectiveFinish','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/experiment.md'},{'artifact':'evidence/coaching-analysis.json'}]}
 ir.refresh_grounding(p);source=ir.compile_policy(p);assert ir.extract(source,p)==p;out.mkdir(parents=True)
 for n,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/n,v)
 (out/'policy.bas').write_text(source);(out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
 shutil.copytree(b.PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'));(out/'tooling/productive20260923').mkdir();shutil.copy2(b.HERE/'finish_binding.py',out/'tooling/productive20260923/finish_binding.py')
 converter=(b.PARENT/'convert.py').read_text().replace('tooling/druidlane20260923','tooling/productive20260923').replace('import druid_binding\ndruid_binding.configure()\nir = druid_binding.ir','import finish_binding\nfinish_binding.configure()\nir = finish_binding.ir');(out/'convert.py').write_text(converter)
 (out/'evidence').mkdir();shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-23-selective-finish.md',out/'evidence/experiment.md');shutil.copy2(b.PARENT/'evidence/coaching-review.json',out/'evidence/coaching-review.json')
 manifest={'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'binding':b.VERSION,'parent_source_sha256':ir.digest((b.PARENT/'policy.bas').read_bytes()),'engine_commit':'d6827a4bd3a55a46cf86f88e921f147137709c64','game_version':'2026.9.23.1','hosted_complete':False,'score_gate_passed':None};write(out/'manifest.json',manifest)
 split=lambda s:dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)",s,re.S));old,new=split((b.PARENT/'policy.bas').read_text()),split(source)
 changed=[k for k in old if old[k]!=new[k]];assert changed==['R_observe'],changed
 write(STUDY/'skill-difference.json',{'changed':changed,'unchanged':[k for k in old if old[k]==new[k]],'source_sha256':manifest['source_sha256']});print(json.dumps(manifest))
if __name__=='__main__':main()
