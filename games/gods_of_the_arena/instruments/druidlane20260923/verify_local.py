"""Verify new routing, inherited mechanics and exact source/IR provenance."""
from pathlib import Path
import json, hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-druid-lane-20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    pair=STUDY/'druid-lane'
    for mode in ['compile','extract']:
        out=STUDY/'conversion-check'/mode
        cmd=[sys.executable,str(pair/'convert.py'),mode,'--out',str(out)]
        if mode=='extract':cmd+=['--source',str(pair/'policy.bas')]
        if not out.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
        assert (out/'policy.bas').read_bytes()==(pair/'policy.bas').read_bytes()
        assert read(out/'policy.ir.json')==read(pair/'policy.ir.json')
    write(STUDY/'conversion-proof.json',{'passed':True,'source_sha256':sha(pair/'policy.bas'),'compile_extract_equal':True})
    for label,count in [('baseline-practice',92),('druid-lane-practice',92),('druid-lane-openings',100),('druid-lane-buyback',180),('druid-lane-portals',84)]:
        d=read(STUDY/(label+'.json'));assert len(d['rows'])==count and all(r['passed'] for r in d['rows'])
    broad=read(STUDY/'druid-lane-scenarios.json');assert broad['passed'] and broad['checks']==126
    native=read(STUDY/'native-result.json');assert native['passed'] and len(native['rows'])==16
    pairs=[]
    for row in native['rows']:
        if row['name']!='druid-lane' or row['hero']['class']==3:continue
        folder=STUDY/'native'/'druid-lane'/row['context']/str(row['seed'])
        control=STUDY/'native'/'baseline'/row['context']/str(row['seed'])
        before,after=read(control/'live.json'),read(folder/'live.json')
        for key in ['ticks','state_hash','actions','winner','fort_hp','commands']:assert before[key]==after[key],(row['context'],row['seed'],key)
        command_hashes=[]
        for location in [control,folder]:
            q=subprocess.run([str(STUDY/'bin/command-hash'),str(location/'replay.bin')],capture_output=True,text=True,check=True)
            command_hashes.append(json.loads(q.stdout.splitlines()[-1]))
        assert command_hashes[0]==command_hashes[1],row
        pairs.append({'context':row['context'],'seed':row['seed'],'class':row['hero']['class'],'command_and_terminal_state_equal':True,'canonical_command_hash':command_hashes[0]})
    assert len(pairs)==8
    write(STUDY/'non-druid-equivalence.json',{'passed':True,'pairs':pairs,'scope':'Eight fixed complete local games across both colors and lead/later positions; all subjects naturally non-Druid. Additional action guards prove only Druid runs lane recovery; hosted comparison is separate.'})
    runtime=read(STUDY/'runtime-provenance.json');engine=ROOT.parent/'polyworld-gota-engine-score-20260922'
    for n,digest in runtime['binaries'].items():assert sha(STUDY/'bin'/n)==digest
    for n,digest in runtime['engine_files'].items():assert sha(engine/n)==digest
    write(STUDY/'practice-provenance.json',{'engine_commit':runtime['engine_commit'],'instrument_sha256':sha(Path(__file__).with_name('practice.nim')),'binary_sha256':sha(STUDY/'practice'),'build_log_sha256':sha(STUDY/'build-practice.log'),'buyback_binary_sha256':sha(STUDY/'buyback-practice'),'opening_binary_sha256':sha(ROOT.parent/'polyworld/tmp/gota-blue-khors-20260923/practice')})
    summary={'passed':True,'source_sha256':sha(pair/'policy.bas'),'druid_recovery_cases':92,'opening_cases':100,'inherited_buyback_cases':180,'portal_cases':84,'broader_cases':126,'full_native_games':16,'max_fixture_instructions':max(read(STUDY/('druid-lane-'+n+'.json'))['max_instructions'] for n in ['practice','openings','buyback','portals','scenarios']),'max_fixture_work':max(read(STUDY/('druid-lane-'+n+'.json'))['max_work'] for n in ['practice','openings','buyback','portals','scenarios']),'competitive_inference':False}
    assert summary['max_fixture_instructions']<19000 and summary['max_fixture_work']<50000
    write(STUDY/'local-summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
