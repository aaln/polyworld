"""Export the validation comparison; no model fitting or parameter selection."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'docs/opponents/jordan-v268'
r=json.loads((OUT/'evidence.json').read_text());h=r['heldout'];v=r['observability']['all_jordan'];purple='#6842a6';grey='#aab4b9';green='#32816b'
fig,axes=plt.subplots(1,2,figsize=(12,5.7));fig.patch.set_facecolor('#faf9f6')
for ax in axes:ax.set_facecolor('#faf9f6');ax.spines[['top','right']].set_visible(False);ax.set_ylim(0,80);ax.set_ylabel('Accuracy / selected fraction (%)')
vals=[h['accuracy'],h['population_accuracy'],h['robustness_baselines']['class']['accuracy']]
axes[0].bar(range(3),[100*x for x in vals],color=[purple,grey,green],width=.65)
axes[0].set_xticks(range(3),['Jordan IR','Population','Population\n+ class']);axes[0].set_title('Heldout choice prediction · 1,466 starts',loc='left',fontsize=13)
for i,x in enumerate(vals):axes[0].text(i,100*x+1,f'{100*x:.1f}%',ha='center',weight='bold')
pref=next(p for p in r['preferences'] if p['id']=='Jordan268_I_O15');n=pref['predictions']['n'];vals2=[155/n,36/n,98/n]
axes[1].bar(range(3),[100*x for x in vals2],color=[purple,grey,green],width=.65);axes[1].set_xticks(range(3),['Jordan\nobserved','Population\nforecast accuracy','Population + class\nforecast accuracy']);axes[1].set_title('O15: hero + creep + structure nearby\nHP >100 · 238 heldout starts',loc='left',fontsize=13)
for i,x in enumerate(vals2):axes[1].text(i,100*x+1,f'{100*x:.1f}%',ha='center',weight='bold')
fig.suptitle('Jordan v268 — first opponent model',x=.07,ha='left',fontsize=20,weight='bold')
fig.text(.07,.06,f"20 Jordan games · 16 train / 4 chronological holdout · {100*v['fraction']:.1f}% of living hero-ticks visible\nOnly 3 distinct heldout trajectories. Choice is scored at inferred boundaries. No validated rollout proxy.",fontsize=10,color='#465257')
fig.tight_layout(rect=[.035,.16,1,.91]);fig.savefig(OUT/'validation.png',dpi=180);fig.savefig(OUT/'validation.svg')
