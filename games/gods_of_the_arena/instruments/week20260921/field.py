"""Conditional fixed mixed-team holdout: same byte-exact candidate, one seat."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import hosted as h

def prepare(c):
    path=h.STUDY/'field-plan.json'
    if path.exists():return h.read(path)
    members=h.get(c,'/v2/league-policy-memberships?league_id=league_3c60897b-25cf-4b37-9d1a-8554c1198f28&champions_only=true&limit=100')
    names=['richard','Jordan','relh','Andre von Auto','daveey','daveey-2','Scott Smith','BeWellBot','Andrew Brower']
    by_name={x['player']['name']:x for x in members}
    chosen=[by_name[n] for n in names]
    assert len({x['player']['id'] for x in chosen})==9
    h.write(h.STUDY/'field-memberships.json',chosen)
    candidate=h.read(h.STUDY/'uploads/lane/uploaded-version.json')['id']
    cfg={k:v for k,v in h.read(h.STUDY/'canonical-game.json')['manifest']['variants'][0]['game_config'].items() if k not in ('seed','players','tokens')}
    arms=[]
    for label,version in [('candidate',candidate),('incumbent',h.INCUMBENT)]:
        for side in (0,1):
            # Third pick on each team: test after other policies have chosen heroes.
            subject=side*5+2
            pool=iter(x['policy_version']['id'] for x in chosen)
            roster=[version if i==subject else next(pool) for i in range(10)]
            arm={'name':label,'side':side,'version':version,'own_slots':[subject],
              'roster':roster,'games':40,'kind':'mixed','names':names}
            folder=h.STUDY/'field'/label/str(side)
            body={'idempotency_key':'gota-week0921-field-'+label+'-'+str(side)+'-'+candidate[:8],
              'target':{'coworld_id':h.GAME,'variant_id':'competition'},'game_config_overrides':cfg,
              'num_episodes':40,'roster':[{'slot':i,'player':{'policy_ref':v}} for i,v in enumerate(roster)],
              'notes':'Prospective mixed-team score holdout, one subject seat, nine distinct frozen current players; candidate/control same roster per color. Score formula pinned; no league mutation.'}
            h.freeze(folder/'arm.json',arm);h.freeze(folder/'request.json',body);arms.append(arm)
    plan={'conditional_on':'hosted-result.json complete and passed', 'candidate':candidate,'games':160,
      'source_sha256':h.read(h.STUDY/'hosted-plan.json')['source_sha256'],'arms':arms,
      'decision_rule':'No subject failures; all replay/score audits pass; clean-opponent mean subject score >= incumbent on each color and >=1.20x overall; at least 30 clean games per cell. Tainted games separately reported, no silently dropped failures. Two fixed rosters do not establish universal field superiority.'}
    h.freeze(path,plan);return plan

def main():
    with h.research.lock(h.STUDY/'hosted.lock',blocking=False),h.client() as c:
        plan=prepare(c)
        if not (h.STUDY/'hosted-result.json').exists():
            print('Frozen mixed-team plan; awaiting uniform comparison.');return
        assert h.read(h.STUDY/'hosted-result.json')['passed'],'Uniform score gate failed; no conditional field spend.'
        # The previous writer is paused. Queue up to the existing global
        # three-request limit; reservation still checks all campaign requests.
        # Reusing created.json preserves idempotency when this script resumes.
        assert h.read(h.CAMPAIGN/'service.json')['state']=='paused'
        for arm in plan['arms'][:3]:
            folder=h.STUDY/'field'/arm['name']/str(arm['side'])
            if (folder/'batch/created.json').exists():continue
            ident=h.reserve_create(c,h.read(folder/'request.json'),folder/'batch')
            print(json.dumps({'queued_field':arm['name'],'side':arm['side'],'request':ident}),flush=True)
        for arm in plan['arms']:
            folder=h.STUDY/'field'/arm['name']/str(arm['side'])
            if (folder/'result.json').exists():continue
            receipt=folder/'batch/created.json'
            ident=h.read(receipt)['id'] if receipt.exists() else h.reserve_create(c,h.read(folder/'request.json'),folder/'batch')
            print(json.dumps({'field':arm['name'],'side':arm['side'],'request':ident}),flush=True)
            while True:
                eps=h.episodes(c,ident);h.write(folder/'episodes.json',eps)
                done=[e for e in eps if e['status'] in ('completed','failed','cancelled','error')]
                with ThreadPoolExecutor(4) as pool:
                    rows=list(pool.map(lambda e:h.collect(c,arm,folder,e),done))
                h.write(folder/'progress.json',{'audited':len(rows),'total':len(eps),'rows':rows})
                if len(rows)==40:break
                print(json.dumps({'field':arm['name'],'side':arm['side'],'audited':len(rows)}),flush=True)
                time.sleep(10)
            clean=[r for r in rows if r['valid']]
            result={'arm':arm,'games':40,'mean_score_all':sum(r.get('score',0) for r in rows)/40,
              'clean_games':len(clean),'mean_score_clean':sum(r['score'] for r in clean)/max(1,len(clean)),
              'subject_invalid':sum(not r.get('subject_valid',False) for r in rows),
              'tainted':sum(not r['valid'] for r in rows),'rows':rows}
            h.write(folder/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('arm','rows')}),flush=True)
        results=[h.read(h.STUDY/'field'/a['name']/str(a['side'])/'result.json') for a in plan['arms']]
        candidate,control=results[:2],results[2:]
        passed=all(r['subject_invalid']==0 and r['clean_games']>=30 for r in results) and all(candidate[i]['mean_score_clean']>=control[i]['mean_score_clean'] for i in (0,1)) and sum(r['mean_score_clean'] for r in candidate)>=1.2*sum(r['mean_score_clean'] for r in control)
        h.write(h.STUDY/'field-result.json',{'complete':True,'passed':passed,'results':results,'scope':'Two fixed rosters, middle draft seats, empirical score holdout; not universal league qualification.'})

if __name__=='__main__':main()
