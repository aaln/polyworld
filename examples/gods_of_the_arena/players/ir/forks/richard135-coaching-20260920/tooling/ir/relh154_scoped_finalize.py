"""Measured scoped-followup evidence -> semantic IR -> identical evaluated BASIC."""
from copy import deepcopy
import json,re
from relh154_scoped import STUDY,OLD,RECORD
from policy_ir import read,write,digest,bundle,compile_policy,extract


def finalize():
    d=read(STUDY/'hosted-result.json');c=read(STUDY/'confirmation/result.json');name=d['selected']
    assert c['passed'] and c['name']==name and name in d['qualified']
    selected=[v for k,v in d['arms'].items() if k.split('/')[1]==name]+list(c['arms'].values())
    assert len(selected)==7 and all(r['games']==40 and r['wins']==40 and r['all_full_audits_passed'] for r in selected)
    q=read(STUDY/'local/qualification.json');assert name in q['qualified']
    reviewed=read(STUDY/'hosted'/name/'review/decisions.json')['cases']
    assert reviewed and all(r['win'] and r['proof']['all_state_hashes_equal'] and r['proof']['all_actions_consumed'] for r in reviewed)
    first=reviewed[0]['first_recalls'];assert all(first[s]['tick']<3222 for s in ('5','6','7','8'))
    behavior=('a blue side-tower alarm after 150 HP of damage, with the original commitment and release rules' if name=='legacy' else 'a blue side-tower alarm after 150 HP of damage, with arrival protection and extended commitment limited to that alarm')
    note=(f'Validated relh-gods-of-the-arena:v154 repair ({name}): 40/40 blue in discovery, '
      'then 40/40 red and 40/40 blue in fresh confirmation: 120/120 against relh. '
      'The deployed control won 40/40 red and 0/40 blue. Required blue-side preservation '
      'checks won 40/40 each against g002 v1, black-kite v16, macromackie v4, and Jordan v254. '
      'All 280 selected-candidate hosted games won and passed full replay, runtime, roster, '
      'release, and equipment audits. '
      f'Behavior: {behavior}. Red execution is unchanged, verified through the lowered '
      'source and six complete games with identical actions and state hashes. Local results '
      'were 12/12, matching the deployed policy. Real-VM middle-lane commands and release '
      'timing also match the deployed policy. The semantic IR reflects these results and '
      'compiles to the exact tested BASIC, with reverse extraction verified. '
      'The first, broader candidate also beat relh 120/120 but produced five Jordan draws '
      'and was not promoted. This followup passed the original preservation requirements. '
      'Controls were reused, seeds differ, and repeated fixed-lineup games are correlated. '
      'These results do not establish independent-trial significance, guaranteed future '
      'wins, or mixed ten-player performance. The separate stale red rally issue and '
      'red-side weakness against black-kite remain outside this change.')
    paths=['prospective.json','vm-proof.json','vm-budget.json','local/qualification.json','hosted-result.json',
           'confirmation/result.json','hosted/'+name+'/review/decisions.json']
    evidence=[{'artifact':str(STUDY/p),'sha256':digest((STUDY/p).read_bytes())} for p in paths]
    source=(STUDY/'local/candidates'/name/'policy.bas').read_text()
    result={'confirmed':name,'promotion_ready':True,'scope':note,'evidence':evidence,'source_sha256':digest(source.encode()),
      'relh154':{'prior_red':40,'prior_blue':0,'discovery_blue':40,'fresh_red':40,'fresh_blue':40,'candidate_games':120},
      'preservation':{k:40 for k in ('g002v1','black-kitev16','macromackie4','Jordan254')},
      'candidate_games':280,'candidate_wins':280,'first_recalls':first,'prior_broad_candidate_rejected':True,'general_stale_rally_fixed':False}
    write(STUDY/'final-result.json',result)
    parent=read(STUDY/'semantic-feedback'/name/'policy.ir.json');p=deepcopy(parent)
    p['belief']['claims']['B_candidate']={'status':'supported','claim':note,'evidence':evidence}
    p['belief']['claims']['B_relh_warning']={'status':'supported','claim':f'{behavior}. Exact relh v154: 120/120, including fresh 40/40 on each side. First recalls in the reconstructed blue win: '+str({k:v['tick'] for k,v in first.items()})+'. All four required blue preservation checks were 40/40. Evidence supports the selected implementation on these tested matchups.','evidence':evidence}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Confirmed scoped-recall followup; freshrelh and requestedpreservation passed; evaluated BASIC unchanged.',
        needs_review=[x for x in parent['update']['needs_review'] if x not in ('belief/B_candidate','belief/B_relh_warning','goal/G_defense')],evidence=parent['update']['evidence']+evidence)
    assert compile_policy(p)==source and extract(source,p)==p
    out=STUDY/'final-feedback'
    if out.exists():assert read(out/'policy.ir.json')==p
    else:bundle(p,out)
    table='| Matchup | Prior red | New red | Prior blue | New blue |\n|---|---:|---:|---:|---:|\n| Relh v154 |40/40|40/40 fresh|0/40|40/40 fresh (+40/40 discovery)|\n'
    table+='| g002 v1 |unchanged|source/gameplay parity|40/40|40/40|\n| black-kite v16 |unchanged|source/gameplay parity|40/40|40/40|\n| macromackie v4 |unchanged|source/gameplay parity|40/40|40/40|\n| Jordan v254 |unchanged|source/gameplay parity|40/40|40/40|\n'
    report='# Relh154 successful followup\n\n'+note+'\n\n'+table+'\n'
    report+='## Mechanism\n\nThe old blue alarm excluded an outer tower 84 tiles from home and required four living visible heroes. Wider coverage alone won 0/40. The new alarm responds to at least two living visible enemy heroes near a standing side tower missing 150 HP, before tick 3,600. This gives defenders time to return before the lane collapses. The initial change also lengthened unrelated defensive commitments and produced five Jordan draws. This followup preserves the original release behavior. Exact native traces and timing are retained in `hosted/'+name+'/review/decisions.json`.\n\n'
    report+='Exact evaluated IR/BASIC pair: `final-feedback/`. Frozen sourceSHA: `'+result['source_sha256']+'`. Failed variants and previous requests remain preserved. These are two-player, five-hero teams; mixed ten-player games were not evaluated.\n'
    (STUDY/'REPORT.md').write_text(report)
    ids=[read(p)['id'] for root in (STUDY/'batches',STUDY/'confirmation') for p in root.glob('*/*/*/batch/created.json')]
    t=RECORD.read_text().replace('status: running','status: confirmed');t=re.sub(r'^evals:.*$','evals: '+json.dumps(ids),t,flags=re.M)
    t=t.split('## Result\n',1)[0]+'## Result\n\n'+note+'\n\n## Verdict\n\nConfirmed selected '+name+' under the original followup gate. Earlier broadcandidate Jordan regression remains recorded.\n\nEvidence: '+str(STUDY/'final-result.json')+'\n';RECORD.write_text(t)
    print('CONFIRMED',name,'280/280; relh120/120; all required preservation.',flush=True)
    return note

if __name__=='__main__':finalize()
