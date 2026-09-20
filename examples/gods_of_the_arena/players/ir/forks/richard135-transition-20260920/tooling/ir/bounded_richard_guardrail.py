"""Additional round-379 threat requirement for a selected bounded candidate."""
import time
from bounded_core import STUDY
from economy_feedback import record
from policy_ir import read,write,digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure_hosted import prepare_head,result as head_result
from threat_coverage_hosted import control
from win_hosted import live

ROOT=STUDY/'additional-richard'


def main():
    ROOT.mkdir(exist_ok=True)
    plan=read(STUDY/'additional-threats-needed.json')
    freeze(ROOT/'plan.json',plan)
    while alive(read(STUDY/'hosted-process.json')['pid']):time.sleep(15)
    report=read(STUDY/'hosted-comparison.json');name=report['selected']
    if not name:
        write(ROOT/'not-run.json',{'reason':'No bounded candidate passed its original complete gates'});return
    src=STUDY/'hosted'/name;ref=control(plan['rival']);before=read(ref/'plan.json');game=live()
    if game['version']!=before['game_version'] or game['manifest']['game']['runnable']['source_url']!=before['game_source']:
        raise ValueError('Release changed before additional threat check')
    prepare_head(ROOT/'candidate',read(src/'uploaded-version.json'),ref,'Additional actual Richard78 league threat',plan['requirement'])
    with drained_wide(ROOT):
        b=head_result(ref);a=head_result(ROOT/'candidate')
        checks={'red_floor':a['colors']['red']['win']>=24}
        for color in ('red','blue'):checks[color]=a['colors'][color]['win']>=b['colors'][color]['win']-2
        r={'candidate':a,'control':b,'checks':checks,'passed':all(checks.values()),
           'candidate_name':name,'plan_sha256':digest((ROOT/'plan.json').read_bytes())}
        write(ROOT/'result.json',r)
        parent=src/'final-feedback'
        if not (ROOT/'feedback').exists():
            record(parent/'policy.ir.json',parent/'policy.bas',f'Additional Richard78 redleague threat: candidate{a["colors"]}, '
                f'deployed{b["colors"]};checks{checks}. Original requirements retained.',ROOT/'result.json',ROOT/'feedback')
        print('Additional Richard check',checks,flush=True)


if __name__=='__main__':main()
