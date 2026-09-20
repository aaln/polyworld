"""Replay-derived transition tests against the real BASIC VM, actual red classes."""
from copy import deepcopy
import unittest

from binding import CONTRACTS
from hero_binding import class_id
from policy_ir import compile_policy,extract
from stale_rally_repair import make,VARIANTS,prepare,STUDY
import test_rush_unblock as unblock
from test_rush_defense import scene
import test_policy_ir as f


def tower_scene(slot,tick=10472,count=4):
    c=scene(0,count=count,worldTick=tick)
    c['self'].update(selfId=100+slot,selfClass=class_id(0,slot),selfX=73,selfY=11)
    c['objects'][2].update(objectId=11,objectX=69,objectY=11)
    for e in c['objects'][4:]:e.update(objectX=69,objectY=14,objectTarget=11)
    return c


class StaleAnchorTests(unittest.TestCase):
    factory=staticmethod(make)
    run_vm=f.RealVmTests.run_vm
    play=unblock.UnblockTests.play
    @classmethod
    def setUpClass(cls):f.RealVmTests.setUpClass.__func__(cls)

    def test_dead_anchor_retires_for_all_red_sentry_classes(self):
        for slot in [0,2,3]:
            first=tower_scene(slot)
            for representation in ['absent','dead']:
                gone=tower_scene(slot,tick=10473,count=0)
                if representation=='absent':gone['objects'].pop(2)
                else:gone['objects'][2]['objectHp']=0
                old=self.play('warning100',[first,gone])
                self.assertEqual(old[-1]['memory']['defActive'],1)
                for name in VARIANTS[1:]:
                    new=self.play(name,[first,gone],('defActive','liveAnchorId','liveAnchorRetired'))
                    self.assertEqual(new[0]['memory']['liveAnchorId'],11)
                    self.assertEqual(new[-1]['memory']['defActive'],0)
                    self.assertEqual(new[-1]['memory']['liveAnchorRetired'],1)

    def test_enemy_fog_and_protection_do_not_retire_standing_own_anchor(self):
        for name in VARIANTS[1:]:
            first=tower_scene(2);fog=tower_scene(2,tick=10473,count=0)
            fog['objects'][2]['objectAlive']=0
            rows=self.play(name,[first,fog],('defActive','liveAnchorId'))
            self.assertEqual(rows[-1]['memory'],{'defActive':1,'liveAnchorId':11})

    def test_respawn_still_checks_liveness_and_fresh_group_reanchors(self):
        for name in VARIANTS[1:]:
            first=tower_scene(0);next_scene=tower_scene(0,tick=12000)
            next_scene['objects'][2].update(objectId=28,objectX=106,objectY=16)
            for e in next_scene['objects'][4:]:e.update(objectX=102,objectY=18,objectTarget=28)
            rows=self.play(name,[first,next_scene],('defActive','liveAnchorId','liveAnchorRetired'))
            self.assertEqual(rows[-1]['memory'],{'defActive':1,'liveAnchorId':28,'liveAnchorRetired':1})

    def test_core_creep_detection_from_replay_rally_is_independent(self):
        for slot in [0,2,3]:
            c=tower_scene(slot,tick=13081,count=0);c['objects'].pop(2)
            creep=f.obj(1858,kind=3,team=1,x=104,y=15,hp=60)
            c['objects'].append(creep)
            old=self.play('warning100',[c])[0]
            self.assertEqual(old['memory']['defActive'],0)
            new=self.play('retire_core',[c],('creepCoreId','defActive','bestId'))[0]
            self.assertEqual(new['memory'],{'creepCoreId':1858,'defActive':1,'bestId':1858})
            for change in [{'objectHp':0},{'objectTeam':0},{'objectX':70,'objectY':40}]:
                altered=deepcopy(c);altered['objects'][-1].update(change)
                self.assertEqual(self.play('retire_core',[altered],('creepCoreId',))[0]['memory']['creepCoreId'],0)

    def test_roundtrip_blue_branch_and_vm_budget(self):
        baseline=make('warning100')['skill']['observe'];rows=[]
        blue=CONTRACTS[baseline['operator']].source(baseline['parameters']).split('\nelse\n',1)[1]
        for name in VARIANTS[1:]:
            p=make(name);self.assertEqual(extract(compile_policy(p),p),p)
            obs=p['skill']['observe']
            self.assertEqual(CONTRACTS[obs['operator']].source(obs['parameters']).split('\nelse\n',1)[1],blue)
            for team in [0,1]:
                for slot in range(5):
                    c=tower_scene(slot) if team==0 else scene(1)
                    c['self'].update(selfClass=class_id(team,slot),selfGold=150)
                    c['objects'] += [f.obj(3000+i,kind=3,team=i%2,x=i%116,y=i*7%116) for i in range(240-len(c['objects']))]
                    rows += self.play(name,[c])
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        print('Dense240 VM maxima',max(r['instructions'] for r in rows),max(r['work'] for r in rows))


if __name__=='__main__':
    prepare();unittest.main()
