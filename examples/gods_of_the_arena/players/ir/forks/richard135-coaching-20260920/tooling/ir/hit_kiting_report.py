"""Completed, audited screen -> empirical beliefs -> unchanged tested BASIC."""
import argparse
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from html import escape
from policy_ir import HERE,bundle,compile_policy,digest,extract,read,write
from hypothesis_study import sign_p

def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();d=a.directory.resolve()
    report=read(d/'screen-result.json');plan=read(d/'plan.json')
    if report['audited_games']!=120 or report['invalid_games_scored']:raise ValueError('Incomplete audited screen')
    metrics={}
    for arm in ['parent','candidate','baseline']:
        games=[read(p) for p in (d/'screen'/arm).glob('*/result.json')]
        if len(games)!=40:raise ValueError('Incomplete arm')
        hh=[r['heroes'][r['candidate_slots'][0]] for r in games]
        ticks=sum(r['ticks'] for r in games);decisions=sum(h['decisions'] for h in hh)
        deaths=sum(h['deaths'] for h in hh);hits=sum(h['basic_hit_events'] for h in hh)
        glory=[h['score']*(h['total_xp']-100*r['ticks']/1440) for r,h in zip(games,hh)]
        metrics[arm]={'wins':sum(h['score'] for h in hh),'games':40,'deaths':deaths,
            'deaths_per_game_minute':deaths/(ticks/1440),'deaths_per_1000_alive_decisions':1000*deaths/decisions,
            'basic_hit_events':hits,'hits_per_game_minute':hits/(ticks/1440),'mean_glory':sum(glory)/40,
            'mean_xp':sum(h['total_xp'] for h in hh)/40,
            'timeouts':sum(r['timeout'] for r in games),'total_ticks':ticks,'alive_decisions':decisions,
            'kite_bursts':sum(h['kite_bursts'] or 0 for h in hh),'kite_escapes':sum(h['kite_escapes'] or 0 for h in hh)}
    pairs=report['comparisons']['parent']['pairs']
    reductions=sum(p['candidate']['deaths']<p['control']['deaths'] for p in pairs)
    increases=sum(p['candidate']['deaths']>p['control']['deaths'] for p in pairs)
    result={'stage':'directional_local_screen','game_version':plan['game_version'],
        'source_sha256':plan['sources'],'gates':report['gates'],'activation':report['activation'],
        'passed':report['passed'],'audited_games':120,'metrics':metrics,
        'death_pairs':{'reduced':reductions,'increased':increases,'one_sided_exact_p':sign_p(reductions,increases)},
        'regressions':{k:r['flagged'] for k,r in report['regressions'].items()},
        'promotion_eligible':False,'limits':'Local default field, 40 independent cases/class balanced. Survival and damage metrics are directional. Hosted incumbents untested; no league change from this screen.'}
    path=HERE/'hit-kiting-20260915-screen.json';write(path,result)
    reference={'artifact':str(path.relative_to(HERE.parents[3])),'sha256':digest(path.read_bytes())}
    p=read(d/'candidate/policy.ir.json');source=compile_policy(p)
    if digest(source.encode())!=plan['sources']['candidate']:raise ValueError('Candidate mismatch')
    updated=deepcopy(p)
    m=metrics['candidate'];c=metrics['parent'];b=metrics['baseline']
    updated['belief']['claims']['B_kite']={'claim':f"Completed 40-case local screen: {m['wins']} wins versus v2 {c['wins']} and default {b['wins']}; deaths {m['deaths']} versus v2 {c['deaths']}; basic-hit events {m['basic_hit_events']} versus {c['basic_hit_events']}. Preregistered screen {'passed' if report['passed'] else 'failed'}. Live-field superiority unestablished.",'status':'requires_review','evidence':[reference]}
    act=report['activation'];fraction=act['landed_before_retreat_fraction']
    updated['belief']['claims']['B_kite_timing']={'claim':f"Replay-observed basic hit within1tick before {act['verified_bursts']}/{act['verified_bursts']+act['unverified_bursts']} normal retreats; displacement observed in {act['games']}/40 games. The published lifetime hit counter drives normal retreats; emergency escapes are separate. All120 complete action/state replays verified.",'status':'supported' if fraction>=1.0 and act['verified_bursts']>0 else 'requires_review','evidence':[reference]}
    updated['goal']['G_wave']['preference']='When no observed target exists, retain v2 allied-wave following. Combat execution is specified separately by G_kite.'
    updated['goal']['G_glory']={'preference':'Track lifetime-XP-minus-duration Glory on fort wins as a secondary measure; preserving fort wins and reducing deaths gates kiting changes.','provenance':'authored'}
    r=next(r for r in updated['strategy'] if r['id']=='R2')
    if 'G_glory' not in r['for']:r['for'].append('G_glory')
    updated['update']['parent']=digest(p);updated['update']['revision']+=1
    updated['update']['change']={'origin':'completed_kiting_screen','verdict':'screen_passed' if report['passed'] else 'screen_failed'}
    updated['update']['evidence'].append(reference)
    assert compile_policy(updated)==source and extract(source,updated)==updated
    bundle(updated,d/'evaluated')
    write(HERE/'hypotheses/confirmed_hit_kite.evaluated.ir.json',updated)
    (HERE/'hypotheses/confirmed_hit_kite.evaluated.bas').write_text(source)
    rows=''.join('<tr><td>'+escape(arm)+'</td>'+''.join(f'<td>{m[k]:.3f}</td>' for k in ['wins','deaths','deaths_per_game_minute','basic_hit_events','mean_glory'])+'</tr>' for arm,m in metrics.items())
    (HERE/'hit-kiting-20260915-screen.html').write_text('<!doctype html><meta charset="utf-8"><title>GOTA kiting screen</title><style>body{font:17px system-ui;max-width:1000px;margin:40px auto;background:#101821;color:#e7edf4}td,th{padding:12px;border-bottom:1px solid #526171;text-align:right}p{line-height:1.6}</style><h1>V2 confirmed-hit kiting screen</h1><p>Published2026.9.15.3. Forty fresh matched cases per arm; all120 replays verified. Screen '+('passed' if report['passed'] else 'failed')+'. No league promotion.</p><table><tr><th>Policy</th><th>Wins /40</th><th>Deaths</th><th>Deaths/min</th><th>Basic hits</th><th>Mean Glory</th></tr>'+rows+'</table><p>'+escape(updated['belief']['claims']['B_kite_timing']['claim'])+'</p><p>'+escape(result['limits'])+'</p>')
    write(d/'reported-result.json',result)
    print(__import__('json').dumps(result,indent=2))
if __name__=='__main__':main()
