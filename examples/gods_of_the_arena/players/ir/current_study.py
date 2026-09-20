"""Frozen current-release local screen and fresh-seed confirmation."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import subprocess

from hypothesis_study import paired, confirmatory_gate, sign_p
from policy_ir import HERE, ROOT, digest, read, write


def regression(summary):
    checks=[]
    metrics={"win":(lambda h:h["score"],1),
             "timeout":(lambda h:int(h["timeout"]),-1),
             "deaths_per_1000_decisions":(lambda h:1000*h["deaths"]/max(1,h["decisions"]),-1)}
    for group in ["all",*range(10)]:
        rows=[r for r in summary["pairs"] if group=="all" or r["class"]==group]
        for key,(value,direction) in metrics.items():
            ds=[value(r["candidate"])-value(r["control"]) for r in rows]
            p=sign_p(sum(d*direction<0 for d in ds),sum(d*direction>0 for d in ds))
            checks.append({"class":group,"metric":key,"n":len(ds),"mean_delta":sum(ds)/len(ds),
                           "adverse_sign_p":p,"flagged":p<.05/33})
    return {"threshold":.05/33,"comparisons":checks,"flagged":[x for x in checks if x["flagged"]]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    parser.add_argument("--workers",type=int,default=8)
    args=parser.parse_args();d=args.directory.resolve()
    binary=d/"episode-current";auditor=d/"audit";config=d/"config.json"
    baseline=d/"baseline.bas"
    if not baseline.exists():baseline.write_bytes((ROOT/"tmp/gota-ir/runtime-2026.9.15.1/examples/gods_of_the_arena/players/base.bas").read_bytes())
    sources={"parent":d/"parent/policy.bas","candidate":d/"candidate/policy.bas","baseline":baseline}
    if not (d/"plan.json").exists():
        rng=random.Random(20260915)
        def cases(start,n):
            slots=list(range(10))*(n//10);rng.shuffle(slots)
            return [{"seed":start+i,"slot":slot} for i,slot in enumerate(slots)]
        plan={"created_at":datetime.now(timezone.utc).isoformat(),"game_version":"2026.9.15.1",
              "published_source":"5422fb0c4b230ca7bfa57a69e450a369da2dabe9",
              "sources":{k:digest(p.read_bytes()) for k,p in sources.items()},
              "binary_sha256":digest(binary.read_bytes()),"auditor_sha256":digest(auditor.read_bytes()),
              "config_sha256":digest(config.read_bytes()),
              "instruments":{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in
                             [HERE/n for n in ["current_study.py","episode_current.nim","audit_current.nim","binding.py","policy_ir.py","independent_ir.py","hypothesis_study.py"]]},
              "screen":cases(715100,40),"validation":cases(716000,120),
              "screen_rule":"At least four added wins vs BOTH unchanged v2 and default, and accepted planned equipment in >=20/40 games across >=3 classes. No strength claim from this screen.",
              "validation_rule":"One candidate on 120 fresh independent seeds, 12/class. Gain>=.05 vs v2 and >=.10 vs default; paired one-sided exact p<.025 for both. Accepted planned equipment in >=60/120 cases across >=3 classes. No adverse flag in 33 comparisons (win/timeout/death rate overall + 10 classes), .05/33 for each reference. Gear count, XP/level and economy are descriptive: lower gear count is an intended change, not a regression by itself.",
              "stop_rule":"All games and state audits finish before each stage aggregate. No optional stopping, sample extension or retuning. Invalid runs are preserved and block advancement until exact-input recovery. Passing local validation qualifies for hosted confirmation only."}
        write(d/"plan.json",plan)
    plan=read(d/"plan.json")
    for p,sha in [(binary,plan["binary_sha256"]),(auditor,plan["auditor_sha256"]),(config,plan["config_sha256"]),
                  *[(sources[k],v) for k,v in plan["sources"].items()],*[(ROOT/k,v) for k,v in plan["instruments"].items()]]:
        if digest(p.read_bytes())!=sha:raise ValueError(f"Frozen input changed: {p}")

    def run_case(stage,arm,case):
        folder=d/stage/arm/f"seed-{case['seed']}-slot-{case['slot']}"
        if (folder/"result.json").exists():
            r=read(folder/"result.json")
            if (r["seed"]!=case["seed"] or r["candidate_slots"]!=[case["slot"]]
                or r["candidate_sha256"]!=plan["sources"][arm]
                or r["baseline_sha256"]!=plan["sources"]["baseline"]
                or r["binary_sha256"]!=plan["binary_sha256"]
                or r["config_sha256"]!=plan["config_sha256"]):raise ValueError("Cached input mismatch")
        else:
            if folder.exists():folder.rename(folder.with_name(folder.name+".incomplete-"+datetime.now().strftime("%H%M%S%f")))
            folder.mkdir(parents=True)
            command=[str(binary),"--config",str(config),"--seed",str(case["seed"]),"--record",str(folder/"episode.replay")]
            command += ["--bot:"+str(sources[arm] if i==case["slot"] else baseline) for i in range(10)]
            try:
                proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=300)
                (folder/"stdout.log").write_text(proc.stdout);(folder/"stderr.log").write_text(proc.stderr)
                proc.check_returncode()
                r=json.loads(proc.stdout.splitlines()[-1])
                if len(r["heroes"])!=10 or not 0<r["ticks"]<=28800:raise ValueError("Invalid episode result")
                r.update(candidate_slots=[case["slot"]],candidate_sha256=plan["sources"][arm],
                         baseline_sha256=plan["sources"]["baseline"],binary_sha256=plan["binary_sha256"],
                         config_sha256=plan["config_sha256"],command=command,
                         replay_sha256=digest((folder/"episode.replay").read_bytes()),
                         trace_sha256=digest((folder/"episode.replay.trace.jsonl").read_bytes()))
                write(folder/"result.json",r)
            except Exception as error:
                write(folder/"failure.json",{"type":type(error).__name__,"seed":case["seed"],"slot":case["slot"]})
                raise
        for suffix,key in [("episode.replay","replay_sha256"),("episode.replay.trace.jsonl","trace_sha256")]:
            if digest((folder/suffix).read_bytes())!=r[key]:raise ValueError("Tape/trace hash changed")
        return r

    def audit_case(stage,arm,case):
        folder=d/stage/arm/f"seed-{case['seed']}-slot-{case['slot']}";r=read(folder/"result.json")
        dest=folder/"audit.json"
        if dest.exists():a=read(dest)
        else:
            proc=subprocess.run([str(auditor),"--replay",str(folder/"episode.replay")],cwd=ROOT,
                                capture_output=True,text=True,timeout=300,check=True)
            a=json.loads(proc.stdout.splitlines()[-1]);a.update(binary_sha256=plan["auditor_sha256"],replay_sha256=r["replay_sha256"])
            write(dest,a)
        if (a["hash_mismatches"] or a["actions_consumed"]!=r["actions"] or a["ticks"]!=r["ticks"]
            or a["binary_sha256"]!=plan["auditor_sha256"] or a["replay_sha256"]!=r["replay_sha256"]):raise ValueError("Incomplete replay verification")

    for stage in ["screen","validation"]:
        jobs=[(arm,case) for arm in sources for case in plan[stage]]
        rows={k:[] for k in sources}
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            fs={pool.submit(run_case,stage,arm,case):arm for arm,case in jobs}
            for n,f in enumerate(as_completed(fs),1):
                rows[fs[f]].append(f.result())
                if n%10==0:print(f"{stage}: {n}/{len(jobs)} games complete",flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            fs=[pool.submit(audit_case,stage,arm,case) for arm,case in jobs]
            for n,f in enumerate(as_completed(fs),1):
                f.result()
                if n%20==0:print(f"{stage}: {n}/{len(jobs)} replay audits complete",flush=True)
        pairs={k:paired(rows[k],rows["candidate"]) for k in ["parent","baseline"]}
        active=[r["heroes"][r["candidate_slots"][0]] for r in rows["candidate"] if r["heroes"][r["candidate_slots"][0]]["loadout_purchases"]]
        activation={"games":len(active),"classes":sorted({h["class"] for h in active}),"purchases":sum(h["loadout_purchases"] for h in active)}
        if stage=="screen":
            gates={k:{"gain_wins":p["wins"]-p["control_wins"],"passed":p["wins"]-p["control_wins"]>=4} for k,p in pairs.items()}
            sweeps={};activated=len(active)>=20 and len(activation["classes"])>=3
        else:
            gates={k:confirmatory_gate(p,.05 if k=="parent" else .10) for k,p in pairs.items()}
            sweeps={k:regression(p) for k,p in pairs.items()};activated=len(active)>=60 and len(activation["classes"])>=3
        passed=activated and all(g["passed"] for g in gates.values()) and not any(s["flagged"] for s in sweeps.values())
        report={"stage":stage,"comparisons":pairs,"gates":gates,"regressions":sweeps,"activation":activation,
                "passed":passed,"games":len(jobs),"audited_games":len(jobs),"invalid_games_scored":0,
                "by_class":{k:[{"class":c,"n":sum(r["class"]==c for r in p["pairs"]),
                                  "control_wins":sum(r["control"]["score"] for r in p["pairs"] if r["class"]==c),
                                  "candidate_wins":sum(r["candidate"]["score"] for r in p["pairs"] if r["class"]==c)} for c in range(10)] for k,p in pairs.items()}}
        write(d/(stage+"-result.json"),report)
        print(json.dumps({"stage":stage,"wins":{k:[p["control_wins"],p["wins"]] for k,p in pairs.items()},"gates":gates,"activation":activation,"passed":passed}),flush=True)
        if not passed:break
    write(d/"local-result.json",{"plan":plan,"last_stage":stage,"hosted_eligible":stage=="validation" and passed,
                                "result":report})


if __name__=="__main__":main()
