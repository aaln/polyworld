"""Pinned v4 comparison of the two user-selected tournament policies."""
from pathlib import Path
from datetime import datetime,timezone
from policy_ir import read,write
from release_workspace import RUN
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head,result
from threat_coverage_hosted import control
from win_hosted import live
from economy_feedback import record
ROOT=RUN/'coached-lanes/r5-macromackie-v4'
DESIGN='Investigate userleague loss ereq_fbb5fabf: exactmacromackie-gota:v4 fiveheroes versusfive currentownedpolicy copies. Anchor80 and blue_repair80,40episodes/color, fixedsamegameconfig andrival. Serialdrainedbatches withfullruntime/replay/equipmentaudits. Sourceunchanged, noselection. Differentgeneratedseeds, trajectorydiversity reported; directional fixedlineup evidence, not independenttrialsignificance or widefieldproof.'
def main():
 game=live();old=read(control('gota-g002:v1')/'plan.json')
 ep=read(ROOT/'requested-episode.json');cfg={k:v for k,v in ep['game_config'].items() if k not in ('seed','players','tokens')}
 assert cfg==old['config']
 ref=ROOT/'reference';ref.mkdir(exist_ok=True)
 freeze(ref/'plan.json',old|{'rival':'macromackie-gota:v4','rival_version':'1a78a3f9-8112-4c2c-831a-f0ffee8dbacc','rival_key':'macromackie_v4'})
 versions={'anchor':{'id':'9cedf3ff-c7ce-4cff-897f-d48b44e049ad','name':'aaron-gota-ir-coordinated-support-anchor-0916','version':1},'blue_repair':{'id':'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a','name':'aaron-gota-ir-perimeter-blue_repair-0916-aaron','version':1}}
 freeze(ROOT/'prospective.json',{'design':DESIGN,'episodes_per_arm':80,'versions':versions,'promotion':False})
 for name,v in versions.items():prepare_head(ROOT/'hosted'/name,v,ref,'Macromackie v4 '+name,DESIGN)
 results={}
 for name in versions:
  results[name]=result(ROOT/'hosted'/name)
  print(name,results[name]['colors'],flush=True)
 write(ROOT/'comparison.json',{'results':results,'scope':DESIGN,'promotion_performed':False})
 src=RUN/'coached-lanes/r5-anchored-support/hosted/anchor/tournament-portfolio/policy'
 record(src/'policy.ir.json',src/'policy.bas',f'Macromackie v4 exactmatchup comparison: '+str({n:r['colors'] for n,r in results.items()})+'. No executablechange orpromotion.',ROOT/'comparison.json',ROOT/'evaluated-feedback')
if __name__=='__main__':main()
