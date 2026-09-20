"""Build this audited GotA episode IR from native, rule-instrumented evidence.

The narrative and findings are specific to ereq_0806a449; other episodes fail closed.
This reader never infers a private opponent policy or issues quality verdicts.
Use the source-matched replay_semantic_episode_probe.nim before this command.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clock(tick):
    seconds = tick / 24
    return f"{int(seconds // 60):02d}:{seconds % 60:05.2f}"


def predicate(name, values):
    if name == "always":
        return True
    if name == "inventory_has_empty":
        return values["emptySlot"] != 0
    if name == "no_candidate_no_motion":
        return values["bestId"] == 0 and values["motionActive"] == 0
    raise ValueError(f"Unimplemented predicate: {name}")


def check_rules(row, policy):
    """Compare IR guards with independently executed fire markers and action ranges."""
    events = row["rule_events"]
    expected_order = [r["id"] for r in policy["strategy"]]
    assert [e["rule"] for e in events if e["phase"] == "eval"] == expected_order
    reports, action_cursor = [], 0
    for rule in policy["strategy"]:
        ev = [e for e in events if e["rule"] == rule["id"]]
        assert ev[0]["phase"] == "eval" and ev[-1]["phase"] == "exit"
        expected = predicate(rule["when"], ev[0]["values"])
        fired = any(e["phase"] == "fire" for e in ev)
        assert [e["phase"] for e in ev] == (["eval", "fire", "exit"] if fired else ["eval", "exit"])
        assert ev[0]["command_offset"] == action_cursor
        action_cursor = ev[-1]["command_offset"]
        actions = row["actions"][ev[0]["command_offset"]:action_cursor]
        assert fired or not actions
        reports.append({"rule": rule["id"], "skill": rule["skill"], "predicate": rule["when"],
                        "expected": expected, "fired": fired, "consistent": expected == fired,
                        "values_at_evaluation": ev[0]["values"], "actions": actions,
                        "goals": rule["for"]})
    assert action_cursor == len(row["actions"])
    return reports


def selected_writer(reports):
    writers = [r["rule"] for r in reports if any(a["kind"] in (1, 2) for a in r["actions"])]
    return writers[-1] if writers else None


def terms(row, previous_tick=None):
    m, o = row["memory"], row["observation"]
    self_data = o["self"]
    enemy = [x for x in o["objects"] if x["team"] != self_data["selfTeam"] and x["kind"] == 2
             and x["alive"] and x["hp"] > 0]
    result = ["sentry assignment", "visible living enemy count", "selected target", "own structure condition"]
    result.append("defense commitment active" if m["defActive"] else "ordinary target selection")
    if m["defActive"]:
        result += ["defense deadline", "defense rally point", "defense intercept eligibility"]
    if len(o["objects"]) > m["defMotionLimit"]:
        result.append("combat motion budget gate exceeded")
    if m["defActive"] and (self_data["selfX"], self_data["selfY"]) == (m["defPointX"], m["defPointY"]):
        result.append("self tile equals rally tile")
    if not enemy:
        result.append("no living enemy hero in current visibility")
    if previous_tick is not None and row["tick"] > previous_tick + 1 and m["defActive"]:
        result.append("defense memory persists across a decision gap")
    return result


def observable_summary(row):
    objects, own = row["observation"]["objects"], row["observation"]["self"]
    towers = [o for o in objects if o["kind"] == 4 and o["team"] == own["selfTeam"] and o["hp"] > 0]
    god = next(o for o in objects if o["kind"] == 1 and o["team"] == own["selfTeam"])
    enemies = [o for o in objects if o["kind"] == 2 and o["team"] != own["selfTeam"] and o["alive"] and o["hp"] > 0]
    return {"hp": own["selfHp"], "max_hp": own["selfMaxHp"], "tile": [own["selfX"], own["selfY"]],
            "hits": own["selfAttacksLanded"], "level": own["selfLevel"], "gold": own["selfGold"],
            "own_god_hp": god["hp"], "own_standing_towers": len(towers),
            "visible_living_enemy_heroes": [{k: o[k] for k in ("id", "x", "y", "hp")} for o in enemies]}


def proxy(state):
    # Retrospective full-state material proxy; not calibrated win probability.
    return sum((1 if x["team"] == 0 else -1) * max(0, x["hp"]) /
               (100 if x["kind"] == 1 else x["max_hp"])
               for x in state["structures"] if x["kind"] in (1, 4))


GLOSSARY = {
    "sentry assignment": "defSentry after R1; class-selected role, not a belief about a teammate's intent.",
    "visible living enemy count": "Count current observation objects with enemy team, kind=2, alive=true and hp>0. Never substitute defCount when defFront=0.",
    "selected target": "bestId after R1, including zero for no candidate; join nonzero IDs only to the current visible object list.",
    "own structure condition": "HP and standing status (hp>0) of allied kinds 1 and 4 in the current observation. Standing is distinct from objectAlive/exposure.",
    "ordinary target selection": "R1's defActive=0 branch, which performs ordinary bounded target selection.",
    "no living enemy hero in current visibility": "No current observed enemy kind=2 object has alive=true and hp>0. This says nothing about enemies outside visibility or enemy footmen.",
    "defense commitment active": "defActive=1 after R1, from worldTick<defUntil; commitment may outlive the visible group that initiated it.",
    "defense deadline": "Persistent defUntil and its remaining ticks, max(0,defUntil-worldTick). This is a commitment expiry, not a forecast or confidence.",
    "defense rally point": "Persisted defPointX/defPointY selected by R1; actual R4 walk destination may differ if terrain fallback runs.",
    "defense intercept eligibility": "Visible living enemy hero/footman within squared distance 100 of self, and within squared distance 400 of the remembered threat or squared distance 9 of self. R1 then ranks eligible candidates.",
    "combat motion budget gate exceeded": "objectCount()>defMotionLimit at R2; on this subject's active defense branch the limit is 40. This selects attack-only execution before cadence calculations.",
    "defense renewal from fewer than four nearby heroes": "A current nonzero defFront and defAnchor, defCount<defGroupSize, and an increase from pre-decision defUntil to the new deadline. Record the exact renewal tick; never backdate it to the span's start.",
    "defense memory persists across a decision gap": "At the first invocation after a missing-tick interval, R1 still yields defActive=1; verify the interval's death/respawn cause separately.",
    "self tile equals rally tile": "Host integer selfX/selfY equals defPointX/defPointY. This does not prove exact physical arrival, unobstructed movement, or tactical safety.",
}


def build(evidence, artifacts, output):
    output.mkdir(parents=True, exist_ok=True)
    policy, episode, result = read(evidence / "policy.ir.json"), read(evidence / "requested-episode.json"), read(artifacts / "results.json")
    assert episode['id'] == 'ereq_0806a449-3d7c-4160-868a-3e157634ebbc', 'Narrative is specific to the audited episode.'
    eq, parity = read(evidence / "instrumentation-equivalence.json"), read(evidence / "policy-parity.json")
    assert eq["unmodified_vs_instrumented_rows_equal_excluding_rule_events"]
    assert parity["compile_exact"] and parity["reverse_executable_exact"]
    assert parity["source_bytes_sha256"] == sha(evidence / "policy.bas")
    assert parity["ir_bytes_sha256"] == sha(evidence / "policy.ir.json")
    assert episode["id"] == artifacts.name and episode["participants"][0]["policy_name"] == "aaron-gota-ir-relh154-legacy-0916"
    assert episode["coworld_version"] == policy["execution"]["game_version"] == "2026.9.16.5"
    assert result["scores"] == [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    trace = evidence / "reconstructed-instrumented.jsonl"
    spans, timeline, checks, event_examples, globals_count = [], [], Counter(), {}, 0
    last_tick, previous_key, current, summary, terminal_state = 0, None, None, None, None
    structure_events, previous_structures = [], None
    terms_by_id = defaultdict(list)
    death_ticks = []
    prior_subject_state = None
    for line_no, line in enumerate(trace.open(), 1):
        row = json.loads(line)
        if row["type"] == "summary":
            summary = row
        elif row["type"] == "ground_truth":
            terminal_state = row
            timeline.append({"tick": row["tick"], "proxy": proxy(row)})
            subject = row["heroes"][0]
            if subject["state"] == "Dying" and prior_subject_state != "Dying":
                death_ticks.append(row["tick"])
            prior_subject_state = subject["state"]
            now = {s["id"]: s for s in row["structures"]}
            if previous_structures:
                for id_, s in now.items():
                    old = previous_structures[id_]
                    if old["hp"] > 0 and s["hp"] <= 0:
                        structure_events.append({"tick": row["tick"], "id": id_, "team": s["team"], "kind": s["kind"]})
            previous_structures = now
        elif row["type"] == "decision":
            assert row["slot"] == 0
            rr = check_rules(row, policy)
            checks["ticks"] += 1
            checks["rule_evaluations"] += len(rr)
            checks["consistent_evaluations"] += sum(r["consistent"] for r in rr)
            checks["fired"] += sum(r["fired"] for r in rr)
            checks["locomotion_overlap_ticks"] += sum(any(a["kind"] in (1, 2) for a in r["actions"]) for r in rr) > 1
            checks["target_attack_ticks"] += bool(row["memory"]["bestId"])
            checks["attack_over_motion_limit_ticks"] += bool(row["memory"]["bestId"]) and len(row["observation"]["objects"]) > row["memory"]["defMotionLimit"]
            checks["active_motion_ticks"] += bool(row["memory"]["motionActive"])
            writer = selected_writer(rr)
            key = (bool(row["memory"]["defActive"]), writer, tuple(r["rule"] for r in rr if r["fired"]))
            assert writer in ("R2", "R4"), "Unmodeled locomotion owner; update the lift explicitly."
            globals_count = len(row["memory"])
            row["rules"] = rr
            row["source_line"] = line_no
            if key != previous_key or row["tick"] != last_tick + 1:
                if current:
                    current["termination"] = "host decision gap" if row["tick"] != last_tick + 1 else "channel choice changed"
                    current["next_tick"] = row["tick"]
                current = {"id": f"{episode['id']}.dp{len(spans)+1:02d}", "start": row, "end": row,
                           "ticks": 0, "rule": writer, "skill": next(r["skill"] for r in rr if r["rule"] == writer),
                           "defense_active": key[0], "fired": list(key[2]), "action_counts": Counter(),
                           "weak_refresh_ticks": [], "same_rally_tile_ticks": 0, "fidelity": "consistent",
                           "unglossed": terms(row, last_tick or None)}
                spans.append(current)
            current["end"] = row
            current["ticks"] += 1
            current["action_counts"].update(str(a["kind"]) for a in row["actions"])
            if not all(r["consistent"] for r in rr):
                current["fidelity"] = "inconsistent"
            m, b, own = row["memory"], row["memory_before"], row["observation"]["self"]
            if m["defFront"] and m["defAnchor"] and m["defCount"] < m["defGroupSize"] and m["defUntil"] > b["defUntil"]:
                current["weak_refresh_ticks"].append(row["tick"])
            if writer == "R4" and m["defActive"] and (own["selfX"], own["selfY"]) == (m["defPointX"], m["defPointY"]):
                current["same_rally_tile_ticks"] += 1
            if row["tick"] in (838, 8150, 8255, 13530):
                event_examples[str(row["tick"])] = row
            previous_key, last_tick = key, row["tick"]
    assert summary and summary == eq["replay_equivalence"]
    assert summary["all_state_hashes_equal"] and summary["all_actions_consumed"]
    assert summary["ticks"] == result["ticks"] == len(timeline)
    assert len(death_ticks) == 6 and checks["ticks"] == eq["counts"]["decisions"]
    assert checks["consistent_evaluations"] == checks["rule_evaluations"]
    current["termination"], current["next_tick"] = "episode ended", None
    baseline_proxy = timeline[0]["proxy"]
    for s in spans:
        begin, end = s["start"]["tick"], s["end"]["tick"]
        s["start_tick"], s["end_tick"] = begin, end
        s["observation_start"], s["observation_end"] = observable_summary(s["start"]), observable_summary(s["end"])
        s["proxy_start"] = timeline[begin - 2]["proxy"] if begin > 1 else baseline_proxy
        s["proxy_end"] = timeline[end - 1]["proxy"]
        s["proxy_delta"] = s["proxy_end"] - s["proxy_start"]
        if s["weak_refresh_ticks"]:
            s["unglossed"].append("defense renewal from fewer than four nearby heroes")
        for term in s["unglossed"]:
            terms_by_id[term].append(s["id"])
    candidates = sorted([s for s in spans if s["proxy_delta"] < 0], key=lambda x: x["proxy_delta"])[:5]
    candidate_records = [{"id": f"{episode['id']}.q{i+1:02d}", "dp": s["id"], "reason": "largest negative material-proxy change over a decision span",
                          "interval_ticks": [s["start_tick"], s["end_tick"]], "proxy_delta": s["proxy_delta"],
                          "actual": {"locomotion_rule": s["rule"], "skill": s["skill"], "episode_score": 0},
                          "source_afforded_skills": [r["skill"] for r in s["start"]["rules"] if r["fired"]],
                          "alternative_branches": [], "rollout_count": 0, "verdict": None,
                          "limits": "All source-afforded skills already ran. Unchosen strategic alternatives need explicit lifted interfaces. No live g002 policy or equivalent opponent reconstruction is available in this evidence bundle."}
                         for i, s in enumerate(candidates)]
    initial_defense = next(s for s in spans if s["defense_active"])
    sentry_span = next(s for s in spans if s["start_tick"] <= 8150 <= s["end_tick"])
    findings = [
        {"id": episode['id']+'.f01', "kind": "structural", "layer": "strategy / embedder contract", "blocks": ["strategy"],
         "evidence": [spans[0]['id'], initial_defense['id']],
         "observation": "Rules execute sequentially. R1 writes target/defense state, R2 controls combat, E0 consumes inventory, E1 and E2 both attempt purchases, R4 conditionally writes movement. R2/R4 share the locomotion output but only one writes it on each observed tick: no cross-rule overwrite occurred here. Purchases have cumulative effects on shared resources, not a single winner.",
         "proposal": "Represent rule order, read/write channels, guard evaluation phase, cumulative purchase effects and emitted-command provenance explicitly. Preserve the current execution order in the embedder."},
        {"id": episode['id']+'.f02', "kind": "structural", "layer": "1 and 5 fused", "blocks": ["skill.observe", "strategy.R1", "goal.G_defense"],
         "evidence": [initial_defense['id'], sentry_span['id']],
         "observation": "observe/lineup_paired_legacy detects the visible rush, commits to defense, refreshes its deadline and chooses a target. These strategy choices are embedded in the observer.",
         "proposal": "In a future behavior-preserving lift, give recognition, commitment initiation, commitment renewal and defensive target selection separate named predicates/rules. Do not replace the algorithm during the lift."},
        {"id": episode['id']+'.f03', "kind": "ontology_gap", "layer": "1 — situation", "blocks": ["situation.grounded.predicates"],
         "evidence": [s['id'] for s in spans],
         "observation": "The deployed glossary has only always, inventory_has_empty and no_candidate_no_motion. It cannot name the defense, sentry, renewal and intercept distinctions exercised here.",
         "proposal": "Review the exact unglossed list as a proposed glossary extension, then add grounding and boundary fixtures for accepted terms."},
        {"id": episode['id']+'.f04', "kind": "measured_behavior_no_quality_verdict", "layer": "not yet causally routed", "blocks": ["belief.B_persistent_defense", "belief.B_stale_rally", "skill.observe", "skill.fallback"],
         "evidence": [initial_defense['id'], sentry_span['id']],
         "observation": "The subject initiates defense at tick 838 and never records defActive=0 on a later living decision. A below-threshold visible group can refresh an existing sentry commitment. At tick 8150, one living observed enemy at (94,19) renews the deadline to 15350; the subject at (103,9) has no eligible target inside the ten-tile intercept radius and emits walkTo(103,9).",
         "proposal": "Attach this as a scoped activation example and a candidate for renewal/release research. It establishes intentional no-target rallying, not avoidable loss, successful defense, or collision failure."},
        {"id": episode['id']+'.f05', "kind": "evidence_gap", "layer": "research tooling", "blocks": ["belief.grounded", "execution", "update"],
         "evidence": [s['id'] for s in candidates],
         "observation": "Original policy logs have no rule trace; reconstructed globals contain commitments, not probabilistic enemy-intent estimates. Live opposing policies and forceable alternative-skill interfaces are absent.",
         "proposal": "Capture native rule events and decision-time observations during future episodes. Define branchable skill interfaces and recover validated live opponents before decision-quality verdicts. Keep absent confidence values null."},
        {"id": episode['id']+'.f06', "kind": "measured_execution_gate_no_quality_verdict", "layer": "not yet causally routed",
         "blocks": ["skill.attack.parameters.defense_motion_limit", "skill.attack", "belief.B_cadence_mechanism", "goal.G_cadence"],
         "evidence": [s['id'] for s in spans if s['rule']=='R2'],
         "observation": f"All {checks['target_attack_ticks']} subject decisions with a selected target exceed the defensive motion limit of 40 observed objects. The source therefore takes its attack-only budget branch. motionActive remains zero throughout all {checks['ticks']} living decisions; the cadence skill's presence is not evidence it activated here.",
         "proposal": "Record this activation limit separately from cadence efficacy. Investigate a cheaper combat observation set or budget-safe implementation before testing a different limit; preserve VM bounds and compare responding-policy outcomes before judging improvement."},
    ]
    fidelity = {"status": "reconstructed", "consistent": len(spans), "inconsistent": 0, "unresolvable": 0,
                "counts_scope": "complete primary-perspective decision points; all tick-level rule evaluations also checked",
                "tick_checks": dict(checks), "channels": ["bookkeeping", "target and defense", "combat/locomotion", "inventory consumption", "ordered purchases"],
                "original_internal_fidelity": "unresolvable: the original policy did not log rule evaluations",
                "scope": "Exact IR/source round trip, actual guard/fire markers and command ranges in the output-equivalent reconstruction. Not original internal-state identity, intent correctness, or quality."}
    fidelity['per_channel_decision_point_counts'] = {name: {"consistent": len(spans), "inconsistent": 0, "unresolvable": 0}
                                                  for name in fidelity['channels']}
    assert checks['locomotion_overlap_ticks'] == 0
    for name in ['policy.ir.json', 'policy.bas', 'policy.instrumented.bas', 'policy-parity.json', 'instrumentation-equivalence.json',
                 'guide-episode-semantic-ir-v2.md', 'replay_semantic_episode_probe.nim']:
        shutil.copy2(evidence / name, output / name)
    for name in ['results.json', 'episode.json']:
        shutil.copy2(artifacts / name, output / name)
    provenance_paths = [trace, evidence/'reconstructed-final.jsonl', artifacts/'replay.bin', artifacts/'owned.jsonl',
                        artifacts/'decoded.jsonl', artifacts/'audit.json', evidence/'replay-semantic-probe', Path(__file__).resolve()]
    provenance_paths += [evidence/'requested-episode.json', artifacts/'game.log']
    receipt = artifacts.parents[2]/'r5-relh154/scoped-followup/deployment-pair/deployment-verified.json'
    deployment = read(receipt)
    assert deployment['source_sha256'] == parity['source_bytes_sha256']
    assert deployment['semantic_ir_sha256'] == parity['ir_canonical_sha256']
    provenance_paths.append(receipt)
    provenance = {"episode_request_id": episode["id"], "episode_id": episode["episode_id"], "reconstruction": True,
                  "primary_slot": 0, "owned_slots_equivalence_checked": [0, 1, 2, 3, 4],
                  "game_version": episode["coworld_version"], "source_commit": "f2ab9598d8f8001b6beae3e66404e341770c803f",
                  "policy_version_id": episode['participants'][0]['policy_version_id'], "policy_id": episode['participants'][0]['policy_id'],
                  "ir_canonical_sha256": parity['ir_canonical_sha256'], "ir_bytes_sha256": parity['ir_bytes_sha256'],
                  "basic_sha256": parity['source_bytes_sha256'], "effective_seed": result['seed'],
                  "requested_seed": episode['game_config']['seed'], "map_seed": episode['game_config']['map_preset']['seed'],
                  "guide": {"filename": "guide-episode-semantic-ir (1).md", "sha256": sha(output/'guide-episode-semantic-ir-v2.md'), "section_11_applied": True},
                  "counterfactual_seeds": [], "live_opponent_rollouts": False,
                  "equivalence": summary, "global_count": globals_count,
                  "viewing": "Existing five-frame schematic of the coached interval inspected; no native viewer playback claimed. No game-specific replay-inspection skill binding was found; repository-native probes were used.",
                  "sources": [{"path": str(p.resolve()), "sha256": sha(p)} for p in provenance_paths]}
    write(output/'provenance.json', provenance)
    structured = {"schema": "gota-episode-semantic-ir/1", "status": "reconstructed; decision-quality candidates only",
                  "episode": episode, "outcome": result, "primary_slot": 0, "decision_point_count": len(spans),
                  "decision_points": spans, "fidelity": fidelity, "quality_candidates": candidate_records,
                  "findings": findings, "unglossed_terms": dict(terms_by_id), "notable_trace_examples": event_examples,
                  "ground_truth_assessment_only": {"structure_destructions": structure_events, "subject_deaths": death_ticks},
                  "provenance": provenance}
    write(output/'episode.ir.json', structured)
    write(output/'research-handoff.json', {"status": "proposals_only", "policy_modified": False, "episode": episode['id'],
                                         "findings": findings, "candidates": candidate_records, "unglossed": dict(terms_by_id)})
    write(output/'proposed-glossary.json', {term: {"status": "proposed_only", "grounding": GLOSSARY[term], "decision_points": ids}
                                          for term, ids in terms_by_id.items()})
    render(output, structured, policy, timeline, terminal_state)
    print(json.dumps({"output": str(output), "decision_points": len(spans), "fidelity": fidelity, "candidates": candidate_records}, indent=2))


def render(output, doc, policy, timeline, terminal_state):
    ep, spans, result, p = doc['episode'], doc['decision_points'], doc['outcome'], doc['provenance']
    md = [f"# Reconstructed episode IR — {ep['id']}", "", "## 1. Episode header", "",
          f"**Status:** reconstructed; fidelity is reconstruction-to-IR; decision quality is candidates only. Revised guide section 11 applies.", "",
          f"**Episode:** `{ep['episode_id']}`; request `{ep['id']}`; round `{ep['round_id']}`. "
          f"[Observatory](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:{ep['id']}).",
          f"**Environment:** Gods of the Arena / Competition, `{ep['coworld_version']}`, source `{p['source_commit']}`.",
          f"**Policy:** `{ep['participants'][0]['policy_name']}:v1`; version `{p['policy_version_id']}`; policy ID `{p['policy_id']}`.",
          f"**IR:** `{policy['id']}`, canonical SHA256 `{p['ir_canonical_sha256']}`; file-byte SHA256 `{p['ir_bytes_sha256']}`.",
          f"**BASIC:** SHA256 `{p['basic_sha256']}`; [frozen executable](policy.bas); [frozen IR](policy.ir.json).",
          "**Perspective:** slot 0, DeathKnight, Red, hero 100. Slots 1–4 are independent instances of the same version "
          "(Crossbowman, Lich, Warlock, Berserker). Their internal states are not shared with slot 0. All five owned instances are covered by command/state equivalence; the detailed account and fidelity counts cover slot 0.",
          f"**Opponents:** slots 5–9, `gota-g002:v1`, version `{ep['participants'][5]['policy_version_id']}`, policy ID `{ep['participants'][5]['policy_id']}`.",
          f"**Seed:** effective `{result['seed']}` from results/replay; requested seed `{p['requested_seed']}` is not the effective seed; map seed `{p['map_seed']}`.",
          f"**Outcome:** Red loss, Blue win; scores `{result['scores']}`. Duration {result['ticks']:,} ticks = {clock(result['ticks'])} at 24 Hz.",
          f"**Segmentation:** {len(spans)} decision points from 12,261 living decisions. A point begins when the locomotion owner, "
          "matched rule set, or fused R1 defense choice changes, or when the host resumes decisions after a death. Repeated target IDs, "
          "rally-coordinate updates, inventory use and attack ticks are execution details while those choices persist. Six death gaps are recorded as span terminations; no policy decisions are invented during them.",
          "**Observation timing:** Situation uses the visibility-filtered object list immediately before this hero's VM runs and the VM's host snapshot. "
          "Predicate truth is recorded at its rule's evaluation phase, since E0 changes the inventory facts used by E2. End-of-tick omniscient frames are kept separately for retrospective quality filtering.",
          "**Reconstruction caveat:** the original logs contain only start/completion messages. The reconstruction reproduces every owned command "
          "and every state hash in this episode. Its beliefs and rule evaluations are its own; output-equivalent but internally different "
          "original behavior is invisible. Trace prints add no globals; an uninstrumented run also matches every captured observation, "
          "all 227 globals before/after each subject decision, and all captured state projections.",
          "", "**Common rule and parameter contract**", "",
          "Rules run in this order. Every matching rule fires. R2/R4 share locomotion, with only one writer on each observed tick; purchases compose sequentially. "
          "There is no global one-rule winner or runtime ordering of abstract goals. Parameter sets below are frozen and referenced by every Selected line.", ""]
    for r in policy['strategy']:
        md.append(f"- `{r['id']}`: `{r['when']}` → `{r['skill']}`; goals {', '.join('`'+g+'`' for g in r['for'])}.")
    md += ["", "<details><summary>Exact skill operators and static parameters</summary>", "", "```json", json.dumps(policy['skill'], indent=2), "```", "", "</details>", "",
           "## 2. Arc", "",
           "The DeathKnight followed the opening wave route while no attack candidate was selected. At 00:34.92, four living visible enemy heroes "
           "near an allied tower caused `observe` to activate defense and `fallback` to send it toward a defensive rally. "
           "Across later combats and respawns it alternated between attacking selected nearby targets and returning to defensive rally points, "
           "retaining its sentry commitment. The episode ended at 09:24.88 with Red's god destroyed and Blue winning.", "", "## 3. Decision points", ""]
    for s in spans:
        a, b = s['start'], s['end']
        m, obs, last = a['memory'], s['observation_start'], s['observation_end']
        true_predicates = list(dict.fromkeys(r['predicate'] for r in a['rules'] if r['expected']))
        rr = {r['rule']: r for r in a['rules']}
        eligible = ', '.join('`'+r['skill']+'`' for r in a['rules'] if r['expected'])
        goal = ', '.join('`'+g+'`' for g in rr[s['rule']]['goals'])
        term = s['termination']
        if term == 'host decision gap':
            term += f"; next invocation at tick {s['next_tick']} after a replay-verified death/respawn gap"
        elif term == 'channel choice changed':
            term += f" at tick {s['next_tick']}"
        enemy_text = ', '.join(f"{e['id']} at ({e['x']},{e['y']}), HP {e['hp']}" for e in obs['visible_living_enemy_heroes']) or 'none'
        fired_text = ' → '.join(f"`{r['rule']}`" for r in a['rules'] if r['fired'])
        action_text = ', '.join(f"{x['kind']}({x['first']},{x['second']})" for x in a['actions'])
        # Names marked here are the exact vocabulary candidates in the glossary appendix.
        tags = '; '.join(f"{t} [unglossed]" for t in s['unglossed']
                        if t != 'defense renewal from fewer than four nearby heroes' or s['start_tick'] in s['weak_refresh_ticks'])
        selected_object = next((x for x in a['observation']['objects'] if x['id']==m['bestId']), None)
        target_text = (f" Selected target is a visible { {1:'god',2:'hero',3:'footman',4:'tower',5:'barracks'}.get(selected_object['kind'],'object')} "
                       f"at ({selected_object['x']},{selected_object['y']}), HP {selected_object['hp']}." if selected_object else '')
        renewal_clause = (f" During the span, defense renewal from fewer than four nearby heroes [unglossed] occurred "
                          f"on {len(s['weak_refresh_ticks'])} ticks, first at tick {s['weak_refresh_ticks'][0]}." if s['weak_refresh_ticks'] else '')
        md += [f"### {s['id']}", "",
               f"**Header —** tick {s['start_tick']}, {clock(s['start_tick'])}; slot 0. No environment-defined phase is recorded.",
               f"**Situation —** True glossary predicates: {', '.join('`'+x+'`' for x in true_predicates)}. "
               f"Affordances: {eligible}; these are the source guards, not mutually exclusive options. "
               f"Self HP {obs['hp']}/{obs['max_hp']}, tile {tuple(obs['tile'])}; living visible enemy heroes: {enemy_text}. "
               f"`defActive={m['defActive']}`, `defSentry={m['defSentry']}`, `bestId={m['bestId']}`.{target_text} Distinctions: {tags}.",
               f"**Belief —** No probabilistic estimate or confidence is recorded. Persistent commitment state after `observe`: "
               f"`defUntil={m['defUntil']}`, `defHoldTicks={m['defHoldTicks']}`, rally `({m['defPointX']},{m['defPointY']})`, "
               f"remembered threat `({m['defThreatX']},{m['defThreatY']})`. `defCount={m['defCount']}` is scratch state and may be stale "
               "when no current front exists; it is not a confidence or a claim about unseen enemies. Authored B_* research claims are not runtime beliefs.",
               f"**Goal in force —** Locomotion rule `{s['rule']}` cites {goal}. R1 continues to cite `G_base`, `G_defense`; "
               "the other fired rules retain the goals in the common contract. No runtime goal hierarchy was observed.",
               f"**Arbitration —** Actual ordered firing: {fired_text}. Bookkeeping: R0. Recognition/target/defense: R1 "
               f"(`defActive={m['defActive']}`). Combat: R2 emitted {len(rr['R2']['actions'])} commands. "
               f"Consumption: E0 emitted {len(rr['E0']['actions'])}. Purchases: E1 then E2 "
               f"({'matched' if rr['E2']['fired'] else 'did not match'}), {len(rr['E1']['actions'])}+{len(rr['E2']['actions'])} attempts. "
               f"Fallback R4 {'matched' if rr['R4']['fired'] else 'did not match'}. **Locomotion winner: {s['rule']}.** "
               "Rule predicates were checked against executed fire markers at their evaluation phases.",
               f"**Selected —** All matched skills listed under Affordances execute with the frozen static parameters above. "
               f"Locomotion skill `{s['skill']}` uses " + (f"target `bestId={m['bestId']}`" if s['rule']=='R2' else f"the emitted walk destination below; defense rally is `({m['defPointX']},{m['defPointY']})`" ) +
               f". Start-tick commands: `{action_text}` (1=walkTo, 2=attackTarget, 3=buyItem, 4=useItem). "
               "A command is an invocation; purchase acceptance is not inferred from an attempt.",
               f"**Execution span —** ticks {s['start_tick']}–{s['end_tick']} ({s['ticks']/24:.2f} seconds of living execution), terminated by {term}. "
               f"The policy {'issued target attacks' if s['rule']=='R2' else 'issued movement orders while no target was selected'} "
               "with inventory rules continuing in order; target and destination changes within the span are retained in the raw trace." + renewal_clause,
               f"**Consequence —** Between the first and last policy snapshots: self HP {obs['hp']}→{last['hp']}, "
               f"tile {tuple(obs['tile'])}→{tuple(last['tile'])}, successful basic-hit counter {obs['hits']}→{last['hits']}; "
               f"own visible god HP {obs['own_god_hp']}→{last['own_god_hp']}, own standing towers {obs['own_standing_towers']}→{last['own_standing_towers']}. "
               f"`no_candidate_no_motion` is {'true' if rr['R4']['fired'] else 'false'} throughout this span. "
               "These are temporal changes, not causal attribution to this hero. No stated hidden-state belief is available to score.", ""]
    f = doc['fidelity']
    md += ["## 4. Judgment I — Fidelity (reconstructed)", "",
           f"**Consistent {f['consistent']}; inconsistent 0; unresolvable 0**, for the reconstructed primary-perspective decision points. "
           f"Every one of {f['tick_checks']['rule_evaluations']:,} rule evaluations across {f['tick_checks']['ticks']:,} living ticks also matches the IR guard. "
           "No inconsistency list entries. Each channel's fired rules and command ranges were checked; ordered purchase actions are retained individually.", "",
           "Per channel (bookkeeping, target/defense, combat/locomotion, inventory consumption, ordered purchases): "
           "43 consistent, 0 inconsistent, 0 unresolvable decision points each. These are repeated views of the same 43 points, not 215 independent decisions. "
           "There are zero ticks with both R2 and R4 writing locomotion.", "",
           "The IR compiles byte-for-byte to the deployed source and reverse-extracts to the same executable contract. "
           "The instrumented reconstruction reproduces 67,929 commands from all five owned heroes and all 13,557 state hashes, consuming all 128,895 recorded actions. "
           "The uninstrumented/instrumented comparison also preserves all captured observations and globals. "
           "These checks establish reconstructed executable fidelity. **Original internal fidelity is unresolvable** because original rule evaluations were not logged. "
           "No independent claim about the truth of authored goals, inferred intent, or original private internal state follows.", "",
           "## 5. Judgment II — Decision quality (reconstructed; candidates only)", "",
           "No win-probability series is supplied. The retrospective proxy is "
           "`(own god HP − enemy god HP)/100 + sum(own tower HP/maxHP) − sum(enemy tower HP/maxHP)`, with HP floored at zero. "
           "Each god contributes up to four tower-equivalent units; barracks are excluded. For each decision span, compare the state immediately before "
           "its first tick with its last post-tick state; rank the five largest decreases. This is an explicit material heuristic, not a win probability "
           "or a causal estimate. Longer spans have more exposure, and other heroes cause much of the change.", ""]
    for c in doc['quality_candidates']:
        md += [f"### {c['id']}", "", f"**dp:** `{c['dp']}`; ticks {c['interval_ticks'][0]}–{c['interval_ticks'][1]}.",
               f"**Actual:** `{c['actual']['skill']}` via `{c['actual']['locomotion_rule']}`; episode score 0; proxy change {c['proxy_delta']:.4f}.",
               f"**Initiation conditions satisfied:** {', '.join('`'+s+'`' for s in c['source_afforded_skills'])}. "
               "All these skills already ran. The current IR supplies no unchosen exclusive defense-versus-advance skill with an independently forceable interface.",
               "**Alternatives / rollouts / verdict:** not run; n=0; no confidence interval and no verdict. "
               "The exact g002 executable or an output-equivalent live reconstruction is absent. Replaying its actions would freeze its response, "
               "so the successful replay reconstruction is not counterfactual evidence.", ""]
    md += ["No confidence-above-0.6 falsification candidates can be selected: runtime confidence is absent. "
           "There are no fidelity inconsistencies to add. No frozen-world trials were used.", "",
           "## 6. Judgment III — Diagnosis (reconstructed; proposed evidence updates)", "",
           "There are no rollout-backed decision-quality findings and no fidelity inconsistencies. Therefore none is routed as a demonstrated "
           "strategy, belief, skill-interface, or execution failure. The following are structural findings, glossary gaps, and measured-behavior "
           "proposals permitted by revised section 11; they remain proposals and do not edit the policy.", ""]
    for finding in doc['findings']:
        md += [f"### {finding['id']}", "", f"**Kind / layer:** {finding['kind']} / {finding['layer']}.",
               f"**IR blocks:** {', '.join('`'+x+'`' for x in finding['blocks'])}.",
               f"**Evidence:** {', '.join('`'+x+'`' for x in finding['evidence'])}.",
               f"**Observation:** {finding['observation']}", f"**Proposed update:** {finding['proposal']}", ""]
    md += ["## 7. Unglossed terms", "", "These exact phrases are proposed vocabulary, not newly installed predicates. "
           "Their decision-point references are complete for the distinctions annotated above.", ""]
    for term, ids in doc['unglossed_terms'].items():
        md.append(f"- **{term}** — {GLOSSARY[term]} Evidence: {', '.join('`'+id_.split('.')[-1]+'`' for id_ in ids)}.")
    md += ["", "## 8. Provenance", "",
           f"- Revised guide: `guide-episode-semantic-ir (1).md`, SHA256 `{p['guide']['sha256']}`; [frozen copy](guide-episode-semantic-ir-v2.md).",
           f"- Policy IR canonical hash `{p['ir_canonical_sha256']}`; byte hash `{p['ir_bytes_sha256']}`. These hash conventions are distinct.",
           f"- Simulator source `{p['source_commit']}`, release `{p['game_version']}`; original engine files were clean. Added probe instrumentation is [preserved here](replay_semantic_episode_probe.nim).",
           f"- Seed used for both reconstruction runs: `{p['effective_seed']}`. Counterfactual seeds: none. Other agents' recorded actions were used solely to reproduce the actual trajectory.",
           "- Rule instrumentation: eval/fire/exit markers at the original top-level rule regions; no added globals; "
           "[instrumentation equivalence](instrumentation-equivalence.json), [IR/source parity](policy-parity.json).",
           "- Full per-tick state is recoverable from the source-matched replay; the exported ground-truth JSONL is a projection, not a simulator checkpoint. "
           "The document uses full-state information only in labeled assessment/provenance, except public episode outcome and host termination facts.",
           "- All raw artifacts and SHA256 hashes: [provenance.json](provenance.json). "
           "All 43 structured blocks, exact start/end observations, rule events, and trace line references: [episode.ir.json](episode.ir.json).",
           "- Native viewer playback was not used. The existing five-frame schematic of the coached interval was inspected before measurement. "
           "No game-specific replay-inspection binding was found; repository-native tooling supplied the observations and replay checks.",
           "- No behavioral edits, evidence attachment, hosted games, uploads or league changes were performed.", ""]
    (output/'episode.ir.md').write_text('\n\n'.join(x for x in md if x != '') + '\n')
    sentinel = next(s for s in spans if s['start_tick'] <= 8150 <= s['end_tick'])
    refresh_count = sum(len(s['weak_refresh_ticks']) for s in spans)
    summary = f"""# Coach and autoresearcher handoff

