"""Generate our coordinated source-informed candidate from current semantic IR."""
from pathlib import Path
import json,pprint,shutil,re
import pressure_binding as b
ROOT,STUDY=b.ROOT,b.ROOT.parent/'polyworld/tmp/gota-richard174-source-20260923'
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    out=STUDY/'guarded-siege';assert not out.exists(),'Preserve frozen source'
    specs=b.configure();ir=b.ir;p=json.loads((b.PARENT/'policy.ir.json').read_text());parent=ir.digest(p)
    p['id']='gota_guarded_siege20260923';p['execution']['binding']=b.VERSION
    rules={r['skill']:r for r in p['strategy']}
    p['skill']={k:{'operator':'siege_'+k,'parameters':v.defaults()} for k,v in specs.items()}
    p['strategy']=[rules[k] if k in rules else {'id':'R_'+k,'when':'active','skill':k,'for':['Score']} for k in specs]
    p['situation']['notes']+=' Public exposed tower, allied wave cover and self-targeted in-range enemy hero predicates support guarded siege pressure. All other current host facts and Druid lane recovery remain.'
    p['belief']['claims']['RichardSourceTransfer']={'status':'requires_review','claim':'Richard v174 source reconstructs82818commands and every state hash across4Warlock games; structure mode frequent and siege-retaliation guard141times. Four exact current-source games show109 guarded structure opportunities while selecting nonlethal creeps. These are descriptive diagnosis; our coordinated transfer must pass local safety/choice checks and fresh score comparison.','evidence':[{'artifact':'evidence/opponent/richard_v174.source.ir.json'},{'artifact':'evidence/own-diagnosis.json'}]}
    # Parent CompetitiveGain is explicitly scoped to the inherited Druid study.
    p['belief']['claims']['CompetitiveGain']={'status':'requires_review','claim':'The full new siege candidate must qualify independently against the newly deployed Druid source; parent gains do not validate this transfer.','evidence':[{'artifact':'evidence/trial-report.json'}]}
    p['update']={'revision':1,'parent':parent,'change':{'origin':'User-requested Richard174 source-informed transfer: guarded structure pressure and siege retaliation as one coordinated behavior.'},'needs_review':['belief/RichardSourceTransfer','belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/opponent/provenance.json'}]}
    ir.refresh_grounding(p);source=ir.compile_policy(p);assert ir.extract(source,p)==p
    out.mkdir()
    for n,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/n,v)
    (out/'policy.bas').write_text(source);(out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    shutil.copytree(b.PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'));(out/'tooling/richard17420260923').mkdir();shutil.copy2(b.HERE/'pressure_binding.py',out/'tooling/richard17420260923/pressure_binding.py')
    converter=(b.PARENT/'convert.py').read_text().replace('tooling/druidlane20260923','tooling/richard17420260923').replace('import druid_binding\ndruid_binding.configure()\nir = druid_binding.ir','import pressure_binding\npressure_binding.configure()\nir = pressure_binding.ir');(out/'convert.py').write_text(converter)
    shutil.copytree(ROOT/'docs/opponents/richard-v174/source-audit-20260923',out/'evidence/opponent')
    rows=[json.loads(f.read_text()) for f in (STUDY/'own-audits-r2').glob('*/result.json')];assert len(rows)==4 and all(x['all_state_hashes_equal'] for x in rows);write(out/'evidence/own-diagnosis.json',{'rows':rows,'opportunities':sum(x['counts'].get('safe_tower_opportunity_while_nonlethal_creep_selected',0) for x in rows),'scope':'Retrospective current-source diagnosis, not transfer evidence.'})
    manifest={'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'binding':b.VERSION,'parent_source_sha256':ir.digest((b.PARENT/'policy.bas').read_bytes()),'engine_commit':'1b70894436b7ffdcd0d421b6b32c2415c9c8bfde','game_version':'2026.9.22.3','hosted_complete':False,'score_gate_passed':None};write(out/'manifest.json',manifest)
    split=lambda s:dict(re.findall(r"' @rule (\w+)\n(.*?)(?=\n' @rule |\Z)",s,re.S))
    old,new=split((b.PARENT/'policy.bas').read_text()),split(source);write(STUDY/'skill-difference.json',{'changed':[k for k in old if old[k]!=new[k]],'added':[k for k in new if k not in old],'unchanged':[k for k in old if old[k]==new[k]],'source_sha256':manifest['source_sha256']});print(json.dumps(manifest))
if __name__=='__main__':main()
