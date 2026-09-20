"""Fork the exact primary Python IR with one attributed semantic change."""
from copy import deepcopy
from pathlib import Path
import json,pprint,sys
ROOT=Path(__file__).resolve().parents[4];CLEAN=ROOT.parent/'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0,str(CLEAN))
from policy_ir import read,digest,refresh_grounding,bundle,compile_policy,extract,write
import contracts
STUDY=ROOT/'tmp/gota-ir/jordan268-counter-20260920'

def make(name):
 if name=='redrace':
  parent=read(STUDY/'candidates/counterrace/policy.ir.json');p=deepcopy(parent)
  p['id']='gota_jordan268_redrace'
  p['skill']['observe']['operator']='lineup_j268_both_local_recall'
  p['skill']['observe']['parameters']['red_recall_radius']=28
  p['goal']['G_defense']['preference']+=' Apply the nearby-only recall eligibility to red as well, preserving distant offensive groups.'
  p['belief']['claims']['Jordan268_red_counterpressure']={'claim':'Counterrace confirmed40/40 on blue but14/40 on red. The audited red loss shows three remote heroes recalling into prolonged defense. Extend nearby-only recall to red as a separate untested hypothesis.', 'status':'untested','evidence':[{'artifact':str(STUDY/'hosted/confirmation/counterrace/red/result.json'),'sha256':digest((STUDY/'hosted/confirmation/counterrace/red/result.json').read_bytes()),'opponent_preference':'Jordan268_I_O15'},{'artifact':str(STUDY/'hosted/confirmation/counterrace/blue/result.json'),'sha256':digest((STUDY/'hosted/confirmation/counterrace/blue/result.json').read_bytes())}]}
  p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change={'origin':'Audited counterrace confirmation and Jordan268 IR','experiment':'2026-09-19-jordan268-redrace','lever':'red remote recall eligibility','parent_candidate':'counterrace'},needs_review=['belief/Jordan268_red_counterpressure'])
  refresh_grounding(p);return p
 if name=='counterrace':
  parent=read(STUDY/'candidates/waveclear/policy.ir.json');p=deepcopy(parent)
  p['id']='gota_jordan268_counterrace'
  p['skill']['observe']['operator']='lineup_j268_local_recall'
  p['skill']['observe']['parameters']['recall_radius']=28
  p['goal']['G_defense']['preference']+=' On blue, preserve offensive pressure when farther than28tiles from home; only nearby heroes accept defense recall.'
  p['belief']['claims']['Jordan268_counterpressure']={'claim':'Opposing Jordan268 hero contact by assembling five heroes failed 0/4. A separate counterpressure hypothesis keeps distant blue heroes on their ordinary offensive path while retaining nearby defense. Competitive effect untested.', 'status':'untested','evidence':[{'artifact':str(STUDY/'hosted/screen/assembly/blue/result.json'),'sha256':digest((STUDY/'hosted/screen/assembly/blue/result.json').read_bytes()),'opponent_preference':'Jordan268_I_O15'}]}
  p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change={'origin':'Jordan268 IR-guided counterpressure after failed assembly','experiment':'2026-09-19-jordan268-counterrace','lever':'blue remote recall eligibility','parent_candidate':'waveclear'},needs_review=['belief/Jordan268_counterpressure'])
  refresh_grounding(p);return p
 if name=='assembly':
  parent=read(STUDY/'candidates/waveclear/policy.ir.json');p=deepcopy(parent)
  p['id']='gota_jordan268_assembly'
  p['skill']['fallback']['operator']='lineup_j268_opening_assembly'
  p['skill']['fallback']['parameters'].update(assembly_ticks=1200,assembly_x=91,assembly_y=104)
  p['goal']['G_defense']['preference']+=' On blue, initially assemble at the friendly eastern outer tower, avoiding separate creep escorts before first contact.'
  p['belief']['claims']['Jordan268_opening_split']={'claim':'Two inspected blue losses split our initial heroes 3/2; Jordan brings five to the eastern lane, where the pair dies before sentries arrive. Initial blue assembly may improve this contact. Competitive effect untested.', 'status':'untested','evidence':[{'artifact':str(STUDY/'waveclear-blue-loss-macro.jsonl'),'sha256':digest((STUDY/'waveclear-blue-loss-macro.jsonl').read_bytes()),'episode':'ereq_502b5274-729e-4428-b028-50d7395be69d','opponent_preference':'Jordan268_I_O15'}]}
  p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change={'origin':'Jordan268 opponent IR and blue-loss replay','experiment':'2026-09-19-jordan268-assembly','lever':'blue opening formation','parent_candidate':'waveclear'},needs_review=['belief/Jordan268_opening_split'])
  refresh_grounding(p);return p
 parent=read(ROOT/'docs/opponents/jordan-v268/observer-policy.ir.json');p=deepcopy(parent)
 p['id']='gota_jordan268_'+name
 assert name=='waveclear'
 p['skill']['observe']['parameters'].update(creep_first=1,redbranch_creep_first=1)
 p['belief']['claims']['Jordan268_I_O15']={
  'claim':'Observed exact Jordan v268 prefers hero targets over creep targets in the model O15 context; 155/238 heldout selections, class-conditioned population98/238. Defense wave clearing may exploit this tendency; competitive effect is untested.',
  'status':'untested','evidence':[{'artifact':str(ROOT/'docs/opponents/jordan-v268/evidence.json'),'sha256':digest((ROOT/'docs/opponents/jordan-v268/evidence.json').read_bytes()),'preference_id':'Jordan268_I_O15','opponent_version':'207ffaf9-0d1e-4d92-a15d-4352f1bddec2'}]}
 p['goal']['G_defense']['preference']+=' Experimental Jordan268 fork: in the existing active defense region, prefer living visible enemy creeps over heroes. Test whether clearing their cover improves the fort race against the observed hero-target preference.'
 p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change={'origin':'Jordan268 opponent IR-guided fork','experiment':'2026-09-19-jordan268-waveclear','lever':'defense target-kind priority','changed_parameters':['observe.creep_first','observe.redbranch_creep_first']},needs_review=['belief/Jordan268_I_O15','goal/G_defense'])
 refresh_grounding(p);return p

if __name__=='__main__':
 name=sys.argv[1];p=make(name);dest=STUDY/'candidates'/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert read(dest/'policy.ir.json')==p
 else:bundle(p,dest)
 prefix='"""Executable primary IR fork; generated BASIC is bound by policy_ir.py."""\n'
 if name in ('assembly','counterrace','redrace'):prefix+='from games.gods_of_the_arena.instruments.jordan268_counter import contracts\n'
 (dest/'policy.py').write_text(prefix+'\nPOLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
 assert extract(compile_policy(p),p)==p
 print(json.dumps({'candidate':name,'path':str(dest),'basic_sha256':digest(compile_policy(p).encode()),'ir_sha256':digest(p),'bytes':len(compile_policy(p).encode())}))
