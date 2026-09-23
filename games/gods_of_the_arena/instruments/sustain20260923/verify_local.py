"""Verify new routing, inherited mechanics and exact source/IR provenance."""
from pathlib import Path
import json, hashlib, subprocess, sys
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-field-sustain-20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    pair=STUDY/'field-sustain'
    for mode in ['compile','extract']:
        out=STUDY/'conversion-check'/mode
        cmd=[sys.executable,str(pair/'convert.py'),mode,'--out',str(out)]
        if mode=='extract':cmd+=['--source',str(pair/'policy.bas')]
        if not out.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
        assert (out/'policy.bas').read_bytes()==(pair/'policy.bas').read_bytes()
        assert read(out/'policy.ir.json')==read(pair/'policy.ir.json')
    write(STUDY/'conversion-proof.json',{'passed':True,'source_sha256':sha(pair/'policy.bas'),'compile_extract_equal':True})
    for label,count in [('baseline-practice',68),('field-sustain-practice',68),('field-sustain-openings',100),('field-sustain-buyback',180),('field-sustain-portals',84)]:
        d=read(STUDY/(label+'.json'));assert len(d['rows'])==count and all(r['passed'] for r in d['rows'])
    broad=read(STUDY/'field-sustain-scenarios.json');assert broad['passed'] and broad['checks']==126
    native=read(STUDY/'native-result.json');assert native['passed'] and len(native['rows'])==12
    runtime=read(STUDY/'runtime-provenance.json');engine=ROOT.parent/'polyworld-gota-engine-score-20260922'
    for n,digest in runtime['binaries'].items():assert sha(STUDY/'bin'/n)==digest
    for n,digest in runtime['engine_files'].items():assert sha(engine/n)==digest
    write(STUDY/'practice-provenance.json',{'engine_commit':runtime['engine_commit'],'instrument_sha256':sha(Path(__file__).with_name('practice.nim')),'binary_sha256':sha(STUDY/'practice'),'build_log_sha256':sha(STUDY/'build-practice.log'),'buyback_binary_sha256':sha(STUDY/'buyback-practice'),'opening_binary_sha256':sha(ROOT.parent/'polyworld/tmp/gota-blue-khors-20260923/practice')})
    summary={'passed':True,'source_sha256':sha(pair/'policy.bas'),'sustain_cases':68,'opening_cases':100,'inherited_buyback_cases':180,'portal_cases':84,'broader_cases':126,'full_native_games':12,'max_fixture_instructions':max(read(STUDY/('field-sustain-'+n+'.json'))['max_instructions'] for n in ['practice','openings','buyback','portals','scenarios']),'max_fixture_work':max(read(STUDY/('field-sustain-'+n+'.json'))['max_work'] for n in ['practice','openings','buyback','portals','scenarios']),'competitive_inference':False}
    assert summary['max_fixture_instructions']<19000 and summary['max_fixture_work']<50000
    write(STUDY/'local-summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
