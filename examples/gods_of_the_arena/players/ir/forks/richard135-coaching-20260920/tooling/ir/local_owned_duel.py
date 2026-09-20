"""A stronger local diagnostic opponent, preserving all original study gates."""
from bounded_core import make as core
from mage_reserve import make as reserve
from warlock_cadence import make as spells
from breach_pressure import DEPLOYED
from release_workspace import RUN
from rush_defense_eval import evaluate
from policy_ir import read,write
from economy_feedback import record

STUDY=RUN/'coached-lanes/r5-owned-duel'
VARIANTS=['deployed','core96','cap4','cap5','warlock']


def make(name):
    if name in ('deployed','core96'):return core(name)
    if name in ('cap4','cap5'):return reserve(name)
    return spells(name)


def main():
    evaluate('local',VARIANTS,12,782000,make,STUDY,RUN/'r5/fast/audit-local',
             opponents_override={'promoted_blue_repair':DEPLOYED/'policy.bas'})
    r=read(STUDY/'local/result.json')
    report={'metrics':r['metrics'],'verified_games':r['verified_games'],
        'scope':'84completegames: five compared policies plus two retained legacy diagnostics,12each. '
                'Opponent is exact deployed blue_repair on both colors. Additional diagnostic only; '
                'original local/hosted gates unchanged. New regressions must be investigated before promotion.'}
    write(STUDY/'comparison.json',report)
    for name in VARIANTS:
        src=STUDY/'local/candidates'/name;out=STUDY/'feedback'/name
        if not out.exists():record(src/'policy.ir.json',src/'policy.bas',
            f'Additional local deployed-opponent diagnostic: {r["metrics"][name]}. '
            'This does not replace original hosted or local gates.',STUDY/'comparison.json',out)
    print('Owned opponent diagnostic',report,flush=True)


if __name__=='__main__':main()