[Full episode IR](episode.ir.md) · [Structured evidence](episode.ir.json) · [Machine-readable proposals](research-handoff.json)

![Decision timeline with policy memory and separately labeled retrospective structure state](decision-timeline.png)

The linked game is a verified **09:24.88 loss** by `aaron-gota-ir-relh154-legacy-0916:v1` against `gota-g002:v1`.
The report follows the primary DeathKnight (slot 0), using **{len(spans)} decision points**. All five owned instances were checked against the replay.

The most useful observation is in `{sentinel['id']}` (ticks {sentinel['start_tick']}–{sentinel['end_tick']}). At tick 8150 (05:39.58), the DeathKnight is at (103,9),
sees a living enemy at (94,19), and renews its defense deadline to 15350. That enemy is √181 ≈ 13.45 tiles away, outside the ten-tile defensive intercept radius.
`bestId=0`, so `fallback` issues `walkTo(103,9)`. This explains the no-target rallying in policy terms; it does not establish that leaving would win.
Across this primary perspective, {refresh_count:,} ticks extend an existing defense deadline while the current observed group count is below four.
Once defense activates at tick 838, the subject never records an inactive defense state on a later living decision, including after six respawns.

A second activation gap: **all 2,900 target-attack decisions exceed the 40-object defense motion limit**. R2 takes its attack-only budget branch,
and `motionActive` stays zero. The cadence controller does not activate for this hero in this episode. This is a concrete execution condition to investigate,
not proof that enabling cadence in those states would improve the result.

