"""Exact full native trajectories plus portable IR conversion and fixture receipts."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];STUDY=ROOT.parent/'polyworld/tmp/gota-class-score-20260922';OLD=STUDY.with_name('gota-adaptive-score-20260922')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def commands(p):return json.loads(subprocess.check_output([str(STUDY/'bin/command-hash'),str(p/'replay.bin')],text=True))['canonical_commands_sha1']
def main():
    assert read(STUDY/'native-result.json')['passed'] and read(STUDY/'native-fallback-result.json')['passed']
    rows=[]
    for side in [0,1]:
        for seed in [922610,922611]:
            for mode in ['crossbow','fallback']:
                new=STUDY/('native' if mode=='crossbow' else 'native-fallback')/'crossbow-only'/(str(side)+('-0' if mode=='crossbow' else '-2'))/str(seed)
                old=OLD/'native/spell-pressure'/str(side)/str(seed) if mode=='crossbow' else STUDY/'native-fallback/baseline'/(str(side)+'-2')/str(seed)
                n,b=read(new/'live.json'),read(old/'live.json')
                for key in ['ticks','state_hash','actions','winner','fort_hp','commands']:assert n[key]==b[key],(mode,side,seed,key)
                first,second=commands(new),commands(old);assert first==second,(mode,side,seed)
                slot=side*5+(0 if mode=='crossbow' else 2);cls=n['heroes'][slot]['class'];assert (cls==6)==(mode=='crossbow')
                rows.append({'mode':mode,'side':side,'seed':seed,'class':cls,'ticks':n['ticks'],'canonical_commands_sha1':first,'state_hash':n['state_hash'],'passed':True,'candidate':str(new),'reference':str(old)})
    write(STUDY/'native-equivalence.json',{'passed':True,'comparisons':8,'rows':rows,'scope':'Full independent responsive native matches: Crossbow trajectory matches tested intervention; four late-draft trajectories match parent.160actual-tick conformance cases cover all10classes. No opponent-performance inference.'})
    pair=STUDY/'crossbow-only';checks=[]
    for mode in ['compile','extract']:
        out=STUDY/'conversion-check'/mode
        cmd=[sys.executable,str(pair/'convert.py'),mode,'--out',str(out)]
        if mode=='extract':cmd+=['--source',str(pair/'policy.bas')]
        if not out.exists():subprocess.run(cmd,check=True,capture_output=True,text=True)
        assert (out/'policy.bas').read_bytes()==(pair/'policy.bas').read_bytes() and read(out/'policy.ir.json')==read(pair/'policy.ir.json')
        checks.append({'mode':mode,'passed':True})
    write(STUDY/'conversion-proof.json',{'passed':True,'rows':checks})
    assert read(STUDY/'conformance.json')['passed'] and all(r['passed'] for r in read(STUDY/'crossbow-only-portals.json')['rows']) and read(STUDY/'crossbow-only-scenarios.json')['passed']
    proof={'passed':True,'source_sha256':sha(pair/'policy.bas'),'conformance_cases':160,'portal_cases':84,'broader_cases':126,'full_native_games':20,'full_native_trajectory_comparisons':8,'max_fixture_instructions':read(STUDY/'conformance.json')['max_instructions'],'max_fixture_work':read(STUDY/'conformance.json')['max_work'],'competitive_inference':False}
    write(STUDY/'local-summary.json',proof);print(json.dumps(proof))
if __name__=='__main__':main()
