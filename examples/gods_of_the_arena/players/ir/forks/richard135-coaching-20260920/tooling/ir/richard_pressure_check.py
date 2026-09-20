"""Fill the untested Richard78 matchup for an existing local-qualified candidate.

This diagnostic does not overwrite its failed earlier absolute red-kite gate
and cannot promote a champion. Complete both colors before a matchup verdict.
"""
from economy_feedback import record
from policy_ir import read,write,digest,compile_policy,extract
from release_workspace import RUN
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head,result as head_result
from threat_coverage_hosted import control
from win_hosted import live

STUDY=RUN/'coached-lanes/r5-richard-pressure-check'
PRIOR=RUN/'coached-lanes/r5-red-pressure'


def main():
    STUDY.mkdir(exist_ok=True)
    p=read(PRIOR/'promotion-guardrail/feedback/policy.ir.json')
    source=(PRIOR/'local/candidates/pressure20/policy.bas').read_bytes()
    assert compile_policy(p).encode()==source and extract(source.decode(),p)==p
    version=read(PRIOR/'hosted/pressure20/uploaded-version.json')
    assert read(PRIOR/'hosted/pressure20/upload-request.json')['content_hash']==digest(source)
    assert 'pressure20' in read(PRIOR/'local/comparison.json')['qualified']
    old=read(PRIOR/'promotion-guardrail/result.json')
    assert not old['passed'] and not old['checks']['red_kite_absolute']
    design=('Existing pressure20 source, locally qualified and Jordan80/80, but earlier '
            'promotion rejected for red-kite21/40 below24. New targeted Richard78 diagnostic '
            'only; preserve that failed result. Forty episodes on EACH color, exact version '
            'and gameplay config, complete full replay/VM/equipment/command-diversity audits. '
            'Reuse deployed blue_repair control red11W24L5D and blue40W. No promotion. '
            'Correlated fixed-lineup trajectories are not independent statistical trials.')
    freeze(STUDY/'prospective-plan.json',{'candidate':version['id'],'candidate_basic_sha256':digest(source),
        'candidate_ir_sha256':digest(p),'new_episodes':80,'episodes_per_color':40,
        'prior_failed_gate':str(PRIOR/'promotion-guardrail/result.json'),
        'matchup_checks':{'red_wins_minimum':28,'red_gain_minimum':10,'blue_wins_minimum':38},
        'promotion_eligible_from_this_study':False,'design':design})
    live()
    reference=control('richard-gods-of-the-arena:v78')
    prepare_head(STUDY/'richard',version,reference,'Richard78 missing pressure20 matchup',design)
    a=head_result(STUDY/'richard');b=head_result(reference)
    checks={'red_absolute':a['colors']['red']['win']>=28,
            'red_gain':a['colors']['red']['win']>=b['colors']['red']['win']+10,
            'blue':a['colors']['blue']['win']>=38}
    result={'candidate':a,'control':b,'checks':checks,'matchup_passed':all(checks.values()),
            'promotion_eligible':False,'prior_failed_gate_retained':True,
            'new_candidate_games':80,'reused_control_games':80,'design':design}
    write(STUDY/'result.json',result)
    if not (STUDY/'feedback').exists():
        record(PRIOR/'promotion-guardrail/feedback/policy.ir.json',PRIOR/'local/candidates/pressure20/policy.bas',
               f'Richard78 pressure20 diagnostic: candidate {a["colors"]}, deployed {b["colors"]}. '
               f'Matchup checks {checks}. Prior red-kite absolute promotion gate remains failed. '
               'No promotion eligibility from this targeted test.',STUDY/'result.json',STUDY/'feedback')
    print('Richard pressure diagnostic',a['colors'],checks,flush=True)


if __name__=='__main__':main()
