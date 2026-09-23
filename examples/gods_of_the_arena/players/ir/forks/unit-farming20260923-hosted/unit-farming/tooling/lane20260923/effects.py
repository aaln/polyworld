"""Mechanism diagnostics on four lexically selected episodes per frozen trial cell."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,subprocess,time,hashlib,statistics
ROOT=Path(__file__).resolve().parents[4]
STUDY=ROOT.parent/'polyworld/tmp/gota-lane-recovery-20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',default='trial');p.add_argument('--watch',action='store_true');a=p.parse_args();out=STUDY/a.stage
    while not (out/'result.json').exists():
        if not a.watch:raise SystemExit('Wait for complete screen cells')
        time.sleep(10)
    plan=read(out/'plan.json');cases=[]
    for arm in plan['arms']:
        cell=read(out/arm['name']/arm['cell']/'result.json')
        for row in sorted(cell['rows'],key=lambda r:r['episode'])[:4]:
            cases.append({'name':arm['name'],'cell':arm['cell'],'side':arm['side'],'slot':arm['own_slots'][0],'episode':row['episode'],'source_sha256':arm['source_sha256']})
    definition={'selection':'First4 lexical episode UUIDs per cell after all cells complete; rule chosen before detailed effect decoding. Retrospective diagnostic subset, no independent holdout/competitive gate.','cases':cases,'instrument_sha256':sha(Path(__file__).with_name('effect_audit.nim')),'binary_sha256':sha(STUDY/'sustain-effect-audit')}
    path=out/'effects-plan.json'
    if path.exists():assert read(path)==definition
    else:write(path,definition)
    def decode(c):
        src=out/c['name']/c['cell']/'artifacts'/c['episode'];dst=out/'effects'/c['episode']/'audit.json'
        if not dst.exists():
            q=subprocess.run([str(STUDY/'sustain-effect-audit'),'--replay',str(src/'replay.bin')],capture_output=True,text=True,timeout=900);assert q.returncode==0,q.stderr[-1200:]
            d=json.loads(q.stdout.splitlines()[-1]);write(dst,d);(dst.parent/'stderr.log').write_text(q.stderr)
        d=read(dst);assert d['hash_mismatches']==0
        return {**c,'ticks':d['ticks'],'hero':d['heroes'][c['slot']],'audit_sha256':sha(dst)}
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(decode,cases))
    cells=[]
    for arm in plan['arms']:
        r=[x for x in rows if x['name']==arm['name'] and x['cell']==arm['cell']]
        keys=sorted({k for x in r for k in x['hero']['totals']})
        cells.append({'name':arm['name'],'cell':arm['cell'],'side':arm['side'],'n':len(r),'mean_totals':{k:statistics.mean(x['hero']['totals'].get(k,0) for x in r) for k in keys},'classes':[x['hero']['class'] for x in r]})
    write(out/'effects-summary.json',{'plan':definition,'cells':cells,'rows':rows,'scope':f'Typed actual effects on mechanical{len(rows)}game subset; may differ in classes and scene mix. Full{plan["games"]}game score gate remains separate; no component causality.'})
    print(json.dumps({'completed':len(rows),'cells':cells}))
if __name__=='__main__':main()
