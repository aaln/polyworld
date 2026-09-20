"""Check recall thresholds in the actual VM; this is not a gameplay win test."""
from copy import deepcopy
import test_policy_ir as f
import test_rush_unblock as u
from test_shared_engagement import defense_case
from anchored_support import make
from policy_ir import compile_policy,extract,refresh_grounding,write
from macromackie_review import ROOT
class Probe(u.UnblockTests):
 @staticmethod
 def factory(name):
  p=make('anchor' if name!='blue_repair' else 'deployed')
  if name=='three':
   p=deepcopy(p);p['skill']['observe']['parameters']['redbranch_group_size']=3;refresh_grounding(p)
  assert extract(compile_policy(p),p)==p
  return p
if __name__=='__main__':
 Probe.setUpClass();vm=Probe();results=[]
 for slot in (1,4):
  for count in (3,4):
   case=defense_case(slot,tower=True,count=count)
   case['self'].update(selfX=25,selfY=15)
   case['objects'][3+slot].update(objectX=25,objectY=15)
   for name in ('anchor','blue_repair','three'):
    r=vm.play(name,[case],('defActive','defCount','defAnchor','defUntil'))[0]
    expected=int(count>=4 or name=='three')
    assert r['memory']['defActive']==expected
    results.append({'slot':slot,'enemy_count':count,'source':name,'result':r})
 for slot in (1,4):
  a=defense_case(slot,tower=True,count=4)
  q=defense_case(slot,tower=True,count=3);q['self']['worldTick']=580
  for c in (a,q):
   c['self'].update(selfX=40,selfY=30);c['objects'][3+slot].update(objectX=40,objectY=30)
  seq=[a]+[q|{'self':q['self']|{'worldTick':tick}} for tick in range(101,581)]
  h=vm.play('anchor',seq,('defActive','defUntil'))
  g=vm.play('blue_repair',seq,('defActive','defUntil'))
  assert h[-1]['memory']['defActive']==0 and g[-1]['memory']['defActive']==1
  results.append({'slot':slot,'experiment':'four observed, travel unresolved, three stillattacktower480ticks later','anchor':h,'blue_repair':g})
 write(ROOT/'mechanism-test.json',{'passed':True,'rows':results,'scope':'RealBASICVM fixtures reproduce thresholdandclock. Three thresholdmutant is diagnostic only, not a validatedcandidate orprovenwinningfix. Originalexecutablesunchanged.'})
 print('PASS: three visible towerattackers failfreshrecall; fourtrigger; anchor20sectimeoutcanexpireintransit whiledeployedstaysrecalled.')
