"""Apply human coaching across IR layers without editing captured inputs."""
from binding import CONTRACTS
from policy_ir import digest, read, refresh_grounding
from release_workspace import RUN
from rush_candidates import make as rush_make

STUDY=RUN/'coached-lanes'
VARIANTS={'outer':{'primary_lane':2}, 'center':{'primary_lane':1},
          'rotate':{'primary_lane':2,'rotate_ticks':240},
          'presence':{'primary_lane':2,'require_creep_target':0}}


def make(name):
    p=rush_make('outer');p['id']='gota_coached_'+name
    p['skill']['observe']={'operator':'coached_lane','parameters':CONTRACTS['coached_lane'].defaults()|VARIANTS[name]}
    p['skill']['fallback']={'operator':'coached_route','parameters':CONTRACTS['coached_route'].defaults()}
    p['goal']['G_wave']['preference']='Persist in one assigned lane, escort and clear the wave, attack towers only with allied creep support, and rotate deliberately when validated lane-progress and support conditions allow.'
    p['goal']['G_survival']['preference']='Avoid unsupported tower dives and off-lane chases. Fight local blockers to preserve the push. Judge the combined strategy by fort wins; do not optimize deaths in isolation.'
    p['goal']['G_base']['preference']='Observed exposed fort first, then creep-supported lane towers and immediate lane blockers; avoid global nearest-target distraction.'
    refs=[{'artifact':str(STUDY/'capture-manifest.json'),'sha256':digest((STUDY/'capture-manifest.json').read_bytes())},
          {'artifact':str(RUN/'rush-study/local/result.json'),'sha256':digest((RUN/'rush-study/local/result.json').read_bytes())}]
    p['belief']['claims']['B_coaching']={'claim':'Human coaching speech1/2/9/10/13/23: stick to a lane, advance with creeps, avoid unsupported tower dives, rotate and finish the base. Captured executable reference is unrelatedPudgeWars; actual baseline is currentGotA bounded policy. Creep threshold and rotation triggers are authored hypotheses, not recovered Jordan code. Combined policy unvalidated. Pure rush predecessor failed local gates.', 'status':'untested','evidence':refs}
    p['situation']['notes']+=' Coached tower support uses current observed living allied creeps within conservative4/4/5tile radii for outer/inner/gate; actual world radii are5/5.5/6tiles. Towers retain a valid target. Goal/strategy/selection/navigation changed together.'
    p['update']['change']='Coaching-guided combined persistent lane, creep-gated siege, blocker clearing and direct fort finishing: '+name
    p['update']['needs_review']=['belief/B_coaching','goal/G_fort','goal/G_survival']
    p['update']['evidence']+=refs
    refresh_grounding(p);return p
