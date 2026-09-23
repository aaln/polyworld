"""Create a separate coaching-derived semantic IR and reproducible BASIC pair."""
from pathlib import Path
import json,pprint,shutil,re
import druid_binding as b
ROOT,HERE,PARENT=b.ROOT,b.HERE,b.PARENT
STUDY=ROOT.parent/'polyworld/tmp/gota-druid-lane-20260923'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    out=STUDY/'druid-lane';assert not out.exists(),'Preserve candidate snapshots'
    p=json.loads((PARENT/'policy.ir.json').read_text());ir=b.ir;parent_digest=ir.digest(p)
    specs=b.configure();p['id']='gota_druid_lane_recovery20260923';p['execution']['binding']=b.VERSION
    oldrules={r['skill']:r for r in p['strategy']}
    predicates={'lane_recovery':'active_druid'}
    p['skill']={k:{'operator':'druidlane_'+k,'parameters':v.defaults()} for k,v in specs.items()}
    p['strategy']=[oldrules[k] if k in oldrules else {'id':'R_'+k,'when':predicates[k],'skill':k,'for':['Score','survive_and_replenish']} for k in specs]
    p['goal']['survive_and_replenish']['preference']='Druid only: stay near the current lane while useful healing can safely recover a health-only retreat. Return for an affordable missing core item, absent healing or danger. Resume farming at60%HP/20%mana; hold at most12seconds.'
    p['situation']['notes']+=' Lane recovery checks public current healing resources and affordable missing core items. A learned charged affordable heal within8seconds, a successfully used potion or pending accepted heal supports a bounded12second safe hold. No passive field HP regeneration is assumed.'
    p['belief']['claims']={
        'CoachingInterpretation':{'status':'supported','claim':'The verified recorded Druid kept walking home after healing. The previous broader field-sustain bundle failed its240game score gate. The all-class lane-recovery study also failed overall while later-draft means improved; that is a hypothesis for a new Druid-only source, not evidence of qualification.','evidence':[{'artifact':'evidence/coaching-review.json'}]},
        'RecoveryMechanism':{'status':'requires_review','claim':'Actual-tick practice must show safe lane healing through brief cooldowns, preserved useful shopping, no empty-resource wait, bounded timeout, and normal farming after recovery.','evidence':[{'artifact':'evidence/practice.json'}]},
        'CompetitiveGain':{'status':'requires_review','claim':'A fresh400game natural later-draft comparison must improve score, preserve both colors and satisfy the new frozen rule; non-Druid commands must equal the deployed baseline. Local checks cannot qualify promotion.','evidence':[{'artifact':'evidence/trial-report.json'}]}}
    p['update']={'revision':1,'parent':parent_digest,'change':{'origin':'New Druid-only hypothesis from the rejected all-class lane-recovery experiment. Fork deployed blue-center; require fresh400game comparison and preserved non-Druid commands.'},'needs_review':['belief/RecoveryMechanism','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/session-input-manifest.json'},{'artifact':'evidence/coaching-review.json'}]}
    ir.refresh_grounding(p);source=ir.compile_policy(p);assert ir.extract(source,p)==p
    out.mkdir(parents=True)
    for n,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/n,v)
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n');(out/'policy.bas').write_text(source)
    shutil.copytree(PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(HERE.parent/'lane20260923',out/'tooling/lane20260923',ignore=shutil.ignore_patterns('__pycache__'))
    (out/'tooling/druidlane20260923').mkdir();shutil.copy2(HERE/'druid_binding.py',out/'tooling/druidlane20260923/druid_binding.py')
    converter=(PARENT/'convert.py').read_text().replace('tooling/bluekhors20260923','tooling/druidlane20260923').replace('import blue_binding\nblue_binding.configure()\nir = blue_binding.ir','import druid_binding\ndruid_binding.configure()\nir = druid_binding.ir')
    (out/'convert.py').write_text(converter)
    (out/'evidence').mkdir()
    for n in ['session-input-manifest.json','coaching-review.json']:shutil.copy2(STUDY/n,out/'evidence'/n)
    manifest={'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'binding':b.VERSION,'parent_source_sha256':ir.digest((PARENT/'policy.bas').read_bytes()),'engine_commit':'1b70894436b7ffdcd0d421b6b32c2415c9c8bfde','game_version':'2026.9.22.3','hosted_complete':False,'score_gate_passed':None}
    write(out/'manifest.json',manifest)
    split=lambda s:dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)",s,re.S))
    old,new=split((PARENT/'policy.bas').read_text()),split(source)
    write(STUDY/'skill-difference.json',{'changed':[k for k in old if old[k]!=new[k]],'added':[k for k in new if k not in old],'unchanged':[k for k in old if old[k]==new[k]],'source_sha256':manifest['source_sha256']})
    print(json.dumps(manifest))
if __name__=='__main__':main()
