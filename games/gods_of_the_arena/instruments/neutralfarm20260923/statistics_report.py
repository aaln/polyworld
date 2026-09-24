"""Full replay62 audits and matched three-arm score/XP diagnostics."""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT.parent / 'polyworld/tmp/gota-lane-neutral62-20260923'
spec = importlib.util.spec_from_file_location('lane_statistics', HERE.parent/'lanefarm20260923/statistics_report.py')
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
base.RAW = RAW
read, write = base.read, base.write


def decode(folder):
    # The parent audit expects telemetry in sharing/. This is a fresh release62
    # decoder; never reuse the release61 decoder or alter captured artifacts.
    import subprocess
    dest = RAW/'sharing'/folder.name
    dest.mkdir(parents=True, exist_ok=True)
    out = dest/'telemetry.json'
    if out.exists(): return
    p = subprocess.run([str(RAW/'bin/telemetry'), '--replay', str(folder/'replay.bin')],
                       capture_output=True, text=True, timeout=900)
    (dest/'stderr.log').write_text(p.stderr)
    assert p.returncode == 0, p.stderr[-2000:]
    d = json.loads(p.stdout.splitlines()[-1])
    assert d['hash_mismatches'] == 0
    write(out, d)


def interval975(rows, draws=10000, seed=9236102):
    """Same whole-pair stratified draws as shared score_statistics; 97.5% CI."""
    groups = defaultdict(list)
    for row in rows: groups[row['baseline']['cell']].append(row)
    rng = random.Random(seed)
    values = []
    for _ in range(draws):
        values.append(sum(sum(r['candidate']['score']-r['baseline']['score']
                              for r in rng.choices(g, k=len(g)))
                          for g in groups.values()) / len(rows))
    values.sort()
    return [values[int(draws*.0125)], values[int(draws*.9875)-1]]


def metrics(rows, arm):
    result = base.metrics(rows, arm)
    for key in ['neutral_xp', 'camp_engagements']:
        vals = []
        for r in rows:
            own = r[arm]
            h = read(RAW/'sharing'/own['episode']/'telemetry.json')['heroes'][own['slot']]
            vals.append(h['xp_sources'].get('neutral', 0) if key == 'neutral_xp' else h[key])
        result['means'][key] = sum(vals)/len(vals)
    return result


def summarize(rows):
    result = {'overall':base.paired_summary(rows)}
    result['overall']['delta975'] = interval975(rows)
    for label, func in [('by_context',lambda r:r['baseline']['cell']),
                        ('by_class',lambda r:str(r['baseline']['hero']['class'])),
                        ('by_color',lambda r:str(r['baseline']['slot']//5))]:
        result[label] = {k:base.paired_summary([r for r in rows if func(r)==k])
                         for k in sorted({func(r) for r in rows})}
    result['telemetry'] = {arm:metrics(rows,arm) for arm in ['baseline','candidate']}
    result['class_telemetry'] = {key:{arm:metrics([r for r in rows if str(r['baseline']['hero']['class'])==key],arm)
                                      for arm in ['baseline','candidate']} for key in result['by_class']}
    result['streams'] = {}
    for arm in ['baseline','candidate']:
        groups = defaultdict(list)
        for r in rows:
            episode = r[arm]['episode']
            groups[read(RAW/'sharing'/episode/'telemetry.json')['canonical_commands_sha1']].append(episode)
        result['streams'][arm] = {'unique':len(groups),'duplicates':[v for v in groups.values() if len(v)>1]}
    result['pilot_advance'] = result['overall']['mean_delta']>0 and result['overall']['delta975'][0]>=0
    return result


def main():
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(decode,[p.parent for p in (RAW/'artifacts').glob('*/audit-result.json')]))
    paths = {label:RAW/'counterfactual'/label/'paired-results.json' for label in ['lane-only','lane-neutral']}
    if not all(p.exists() and read(p)['complete'] for p in paths.values()):
        print(json.dumps({'decoded':len(list((RAW/'sharing').glob('*/telemetry.json'))),'complete':False}));return
    plan = read(RAW/'hosted-plan.json')
    cohorts = {label:read(p)['pairs'] for label,p in paths.items()}
    episodes = {r[arm]['episode'] for rows in cohorts.values() for r in rows for arm in ['baseline','candidate']}
    assert len(episodes)==120
    with ThreadPoolExecutor(4) as pool:list(pool.map(decode,[RAW/'artifacts'/e for e in episodes]))
    for label,rows in cohorts.items():
        assert len(rows)==40 and len({r['baseline']['episode'] for r in rows})==40
        for r in rows:
            base.audit_pair(r, {'source_hashes':{'baseline':plan['source_hashes']['baseline'],'candidate':plan['source_hashes'][label]}})
    result = {'contrasts':{label:summarize(rows) for label,rows in cohorts.items()}}
    lane = {r['baseline']['episode']:r for r in cohorts['lane-only']}
    camp = {r['baseline']['episode']:r for r in cohorts['lane-neutral']}
    assert set(lane)==set(camp)
    # Hold common original controls/seeds fixed for the incremental camp effect.
    incremental = []
    for key,r in lane.items():
        before = dict(r['candidate'], cell=r['baseline']['cell'], roster=r['baseline']['roster'])
        after = camp[key]['candidate']
        assert before['seed']==after['seed'] and before['slot']==after['slot']
        incremental.append({'baseline':before,'candidate':after})
    result['camp_vs_lane'] = summarize(incremental)
    result['camp_vs_lane'].pop('pilot_advance')
    result.update(complete=True, all_120_games_10_vms_valid=True,
                  full_hash_xp_score_config_pair_audits=True, deployment_qualified=False,
                  scope='Fresh release62 discovery:40 matched seeds,4 fixed side/seat contexts. Two97.5% baseline contrast intervals apply Bonferroni adjustment. Incremental camp effect and all class/context/mechanism slices exploratory. Fixed roster, no independent confirmation or verdict N floor. Primary expected individual score; other metrics diagnostic. No promotion.')
    write(RAW/'statistics.json', result)
    print(json.dumps({k:v['overall'] for k,v in result['contrasts'].items()}|{'camp_vs_lane':result['camp_vs_lane']['overall']},indent=2))


if __name__=='__main__':main()
