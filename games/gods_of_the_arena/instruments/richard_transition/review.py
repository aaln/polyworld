"""Count exact reconstructed decisions; distinguish samples from whole games."""
from collections import Counter
from statistics import median
from study import STUDY, read, write, digest


def main():
    trace=STUDY/'defense-state';proof=read(trace/'equivalence.json')
    assert proof['summaries']['owned']['all_state_hashes_equal']
    own=[read_line for line in (trace/'owned.jsonl').open()
         if (read_line:=__import__('json').loads(line)).get('type')=='decision']
    active=[r for r in own if r['memory'].get('gaActive')]
    defending=[r for r in active if r['memory']['defSentry']]
    frames={r['tick']:r for line in (trace/'decoded.jsonl').open()
            if (r:=__import__('json').loads(line)).get('type')=='frame'}
    final=frames[max(frames)]
    end=[{k:v for k,v in h.items() if k!='visible_post_tick'} for h in final['heroes']]
    data={'episode':read(STUDY/'session-binding.json')['episode'],
        'exact_owned_source_reconstruction':proof,
        'decision_samples':{'sample_interval_ticks':120,'active':len(active),
            'phase_counts':dict(Counter(r['memory']['defSentryRole'] for r in active)),
            'emergency_active':len(defending),
            'remembered_only':sum(r['memory']['coreRespond']<2 and r['memory']['coreValue']==400 for r in defending),
            'without_visible_enemy_hero':sum(r['memory']['defCount']==0 for r in defending),
            'core_damaged':sum(r['memory']['coreValue']<400 for r in defending)},
        'final_hero_benchmarks':end,
        'findings':[
            'The actual episode uses the tested formation4800_budget red source; it is not the deployed Jordan branch.',
            'Memory-only defense occupies many sampled decisions. A static-damaged-core renewal bug exists, but the core remains400HP in these defense samples; it is not the measured cause of this episode stall.',
            'The prior four-healthy readiness requirement can suppress shared hero pursuit when defenders die. The observed Ranger and friendly progression gap motivates coordinated focus and scaling, not a claim that item order alone caused defeat.',
            'There is no public global enemy-position oracle. Missing heroes require scouting or uncertainty, not invented targets.'],
        'limits':'Correlated sampled decisions from one selected coached loss. These are exact source/state reconstructions, not reacting counterfactuals or a cohort effect estimate.'}
    combat=STUDY/'combat-state'
    if (combat/'equivalence.json').exists():
        events=[__import__('json').loads(l) for l in (combat/'owned.jsonl').open()]
        stats=[r for r in events if r.get('type')=='final_stats']
        hits=[r for r in events if r.get('type')=='basic_hit' and r['slot']==6]
        gaps=[b['tick']-a['tick'] for a,b in zip(hits,hits[1:])]
        data['ranger_native_stats']={'stats':stats,'late_hit_count':len(hits),
            'first_tick':hits[0]['tick'],'last_tick':hits[-1]['tick'],
            'inter_hit_ticks':dict(Counter(gaps)),'median_inter_hit_ticks':median(gaps),
            'equivalence':read(combat/'equivalence.json')}
        # Count opponent command timing only from the actual replay. No rival
        # executable or unobserved state is exposed to the candidate controller.
        cmds=[r for l in (combat/'decoded.jsonl').open()
              if (r:=__import__('json').loads(l)).get('type')=='action' and r['slot']==6 and r['tick']>=12500]
        data['ranger_native_stats']['late_command_kinds']=dict(Counter(r['kind'] for r in cmds))
    write(STUDY/'diagnosis.json',data)
    print(data['decision_samples'],flush=True)


if __name__=='__main__':main()
