"""Audit a completed hypothesis study, update each IR, and render its findings."""

import argparse
from copy import deepcopy
import html
import json
from pathlib import Path

from hypothesis_study import (HYPOTHESES, activation, confirmatory_gate, paired,
                              regression_sweep)
from policy_ir import HERE, bundle, compile_policy, digest, read, write


CLASSES = ["Vanguard Knight", "Ranger", "Arcanist", "Druid Warden", "Demon Hunter",
           "Death Knight", "Crossbowman", "Lich", "Warlock", "Berserker"]


def load_cases(directory, phase, arm, cases, source_hash, baseline_hash):
    rows = []
    for case in cases:
        path = directory / phase / arm / f"seed-{case['seed']}-slot-{case['slot']}" / "result.json"
        row = read(path)
        if (row["seed"] != case["seed"] or row["candidate_slots"] != [case["slot"]]
                or row["candidate_sha256"] != source_hash or row["baseline_sha256"] != baseline_hash):
            raise ValueError(f"case/source mismatch: {path}")
        for key, filename in [("replay_sha256", "episode.replay"), ("trace_sha256", "episode.replay.trace.jsonl")]:
            if digest((path.parent / filename).read_bytes()) != row[key]:
                raise ValueError(f"artifact hash mismatch: {path.parent / filename}")
        if len(row["heroes"]) != 10 or {h["class"] for h in row["heroes"]} != set(range(10)):
            raise ValueError("missing hero/class")
        if any(h["max_work"] > 50000 or h["max_instructions"] > 20000 for h in row["heroes"]):
            raise ValueError("VM budget exceeded")
        rows.append(row)
    return rows


def class_summary(summary):
    output = []
    for index, name in enumerate(CLASSES):
        rows = [p for p in summary["pairs"] if p["class"] == index]
        output.append({"class": name, "n": len(rows),
                       "control_wins": sum(p["control"]["score"] for p in rows),
                       "wins": sum(p["candidate"]["score"] for p in rows),
                       "control_deaths": sum(p["control"]["deaths"] for p in rows),
                       "deaths": sum(p["candidate"]["deaths"] for p in rows),
                       "control_equipment": sum(p["control"]["equipment_count"] for p in rows),
                       "equipment": sum(p["candidate"]["equipment_count"] for p in rows)})
    return output


def trace_examples(directory, name):
    # Deterministic illustrations, never selected by win outcome.
    examples = {}
    case_name = "seed-61000-slot-0"
    slot = 0
    if name == "recovery":
        for path in sorted((directory / "discovery" / name).glob("*/result.json")):
            row = read(path)
            selected_slot = row["candidate_slots"][0]
            if row["heroes"][selected_slot]["recovery_activations"]:
                case_name, slot = path.parent.name, selected_slot
                break
    for arm in ["parent", name]:
        path = directory / "discovery" / arm / case_name / "episode.replay.trace.jsonl"
        selected = []
        previous = 0
        with path.open() as stream:
            for line in stream:
                event = json.loads(line)
                if event["slot"] != slot:
                    continue
                relevant = (event["recovery_activations"] > previous if name == "recovery"
                            else event["target_kind_after_tick"] in [1,4] if name == "structures"
                            else any(a["kind"] == 3 and a["first"] in [1,2] for a in event["commands"]))
                previous = event["recovery_activations"]
                if relevant:
                    selected.append(event)
                if len(selected) == 3:
                    break
        examples[arm] = {"trace": str(path), "events": selected,
                         "case_selection": "First activating case for recovery, first seed/seat for other mechanisms; never selected by wins.",
                         "note": "Sparse trace; an empty excerpt does not establish absence. Complete-game counters determine activation."}
    if name == "recovery" and examples[name]["events"]:
        tick = examples[name]["events"][0]["tick"]
        events = [json.loads(line) for line in Path(examples["parent"]["trace"]).read_text().splitlines()]
        examples["parent"]["events"] = sorted((e for e in events if e["slot"] == slot),
                                                key=lambda e: abs(e["tick"] - tick))[:2]
    return examples


