"""Freeze a separate XP-only IR fork without changing the running trial."""
import json
import pprint
import shutil
import harvest_binding as b

OUT=b.ROOT/'examples/gods_of_the_arena/players/ir/forks/harvest-value20260923-local/harvest-value'


def main():
    assert not OUT.exists(),'Preserve captured candidate'
    p=json.loads((b.PARENT/'policy.ir.json').read_text());specs=b.configure()
    parent=b.ir.digest(p)
    p['id']='gota_harvest_value20260923'
    p['execution'].update(binding=b.VERSION,game_version='2026.9.23.3')
    p['skill']={k:{'operator':'harvest61_'+k,'parameters':p['skill'][k]['parameters']} for k in specs}
    p['situation']['notes']+=' Harvest work proxy is integer basic-hit count plus travel tiles beyond reach. Creep reward15 is an upper bound before sharing, not marginal last-hit XP. Only public visible current objects are eligible.'
    p['goal']['Score']['preference']='Maximize expected individual floor(max(0,lifetime XP-200*elapsed minutes)), including draft. No team-win, survival, death-count, productive-frequency or nonzero-mean hard constraint. These are diagnostic mechanisms, not separate objectives. Accept more deaths or losses if score improves. Terminal god500 personal XP remains an economic reward.'
    p['belief']['claims']={
        'RewardWorkRanking':{'status':'requires_review','claim':'Integer XP/work ranking may find more quick hero finishes and avoid costly low-yield targets while retaining structure rewards and resource recovery. No calibration or score gain demonstrated.','evidence':[{'artifact':'README.md'}]},
        'ProxyLimitations':{'status':'requires_review','claim':'Chebyshev travel ignores obstacles; attacks/work ignores spell burst, shared XP, competing last hitters and enemy reactions. Prospective paired score test required.','evidence':[{'artifact':'README.md'}]}}
    p['update']={'revision':1,'parent':parent,'change':{'origin':'User: stop optimizing game wins; prepare XP harvesting at all costs. Use discrete math and statistical aggregation.','deployment_qualified':False},'needs_review':['belief/RewardWorkRanking','belief/ProxyLimitations'],'evidence':[{'artifact':'README.md'}]}
    b.ir.refresh_grounding(p);source=b.ir.compile_policy(p);assert b.ir.extract(source,p)==p
    OUT.mkdir(parents=True)
    for name,value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',b.ir.grounded(p))]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (OUT/'policy.bas').write_text(source)
    shutil.copytree(b.PARENT/'tooling',OUT/'tooling',ignore=shutil.ignore_patterns('__pycache__'))
    (OUT/'tooling/controltactics20260923').mkdir()
    shutil.copyfile(b.HERE/'harvest_binding.py',OUT/'tooling/controltactics20260923/harvest_binding.py')
    converter=(b.PARENT/'convert.py').read_text().replace('crowd-control legality','XP harvesting').replace('tooling/control20260923','tooling/controltactics20260923').replace('import control_binding\ncontrol_binding.configure()\nir = control_binding.ir','import harvest_binding\nharvest_binding.configure()\nir = harvest_binding.ir')
    (OUT/'convert.py').write_text(converter)
    (OUT/'manifest.json').write_text(json.dumps({'source_sha256':b.ir.digest(source.encode()),'ir_sha256':b.ir.digest(p),'binding':b.VERSION,'parent_source_sha256':b.ir.digest((b.PARENT/'policy.bas').read_bytes()),'engine_commit':'e42c4822f44e04726b09bb4ffe853152c7a18207','hosted_complete':False,'deployment_qualified':False,'stage':'Prepared exploratory fork; local native screen pending'},indent=2)+'\n')
    print(OUT)


if __name__=='__main__':main()
