"""Admission receipts for the narrow reward-finishing hypothesis."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-core-buyback-20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    pair=STUDY/'core-buyback';proof=[]
    for mode in ['compile','extract']:
        out=STUDY/'conversion-check'/mode
        cmd=[sys.executable,str(pair/'convert.py'),mode,'--out',str(out)]
        if mode=='extract':cmd+=['--source',str(pair/'policy.bas')]
        if not out.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
        assert (out/'policy.bas').read_bytes()==(pair/'policy.bas').read_bytes()
        assert read(out/'policy.ir.json')==read(pair/'policy.ir.json')
        proof.append({'mode':mode,'passed':True})
    write(STUDY/'conversion-proof.json',{'passed':True,'rows':proof})
    for name,count in [('practice',180),('portals',84)]:
        d=read(STUDY/('core-buyback-'+name+'.json'))
        assert len(d['rows'])==count and all(r['passed'] for r in d['rows'])
    broad=read(STUDY/'core-buyback-scenarios.json');assert broad['passed'] and broad['checks']==126
    native=read(STUDY/'native-result.json');assert native['passed'] and len(native['rows'])==8
    control=read(STUDY/'baseline-practice.json');assert len(control['rows'])==180 and all(r['passed'] for r in control['rows'])
    runtime=read(STUDY/'runtime-provenance.json')
    for name in ['economy','command-hash','portals','scenarios','episode-v2']:
        assert sha(STUDY/'bin'/name)==runtime['binaries'][name]
    instrument=Path(__file__).with_name('buyback_practice.nim')
    engine=ROOT.parent/'polyworld-gota-engine-score-20260922'
    assert sha(instrument)==sha(engine/'examples/gods_of_the_arena/tools/buyback_practice.nim')
    for name,digest in runtime['engine_files'].items():assert sha(engine/name)==digest
    write(STUDY/'practice-provenance.json',{'engine_commit':runtime['engine_commit'],'instrument_sha256':sha(instrument),'binary_sha256':sha(STUDY/'practice'),'build_log_sha256':sha(STUDY/'build-practice-r2.log'),'initial_failed_capture':'core-buyback-practice-r1.stderr','fixture_repair':'Both sources initially failed exact post-tick spawn-coordinate equality; verify actual spawn region after physics. All gold/HP/mana/charge/cooldown checks retained. Policy bytes unchanged.','runtime_receipt':'runtime-provenance.json'})
    summary={'passed':True,'source_sha256':sha(pair/'policy.bas'),'target_reward_cases':180,'baseline_expectations_passed':180,'portal_cases':84,'broader_cases':126,'full_native_games':8,'max_fixture_instructions':max(read(STUDY/('core-buyback-'+n+'.json'))['max_instructions'] for n in ['practice','portals','scenarios']),'max_fixture_work':max(read(STUDY/('core-buyback-'+n+'.json'))['max_work'] for n in ['practice','portals','scenarios']),'competitive_inference':False}
    assert summary['max_fixture_instructions']<19000 and summary['max_fixture_work']<50000
    write(STUDY/'local-summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