def audit(directory):
    plan, report = read(directory / "plan.json"), read(directory / "result.json")
    for name, sha in plan["sources"].items():
        if digest((directory / name / "policy.bas").read_bytes()) != sha:
            raise ValueError("frozen source no longer matches plan")
    discovery = {name: load_cases(directory, "discovery", name, plan["selection_cases"], sha,
                                  plan["baseline_sha256"]) for name, sha in plan["sources"].items()}
    for name in HYPOTHESES:
        summary = paired(discovery["parent"], discovery[name])
        summary["activation"] = activation(summary, name)
        summary["qualifies"] = summary["wins"] - summary["control_wins"] >= 4 and summary["activation"]["observed"]
        if summary != report["discovery"][name]:
            raise ValueError("discovery report differs from artifacts")
    episodes = sum(len(rows) for rows in discovery.values())
    eligible = [name for name in HYPOTHESES if report["discovery"][name]["qualifies"]]
    if bool(eligible) != (report["validation"] is not None):
        raise ValueError("confirmation coverage does not follow preregistered selection")
    if report["validation"] is not None:
        winner = max(eligible, key=lambda name: report["discovery"][name]["wins"])
        if (report["winner"] != winner or report["source_sha256"] != plan["sources"][winner]
                or read(directory / "selected.json") != {"name": winner, "source_sha256": plan["sources"][winner], "frozen_before_validation": True}):
            raise ValueError("validation candidate differs from frozen selection")
        sources = {"parent": plan["sources"]["parent"], "candidate": plan["sources"][report["winner"]],
                   "baseline": plan["baseline_sha256"]}
        arms = {name: load_cases(directory, "validation", name, plan["validation_cases"], sha,
                                plan["baseline_sha256"]) for name, sha in sources.items()}
        for name in ["parent", "baseline"]:
            summary = paired(arms[name], arms["candidate"])
            if summary != report["validation"][name]:
                raise ValueError("validation report differs from artifacts")
            if (confirmatory_gate(summary, .05 if name == "parent" else .10) != report["gates"][name]
                    or regression_sweep(summary) != report["regressions"][name]):
                raise ValueError("validation gate/regression result does not recompute")
        episodes += sum(len(rows) for rows in arms.values())
        passed = all(g["passed"] for g in report["gates"].values()) and not any(s["flagged"] for s in report["regressions"].values())
    else:
        passed = False
    if report["hosted_evaluation_eligible"] != passed:
        raise ValueError("reported eligibility does not follow completed gates")
    purchase_diagnosis = read(directory / "purchase-diagnosis.json") if (directory / "purchase-diagnosis.json").exists() else None
    if purchase_diagnosis:
        for filename, sha in purchase_diagnosis["artifact_hashes"].items():
            path = directory / "purchase-audits" / filename
            if digest(path.read_bytes()) != sha or read(path)["hash_mismatches"] != 0:
                raise ValueError("purchase audit integrity failure")
    return {**report, "plan": plan, "completed_games": episodes,
            "artifact_audit": {"source_replay_and_trace_checks": "passed", "invalid_games_scored": 0},
            "purchase_diagnosis": purchase_diagnosis,
            "by_class": {name: class_summary(summary) for name, summary in report["discovery"].items()},
            "trace_examples": {name: trace_examples(directory, name) for name in HYPOTHESES}}


