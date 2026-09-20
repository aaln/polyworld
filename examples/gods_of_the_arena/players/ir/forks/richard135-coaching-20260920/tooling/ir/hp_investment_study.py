"""One frozen IR-derived candidate, three matched arms, 120 independent seeds."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import random

from binding import CONTRACTS
from hypothesis_study import confirmatory_gate, paired, regression_sweep, run_arms
from policy_ir import HERE, ROOT, bundle, compile_policy, digest, read, refresh_grounding, write
from reserve_study import purchase_audit
from study_report import class_summary, load_cases


def make_candidate(parent):
    policy = deepcopy(parent)
    policy["id"] = "gota_duelist_hp_investment"
    policy["skill"]["sustain"] = {"operator":"buy_hp_investment", "parameters":CONTRACTS["buy_hp_investment"].defaults()}
    engine_facts = {"B_observation_timing","B_action_effects","B_equipment_resources"}
    for key,claim in policy["belief"]["claims"].items():
        if key not in engine_facts:
            claim["status"] = "requires_review"
            claim["claim"] = "Ancestor policy evidence, not performance evidence for HP Investment. " + claim["claim"]
    policy["belief"]["claims"]["B_hp_investment"] = {
        "claim":"When injured without healing stock, early HP gear can supply immediate health and permanent capacity. Buying it before potions may improve survival and fort wins, but consumes gold and slots otherwise available for consumables or class weapons.",
        "status":"untested","evidence":deepcopy(parent["belief"]["claims"]["B_equipment_resources"]["evidence"])}
    policy["goal"]["G_hp_investment"] = {"preference":"Use affordable, missing HP gear as immediate emergency sustain before ordinary consumable attempts, while retaining the fort-win objective.","provenance":"authored"}
    next(rule for rule in policy["strategy"] if rule["id"]=="E1")["for"].append("G_hp_investment")
    policy["update"] = {"revision":parent["update"]["revision"]+1,"parent":digest(parent),
                        "change":{"origin":"preregistered_hypothesis","hypothesis":"hp_investment","changed_rule":"E1"},
                        "needs_review":["belief/"+k for k,v in policy["belief"]["claims"].items() if v["status"] != "supported"],
                        "evidence":deepcopy(parent["update"]["evidence"])}
    refresh_grounding(policy)
    return policy


def activation_examples(directory, rows):
    case = next((r for r in rows if r["heroes"][r["candidate_slots"][0]]["hp_gear_investments"]),None)
    if case is None:
        return None
    slot=case["candidate_slots"][0]
    label=f"seed-{case['seed']}-slot-{slot}"
    events=[];previous=0
    for line in (directory/"validation/candidate"/label/"episode.replay.trace.jsonl").read_text().splitlines():
        event=json.loads(line)
        if event["slot"]==slot:
            if event["hp_gear_investments"]>previous:
                events.append(event)
            previous=event["hp_gear_investments"]
    if len(events)!=case["heroes"][slot]["hp_gear_investments"]:
        raise ValueError("investment event trace does not match runtime count")
    audits={arm:read(directory/"purchase-audits"/arm/(label+".json"))["heroes"][slot]
            for arm in ["parent","candidate","baseline"]}
    for event in events:
        if not any(e["tick"]==event["tick"] and e["item"] in [5,6,9] for e in audits["candidate"]["hp_equipment_events"]):
            raise ValueError("investment trace lacks a matching accepted purchase")
    return {"selection":"First activating seed/seat in fixed order, not selected by outcome.","seed":case["seed"],
            "slot":slot,"candidate_events":events,"purchase_audits":audits}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    directory=args.output.resolve();directory.mkdir(parents=True,exist_ok=True)
    binary=ROOT/"tmp/gota-ir/hp-investment-episode"
    auditor=ROOT/"tmp/gota-ir/hp-investment-audit"
    baseline=directory/"baseline.bas"
    if not (directory/"plan.json").exists():
        parent=read(HERE/"duelist.ir.json")
        bundle(parent,directory/"parent")
        bundle(make_candidate(parent),directory/"candidate")
        baseline.write_bytes((HERE.parent/"base.bas").read_bytes())
        slots=list(range(10))*12;random.Random(2026091067).shuffle(slots)
        plan={"created_at":datetime.now(timezone.utc).isoformat(),"game_version":"2026.9.10.3",
              "published_commit":"27a8fd51eadf48d2f69591cca4287074e9058e8f",
              "binary_sha256":digest(binary.read_bytes()),"auditor_sha256":digest(auditor.read_bytes()),
              "baseline_sha256":digest(baseline.read_bytes()),
              "sources":{arm:digest((directory/arm/"policy.bas").read_bytes()) for arm in ["parent","candidate"]},
              "cases":[{"seed":67000+i,"slot":slot} for i,slot in enumerate(slots)],
              "rule":"One frozen candidate, no discovery selection. 120 independent seeds, 12/class. Gain>=.05 vs Duelist and >=.10 vs default with one-sided paired exact p<.025 for both. At least 30 activating games spanning >=3 classes. No flagged adverse metric in either existing 55-comparison sweep. All 360 source/trace and replay-state audits must pass.",
              "stop_rule":"No aggregate inspection until all games/audits complete; no optional stopping, further candidates, threshold changes, or sample extension. Local win only makes hosted evaluation eligible; hosted field evidence required for league promotion.",
              "instrument_sources":{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [HERE/"binding.py",HERE/"episode.nim",HERE/"audit_purchases.nim",HERE/"hp_investment_study.py",HERE/"hypothesis_study.py",HERE/"study_report.py",HERE/"reserve_study.py",HERE/"research.py"]}}
        plan["sources"]["baseline"]=plan["baseline_sha256"]
        write(directory/"plan.json",plan)
    plan=read(directory/"plan.json")
    for path,key in [(binary,"binary_sha256"),(auditor,"auditor_sha256"),(baseline,"baseline_sha256")]:
        if digest(path.read_bytes())!=plan[key]:
            raise ValueError("pinned runtime or baseline changed")
    for path,sha in plan["instrument_sources"].items():
        if digest((ROOT/path).read_bytes())!=sha:
            raise ValueError("instrument changed after preregistration")
    sources={"parent":directory/"parent/policy.bas","candidate":directory/"candidate/policy.bas","baseline":baseline}
    for arm,path in sources.items():
        if digest(path.read_bytes())!=plan["sources"][arm]:
            raise ValueError("frozen policy changed")
    run_arms(binary,baseline,sources,plan["cases"],directory/"validation",8)
    rows={arm:load_cases(directory,"validation",arm,plan["cases"],sha,plan["baseline_sha256"]) for arm,sha in plan["sources"].items()}
    jobs=[(arm,case) for arm in sources for case in plan["cases"]]
    def audit_job(job):
        arm,case=job;label=f"seed-{case['seed']}-slot-{case['slot']}"
        return purchase_audit(auditor,directory/"validation"/arm/label/"episode.replay",
                              directory/"purchase-audits"/arm/(label+".json"))
    audits=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for count,audit in enumerate(pool.map(audit_job,jobs),1):
            audits.append(audit)
            if count%20==0:
                print(f"State/purchase audits: {count}/360 complete",flush=True)
    purchases={arm:{"healing_purchases":0,"healing_gold":0,"equipment_purchases":0,"hp_equipment_purchases":0,
                    "hp_from_equipment":0,"healing_rejected_no_space":0} for arm in sources}
    index={arm:{(r["seed"],r["candidate_slots"][0]):r for r in cases} for arm,cases in rows.items()}
    for (arm,case),audit in zip(jobs,audits):
        row=index[arm][case["seed"],case["slot"]];h=audit["heroes"][case["slot"]]
        if audit["actions_consumed"]!=row["actions"] or audit["ticks"]!=row["ticks"]:
            raise ValueError("incomplete replay audit")
        counts=h["successful_purchases"]
        metrics=purchases[arm]
        metrics["healing_purchases"]+=sum(counts[1:3]);metrics["healing_gold"]+=sum(h["gold_spent"][1:3])
        metrics["equipment_purchases"]+=sum(counts[5:]);metrics["hp_equipment_purchases"]+=len(h["hp_equipment_events"])
        metrics["hp_from_equipment"]+=sum(e["hp_after"]-e["hp_before"] for e in h["hp_equipment_events"])
        metrics["healing_rejected_no_space"]+=h["healing_rejected_no_space"]
        if arm=="candidate":
            hero=row["heroes"][case["slot"]]
            if not 0<=hero["hp_gear_investments"]<=sum(counts[i] for i in [5,6,9])<=3:
                raise ValueError("accepted investment counter is inconsistent with replay purchases")
    comparisons={arm:paired(rows[arm],rows["candidate"]) for arm in ["parent","baseline"]}
    gates={arm:confirmatory_gate(summary,.05 if arm=="parent" else .10) for arm,summary in comparisons.items()}
    sweeps={arm:regression_sweep(summary) for arm,summary in comparisons.items()}
    heroes=[r["heroes"][r["candidate_slots"][0]] for r in rows["candidate"]]
    active=[h for h in heroes if h["hp_gear_investments"]]
    classes=sorted({h["class"] for h in active})
    activation={"games":len(active),"classes":classes,"investments":sum(h["hp_gear_investments"] for h in heroes),
                "granted_hp":sum(h["hp_gear_granted_hp"] for h in heroes),"passed":len(active)>=30 and len(classes)>=3}
    passed=activation["passed"] and all(g["passed"] for g in gates.values()) and not any(s["flagged"] for s in sweeps.values())
    report={"plan":plan,"comparisons":comparisons,"gates":gates,"regressions":sweeps,"activation":activation,
            "by_class":{arm:class_summary(summary) for arm,summary in comparisons.items()},"purchases":purchases,
            "qualitative_example":activation_examples(directory,rows["candidate"]),
            "completed_games":360,"state_hash_audited_games":360,"invalid_games_scored":0,
            "verdict":"passed_local_confirmation" if passed else "local_confirmation_inconclusive",
            "hosted_evaluation_eligible":passed,
            "totals":{arm:{"ticks":sum(r["ticks"] for r in cases),"actions":sum(r["actions"] for r in cases),
                           "decisions":sum(r["heroes"][r["candidate_slots"][0]]["decisions"] for r in cases),
                           "timeouts":sum(r["timeout"] for r in cases),
                           "max_work":max(h["max_work"] for r in cases for h in r["heroes"]),
                           "max_instructions":max(h["max_instructions"] for r in cases for h in r["heroes"])} for arm,cases in rows.items()}}
    write(directory/"result.json",report)
    report_path=HERE/"hp-investment-20260910-result.json";write(report_path,report)
    reference={"artifact":str(report_path.relative_to(ROOT)),"sha256":digest(report_path.read_bytes())}
    original=read(directory/"candidate/policy.ir.json");updated=deepcopy(original)
    updated["belief"]["claims"]["B_hp_investment"].update(status="requires_review",evidence=[reference])
    updated["belief"]["claims"]["B_hp_investment_result"]={"claim":"Frozen local comparison across 120 independent seeds: "+json.dumps(gates,sort_keys=True)+". Activation: "+json.dumps(activation,sort_keys=True)+". Verdict "+report["verdict"]+". All 360 replay state sequences matched. This is evidence about this complete candidate among nine defaults; hosted field superiority remains untested.","status":"supported","evidence":[reference]}
    updated["update"].update(parent=digest(original),revision=original["update"]["revision"]+1,
                             change={"origin":"evaluation_feedback","verdict":report["verdict"]},
                             evidence=[*original["update"]["evidence"],reference])
    refresh_grounding(updated)
    if compile_policy(updated)!=compile_policy(original):
        raise ValueError("evaluation feedback changed tested behavior")
    if not (directory/"evaluated").exists():
        bundle(updated,directory/"evaluated")
    write(HERE/"hypotheses/hp_investment.ir.json",updated)
    (HERE/"hypotheses/hp_investment.bas").write_text(compile_policy(updated))
    print(json.dumps({"gates":gates,"activation":activation,"verdict":report["verdict"],"hosted_evaluation_eligible":passed},indent=2),flush=True)


if __name__=="__main__":
    main()
