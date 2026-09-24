"""Stream exact replay telemetry, then apply the prospectively frozen score rule."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util, json, subprocess, time

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT.parent/'polyworld/tmp/gota-weak-neutral62-20260924'
ARCHIVE=Path(json.loads((ROOT/'research/manifest.json').read_text())['archive'])
spec=importlib.util.spec_from_file_location('recovery_statistics',ARCHIVE/'games/gods_of_the_arena/instruments/neutralfarm20260923/statistics_report.py')
stats=importlib.util.module_from_spec(spec);spec.loader.exec_module(stats)
stats.RAW=stats.base.RAW=RAW
read,write=stats.read,stats.write

def extra(rows,arm):
    values=[read(RAW/'sharing'/r[arm]['episode']/'telemetry.json')['heroes'][r[arm]['slot']] for r in rows]
    return {key:sum(v[key] for v in values)/len(values) for key in ['neutral_kills','neutral_damage_taken']}

def main():
    while True:
        folders=[p.parent for p in (RAW/'artifacts').glob('*/audit-result.json') if not (RAW/'sharing'/p.parent.name/'telemetry.json').exists()]
        with ThreadPoolExecutor(3) as pool:list(pool.map(stats.decode,folders))
        paths={k:RAW/'counterfactual'/k/'paired-results.json' for k in ['previous','weak-neutral']}
        if all(p.exists() and read(p)['complete'] for p in paths.values()):break
        print(json.dumps({'decoded':len(list((RAW/'sharing').glob('*/telemetry.json')))}),flush=True)
        time.sleep(10)
    plan=read(RAW/'hosted-plan.json');result={'contrasts':{}}
    for label,path in paths.items():
        rows=read(path)['pairs']
        with ThreadPoolExecutor(3) as pool:list(pool.map(stats.decode,[RAW/'artifacts'/r[a]['episode'] for r in rows for a in ['baseline','candidate']]))
        for r in rows:
            stats.base.audit_pair(r,{'source_hashes':{'baseline':plan['source_hashes']['deployed'],'candidate':plan['source_hashes'][label]}})
        summary=stats.summarize(rows)
        summary['neutral_mechanism']={a:extra(rows,a) for a in ['baseline','candidate']}
        for key in summary['by_class']:
            selected=[r for r in rows if str(r['baseline']['hero']['class'])==key]
            summary['class_telemetry'][key]['neutral_mechanism']={a:extra(selected,a) for a in ['baseline','candidate']}
        result['contrasts'][label]=summary
    result.update(complete=True,games=180,pairs_per_arm=60,source_hashes=plan['source_hashes'],
        status='Discovery; fresh confirmation required before a reliable repair claim. Two97.5percent paired baseline intervals; weak-hero and mechanism slices are descriptive.')
    write(RAW/'statistics.json',result)
    print(json.dumps({k:v['overall'] for k,v in result['contrasts'].items()}),flush=True)

if __name__=='__main__':main()