The representation itself needs attention before another parameter search:

1. **Lift the hidden choices in `observe`.** Expose rush recognition, sentry assignment, commitment renewal, target eligibility and release as named concepts with explicit guards. The existing glossary contains only three predicates. [Fourteen proposed glossary entries](proposed-glossary.json) supply grounding and supporting decisions.
2. **Keep multiple channels explicit.** R1 changes target/defense state; R2 and R4 determine locomotion; E0 consumes inventory; E1 and E2 spend resources in order. Purchases accumulate rather than selecting a single winner. Preserve this structure when lifting or embedding.
3. **Give the coach an evidence contract.** A comment should identify a decision ID, the observed objects, the responsible IR block, the proposed intervention and its status. “Release one sentry earlier” is a hypothesis; “the hero was physically stuck” is not established by this trace.
4. **Give the autoresearcher a staged gate.** First require an output-equivalent lift. Then define forceable alternative skills and branch checkpoints containing world, RNG and every live policy's memory. Acquire a valid live g002 policy or equivalent reconstruction before counterfactual verdicts. Evaluate candidates against reacting peers; report intervals and retain failed cases.
5. **Capture semantic traces during play.** Retain version hashes, effective seed, visibility-filtered decision snapshots, memory transitions, rule guards/firings and command ownership. Keep absent confidence null; authored research beliefs are not the policy's per-tick estimates.

Reconstructed fidelity: **{len(spans)} consistent, 0 inconsistent, 0 unresolvable**; all {doc['fidelity']['tick_checks']['rule_evaluations']:,} rule evaluations checked.
Original internal fidelity remains unresolvable. All 67,929 owned commands and 13,557 state hashes match, and trace instrumentation preserves observed state and globals.
The five negative material-swing candidates have **no rollouts and no quality verdicts**. Their skill alternatives are not separately exposed by this IR.

These are reviewable evidence proposals. The deployed policy and its evidence were not changed. Another research session has already investigated this replay;
this handoff adds a structured episode account and does not claim those prior trials as new evidence or rerun their rejected experiments.
"""
    (output/'coach-and-autoresearcher.md').write_text(summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--episode-artifacts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.evidence.resolve(), args.episode_artifacts.resolve(), args.output.resolve())
