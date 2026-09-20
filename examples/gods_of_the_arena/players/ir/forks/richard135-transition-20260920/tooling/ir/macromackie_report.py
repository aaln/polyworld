"""Human-readable evidence and IR feedback for the macromackie investigation."""
import json
from pathlib import Path
from policy_ir import read,write,digest
from economy_feedback import record
from release_workspace import RUN
from macromackie_review import ROOT,EPISODE

def plot():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import numpy as np
 p=ROOT/'artifacts'/EPISODE
 rows=[json.loads(x) for x in (p/'decoded.jsonl').open()]
 h=next(x for x in rows if x['type']=='header');frames=[x for x in rows if x['type']=='frame']
 terrain=np.array([[v=='.' for v in row] for row in h['terrain']])
 fig,axes=plt.subplots(1,4,figsize=(17,4.8))
 names=['Return to base underway','Recall expires during travel','Recall threshold not met','Defense collapses; god falls']
 for ax,t,title in zip(axes,(5520,5760,9240,9576),names):
  f=min(frames,key=lambda f:abs(f['tick']-t));ax.imshow(terrain,origin='lower',cmap='Greys',alpha=.18,extent=(0,116,0,116))
  for b in f['buildings']:
   if b['hp']>0:ax.scatter(*b['position'],c=['#cf4545','#2975c3'][b['team']],marker='s',s=75 if b['kind']=='Fort' else 20)
  for hero in f['heroes']:
   if hero['hp']<=0:continue
   ax.scatter(*hero['position'],c=['#cf4545','#2975c3'][hero['team']],s=60)
   ax.annotate(str(hero['slot']),hero['position'],xytext=(3,3),textcoords='offset points',fontsize=9)
   if hero['slot'] in (1,4):ax.scatter(*hero['position'],facecolors='none',edgecolors='#d29500',s=220,linewidth=2)
  ax.set(xlim=(0,116),ylim=(0,116),aspect='equal',title=f'{f["tick"]/1440:.2f} min · tick {f["tick"]}\n{title}')
  ax.set_xlabel('Map x');ax.set_ylabel('Map y')
 fig.suptitle('Source-verified replay: the two attackers leave the three defenders\nRed: our anchor policy. Blue: macromackie v4. Gold rings: Crossbowman (1), Berserker (4).')
 fig.tight_layout(rect=(0,0,1,.90));fig.savefig(ROOT/'macro-diagnosis.png',dpi=150,bbox_inches='tight');plt.close(fig)

