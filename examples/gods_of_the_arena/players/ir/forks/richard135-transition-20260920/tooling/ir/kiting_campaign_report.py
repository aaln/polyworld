"""Publish the complete negative campaign; preserve the exact league v2 executable."""
import json
from copy import deepcopy
from html import escape
from policy_ir import HERE,ROOT,read,write,digest,compile_policy,extract,bundle,refresh_grounding

specs=[
 ('Timed firing + emergency escape','kiting-20260915','burst_kite'),
 ('Confirmed hit + emergency escape','hit-kite-20260915','confirmed_hit_kite'),
 ('Confirmed hit, no emergency escape','kiting-ablations-20260915/no_escape','hit_no_escape'),
 ('Target-aware, with emergency escape','kiting-ablations-20260915/targeted','hit_targeted'),
 ('Earlier retreat','kiting-range-20260915/early_all','early_all'),
 ('Target-aware, no emergency escape','kiting-range-20260915/targeted_only','targeted_only'),
 ('Earlier target-aware retreat','kiting-range-20260915/early_targeted','early_targeted'),
 ('Short retreat + offensive spells','kiting-spells-20260915/spell_short','spell_short'),
 ('Long retreat','kiting-spells-20260915/long_bare','long_bare'),
 ('Long retreat + offensive spells','kiting-spells-20260915/spell_long','spell_long')]
rows=[]
for label,folder,policy in specs:
 d=ROOT/'tmp/gota-ir'/folder;report=read(d/'screen-result.json');plan=read(d/'plan.json')
 assert report['audited_games']==120 and report['invalid_games_scored']==0
 values={}
 for arm in ['candidate','parent','baseline']:
  games=[read(p) for p in (d/'screen'/arm).glob('*/result.json')];assert len(games)==40
  hs=[g['heroes'][g['candidate_slots'][0]] for g in games];ticks=sum(g['ticks'] for g in games)
  values[arm]={'wins':sum(h['score'] for h in hs),'deaths':sum(h['deaths'] for h in hs),
   'deaths_per_minute':sum(h['deaths'] for h in hs)/(ticks/1440),'hits':sum(h['basic_hit_events'] for h in hs),
   'xp':sum(h['total_xp'] for h in hs),'mean_glory':sum(h['score']*(h['total_xp']-100*g['ticks']/1440) for g,h in zip(games,hs))/40}
 rows.append({'name':label,'policy':policy,'game_version':plan['game_version'],'n':40,
  'values':values,'activation':report['activation'],'passed':report['passed'],
  'source_sha256':plan['sources']['candidate'],'run':str(d.relative_to(ROOT)),
  'ir':f'hypotheses/{policy}.evaluated.ir.json','basic':f'hypotheses/{policy}.evaluated.bas'})
if any(r['passed'] for r in rows):raise ValueError('A passing candidate needs a confirmation decision; do not finalize retention automatically')
report={'date':'2026-09-15','decision':'retain_exact_league_v2','league_policy_version':'6d0ff780-652f-47a8-82b3-336cb7a10a56',
 'league_basic_sha256':'c23c618705b74ec3154ba7614cdda6fd7bdc84e71ea55c3b0ef171438f0a91c3',
 'candidates':rows,'tests_passed':67,'promotion_eligible':False,
 'limits':'Each candidate has40 completed matched cases; current-release variants reuse the same40 cases adaptively. These are correlated discovery results, not400 independent samples or independent confirmation. The earlier timed candidate used a different release and40other seeds. All complete tapes verify. Spell-matrix qualification used XP instead of the previous raw-basic-hit floor; no previous result was reclassified. No new candidate was uploaded or promoted.'}
