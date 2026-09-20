"""Record accepted buying in the current repo and preserve it in the policy IR."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from policy_ir import HERE, compile_policy, digest, extract, read, write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    args=parser.parse_args();d=args.directory
    game=json.loads((d/"game.stdout.log").read_text().splitlines()[-1])
    audit=read(d/"purchases.json")
    if (audit["hash_mismatches"] or audit["ticks"]!=game["ticks"]
            or audit["actions_consumed"]!=game["actions"] or audit["state_hash"]!=game["state_hash"]
            or len(audit["heroes"])!=10 or len(game["heroes"])!=10):
        raise ValueError("Purchase replay did not reproduce the complete game")
    heroes=[]
    for h in audit["heroes"]:
        events=h["purchase_events"]
        gear=[e for e in events if e["item"]>4]
        if not events or not gear or any(e["gold_before"]<=e["gold_after"] for e in events):
            raise ValueError("Every tested hero must buy and pay for equipment")
        spent=sum(e["gold_before"]-e["gold_after"] for e in events)
        if spent!=sum(h["gold_spent"]):
            raise ValueError("Purchase events and spending totals disagree")
        heroes.append({"slot":h["slot"],"class":h["class"],"first_purchase_tick":events[0]["tick"],
                       "equipment_bought":[e["item"] for e in gear],
                       "consumables_bought":sum(e["item"]<=4 for e in events),
                       "gold_spent":spent,"final_inventory":h["inventory"]})
    if len({h["class"] for h in heroes})!=10:
        raise ValueError("The proof must cover all ten classes")
    policy_path=HERE/"hypotheses/wave_local_balance.evaluated.ir.json"
    parent=read(policy_path);policy=deepcopy(parent)
    basic=compile_policy(parent).encode()
    frozen=HERE.parents[3]/"tmp/gota-ir/wave-local-20260915/candidate/policy.bas"
    if basic!=frozen.read_bytes():raise ValueError("Policy differs from the tested source")
    report={"scope":"Buying functionality on the current pulled repository; not competitive evidence",
            "source":read(d/"source-proof.json"),"candidate_sha256":digest(basic),
            "seed":game["seed"],"ticks":game["ticks"],"all_classes_bought_equipment":True,
            "hash_mismatches":0,"heroes":heroes,
            "artifact_hashes":{name:digest((d/name).read_bytes()) for name in
                               ["game.replay","purchases.json","game.stdout.log","episode","audit-purchases"]}}
    evidence_path=HERE/"item-buying-20260915.json";write(evidence_path,report)
    reference={"artifact":str(evidence_path.relative_to(HERE.parents[3])),"sha256":digest(evidence_path.read_bytes())}
    policy["belief"]["claims"]["B_item_execution"]={
        "claim":f"The generated policy bought equipment for all ten hero classes in a complete {game['ticks']}-tick game on repo1d7eb72. Accepted purchase events deducted gold, and replay verification matched every state. E0/E1/E2 match v2 and survive the full IR/BASIC round trip. This proves buying executes; it does not prove the item choices maximize wins.",
        "status":"supported","evidence":[reference]}
    policy["update"]["revision"]+=1
    policy["update"]["parent"]=digest(parent)
    policy["update"]["change"]={"origin":"functionality_feedback","verified":"accepted_item_purchases"}
    policy["update"]["evidence"].append(reference)
    if compile_policy(policy).encode()!=basic or extract(basic.decode(),policy)!=policy:
        raise ValueError("Buying evidence changed executable behavior or broke the IR round trip")
    write(policy_path,policy)
    (HERE/"hypotheses/wave_local_balance.evaluated.bas").write_bytes(basic)
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
