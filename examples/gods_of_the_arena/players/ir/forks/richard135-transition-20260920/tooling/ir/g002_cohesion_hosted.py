"""One deadline contingency after the first targeted replacement is rejected."""
from pathlib import Path
import time
from economy_feedback import record
from g002_cohesion import STUDY
from g002_deadline import ROOT as DEADLINE
from g002_coordination_hosted import wait_for
from policy_ir import read,write,digest
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head,result
from rush_hosted import upload
from threat_coverage_hosted import control
from win_hosted import live

DESIGN=('20minute userdeadline: restore deployed60second carryrecall with48tile continuation '
        'while retaining anchorcaster support, separated rally and arrival-qualified20second '
        'quiet release. Local12casecandidate screen versusdeployed plus6bluefullparity, '
        'nativequiet-release proof and denseVM. Hosted40red40blue versusexactg002v1. '
        'Atleast32red38blue required. Broadopponent and10-playerfield unverified. '
        'Separate contingency; prior failed fullstudies remain failed.')


def main():
    freeze(STUDY/'deadline-prospective.json',{'design':DESIGN,'candidate':'cohesion20','games':80,'red_floor':32,'blue_floor':38,
        'when':'Onlyif first deadline study has no eligible replacement; complete40/color.',
        'selection':'Targeted only; broader original suite not claimed.'})
    wait_for(DEADLINE/'result.json',DEADLINE/'process.json')
    if read(DEADLINE/'result.json')['selected']:
        write(STUDY/'deadline-result.json',{'selected':None,'results':{},'reason':'Earlier targetedsuite alreadyqualified; reserve remainingtime for deployment.'});return
    wait_for(STUDY/'local/comparison.json',STUDY/'local-process.json')
    if 'cohesion20' not in read(STUDY/'local/comparison.json')['qualified']:
        write(STUDY/'deadline-result.json',{'selected':None,'results':{},'reason':'No local qualifier'});return
    wait_for(STUDY/'activation-proof.json',STUDY/'local-process.json')
    proof=read(STUDY/'activation-proof.json')
    if not proof['passed'] or not read(STUDY/'vm-stress.json')['passed']:raise ValueError('No nativeproof')
    source=STUDY/'local/candidates/cohesion20/policy.bas'
    if not any(r['source_sha256']==digest(source.read_bytes()) and sum(r['proof']['release_counts']) and r['proof']['all_actions_consumed'] and r['proof']['all_state_hashes_equal'] for r in proof['rows']):raise ValueError('Source notverified')
    # Waitforfeedbackwrittenaftertheactivationreceipt.
    wait_for(STUDY/'activation-feedback/cohesion20/manifest.json',STUDY/'local-process.json')
    live()
    root,version=upload('cohesion20',STUDY,'aaron-gota-ir-post-defense',
        'Restore deployed60second attackerrecall and48tile continuation; anchorcaster support, separate rally destinations and arrival-qualified quietrelease20seconds with tank60seconds.',
        feedback_override=STUDY/'activation-feedback/cohesion20',validation_note='Deadline local12candidate cases pluscontrols,6blueexactgameplay, nativeactivation anddenseVM passed. Actualg002 andwidefield unvalidated; inert experiment.')
    head=root/'deadline-g002';prepare_head(head,version,control('gota-g002:v1'),'Deadline cohesive counterpush versusg002',DESIGN)
    a=result(head);passed=a['colors']['red']['win']>=32 and a['colors']['blue']['win']>=38
    r={'study':str(STUDY),'name':'cohesion20','version':version,'result':a,'eligible':passed,'source_sha256':digest(source.read_bytes()),'head':str(head),'scope':DESIGN}
    src=STUDY/'activation-feedback/cohesion20'
    if not (root/'deadline-feedback').exists():record(src/'policy.ir.json',src/'policy.bas',f'Completeg00280: {a["colors"]}; targetedeligibility{passed}; broaderfield nottested.',head/'result.json',root/'deadline-feedback')
    write(STUDY/'deadline-result.json',{'selected':'cohesion20' if passed else None,'results':{'cohesion20':r},'promotion_performed':False})
    print('cohesion20',a['colors'],'eligible',passed,flush=True)

if __name__=='__main__':main()
