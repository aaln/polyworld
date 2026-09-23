"""Export personal score and its exact mean XP/time decomposition."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=Path(__file__).resolve().parents[4].parent/'polyworld/tmp/gota-blue-druid-siege-20260923/trial'
r=json.loads((S/'report.json').read_text());old,new=r['cells'];fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5.4))
values=[c['means']['score'] for c in [old,new]];cis=[c['score_ci95'] for c in [old,new]]
bars=ax.bar([0,1],values,color=['#63758b','#267d91'],width=.6)
ax.errorbar([0,1],values,yerr=[[v-ci[0] for v,ci in zip(values,cis)],[ci[1]-v for v,ci in zip(values,cis)]],fmt='none',color='#293644',capsize=5)
ax.bar_label(bars,fmt='%.1f',padding=6);ax.set_xticks([0,1],['Current baseline','Blue Druid candidate']);ax.set_ylabel('Mean individual points');ax.set_title('Blue later draft · 200 games per source');ax.spines[['top','right']].set_visible(False)
a,b=old['means'],new['means'];keys=['hero_xp','creep_xp','building_xp','god_xp'];d=[b[k]-a[k] for k in keys]+[-200*(b['minutes']-a['minutes'])];d.append(b['score']-a['score']-sum(d))
labels=['Hero XP','Creep XP','Structure XP','God XP','Time cost','Clamp / rounding'];bars=bx.barh(range(6),d,color=['#9e4937','#438363','#a89246','#786794','#687e97','#a8a8a8']);bx.bar_label(bars,fmt='%+.1f',padding=4);bx.set_yticks(range(6),labels);bx.invert_yaxis();bx.axvline(0,color='#344',linewidth=.7);bx.set_xlabel('Mean point change versus baseline');bx.set_title('Exact XP and time decomposition');bx.set_xlim(min(d)-30,max(d)+30);bx.spines[['top','right']].set_visible(False)
fig.suptitle('GOTA · independently tested blue-Druid transfer · 2026.9.22.3',fontsize=14);fig.text(.05,.025,'95% whole-game bootstrap intervals. All outcomes and natural draft classes included.\nFresh fixed-roster study; original broad-source results are excluded. Decomposition is descriptive, not causal.',fontsize=9,color='#52606d');fig.tight_layout(rect=[0,.10,1,.94]);fig.savefig(S/'score-breakdown.png',dpi=170);fig.savefig(S/'score-breakdown.svg');plt.close(fig)

svg=S/'score-breakdown.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
