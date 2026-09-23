"""Run exact-host checks and verify portable conversion before any hosted spend."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,os,hashlib,sys,time
ROOT=Path(__file__).resolve().parents[4];RAW=ROOT.parent/'polyworld/tmp/gota-unit-farming59-20260923'
SOURCE=RAW/'unit-farming/policy.bas';PARENT=ROOT/'examples/gods_of_the_arena/players/ir/forks/druid-lane20260923-hosted/druid-lane/policy.bas'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
cases=[('unit',RAW/'unit-practice',{'UNIT_CANDIDATE':'1'}),('baseline-unit',RAW/'unit-practice',{'UNIT_CANDIDATE':'0'}),('practice',RAW/'return-practice',{'RETURN_CANDIDATE':'0','PORTAL_ENFORCE':'1'}),('baseline-practice',RAW/'return-practice',{'RETURN_CANDIDATE':'0','PORTAL_ENFORCE':'1'}),('recovery',RAW/'recovery-practice',{'LANE_CANDIDATE':'1','DRUID_ONLY':'1'}),('openings',RAW/'opening-practice',{'BLUE_CANDIDATE':'1'}),('buyback',RAW/'buyback-practice',{'BUYBACK_CANDIDATE':'1'}),('scenarios',RAW/'bin/scenarios',{})]
def one(case):
    name,exe,flags=case
    if (RAW/(name+'.json')).exists():
        d=read(RAW/(name+'.json'))
    else:
        p=subprocess.run([str(exe)],env=dict(os.environ,WEEK_POLICY=str(PARENT if name.startswith('baseline-') else SOURCE),**flags),capture_output=True,text=True,timeout=600)
        (RAW/(name+'.stdout')).write_text(p.stdout);(RAW/(name+'.stderr')).write_text(p.stderr)
        assert p.returncode==0,(name,p.stderr[-1800:]);d=json.loads(p.stdout.splitlines()[-1]);save(RAW/(name+'.json'),d)
    ok=d['passed'] if 'passed' in d else all(r['passed'] for r in d['rows']);assert ok,name
    row={'name':name,'checks':d.get('checks',len(d.get('rows',[]))),'passed':ok,'binary_sha256':sha(exe),'max_instructions':d['max_instructions'],'max_work':d['max_work']};print(json.dumps(row),flush=True);return row
def main():
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(one,cases))
    for mode in ['compile','extract']:
        out=RAW/'conversion-check'/mode
        cmd=[sys.executable,str(SOURCE.parent/'convert.py'),mode,'--out',str(out)]
        if mode=='extract':cmd+=['--source',str(SOURCE)]
        if not out.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
        assert (out/'policy.bas').read_bytes()==SOURCE.read_bytes()
        assert read(out/'policy.ir.json')==read(SOURCE.parent/'policy.ir.json')
    save(RAW/'conversion-proof.json',{'passed':True,'source_sha256':sha(SOURCE),'compile_extract_equal':True})
    deadline=time.monotonic()+900
    while not (RAW/'native-result.json').exists():
        assert time.monotonic()<deadline,'Native checks did not finish'
        time.sleep(5)
    native=read(RAW/'native-result.json');assert native['passed'] and len(native['rows'])==16
    runtime=read(RAW/'runtime-provenance.json');engine=ROOT.parent/'polyworld-gota-engine-20260923'
    for n,d in runtime['binaries'].items():assert sha(RAW/'bin'/n)==d
    for n,d in runtime['engine_files'].items():assert sha(engine/n)==d
    result={'passed':True,'source_sha256':sha(SOURCE),'rows':rows,'checks':sum(r['checks'] for r in rows if not r['name'].startswith('baseline-')),'native_games':16,'competitive_inference':False,'max_instructions':max(r['max_instructions'] for r in rows),'max_work':max(r['max_work'] for r in rows)}
    assert result['max_instructions']<19000 and result['max_work']<=50000
    save(RAW/'local-summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