def update_policies(directory, report_path, report):
    reference = {"artifact": str(report_path), "sha256": digest(report_path.read_bytes())}
    manifests = {}
    for name, hypothesis in HYPOTHESES.items():
        original = read(directory / name / "policy.ir.json")
        source = compile_policy(original)
        if digest(source.encode()) != report["plan"]["sources"][name]:
            raise ValueError("report/IR source mismatch")
        updated = deepcopy(original)
        summary = report["discovery"][name]
        text = (f"Local discovery, six independent seed clusters with all ten seats: {summary['wins']}/60 "
                f"wins versus matched Duelist {summary['control_wins']}/60. "
                f"Predeclared activation proxy: {json.dumps(summary['activation'], sort_keys=True)}. "
                "Discovery is exploratory and cannot establish superiority.")
        if report.get("winner") == name:
            text += " Frozen independent validation: " + json.dumps(report["gates"], sort_keys=True)
            text += ". Whole-policy local eligibility: " + str(report["hosted_evaluation_eligible"]) + "."
        else:
            text += " This candidate did not qualify for the single fresh-seed confirmation."
        updated["belief"]["claims"][hypothesis["belief"]]["status"] = "requires_review"
        updated["belief"]["claims"][hypothesis["belief"]]["evidence"].append(reference)
        updated["belief"]["claims"]["B_study_result"] = {
            "claim": text + " No hosted field superiority follows from these local games.",
            "status": "supported", "evidence": [reference]}
        if name == "single_heal" and report.get("purchase_diagnosis"):
            diagnosis = report["purchase_diagnosis"]
            updated["belief"]["claims"]["B_purchase_measurement"] = {
                "claim": "Purchase attempts cannot measure actual spending or double successful buys. "
                         "A post hoc, hash-verified replay audit of all ten classes on the first discovery seed "
                         "observed real command acceptance: " + json.dumps(diagnosis["summary"], sort_keys=True)
                         + ". This repairs the measurement interpretation, not the original failed selection gate. "
                         "One seed and differing game durations cannot establish an economy or win-rate advantage.",
                "status": "supported", "evidence": [reference]}
        updated["update"] = {
            "revision": original["update"]["revision"] + 1, "parent": digest(original),
            "change": {"origin": "hypothesis_study_feedback", "hypothesis": name,
                       "verdict": report["verdict"] if report.get("winner") == name else "discovery_inconclusive"},
            "needs_review": original["update"]["needs_review"],
            "evidence": original["update"]["evidence"] + [reference],
        }
        if compile_policy(updated) != source:
            raise ValueError("evidence feedback changed tested BASIC")
        manifests[name] = bundle(updated, directory / "evaluated" / name)
        destination = HERE / "hypotheses"
        destination.mkdir(exist_ok=True)
        write(destination / f"{name}.ir.json", updated)
        (destination / f"{name}.bas").write_text(source)
    return manifests


