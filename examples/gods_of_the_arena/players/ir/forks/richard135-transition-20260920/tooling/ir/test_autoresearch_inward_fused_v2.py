"""Native action equivalence and the reproduced no-enemy work-limit repair."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import unittest
import test_policy_ir as f
from policy_ir import read,write,digest
from test_autoresearch_inward_rally import scene
from autoresearch_inward_fused_v2 import STUDY as S,RAW


class FusedTests(unittest.TestCase):
    captures=[]
    @classmethod
    def setUpClass(cls):
        cls.vm=Path('/Users/aaln/experiments/softmax/gota-autoresearch/cycles/20260920T033342Z-b4ca5b/scenario-vm-public-target')
    @classmethod
    def tearDownClass(cls):
        write(S/'native-captures.json',cls.captures)
    run_vm=f.RealVmTests.run_vm

    def play(self,source,cases):
        rows=self.run_vm(source,cases,['escortId','bestId','defPointX','defPointY','defActive'])
        self.captures.append(dict(source=str(source),source_sha256=digest(source.read_bytes()),inputs=cases,outputs=rows))
        return rows

    def test_every_captured_original_rally_fixture_has_identical_actions(self):
        cases={json.dumps(r['inputs'],sort_keys=True):r['inputs'] for r in read(RAW/'native-captures.json') if r['name']=='relay_sentries'}
        for cc in cases.values():
            old=self.play(RAW/'candidates/relay_sentries/policy.bas',cc)
            new=self.play(S/'candidates/relay_fused/policy.bas',cc)
            self.assertEqual([r['actions'] for r in new],[r['actions'] for r in old])
            self.assertEqual([r['memory'] for r in new],[r['memory'] for r in old])

    def test_no_enemy_dense240_budget_equipment_all_classes_both_colors(self):
        rows=[]
        for team in (0,1):
            for slot in range(5):
                c=scene(team,slot,dense=244)
                c['objects']=[o for o in c['objects'] if o['objectKind']!=2]
                second=deepcopy(c);second['self']['worldTick']=101
                rr=self.play(S/'candidates/relay_fused/policy.bas',[c,second]);rows+=rr
                self.assertTrue(all(any(a['command']=='buyItem' and a['arguments'][0]>4 for a in r['actions']) for r in rr))
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(S/'vm-budget.json',dict(decisions=len(rows),max_instructions=max(r['instructions'] for r in rows),max_work=max(r['work'] for r in rows),limits=dict(globals=256,source_bytes=65536,instructions=20000,work=50000),scope='Reproduced no-enemy240-object stress, both colors/every class; native source/global limits enforced. Finite tested envelope, not universal safety proof.'))

    def test_nearest_ties_retention_death_and_failed_walk_match_original(self):
        for team in (0,1):
            for mode in ('ties','retention','death','failed_walk','no_creeps'):
                c=scene(team,dense=60)
                c['objects']=[o for o in c['objects'] if o['objectKind']!=2]
                cc=[c,deepcopy(c),deepcopy(c)]
                for j,x in enumerate(cc):x['self']['worldTick']=100+j
                if mode=='retention':
                    cc[1]['objects'][-1].update(objectX=c['self']['selfX'],objectY=c['self']['selfY'])
                if mode=='death':
                    cc[1]['objects'][4]['objectHp']=0
                if mode=='failed_walk':
                    for x in cc:x['returns']={'walkTo':0}
                if mode=='no_creeps':
                    for x in cc:x['objects']=[o for o in x['objects'] if o['objectKind']!=3]
                old=self.play(RAW/'candidates/relay_sentries/policy.bas',cc)
                new=self.play(S/'candidates/relay_fused/policy.bas',cc)
                self.assertEqual([r['actions'] for r in new],[r['actions'] for r in old],(team,mode))

    def test_dense_mixed_public_enemies_and_allies(self):
        rows=[]
        for team in (0,1):
            for slot in range(5):
                c=scene(team,slot,dense=244)
                c['objects']=[o for o in c['objects'] if o['objectKind']!=2]
                for o in c['objects'][4:44]:
                    o.update(objectTeam=1-team,objectX=c['self']['selfX']-4,objectY=c['self']['selfY'],objectHp=60)
                rr=self.play(S/'candidates/relay_fused/policy.bas',[c]);rows+=rr
        self.assertLessEqual(max(r['instructions'] for r in rows),20000)
        self.assertLessEqual(max(r['work'] for r in rows),50000)
        write(S/'mixed-budget.json',dict(decisions=len(rows),max_instructions=max(r['instructions'] for r in rows),max_work=max(r['work'] for r in rows),scope='240 visible objects including40 enemy creeps, two colors/allclasses, no alarm.'))


if __name__=='__main__':
    unittest.main()
