"""Preregistered wave-local targeting study on the announced balance simulation."""
from balance_study import main


def activation(pairs, stage):
    rows=pairs["parent"]["pairs"]
    def share(hero):
        return hero["fallback_decisions"]/max(1,hero["decisions"])
    deltas=[share(row["candidate"])-share(row["control"]) for row in rows]
    active=[row for row,delta in zip(rows,deltas) if delta>0]
    report={"games":len(active),"classes":sorted({r["class"] for r in active}),
            "mean_rejoin_share_delta":sum(deltas)/len(deltas)}
    passed=(report["games"] >= (20 if stage=="screen" else 60)
            and len(report["classes"])>=3 and report["mean_rejoin_share_delta"]>=.10)
    return report,passed


if __name__=="__main__":
    main({"hypothesis":"wave_local_balance","screen_seed":715300,"validation_seed":718000,
          "activation":activation,"instruments":["wave_study.py"],
          "mechanism_rule":"Mean per-case rejoin-wave decision share increases by >=.10 vs v2; positive in at least half the cases spanning >=3 classes. This measures movement opportunity, not path success, damage or safe positioning."})