path=HERE/'kiting-campaign-20260915.json';write(path,report)
# Close the IR feedback loop for the retained policy, without changing its actions.
p=read(HERE/'waveguard_xp.evaluated.ir.json');old=compile_policy(p);q=deepcopy(p)
assert digest(old.encode())==report['league_basic_sha256']
q['execution']['game_version']='2026.9.15.3'
q['situation']['notes']='Published e127989/2026.9.15.3. Exact league v2 BASIC validated on40 current-release matched cases; kiting candidates require separate qualification.'
ref={'artifact':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
q['belief']['claims']['B_kiting_campaign']={'claim':'Ten kiting candidates were evaluated with40 matched cases each and full replay verification. The current-release best win count was23/40 versus v2 22/40, but deaths135 versus134 failed preservation. A spell-casting variant reduced deaths to115 but won17/40. None passed both competitive and survival gates. These adaptive results do not rule out better kiting designs; retain the exact tested v2 executable.','status':'requires_review','evidence':[ref]}
q['goal']['G_survival']={'preference':'Preserve hero life through healing and combat decisions; qualify retreat behavior against survival, actual offense and fort wins.','provenance':'authored'}
q['goal']['G_glory']={'preference':'Track win*(lifetime XP -100*simulated minutes) as a secondary objective; fort-win and survival qualification remain primary.','provenance':'authored'}
for r in q['strategy']:
 if r['id'] in ['E0','E1'] and 'G_survival' not in r['for']:r['for'].append('G_survival')
 if r['id'] in ['R2','E2'] and 'G_glory' not in r['for']:r['for'].append('G_glory')
q['update'].update(revision=p['update']['revision']+1,parent=digest(p),change={'origin':'completed_kiting_campaign_feedback','policy_promoted':False})
q['update']['evidence'].append(ref);q['update']['needs_review'].append('belief/B_kiting_campaign')
refresh_grounding(q)
assert compile_policy(q)==old and extract(old,q)==q
out=ROOT/'tmp/gota-ir/kiting-campaign-20260915';out.mkdir(exist_ok=True)
bundle(q,out/'v2-retained');write(HERE/'waveguard_xp.evaluated.ir.json',q)
# Standalone report with a release filter and raw/rate comparison.
payload=json.dumps(rows).replace('</','<\\/')
html='''<!doctype html><html><meta charset="utf-8"><title>GOTA kiting evaluation</title>
<style>body{font:16px system-ui;background:#111b25;color:#e5edf5;max-width:1250px;margin:36px auto;padding:0 24px}h1{font-size:30px}p{line-height:1.6;max-width:1000px}select{font:inherit;padding:7px;background:#20313e;color:inherit;border:1px solid #647686;margin:8px}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{padding:12px 10px;text-align:right;border-bottom:1px solid #3d5261}th:first-child,td:first-child{text-align:left}a{color:#98cfed}small{color:#acc0cf}.result{padding:16px;background:#223442;border-left:4px solid #9fb4c5}</style>
<h1>Kiting trials: v2 retained</h1><p class="result">Kiting now has a reversible IR operator driven by confirmed hit events. None of these candidates met both the fort-win and survival gates, so the selected league policy is unchanged.</p>
<label>Game release<select id="release"><option value="2026.9.15.3">Current tested release · 2026.9.15.3</option><option value="2026.9.15.2">Earlier release · 2026.9.15.2</option><option value="all">Both releases</option></select></label>
<label>Survival metric<select id="metric"><option value="deaths">Total deaths</option><option value="deaths_per_minute">Deaths per simulated minute</option></select></label>
<table><thead><tr><th>Candidate</th><th>Wins /40</th><th>v2 wins /40</th><th>Candidate survival</th><th>v2 survival</th><th>Mean Glory</th><th>Artifacts</th></tr></thead><tbody id="rows"></tbody></table>
<p>All complete action/state tapes were verified. The67 tests cover IR/BASIC round trips, confirmed-hit timing, first observations and respawns, failed movement recovery, observed enemy targets, spell priority and friendly heals. Buying remains the v2 implementation.</p>
<p><small>These are adaptive discovery results. Candidates on release2026.9.15.3 share the same40 cases; do not treat their outcomes as independent replications. The timed candidate used another release and another40 cases. The spell matrix used an XP floor to account for spell damage; earlier failed gates were retained. No candidate received hosted qualification or league promotion.</small></p>
<script>const data=PAYLOAD;const release=document.querySelector('#release'),metric=document.querySelector('#metric');function render(){document.querySelector('#rows').innerHTML=data.filter(r=>release.value==='all'||r.game_version===release.value).map(r=>{const a=r.values.candidate,b=r.values.parent,k=metric.value,f=x=>k==='deaths'?x:x.toFixed(3);return `<tr><td>${r.name}<br><small>${r.game_version}</small></td><td>${a.wins}</td><td>${b.wins}</td><td>${f(a[k])}</td><td>${f(b[k])}</td><td>${a.mean_glory.toFixed(1)}</td><td><a href="${r.ir}">IR</a> · <a href="${r.basic}">BASIC</a></td></tr>`}).join('')}release.onchange=metric.onchange=render;render();</script></html>'''.replace('PAYLOAD',payload)
(HERE/'kiting-campaign-20260915.html').write_text(html)
print('Campaign report complete; canonical IR updated; league BASIC remains '+digest(old.encode()))