def render(report, path):
    esc = html.escape
    title = "GOTA: three hypotheses tested"
    verdict = ("No suggestion qualified for fresh-seed confirmation."
               if report["validation"] is None else
               "The frozen candidate passed local confirmation." if report["hosted_evaluation_eligible"] else
               "The frozen candidate did not pass local confirmation.")
    content = [f"<h1>{title}</h1><p class='meta'>2026-09-10 · {report['completed_games']} complete local games · game 2026.9.10.3</p>",
               f"<div class='verdict'><strong>{verdict}</strong><p>Each suggestion changes one behavior relative to Duelist. All other seats use default policies.</p></div>",
               "<h2>Suggestions and discovery results</h2><table><tr><th>Suggestion</th><th>Mechanism</th><th>Wins / 60</th><th>Duelist / 60</th><th>Change</th></tr>"]
    for name, hypothesis in HYPOTHESES.items():
        r = report["discovery"][name]
        content.append(f"<tr><td>{esc(name.replace('_',' ').title())}</td><td>{esc(hypothesis['description'])}</td>"
                       f"<td>{r['wins']}</td><td>{r['control_wins']}</td><td>{100*r['gain']:+.1f} pp</td></tr>")
    content.append("</table><p>Six seed clusters per arm: these discovery comparisons are exploratory. Qualification requires four additional wins and observed activation.</p>")
    for name in HYPOTHESES:
        content.append(f"<h2>{esc(name.replace('_',' ').title())}: class checks</h2><table><tr><th>Class</th><th>Wins</th><th>Duelist wins</th><th>Deaths</th><th>Duelist deaths</th><th>Final gear</th><th>Duelist gear</th></tr>")
        for row in report["by_class"][name]:
            content.append("<tr>" + "".join(f"<td>{esc(str(row[k]))}</td>" for k in
                           ["class","wins","control_wins","deaths","control_deaths","equipment","control_equipment"]) + "</tr>")
        content.append("</table><p>Six games per class. Death and equipment totals depend on game duration.</p>")
        observed = report["discovery"][name]["activation"]
        if name == "recovery":
            description = f"{observed['activations']} recovery event across {len(observed['classes_activated'])} of ten classes."
        elif name == "structures":
            description = f"Structure-target share rose from {100*observed['control_rate']:.2f}% to {100*observed['candidate_rate']:.2f}% of decisions."
        else:
            description = f"Double healing-purchase attempts rose from {100*observed['control_rate']:.2f}% to {100*observed['candidate_rate']:.2f}% of decisions. This counts attempts, not accepted purchases; see the audit below."
        content.append(f"<p><b>Predeclared activation proxy:</b> {esc(description)}</p>")
    if report["validation"] is not None:
        content.append(f"<h2>Fresh-seed confirmation: {esc(report['winner'])}</h2><table><tr><th>Comparison</th><th>Candidate wins</th><th>Control wins</th><th>Gain</th><th>Exact paired p</th><th>Passed</th></tr>")
        for name, summary in report["validation"].items():
            gate = report["gates"][name]
            content.append(f"<tr><td>{esc(name)}</td><td>{summary['wins']}/120</td><td>{summary['control_wins']}/120</td><td>{100*summary['gain']:+.1f} pp</td><td>{gate['one_sided_exact_p']:.4g}</td><td>{gate['passed']}</td></tr>")
        content.append("</table><p>120 independent seeds, 12 per class. Required gains: 5 points versus Duelist and 10 versus default; p&lt;0.025 for both, with no flagged regressions.</p><h2>Regression sweep</h2>")
        for name, sweep in report["regressions"].items():
            content.append(f"<p>{esc(name)}: {len(sweep['flagged'])} adverse flags in 55 comparisons, at p&lt;{sweep['threshold']:.4g}.</p>")
            if sweep["flagged"]:
                content.append(f"<pre>{esc(json.dumps(sweep['flagged'], indent=2))}</pre>")
    else:
        content.append("<h2>Regression checks</h2><p>No candidate qualified for the independent confirmation or its statistical regression sweeps. Discovery class results are shown above; six cases per class cannot establish class safety.</p>")
    if report.get("purchase_diagnosis"):
        diagnosis = report["purchase_diagnosis"]
        content.append("<h2>Healing: attempts versus actual purchases</h2><p>The attempt-rate proxy did not measure successful double purchases. Recorded commands were re-applied through the real simulator for all ten classes on the first discovery seed, checking every state hash.</p><table><tr><th>Metric</th><th>Duelist</th><th>Single heal</th></tr>")
        for key in ["double_heal_success_ticks", "healing_purchases", "healing_gold", "healing_rejected_no_space", "equipment_purchases"]:
            content.append(f"<tr><td>{esc(key.replace('_',' '))}</td><td>{diagnosis['summary']['parent'][key]}</td><td>{diagnosis['summary']['single_heal'][key]}</td></tr>")
        content.append("</table><p>This is a post hoc mechanism check on one correlated seed, with different game durations. It does not change the failed discovery gate or establish a spending advantage.</p>")
    content.append("<div class='caveat'><b>Limits:</b> No live-field superiority claim. No incomplete or VM-failed games were scored. Discovery is small; class-level validation also has limited power. Historical validation sets were not reused. The IR records measured outcomes without silently changing tested BASIC.</div>")
    content.append("<footer>Method: <a href='https://github.com/Metta-AI/optimizer-seed/tree/main/skills'>optimizer-seed skills</a>. Complete evidence and source hashes are in the adjacent JSON report and IR hypotheses.</footer>")
    css = """*{box-sizing:border-box}body{margin:0;background:#fffdf4;color:#17202d;font:15px/1.55 system-ui,sans-serif}.page{max-width:1080px;margin:auto;padding:42px 30px 70px}h1,h2{font-family:Georgia,serif}h1{font-size:32px;margin:0}h2{font-size:22px;margin-top:34px}.meta,footer{color:#67716c;font-size:13px}.verdict{border-top:3px solid #6e8050;border-bottom:1px solid #d4c9b5;padding:18px 0;margin:24px 0}.verdict strong{font-size:21px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;border-bottom:1px solid #e4dac8;padding:10px 9px;vertical-align:top}th{color:#555;font-size:12px}.caveat{background:#f6eee4;border-left:4px solid #b36e4e;padding:16px;margin-top:30px}pre{white-space:pre-wrap;overflow-wrap:anywhere}footer{margin-top:36px}a{color:#1a3875}@media(max-width:700px){.page{padding:20px 12px}table{font-size:11px}th,td{padding:7px 4px}}"""
    path.write_text(f"<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title><style>{css}</style><main class='page'>{''.join(content)}</main></html>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.directory.resolve())
    write(args.report, report)
    manifests = update_policies(args.directory.resolve(), args.report, report)
    render(report, args.html)
    print({"verdict": report["verdict"], "completed_games": report["completed_games"],
           "parity": {name: m["structural_parity"] for name, m in manifests.items()}, "report": str(args.html)})


if __name__ == "__main__":
    main()
