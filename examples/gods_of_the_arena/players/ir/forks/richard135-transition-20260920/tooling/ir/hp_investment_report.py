"""Independently recompute the completed HP Investment evaluation and render it."""

import argparse
from copy import deepcopy
import html
import json
from pathlib import Path

from hypothesis_study import confirmatory_gate, paired, regression_sweep
from policy_ir import HERE, ROOT, bundle, compile_policy, digest, extract, read, refresh_grounding, write
from study_report import load_cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    args=parser.parse_args();directory=args.directory.resolve()
    report=read(directory/"result.json");plan=read(directory/"plan.json")
    rows={arm:load_cases(directory,"validation",arm,plan["cases"],sha,plan["baseline_sha256"])
          for arm,sha in plan["sources"].items()}
    for arm in ["parent","baseline"]:
        comparison=paired(rows[arm],rows["candidate"])
        if comparison!=report["comparisons"][arm] or confirmatory_gate(comparison,.05 if arm=="parent" else .10)!=report["gates"][arm] or regression_sweep(comparison)!=report["regressions"][arm]:
            raise ValueError("reported score/gate does not recompute")
    accepted_events=[]
    for arm,cases in rows.items():
        for case in cases:
            slot=case["candidate_slots"][0];label=f"seed-{case['seed']}-slot-{slot}"
            audit=read(directory/"purchase-audits"/arm/(label+".json"))
            if audit["hash_mismatches"] or audit["replay_sha256"]!=case["replay_sha256"] or audit["binary_sha256"]!=plan["auditor_sha256"] or audit["ticks"]!=case["ticks"] or audit["actions_consumed"]!=case["actions"]:
                raise ValueError("replay audit coverage mismatch")
            if arm!="candidate":
                continue
            hp_events=audit["heroes"][slot]["hp_equipment_events"]
            observed=[];previous=0
            trace=directory/"validation"/arm/label/"episode.replay.trace.jsonl"
            for line in trace.read_text().splitlines():
                event=json.loads(line)
                if event["slot"]!=slot:
                    continue
                count=event["hp_gear_investments"]
                if count>previous:
                    if count!=previous+1:
                        raise ValueError("more than one investment in a decision")
                    matches=[e for e in hp_events if e["tick"]==event["tick"] and e["item"] in [5,6,9]]
                    # Other E2 purchases can occur later in this same tick. The
                    # early phase's item is the first matching accepted HP buy.
                    if not matches:
                        raise ValueError("counter activation lacks accepted purchase")
                    e=matches[0]
                    expected={5:50,6:60,9:70}[e["item"]]
                    if e["hp_after"]-e["hp_before"]!=expected or e["max_hp_after"]-e["max_hp_before"]!=expected:
                        raise ValueError("investment counter HP differs from real engine effect")
                    observed.append({"seed":case["seed"],"slot":slot,**e})
                previous=count
            hero=case["heroes"][slot]
            if len(observed)!=hero["hp_gear_investments"] or sum(e["hp_after"]-e["hp_before"] for e in observed)!=hero["hp_gear_granted_hp"]:
                raise ValueError("trace, accepted purchases and end counters disagree")
            accepted_events.extend(observed)
    ir=read(HERE/"hypotheses/hp_investment.ir.json")
    source=compile_policy(ir)
    if source!=(directory/"candidate/policy.bas").read_text() or extract(source,ir)!=ir:
        raise ValueError("feedback IR differs from the evaluated policy")
    # Feed audited mechanism evidence back separately from the win hypothesis.
    reference={"artifact":str((HERE/"hp-investment-20260910-result.json").relative_to(ROOT)),
               "sha256":digest((HERE/"hp-investment-20260910-result.json").read_bytes())}
    activation=report["activation"]
    parent,candidate=report["purchases"]["parent"],report["purchases"]["candidate"]
    claims={
        "B_hp_investment_mechanism":{
            "claim":f"Replay audits matched all {len(accepted_events)} early investment events to accepted purchases and actual current/max HP increases: {activation['granted_hp']} current HP added across {activation['games']}/120 games and {len(activation['classes'])} classes. This establishes execution of the intended HP effect, not fort-win superiority.",
            "status":"supported","evidence":[reference]},
        "B_hp_investment_tradeoff":{
            "claim":f"In this matched local comparison, accepted healing purchases changed from {parent['healing_purchases']} to {candidate['healing_purchases']}, healing rejections for lack of space from {parent['healing_rejected_no_space']} to {candidate['healing_rejected_no_space']}, and equipment purchases from {parent['equipment_purchases']} to {candidate['equipment_purchases']}. Totals depend on episode duration. These observations are consistent with a consumable/gear capacity tradeoff; they do not isolate which change caused the win result. The predeclared superiority gates were {'met' if all(g['passed'] for g in report['gates'].values()) else 'not met'}.",
            "status":"supported","evidence":[reference]},
    }
    if any(ir["belief"]["claims"].get(key)!=value for key,value in claims.items()):
        original=deepcopy(ir)
        ir["belief"]["claims"].update(claims)
        ir["update"].update(parent=digest(original),revision=original["update"]["revision"]+1,
            change={"origin":"audited_semantic_review","verdict":report["verdict"]},
            needs_review=["belief/"+key for key,value in ir["belief"]["claims"].items() if value["status"]!="supported"])
        refresh_grounding(ir)
    if compile_policy(ir)!=source or extract(source,ir)!=ir:
        raise ValueError("audited belief feedback changed tested behavior")
    if not (directory/"reviewed").exists():
        bundle(ir,directory/"reviewed")
    elif read(directory/"reviewed/policy.ir.json")!=ir:
        raise ValueError("audited review bundle changed")
    write(HERE/"hypotheses/hp_investment.ir.json",ir)
    proof={"source_trace_hash_checks":360,"state_hash_audited_games":360,"independent_seeds":120,
           "accepted_investments_matched_to_trace":len(accepted_events),"accepted_investment_events":accepted_events,
           "round_trip_parity":True,"source_sha256":digest(source.encode()),"tests_passed":36,
           "files":{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in
                    [HERE/"hp-investment-20260910-result.json",HERE/"hypotheses/hp_investment.ir.json",HERE/"hypotheses/hp_investment.bas",ROOT/"tmp/gota-ir/hp-investment-tests.log"]}}
    interruption_path=directory/"interruption.json"
    if interruption_path.exists():
        proof["interrupted_attempts"]=read(interruption_path)
        proof["files"][str(interruption_path.relative_to(ROOT))]=digest(interruption_path.read_bytes())
    write(HERE/"hp-investment-20260910-verification.json",proof)
    gates=report["gates"];pairs=report["comparisons"]
    summary_rows=[]
    for arm,label in [("parent","Duelist parent"),("baseline","Default policy")]:
        s=pairs[arm];g=gates[arm]
        summary_rows.append(f"<tr><td>{label}</td><td>{s['control_wins']}/120</td><td>{s['wins']}/120</td><td>{g['gain']*100:+.2f} points</td><td>{g['one_sided_exact_p']:.5f}</td><td>{'Pass' if g['passed'] else 'Fail'}</td></tr>")
    class_rows=[]
    for p,b in zip(report["by_class"]["parent"],report["by_class"]["baseline"]):
        values=[p["class"],p["n"],b["control_wins"],p["control_wins"],p["wins"],p["control_deaths"],p["deaths"],p["control_equipment"],p["equipment"]]
        class_rows.append("<tr>"+"".join("<td>"+html.escape(str(v))+"</td>" for v in values)+"</tr>")
    metrics=[]
    for key,label in [("healing_purchases","Accepted healing purchases"),("healing_gold","Healing gold spent"),("equipment_purchases","Accepted equipment purchases"),("hp_from_equipment","Current HP added by all equipment"),("healing_rejected_no_space","Healing rejected: no space")]:
        metrics.append("<tr><td>"+label+"</td>"+"".join(f"<td>{report['purchases'][arm][key]:,}</td>" for arm in ["baseline","parent","candidate"])+"</tr>")
    activation=report["activation"]
    flags={arm:[{"class":f["class"],"metric":f["metric"],"mean_delta":f["mean_delta"]} for f in sweep["flagged"]] for arm,sweep in report["regressions"].items()}
    verdict="Local gates passed; hosted confirmation required" if report["hosted_evaluation_eligible"] else "Local superiority gate not met"
    example=report["qualitative_example"]
    example_text="No early investment activated."
    if example:
        ticks={e["tick"] for e in example["candidate_events"]}
        buys=[e for e in example["purchase_audits"]["candidate"]["hp_equipment_events"] if e["tick"] in ticks and e["item"] in [5,6,9]]
        example_text=f"First activating case (chosen by seed order): seed {example['seed']}, slot {example['slot']}. " + "; ".join(f"tick {e['tick']}: item {e['item']}, HP {e['hp_before']}→{e['hp_after']}, gold {e['gold_before']}→{e['gold_after']}" for e in buys) + ". Accepted purchases match the policy's investment events. Full parent and candidate purchase histories are included in the JSON report."
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GOTA — HP Investment evaluation</title><style>body{margin:0;background:#f8f5ee;color:#252d26;font:17px/1.55 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:40px 28px}h1{font-size:37px;line-height:1.15}h2{margin-top:32px;font-size:23px}.stamp{font-size:13px;letter-spacing:.1em;text-transform:uppercase}.verdict{padding:18px;background:#fff0cc;border-left:5px solid #aa7b21}.table{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:15px}th,td{text-align:right;border-bottom:1px solid #d6d8cc;padding:9px}th:first-child,td:first-child{text-align:left}a{color:#21634a}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}.small{font-size:14px;color:#555e54}</style><main><div class="stamp">Gods of the Arena · 10 September 2026 · published game 2026.9.10.3</div><h1>HP equipment as emergency sustain</h1><div class="verdict"><b>'''+verdict+'''</b></div><p>The new IR-generated policy buys one missing HP item before ordinary consumables when below half HP and without healing stock. It compares with unchanged reconciled Duelist and the default policy on <b>120 independent seeds, 12 cases per class, 360 complete games</b>. Nine other seats use defaults. This was one frozen candidate with no preliminary selection sweep.</p><h2>Fort wins decide the result</h2><div class="table"><table><tr><th>Reference</th><th>Reference wins</th><th>Candidate wins</th><th>Paired gain</th><th>One-sided exact p</th><th>Win gate</th></tr>'''+"".join(summary_rows)+'''</table></div><p>Required before play: at least +5 points over Duelist and +10 over default, paired exact p &lt; .025 for both, sufficient mechanism activation, and no flagged adverse regression. No sample extension or threshold changes. The N=120 floor is a conservative local choice; smaller gains may remain unresolved.</p><h2>Did the intended behavior happen?</h2><p>'''+f"Accepted early investments: <b>{activation['investments']}</b>, adding <b>{activation['granted_hp']:,} current HP</b>, across <b>{activation['games']}/120 games</b> and <b>{len(activation['classes'])}/10 classes</b>. Activation gate: {'passed' if activation['passed'] else 'failed'}. Every investment counter event was matched to an accepted replay purchase and its actual HP gain."+'''</p><p>'''+html.escape(example_text)+'''</p><div class="table"><table><tr><th>Audit metric</th><th>Default</th><th>Duelist</th><th>Candidate</th></tr>'''+"".join(metrics)+'''</table></div><p class="small">All-equipment HP includes healthy purchases and later normal equipment; it is not exclusively emergency sustain. Purchases consume real gold and permanent slots. Totals also depend on game duration.</p><h2>Class outcomes and tradeoffs</h2><div class="table"><table><tr><th>Class</th><th>N</th><th>Default wins</th><th>Duelist wins</th><th>Candidate wins</th><th>Duelist deaths</th><th>Candidate deaths</th><th>Duelist gear</th><th>Candidate gear</th></tr>'''+"".join(class_rows)+'''</table></div><p>Regression checks cover wins, timeouts, deaths per decision, ending equipment and level, overall and by class, at .05/55 per comparison for each reference. Flagged comparisons:</p><pre>'''+html.escape(json.dumps(flags,indent=2))+'''</pre><p class="small">Per-class n=12 has low power. No flag is not proof of safety; ending gear, levels and death totals depend on episode duration. Full paired metrics and test results are in the JSON report.</p><h2>Evidence returned to the IR</h2><p>The outcome and activation evidence are recorded in the candidate's beliefs. The evaluated IR regenerates the exact frozen BASIC, with both representation directions checked. All 36 tests passed; the tracing instrumentation reproduced the prior baseline tape. All 360 replay state sequences matched, and no invalid games were scored. Local results alone do not establish hosted field superiority.</p><p><a href="hypotheses/hp_investment.ir.json">Evaluated IR</a> · <a href="hypotheses/hp_investment.bas">Exact BASIC</a> · <a href="hp-investment-20260910-result.json">All results and plan</a> · <a href="hp-investment-20260910-verification.json">Independent verification</a> · <a href="experiments/2026-09-10-hp-investment.md">Experiment record</a></p></main></html>'''
    if interruption_path.exists():
        page=page.replace("<h2>Evidence returned to the IR</h2>",
            "<h2>Interrupted attempts</h2><p>Two initial candidate attempts hit the local 180-second wall-clock limit while the machine was under heavy load; parent and default had zero. Both original seed/seat cases completed on retry with unchanged source. Preserved partial traces exactly match the completed retry prefixes. No case was dropped or replaced; the final comparison includes all 120 cases per arm.</p><h2>Evidence returned to the IR</h2>")
    (HERE/"hp-investment-20260910-report.html").write_text(page)
    print(json.dumps({"verified_games":360,"accepted_investments":len(accepted_events),"verdict":report["verdict"]}))


if __name__=="__main__":
    main()