def main():
 plot()
 p=ROOT/'artifacts'/EPISODE;proof=read(p/'decisions-proof.json');a=read(p/'audit.json')
 assert read(ROOT/'mechanism-test.json')['passed'] and proof['all_state_hashes_equal'] and proof['all_actions_consumed']
 comparison=read(ROOT/'comparison.json') if (ROOT/'comparison.json').exists() else None
 lines=['# Why anchor lost to macromackie v4','',f'[Requested league replay](https://softmax.com/observatory/v2?tab=overview&detail=episode-request:{EPISODE})','',
 'The red team split into three persistent home defenders and two roaming attackers. The attackers abandoned a return before arrival, then ignored a later three-hero attack because fresh recall required four. Macromackie completed the center-lane breach and killed the god while both attackers were across the map. This is observed policy behavior, not a proven collision failure or VM crash.','',
 '## Verified timeline','',
 '- Tick960 (00:40): middle outer tower already destroyed; middle inner gone by1320 (00:55). The opponents opened through the middle while our heroes initially occupied other lanes.',
 '- Tick2400 (01:40): Death Knight, Lich and Warlock all issue walkTo(100,15), target0, defense expiry8830. The two attackers have already been released. Repeated stationary waiting is an explicit policy order.',
 '- Tick5520 (03:50): both attackers are returning toward(106,12); their expiry is5731. The sentries are actively fighting near the first core guard.',
 '- Tick5730 ->5731 (03:58.75 ->03:58.79): both attacker commands switch from walkTo(106,12) to walkTo(49,15). The timer expires in transit; the next sampled positions are still far from base.',
 '- Tick9240 (06:25): the attackers observe defFront108, defCount3, defAnchor29, but defActive0. They keep moving along the far-side lane. Guard29 is the last standing core guard.',
 '- Native audit records defender deaths at9287 (Death Knight),9358 (Warlock),9416 (Lich). At9480 both attackers are still across the map, while Ranger, Arcanist and Druid attack the last core guard.',
 '- Tick9576 (06:39): our god is dead; enemy god remains400HP. Warlock is newly respawned at full HP, not evidence that it fled the final fight. The last guard and god die in the final96tick sampled interval; exact structure-destruction ticks were not sampled.',
 '',f'We inflicted {sum(h["deaths"] for h in a["heroes"][5:])} hero deaths versus {sum(h["deaths"] for h in a["heroes"][:5])} on our team. The kill lead did not become decisive structure pressure. All five heroes bought equipment.','',
 '## Root conditions, checked in the real BASIC VM','',
 'The anchor policy gives Crossbowman and Berserker a480tick/20second recall and disables renewal for nearby survivors. Sentries retain7200ticks/5minutes. Once an attacker clock has expired, a group of at least4 is required at a friendly structure. This creates asymmetric team commitments. Native fixtures reproduce both the three-versus-four threshold and expiry while travel remains unfinished; blue_repair retains the longer commitment in the same fixture. A threshold3 diagnostic triggers recall but is not a gameplay-validated fix.',
 '',
 '## Competitive comparison','']
 if comparison:
  lines+=['| Policy | Red wins | Blue wins | Total |','|---|---:|---:|---:|']
  for name,r in comparison['results'].items():lines.append(f'| {name} | {r["colors"]["red"]["win"]}/40 | {r["colors"]["blue"]["win"]}/40 | {r["wins"]}/80 |')
 else:lines+=['Full comparison is running; see hosted/ and http://localhost:8834.']
 lines+=['','Both arms use the same pinned macromackie v4, game2026.9.16.5 and configuration, with40episodes percolor. Seeds differ; fixed-policy trajectories repeat. These counts are empirical matchup evidence, not independent-trial significance or broad-field proof. The lab has no validated sample-size floors. All completed cohorts retain full runtime, replay, equipment and roster audits.','',
 'A median-duration anchor red win also has repeated stationary defense and two attackers away. Thus splitting/standing alone is not sufficient to explain every outcome. The actual blue_repair red league win also has these features. Anchor additionally changes caster support; the A/B does not isolate the whole win difference to recall duration.','',
 '## Next hypotheses','',
 '1. Keep a recall active until the returning hero reaches the threatened area; release after actual resolution rather than a travel-blind clock.',
 '2. Add an emergency override for observed pressure on the last core guard or exposed god, independent of the generic four-hero rush threshold.',
 '3. Coordinate return and exit assignments across roles. Keep ordinary creep-backed offense and avoid replacing one permanent-defense failure with another.',
 '',
 'These are proposed repairs, not validated executable changes. Existing policy sources and the user-selected diverse league pair are preserved. The investigation is reflected back into a new IR/source evidence pair.','',
 f'Proof: {proof["ticks"]} ticks, {proof["owned_commands_matched"]} owned commands, every generated command and every state hash matched. Evidence: timeline.json, mechanism-test.json, review-comparison.json, hosted/, macro-diagnosis.png.']
 (ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n')
 if comparison and not (ROOT/'diagnostic-feedback').exists():
  src=ROOT/'evaluated-feedback'
  record(src/'policy.ir.json',src/'policy.bas','Observedmacromackie loss: explicit sharedwaiting; carryrecall expires5731whiletravelling; observedthreeheroes atlastguard do not reacquirebecausegroup4required; allthreehomedefendersdie9287/9358/9416; goddead9576. Nativefixturesreproduceconditions. Samepatterns occur inwins, so no singlecausalfixclaimed. Restorearrivalqualifiedcohesionandcoreemergency as next hypotheses; noexecutablechange orleagueupdate.',ROOT/'REPORT.md',ROOT/'diagnostic-feedback')
 print(ROOT/'REPORT.md')
if __name__=='__main__':main()
