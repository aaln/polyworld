"""Close relh154 study and reflect completed measured results into the frozen IR."""
from copy import deepcopy
import json
import re
from relh154_research import STUDY,RECORD,RUN
from policy_ir import bundle,compile_policy,digest,extract,read,write


def finalize():
    local=read(STUDY/'local/qualification.json');remote=read(STUDY/'hosted-result.json')
    confirm=read(STUDY/'confirmation/result.json');guards=read(STUDY/'guards/result.json')
    assert confirm['passed'] and confirm['name']=='pair150'
    assert remote['outcome_qualified']==['pair150'] and 'pair150' in local['qualified']
    arms=[*remote['arms'].values(),*confirm['arms'].values(),*guards['arms'].values()]
    assert all(r['games']==40 and r['all_full_audits_passed'] for r in arms)
    mechanism=read(STUDY/'hosted/pair150/review/mechanism.json')
    assert mechanism['native_owned_reconstruction']['all_state_hashes_equal']
    assert mechanism['native_owned_reconstruction']['all_actions_consumed']
    for slot in ('5','6','7','8'):
        r=mechanism['first_recalls'][slot];assert r['tick']==922 and r['memory']['pairedRush']==1
    note=('Confirmed exact relh-gods-of-the-arena:v154 improvement on2026.9.16.5: '
      'discovery40/40BLUE, then fresh40/40RED and40/40BLUE,120/120candidategames; '
      'deployed controls40/40RED0/40BLUE. Native reviewed blue win matches30380ownedcommands '
      'and every statehash; fourheroes recall at922 vs3222,95.83s earlier. '
      'Blue observed side-tower damage alarm,100tile warning, arrival-aware quiet clock and '
      '1440tick carryhold tested as a coordinated package. First alarm:3livingvisible '
      'enemyheroes andtower25hp790/950. No opponent-name or hidden-state use. '
      'Wider coverage alone0/40BLUE;50HPvariant rejected locally9/12vs11/12. '
      'Selectedlocal11/12 matchesdeployed, all6RED fullgameparities; nativebudget/IR pass. '
      'Preservation40BLUE each:g002v1,black-kitev16,macromackie4 all40/40; Jordan25435wins5draws0losses, versus40wins. Promotion guard FAILED. '
      'RED executable unchanged. All280 selected-candidate hostedgames fullyaudited. '
      'Historicalcontrols reused,differentgeneratedseeds and correlatedfixedlineups; '
      'no independenttrial significance, futureguarantee or mixed10player qualification. '
      'Existing redstalerally failure andblack-kite redweakness remain outside this repair.')
    paths=['prospective.json','vm-proof.json','vm-budget.json','local/qualification.json','hosted-result.json',
           'confirmation/result.json','guards/result.json','hosted/pair150/review/mechanism.json']
    evidence=[{'artifact':str(STUDY/p),'sha256':digest((STUDY/p).read_bytes())} for p in paths]
    source=(STUDY/'local/candidates/pair150/policy.bas').read_text()
    result={'confirmed':'pair150','relh154':{'prior_red':40,'prior_blue':0,'discovery_blue':40,'fresh_red':40,'fresh_blue':40,'candidate_games':120},
            'rejected':{'wide100':'0/40hostedblue','pair50':'9/12localvs11/12;notuploaded'},
            'source_sha256':digest(source.encode()),'scope':note,'evidence':evidence,'promotion_ready':guards['passed'],
            'all_selected_candidate_hosted_games':280,'prior_controls_reused':True,'general_stale_rally_fixed':False}
    write(STUDY/'final-result.json',result)
    parent=read(STUDY/'qualified-feedback/pair150/policy.ir.json');p=deepcopy(parent)
    p['belief']['claims']['B_candidate']={'status':'supported','claim':note,'evidence':evidence}
    p['belief']['claims']['B_relh_warning']={'status':'supported','claim':'The coordinated blue damaged-side-tower alarm and recall package changed exactrelh154 from0/40BLUE to40/40discovery+40/40freshBLUE whilefreshREDremained40/40. Native firstrecall922vs3222; not a claim about each individual edit or unseen opponents.','evidence':evidence}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Validated relh154 recall package and requested preservation comparisons; tested symbolic behavior retained.',
        needs_review=[x for x in parent['update']['needs_review'] if x not in ('belief/B_candidate','belief/B_relh_warning','goal/G_defense')],evidence=parent['update']['evidence']+evidence)
    assert compile_policy(p)==source and extract(source,p)==p
    out=STUDY/'final-feedback'
    if out.exists():assert read(out/'policy.ir.json')==p
    else:bundle(p,out)
    for name,claim in result['rejected'].items():
        r=read(STUDY/'local/candidates'/name/'policy.ir.json');q=deepcopy(r)
        q['belief']['claims']['B_relh_warning']={'status':'contradicted','claim':'Failed the preregistered qualification for this variant: '+claim+'. This does not refute the entire coordinated mechanism.','evidence':evidence[:1]+[evidence[3],evidence[4]]}
        q['update'].update(revision=r['update']['revision']+1,parent=digest(r),change='Preserved failed variant with measured qualification result.')
        assert compile_policy(q)==(STUDY/'local/candidates'/name/'policy.bas').read_text() and extract(compile_policy(q),q)==q
        dest=STUDY/'rejected-feedback'/name
        if not dest.exists():bundle(q,dest)
    report='# Relh154 repair — completed evaluation\n\n'+note+'\n\n'
    report+='| Policy | Relh red | Relh blue |\n|---|---:|---:|\n| Deployed warning100 |40/40|0/40|\n| New pair150, fresh confirmation |40/40|40/40|\n\n'
    report+='Additional discovery:40/40blue. Required preservation:40/40blue againstg002v1,black-kitev16,macromackie4; Jordan25435wins5draws. Promotion guard FAILED; candidate remains inert. Six localred full games preserve every action andstatehash.\n\n'
    report+='## Why the old policy lost\n\nThe outer side tower was outside the80tile warning radius. Widening the radius was insufficient: the alarm still required four living visible heroes; at the useful warning moment onlythree were alive/visible near the tower. Relh destroyed allthree lane towers before the old squad recall at3222. Most defenders were still travelling when the base fell3754. The new package responds at922 with the tower790/950HP, then keeps recall meaningful duringtravel. Sentries are observed within30tiles of home by2640 (120tick sample resolution; arrival may include respawn), before the old loss.\n\n'
    report+='IR/source: `final-feedback/`. Native replay review: `hosted/pair150/review/`. Full frozen inputs and evidence hashes: `final-result.json`. This is a two-policy, fiveheroes/team result, not mixed10player evidence.\n'
    (STUDY/'REPORT.md').write_text(report)
    ids=[read(p)['id'] for root in (STUDY/'batches',STUDY/'confirmation',STUDY/'guards/batches') for p in root.glob('*/*/*/batch/created.json')]
    text=RECORD.read_text().replace('status: running','status: confirmed')
    text=re.sub(r'^evals:.*$','evals: '+json.dumps(ids),text,flags=re.M)
    text=text.split('## Result\n',1)[0]+'## Result\n\n'+note+'\n\n## Verdict\n\nConfirmed for the coordinatedpair150 package against exactrelh154. Both rejected variants retained. Required Jordan preservation failed:35wins5draws versus40wins. No promotion; retain both livewarning100 champions.\n\nEvidence: '+str(STUDY/'final-result.json')+'\n'
    RECORD.write_text(text)
    print('CONFIRMED relh154120/120;155/160preservation with5Jordandraws; PROMOTIONBLOCKED. ExactIR/BASIC.',flush=True)
    return note

if __name__=='__main__':finalize()
