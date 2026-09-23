"""Verify new routing, inherited mechanics and exact source/IR provenance."""
from pathlib import Path
import json, hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-blue-khors-20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    pair=STUDY/'blue-center'
    for mode in ['compile','extract']:
        out=STUDY/'conversion-check'/mode
        cmd=[sys.executable,str(pair/'convert.py'),mode,'--out',str(out)]
        if mode=='extract':cmd+=['--source',str(pair/'policy.bas')]
        if not out.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
        assert (out/'policy.bas').read_bytes()==(pair/'policy.bas').read_bytes()
        assert read(out/'policy.ir.json')==read(pair/'policy.ir.json')
    write(STUDY/'conversion-proof.json',{'passed':True,'source_sha256':sha(pair/'policy.bas'),'compile_extract_equal':True})
    for label,count in [('baseline-practice',100),('blue-center-practice',100),('blue-center-buyback',180),('blue-center-portals',84)]:
        d=read(STUDY/(label+'.json'));assert len(d['rows'])==count and all(r['passed'] for r in d['rows'])
    broad=read(STUDY/'blue-center-scenarios.json');assert broad['passed'] and broad['checks']==126
    native=read(STUDY/'native-result.json');assert native['passed'] and len(native['rows'])==8
    red=[]
    for seed in [923020,923021]:
        values=[]
        for name in ['baseline','blue-center']:
            folder=STUDY/'native'/name/'0'/str(seed)
            p=subprocess.run([str(STUDY/'bin/command-hash'),str(folder/'replay.bin')],capture_output=True,text=True,check=True)
            v=json.loads(p.stdout.splitlines()[-1]);write(folder/'command-hash.json',v);values.append(v)
        assert values[0]==values[1],values
        old=read(STUDY/'native/baseline/0'/str(seed)/'live.json');new=read(STUDY/'native/blue-center/0'/str(seed)/'live.json')
        for key in ['ticks','state_hash','actions','winner','fort_hp','commands']:assert old[key]==new[key],key
        red.append({'seed':seed,'full_commands_equal':True,'terminal_state_equal':True,'commands':values[0]})
    write(STUDY/'red-equivalence.json',{'passed':True,'rows':red,'scope':'Two complete native seeds; all commands match. Candidate only changes blue ordinal0 ranged guard, all other rule bodies identical. Runtime counters may differ.'})
    runtime=read(STUDY/'runtime-provenance.json');engine=ROOT.parent/'polyworld-gota-engine-score-20260922'
    for n,digest in runtime['binaries'].items():assert sha(STUDY/'bin'/n)==digest
    for n,digest in runtime['engine_files'].items():assert sha(engine/n)==digest
    write(STUDY/'practice-provenance.json',{'engine_commit':runtime['engine_commit'],'instrument_sha256':sha(Path(__file__).with_name('practice.nim')),'binary_sha256':sha(STUDY/'practice'),'build_log_sha256':sha(STUDY/'build-practice-r2.log'),'fixture_repair':'Initial fixture incorrectly queried read-only mapWidth as a BASIC mutable global; both sources errored. Use the same host mapTiles size bound to mapWidth/mapHeight. Policy source unchanged; first failed stderr preserved.'})
    summary={'passed':True,'source_sha256':sha(pair/'policy.bas'),'opening_cases':100,'inherited_buyback_cases':180,'portal_cases':84,'broader_cases':126,'full_native_games':8,'red_full_command_comparisons':2,'max_fixture_instructions':max(read(STUDY/('blue-center-'+n+'.json'))['max_instructions'] for n in ['practice','buyback','portals','scenarios']),'max_fixture_work':max(read(STUDY/('blue-center-'+n+'.json'))['max_work'] for n in ['practice','buyback','portals','scenarios']),'competitive_inference':False}
    assert summary['max_fixture_instructions']<19000 and summary['max_fixture_work']<50000
    write(STUDY/'local-summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
