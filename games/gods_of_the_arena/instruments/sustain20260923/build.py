"""Create a separate coaching-derived semantic IR and reproducible BASIC pair."""
from pathlib import Path
import json,pprint,shutil,re
import sustain_binding as b
ROOT,HERE,PARENT=b.ROOT,b.HERE,b.PARENT
STUDY=ROOT.parent/'polyworld/tmp/gota-field-sustain-20260923'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    out=STUDY/'field-sustain';assert not out.exists(),'Preserve candidate snapshots'
    p=json.loads((PARENT/'policy.ir.json').read_text());ir=b.ir;parent_digest=ir.digest(p)
    specs=b.configure();p['id']='gota_field_sustain20260923';p['execution']['binding']=b.VERSION
    oldrules={r['skill']:r for r in p['strategy']}
    predicates={'recovery_refresh':'always','field_appraisal':'active','retreat_release':'recovered_in_field','field_sustain_and_push':'can_sustain_in_lane'}
    p['skill']={k:{'operator':'sustain_'+k,'parameters':v.defaults()} for k,v in specs.items()}
    p['strategy']=[oldrules[k] if k in oldrules else {'id':'R_'+k,'when':predicates[k],'skill':k,'for':['Score','survive_and_replenish']} for k in specs]
    p['goal']['survive_and_replenish']['preference']='Maximize productive map uptime: use an accepted affordable self-heal while withdrawing; take a short safe field sustain step, resume at75%HP/20%mana without a fountain detour. Preserve urgent threat escape, necessary shopping and committed portal channels.'
    p['situation']['notes']+=' Coaching session2026-09-23t02-52-57-098ze03810 concerns Druid recovery. Source/episode unbound; visual facts and unverified Gemini details separated in coaching-review. Learned ready affordable self-heal, bounded accepted-cast window and current public threat guards ground can_sustain_in_lane. All hero classes use live ability observations.'
    p['belief']['claims']={
        'CoachingInterpretation':{'status':'supported','claim':'Reviewed recording shows Druid recovery and continued homeward travel. Episode/source unbound and playback is scrubbed; exact Gemini HP values and elapsed-time claims are not accepted. Current source independently contains a fountain-only retreat latch.','evidence':[{'artifact':'evidence/coaching-review.json'}]},
        'RecoveryMechanism':{'status':'requires_review','claim':'Actual-engine practice verifies accepted self-heals, field retreat termination and same-decision path cancellation with resource/threat/channel/restock guards. No cooldown waiting or unsafe premature return.','evidence':[{'artifact':'evidence/practice.json'}]},
        'CompetitiveGain':{'status':'requires_review','claim':'Coordinated sustain and retreat-controller changes improve held-out individual score while preserving blue lead ranged performance and both late-draft color contexts. Local healing success is not a score claim.','evidence':[{'artifact':'evidence/trial-report.json'}]}}
    p['update']={'revision':1,'parent':parent_digest,'change':{'origin':'User coaching session2026-09-23t02-52-57-098ze03810; coordinate situation, belief, goals, strategy, healing and interruptible recovery control.'},'needs_review':['belief/RecoveryMechanism','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/session-input-manifest.json'},{'artifact':'evidence/coaching-review.json'}]}
    ir.refresh_grounding(p);source=ir.compile_policy(p);assert ir.extract(source,p)==p
    out.mkdir(parents=True)
    for n,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/n,v)
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n');(out/'policy.bas').write_text(source)
    shutil.copytree(PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'))
    (out/'tooling/sustain20260923').mkdir();shutil.copy2(HERE/'sustain_binding.py',out/'tooling/sustain20260923/sustain_binding.py')
    converter=(PARENT/'convert.py').read_text().replace('tooling/bluekhors20260923','tooling/sustain20260923').replace('import blue_binding\nblue_binding.configure()\nir = blue_binding.ir','import sustain_binding\nsustain_binding.configure()\nir = sustain_binding.ir')
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
