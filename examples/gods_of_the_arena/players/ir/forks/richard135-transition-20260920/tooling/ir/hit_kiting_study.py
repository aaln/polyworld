"""Frozen balance-specific local screen or fresh-seed confirmation; stages are explicit."""
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


def main(definition=None):
    definition=definition or {"hypothesis":"confirmed_hit_kite","screen_seed":721000,"validation_seed":722000}
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    parser.add_argument("--workers",type=int,default=8)
    parser.add_argument("--stage",choices=["screen","validation"],default="screen")
    args=parser.parse_args();d=args.directory.resolve()
    binary=d/"episode-kiting";auditor=d/"audit";config=d/"config.json"
    baseline=d/"baseline.bas"
    if not baseline.exists():baseline.write_bytes((ROOT/"tmp/gota-ir/runtime-2026.9.15.3/examples/gods_of_the_arena/players/base.bas").read_bytes())
    sources={"parent":d/"parent/policy.bas","candidate":d/"candidate/policy.bas","baseline":baseline}
    if not (d/"plan.json").exists():
        rng=random.Random(202609151)
        def cases(start,n):
            slots=list(range(10))*(n//10);rng.shuffle(slots)
            return [{"seed":start+i,"slot":slot} for i,slot in enumerate(slots)]
        plan={"created_at":datetime.now(timezone.utc).isoformat(),"game_version":"2026.9.15.3",
              "hypothesis":definition["hypothesis"],
              "runtime":read(d/"runtime.json"),"runtime_sha256":digest((d/"runtime.json").read_bytes()),
              "published_source":"e1279894d10a7684f303e7a9f1ea2f84c1d14253",
              "sources":{k:digest(p.read_bytes()) for k,p in sources.items()},
              "binary_sha256":digest(binary.read_bytes()),"auditor_sha256":digest(auditor.read_bytes()),
              "config_sha256":digest(config.read_bytes()),
              "instruments":{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in
                             [HERE/n for n in ["hit_kiting_study.py","episode_hit_kiting.nim","kiting_contract.py","audit_current.nim","binding.py","policy_ir.py","independent_ir.py","hypothesis_study.py",*definition.get("instruments",[])]]},
              "screen":cases(definition["screen_seed"],40),"validation":cases(definition["validation_seed"],120),
              "screen_rule":"40 fresh balanced independent cases, candidate and v2 and default each vs nine defaults. Candidate wins >= each reference; deaths <=85% of v2, hits >=80%; movement in >=30% of cases, 100% normal retreats after a replay-observed hit within1tick; no corrected adverse class/regression flag. Directional screen only.",
              "validation_rule":"Not enabled: preregister survival and win confirmation after completed screen. No local or hosted promotion from this screen.",
              "stop_rule":"All games and state audits finish before each stage aggregate. No optional stopping, sample extension or retuning. Invalid runs are preserved and block advancement until exact-input recovery. Announcement simulation never independently qualifies for hosted promotion. Actual published release and hosted incumbent confirmation are required."}
        if "mechanism_rule" in definition:
            plan["screen_rule"]="At least four added wins vs BOTH unchanged v2 and default. "+definition["mechanism_rule"]
            plan["validation_rule"]="120 fresh independent seeds, 12/class; gain>=.05 vs v2 and >=.10 vs default; paired one-sided exact p<.025 for both. No adverse flag in 33 comparisons (win/timeout/death rate overall + 10 classes) at .05/33 per reference. "+definition["mechanism_rule"]
        write(d/"plan.json",plan)
    plan=read(d/"plan.json")
    for p,sha in [(d/"runtime.json",plan["runtime_sha256"]),(binary,plan["binary_sha256"]),(auditor,plan["auditor_sha256"]),(config,plan["config_sha256"]),
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

    if args.stage=="validation" and not read(d/"screen-result.json")["passed"]:
        raise ValueError("Screen did not qualify this candidate")
    for stage in [args.stage]:
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
        heroes={arm:[r["heroes"][r["candidate_slots"][0]] for r in rows[arm]] for arm in rows}
        hs=heroes["candidate"]
        active=[h for h in hs if h["moved_kite_ticks"]>0]
        verified=sum(h["verified_bursts"] for h in hs); unverified=sum(h["unverified_bursts"] for h in hs)
        activation={"games":len(active),"classes":sorted({h["class"] for h in active}),
                    "verified_bursts":verified,"unverified_bursts":unverified,
                    "landed_before_retreat_fraction":verified/max(1,verified+unverified)}
        activated=len(active)>=len(hs)*.3 and verified>0 and verified/max(1,verified+unverified)>=1.0
        metrics={arm:{"deaths":sum(h["deaths"] for h in hh),"hits":sum(h["basic_hit_events"] for h in hh),
                      "xp":sum(h["total_xp"] for h in hh)} for arm,hh in heroes.items()}
        death_ratio=metrics["candidate"]["deaths"]/max(1,metrics["parent"]["deaths"])
        hit_ratio=metrics["candidate"]["hits"]/max(1,metrics["parent"]["hits"])
        gates={k:{"gain_wins":p["wins"]-p["control_wins"],"passed":p["wins"]>=p["control_wins"]} for k,p in pairs.items()}
        gates["survival"]={"death_ratio":death_ratio,"hit_ratio":hit_ratio,"passed":death_ratio<=.85 and hit_ratio>=.8}
        sweeps={k:regression(p) for k,p in pairs.items()}
        passed=activated and all(g["passed"] for g in gates.values()) and not any(s["flagged"] for s in sweeps.values())
        if stage=="validation":
            raise ValueError("Preregister confirmation from successful screen before running validation")
        report={"stage":stage,"comparisons":pairs,"gates":gates,"regressions":sweeps,"activation":activation,
                "metrics":metrics,"passed":passed,"games":len(jobs),"audited_games":len(jobs),"invalid_games_scored":0,
                "by_class":{k:[{"class":c,"n":sum(r["class"]==c for r in p["pairs"]),
                                  "control_wins":sum(r["control"]["score"] for r in p["pairs"] if r["class"]==c),
                                  "candidate_wins":sum(r["candidate"]["score"] for r in p["pairs"] if r["class"]==c)} for c in range(10)] for k,p in pairs.items()}}
        write(d/(stage+"-result.json"),report)
        print(json.dumps({"stage":stage,"wins":{k:[p["control_wins"],p["wins"]] for k,p in pairs.items()},"gates":gates,"activation":activation,"passed":passed}),flush=True)
        if not passed:break
    write(d/(stage+"-local-result.json"),{"plan":plan,"last_stage":stage,"hosted_eligible":stage=="validation" and passed and not plan["runtime"]["simulation_only"],
                                "simulation_only":plan["runtime"]["simulation_only"],
                                "result":report})


if __name__=="__main__":main()
