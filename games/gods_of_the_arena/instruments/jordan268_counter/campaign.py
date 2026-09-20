"""Resumable, serial bulk evaluations of isolated primary IR forks."""
import argparse,concurrent.futures,datetime,json,re,sys,time
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[4];CLEAN=ROOT.parent/'polyworld-gota-clean-20260916-r5/examples/gods_of_the_arena/players/ir'
sys.path.insert(0,str(CLEAN))
from policy_ir import read,write,digest,compile_policy,extract
from hosted_wave import client,get,create,episodes,fetch
from hosted_wave_audit import verify as audit
from win_hosted import live
from release_deploy_pair import verify_owned
from jordan_lineup_guardrails import pin_auditor
import contracts
STUDY=ROOT/'tmp/gota-ir/jordan268-counter-20260920';PLAYER='ply_594ec24d-d7f3-4370-a000-468354ec41c9';JORDAN='207ffaf9-0d1e-4d92-a15d-4352f1bddec2';PARENT='53f15b12-2198-41d1-bb99-df4bdb1ff7fd';BINARY=ROOT.parent/'gota-research-20260916/r5/fast/audit-hosted'

def freeze(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  if read(path)!=value:raise ValueError('Frozen artifact changed: '+str(path))
 else:write(path,value)

def upload(name):
 folder=STUDY/'candidates'/name;policy=read(folder/'policy.ir.json');source=(folder/'policy.bas').read_bytes()
 assert compile_policy(policy).encode()==source and extract(source.decode(),policy)==policy
 meta={'name':'aaron-gota-ir-j268-'+name.replace('_','-')+'-0920','content_hash':digest(source),'size_bytes':len(source),'player_id':PLAYER,'attributes':{},'tags':{'game':'gods_of_the_arena','game_version':'2026.9.16.5','change':name,'semantic_ir_sha256':digest(policy),'validation':'unvalidated experimental fork; not league champion'}}
 freeze(folder/'upload-request.json',meta)
 with client() as c:
  if not (folder/'uploaded-version.json').exists():
   response=c.post('/stats/policies/files/upload',json=meta)
   if response.status_code==409:
    response=c.post('/stats/policies/files/complete',json=meta);response.raise_for_status();version=response.json()
   else:
    response.raise_for_status();payload=response.json();version=payload.get('existing_policy_version')
    if version is None:
     saved=httpx.put(payload['upload_url'],content=source,headers={'Content-Type':'application/octet-stream'},timeout=120);saved.raise_for_status()
     response=c.post('/stats/policies/files/complete',json=meta);response.raise_for_status();version=response.json()
   write(folder/'uploaded-version.json',version)
  version=read(folder/'uploaded-version.json')
  log=ROOT/'games/gods_of_the_arena/players/jordan268-counter/VERSION_LOG.md';text=log.read_text() if log.exists() else '# Jordan268 counter-policy forks\n'
  if version['id'] not in text:
   text+=f"\n## {version['name']}:v{version['version']}\n\n- Version `{version['id']}`; UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}.\n- Change: {policy['update']['change']}.\n- BASIC SHA `{digest(source)}`; IR SHA `{digest(policy)}`. Runtime: published GOTA BASIC host .5, no container/run override.\n- State: unvalidated; inert upload. Evidence: `{folder}`.\n"
   log.write_text(text)
  write(folder/'owned-readback.json',verify_owned(c,version,PLAYER))
 print('UPLOADED',name,version['id'],flush=True);return version['id']

def version(name):return PARENT if name=='parent' else read(STUDY/'candidates'/name/'uploaded-version.json')['id']

def arm(name,color,n,stage):
 game=live();folder=STUDY/'hosted'/stage/name/color;own=list(range(5)) if color=='red' else list(range(5,10));policy=version(name)
 reference=read(STUDY/'reference-episode.json');config={k:v for k,v in reference['game_config'].items() if k not in ('seed','players','tokens')};roster=[policy if slot in own else JORDAN for slot in range(10)]
 plan={'candidate':name,'stage':stage,'color':color,'n':n,'own_slots':own,'policy_version':policy,'rival_version':JORDAN,'roster':roster,'config':config,'game_version':game['version'],'target':{'coworld_id':game['id'],'variant_id':'competition'}}
 freeze(folder/'plan.json',plan)
 pin_auditor(folder)
 body={'idempotency_key':'j268-counter-'+digest(plan)[:24],'target':plan['target'],'game_config_overrides':config,'num_episodes':n,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],'notes':f'Jordan268 IR-guided fork {name}, {color}, {stage}. All10seats pinned. {n} generated-seed cohort; not seed-matched. No promotion.'}
 with client() as c:
  create(c,body,folder/'batch',dry_run=True);request=create(c,body,folder/'batch')
  print('REQUEST',name,color,request,'https://softmax.com/observatory/v2?tab=overview&detail=experience-request:'+request,flush=True)
  # Durable request list immediately after launch.
  ledger=STUDY/'requests.json';data=read(ledger) if ledger.exists() else []
  if not any(r['request']==request for r in data):data.append({'request':request,'name':name,'color':color,'stage':stage,'n':n});write(ledger,data)
  experiment='2026-09-19-jordan268-waveclear' if name=='parent' else read(STUDY/'candidates'/name/'policy.ir.json')['update']['change']['experiment']
  record=ROOT/'games/gods_of_the_arena/experiments'/(experiment+'.md')
  text=record.read_text();line=re.search(r'^evals: (\[.*\])$',text,re.M)
  if line is None:raise ValueError('Experiment record has no request ledger')
  ids=json.loads(line[1])
  if request not in ids:
   ids.append(request);record.write_text(text[:line.start(1)]+json.dumps(ids)+text[line.end(1):])
  while True:
   entries=episodes(c,request);write(folder/'batch/episodes.json',entries)
   if any(e['status'] in {'failed','cancelled','error'} for e in entries):raise ValueError('Failed episode preserved; diagnose before proceeding')
   finished=[e for e in entries if e['status']=='completed']
   def collect(ep):
    with client() as reader:fetch(reader,ep,folder/'artifacts',policy,allow_repeated_subject=True)
    audit(folder/'artifacts'/ep['id'],BINARY,digest(BINARY.read_bytes()))
   with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(collect,finished))
   print('PROGRESS',name,color,len(finished),'/',n,flush=True)
   if len(entries)==n and len(finished)==n:break
   time.sleep(15)
 rows=[];seeds=set()
 for ep in entries:
  f=folder/'artifacts'/ep['id'];r=read(f/'results.json');proof=read(f/'audit.json');cfg={k:v for k,v in ep['game_config'].items() if k not in ('seed','players','tokens')}
  assert ep['policy_version_ids']==roster and cfg==config and ep['coworld_version']==game['version'] and ep['coworld_id']==game['id']
  assert [h['total_xp'] for h in proof['heroes']]==r['total_xp']
  assert r['seed'] not in seeds;seeds.add(r['seed']);us={r['scores'][s] for s in own};them={r['scores'][s] for s in range(10) if s not in own};assert len(us)==len(them)==1
  win=next(iter(us));loss=next(iter(them));assert win in [0,1] and loss in [0,1] and win+loss<=1
  heroes=[proof['heroes'][s] for s in own];rows.append({'episode':ep['id'],'seed':r['seed'],'win':win,'loss':loss,'draw':int(not win and not loss),'ticks':r['ticks'],'deaths':sum(h['deaths'] for h in heroes),'gear_heroes':sum(h['first_gear_tick']>=0 for h in heroes)})
 result={'name':name,'color':color,'n':n,'wins':sum(r['win'] for r in rows),'losses':sum(r['loss'] for r in rows),'draws':sum(r['draw'] for r in rows),'all_replay_vm_roster_checks':True,'rows':rows,'request':request}
 write(folder/'result.json',result);print('RESULT',json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True);return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['upload','arm','screen']);p.add_argument('name');p.add_argument('--color',choices=['red','blue']);p.add_argument('--n',type=int,default=4);p.add_argument('--stage',default='screen');a=p.parse_args()
 if a.command=='upload':upload(a.name)
 elif a.command=='arm':arm(a.name,a.color,a.n,a.stage)
 else:
  for name in ['parent',a.name]:
   for color in ['red','blue']:
    folder=STUDY/'hosted'/a.stage/name/color
    if not (folder/'result.json').exists():arm(name,color,a.n,a.stage)
