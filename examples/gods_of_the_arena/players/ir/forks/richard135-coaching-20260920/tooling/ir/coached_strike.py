"""Combined local combat/survival revisions without abandoning lane objectives."""
from coached_survival import make as survival_make,STUDY as PARENT
from policy_ir import digest,refresh_grounding

STUDY=PARENT.parent/'r5-strike'
VARIANTS={'focus6':('defend',6,1,1),'focus6_recover':('recover30',6,1,1),
          'focus4_recover':('recover45',4,1,1),'outer_focus':('defend',6,2,0)}


def make(name):
    base,radius,red,blue=VARIANTS[name];parent=survival_make(base);p=survival_make(base);p['id']='gota_coached_strike_'+name
    p['skill']['observe']['operator']='coached_strike'
    p['skill']['observe']['parameters'].update(focus_tiles=radius,primary_lane=red,blue_lane=blue)
    p['goal']['G_base']['preference']='Keep the committed lane, creep support, barracks-to-guards chain and exposed god priority. In local fights, concentrate on nearby vulnerable enemy heroes before returning to the wave; the siege-defense radius still limits distractions.'
    ref=PARENT.parent/'r5-convoy/local/result.json'
    p['belief']['claims']['B_strike']={'claim':'Complete40case centerconvoy validation won34/40vsbounded30/40overall, beating bounded20/20 but only14/20vsdefault with1055deaths. Rejected localgate. Standalone perimeter/recovery variants alsofailed. Test a coordinated combination of close hero focus and optional health recovery, preserving primarylane and tower-support constraints. No component is assumed to improve alone.', 'status':'untested','evidence':[{'artifact':str(ref),'sha256':digest(ref.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Coached lane push with focused local combat: '+name,needs_review=['belief/B_strike','goal/G_base','goal/G_survival'])
    refresh_grounding(p);return p
