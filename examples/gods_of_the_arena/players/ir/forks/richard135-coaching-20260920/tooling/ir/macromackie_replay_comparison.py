"""Compare a median red win/loss and the actual deployed-control league win."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from hosted_wave import client,get,fetch
from league_threat_review import run_native
from policy_ir import read,write,digest
from release_workspace import RUN
from hosted_wave_audit import verify
from review_defense_stalls import inspect
from macromackie_review import ROOT

def main():
 arm=ROOT/'hosted/anchor/macromackie_v4/red';rows=[]
 for f in arm.glob('artifacts/*/results.json'):
  r=read(f);rows.append({'episode':f.parent.name,'ticks':r['ticks'],'win':r['outcome']=='RedTeam','directory':str(f.parent)})
 assert len(rows)==40
 cases=[]
 for win in (True,False):
  subset=sorted((r for r in rows if r['win']==win),key=lambda r:(r['ticks'],r['episode']))
  cases.append(subset[len(subset)//2]|{'name':'anchor-median-'+('win' if win else 'loss'),'source':str(RUN/'coached-lanes/r5-anchored-support/hosted/anchor/tournament-portfolio/policy/policy.bas'),'version':'9cedf3ff-c7ce-4cff-897f-d48b44e049ad'})
 cases.append({'name':'blue-repair-league-win','episode':'ereq_fb88f791-70be-4104-8e4f-86f0650b7eeb','source':str(RUN/'coached-lanes/r5-jordan-lineup/candidate/policy.bas'),'version':'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a'})
 write(ROOT/'review-selection.json',{'selection':'Median duration peroutcome of complete40anchorredXP; actualGredleaguewin discovered in12pinnedrecentrounds. Differentseedsandinitialconditions, not causalpair.','cases':cases})
 def one(case):
  if 'directory' in case:p=Path(case['directory'])
  else:
   with client() as c:
    ep=get(c,'/v2/episode-requests/'+case['episode']);fetch(c,ep,ROOT/'artifacts',case['version'],allow_repeated_subject=True)
   p=ROOT/'artifacts'/case['episode']
   binary=RUN/'r5/fast/audit-hosted';verify(p,binary,digest(binary.read_bytes()))
  decoded=run_native('macro-replay-v5',p/'replay.bin',p/'decoded.jsonl')
  binary='replay-assist-context-probe' if case['name'].startswith('anchor') else 'replay-slots-probe'
  proof=run_native(binary,p/'replay.bin',p/'decisions.jsonl',{'PROBE_POLICY':case['source'],'PROBE_SLOTS':'0,1,2,3,4'})
  write(p/'decisions-proof.json',proof)
  stalls=inspect(p/'decoded.jsonl',0);write(p/'stalls.json',stalls)
  r=case|{'proof':proof,'decode':decoded,'stall_windows':len(stalls['stationary_repeated_order_windows']),'shared_windows':stalls['shared_destination_windows']}
  print(case['name'],case['episode'],decoded['winner'],decoded['ticks'],r['stall_windows'],flush=True);return r
 with ThreadPoolExecutor(3) as pool:out=list(pool.map(one,cases))
 write(ROOT/'review-comparison.json',{'cases':out})
if __name__=='__main__':main()
