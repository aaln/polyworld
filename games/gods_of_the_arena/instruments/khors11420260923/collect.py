"""Read-only, frozen recent-league replay audit. Creates no games or policy versions."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse, gzip, hashlib, json, subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'adaptive20260922'))
import field
h=field.h
RAW=ROOT.parent/'polyworld/tmp/gota-khors114-audit-20260923'
BIN=ROOT.parent/'polyworld/tmp/gota-score-20260922/bin58'
COMBAT=ROOT.parent/'polyworld/tmp/gota-adaptive-score-20260922/bin/combat-audit'
IDS={'khors':'145c01e0-0cbf-4e1e-8120-11b437175b91','aaron':'0c766ec9-131f-45d1-a207-ad75aea9ccc5','coach':'d75ff766-e78f-4aa5-b656-55eb29248208'}
HASHES={'khors':'e66729cb198ac6a7a398abc529457b24595013d7070210c09e9445ee138ae160','aaron':'29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36','coach':'29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36'}
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
    rows=[]
    rounds=read(RAW/'rounds.json')['entries']
    for r in rounds:
        d=read(RAW/'round-episodes'/(r['id']+'.json'))
        assert not d.get('next_cursor')
        rows+=d['entries']
    assert len(rows)==72 and len({r['id'] for r in rows})==72
    plan={'schema':'gota-retrospective-league-audit/1','frozen_at':h.research.now(),
      'selection':'All72 episodes of the three latest completed division rounds returned at study start. No outcome selection or extension. All invalid matches retained separately. Every exact subject appearance included, whether allies or opponents.',
      'rounds':[{'id':r['id'],'number':r['round_number']} for r in rounds],
      'ids':IDS,'source_hashes':HASHES,'game_version':'2026.9.22.3','engine_commit':'1b70894436b7ffdcd0d421b6b32c2415c9c8bfde','episodes':rows,
      'low_score_definition':{'zero':'score=0','low':'0<score<500','higher':'score>=500'},
      'questions':['Class and draft availability versus low-score probability','Hero/creep XP per simulated minute and minutes below200XP','Field/keep/dead time, spell damage, accepted resource actions','Own-victim XP earned by khors; ally versus opposing matchups separated'],
      'authority':'Retrospective full replay truth and recorded commands. No source/private memory, forecast, executable proxy or causal counter qualification.',
      'guide_sha256':sha(ROOT/'docs/guides/guide-opponent-model-ir.md'),
      'binaries':{str(p):sha(p) for p in [BIN/'episode-v2',BIN/'economy',BIN/'command-hash',COMBAT]},
      'hosted_games_created':0}
    h.freeze(RAW/'plan.json',plan)
    return plan

def decode(binary,replay,path):
    if path.exists():return read(path)
    args=[str(binary),str(replay)] if binary.name=='command-hash' else [str(binary),'--replay',str(replay)]
    p=subprocess.run(args,capture_output=True,text=True,timeout=600)
    path.with_suffix('.stderr.log').write_text(p.stderr)
    path.with_suffix('.stdout.log').write_text(p.stdout)
    assert p.returncode==0,(str(binary),p.stderr[-1000:])
    d=json.loads(p.stdout.splitlines()[-1]);h.freeze(path,d);return d

def collect(c,ep):
    out=RAW/'league-artifacts'/ep['id'];done=out/'verified.json'
    if done.exists():return read(done)
    out.mkdir(parents=True,exist_ok=True)
    if not (out/'episode.json').exists():h.freeze(out/'episode.json',h.get(c,'/v2/episode-requests/'+ep['id']))
    full=read(out/'episode.json');assert full['policy_version_ids']==ep['policy_version_ids']
    assert full['coworld_id']==h.GAME and full['coworld_version']=='2026.9.22.3'
    if full['status']!='completed':
        d={'episode':ep['id'],'valid':False,'status':full['status']};h.freeze(done,d);return d
    for kind,name in [('results','results.json'),('logs','game.log'),('replay','replay.bin'),('player-status','player-status.json'),('spec','spec.json')]:
        p=out/name
        if not p.exists():
            r=c.get('/v2/episode-requests/'+ep['id']+'/artifacts/'+kind);r.raise_for_status();data=r.content
            if kind=='replay' and data.startswith(b'\x1f\x8b'):data=gzip.decompress(data)
            p.write_bytes(data)
    audit=decode(BIN/'episode-v2',out/'replay.bin',out/'audit.json')
    eco=decode(BIN/'economy',out/'replay.bin',out/'economy.json')
    combat=decode(COMBAT,out/'replay.bin',out/'combat.json')
    commands=decode(BIN/'command-hash',out/'replay.bin',out/'commands.json')
    result=read(out/'results.json');spec=read(out/'spec.json');status=read(out/'player-status.json')
    assert audit['hash_mismatches']==eco['hash_mismatches']==combat['hash_mismatches']==0
    assert audit['ticks']==eco['ticks']==combat['ticks']==result['ticks']
    assert [x['xp'] for x in audit['heroes']]==[x['total_xp'] for x in eco['heroes']]==[x['xp'] for x in combat['heroes']]==result['total_xp']
    assert [max(0,x['xp']*1440-200*audit['ticks'])//1440 for x in audit['heroes']]==result['scores']
    subjects=[]
    for name,version in IDS.items():
        for i,v in enumerate(full['policy_version_ids']):
            if v==version:
                assert spec['players'][i]['content_hash']==HASHES[name]
                subjects.append({'name':name,'slot':i,'source_sha256':HASHES[name]})
    failed=[x['slot'] for x in status['players'] if x.get('exit_code')!=0]
    d={'episode':ep['id'],'valid':not failed,'failed_slots':failed,'subjects':subjects,'ticks':audit['ticks'],'all_replay_hashes_equal':True,**commands,
       'hashes':{p.name:sha(p) for p in out.iterdir() if p.name in ['episode.json','spec.json','player-status.json','replay.bin','results.json','audit.json','economy.json','combat.json','commands.json']}}
    h.freeze(done,d);return d

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--stalls',action='store_true');a=p.parse_args()
    plan=read(RAW/'plan.json') if (RAW/'plan.json').exists() else prepare()
    if a.prepare:print(json.dumps({'prepared':True,'games':len(plan['episodes']),'hosted_created':0}));return
    if a.stalls:
        def one(ep):
            folder=RAW/'league-artifacts'/ep['id']
            result=decode(RAW/'stalls',folder/'replay.bin',folder/'stalls.json')
            assert result['hash_mismatches']==0 and result['all_actions_consumed']
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,plan['episodes']))
        print(json.dumps({'stall_audits':len(plan['episodes'])}));return
    with h.client() as c,ThreadPoolExecutor(max_workers=4) as pool:
        jobs={pool.submit(collect,c,e):e['id'] for e in plan['episodes']};rows=[]
        for f in as_completed(jobs):
            try:rows.append(f.result())
            except Exception as ex:print(json.dumps({'error':jobs[f],'type':type(ex).__name__,'message':str(ex)[:300]}),flush=True);raise
            h.write(RAW/'progress.json',{'audited':len(rows),'total':len(jobs),'invalid':sum(not r['valid'] for r in rows)})
            if len(rows)%8==0:print(json.dumps({'audited':len(rows),'invalid':sum(not r['valid'] for r in rows)}),flush=True)
    h.freeze(RAW/'verified.json',{'complete':True,'rows':sorted(rows,key=lambda r:r['episode'])})
    print(json.dumps({'complete':True,'games':len(rows),'invalid':sum(not r['valid'] for r in rows)}),flush=True)
if __name__=='__main__':main()
