"""Deployment boundaries and IR feedback parity, using isolated synthetic results."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from policy_ir import compile_policy,digest,extract,read,write
from release_hosted import OPTIMIZER
from release_deploy import AARON
from win_screen import STUDY
import win_deploy
import win_reconcile


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.study=Path(self.tmp.name)/'study';self.here=Path(self.tmp.name)/'ir'
        self.here.mkdir();(self.here/'VERSION_LOG.md').write_text('Synthetic test only\n')
        for d in ['local/candidates/bounded','hosted-discovery/bounded','hosted-confirmation/bounded/feedback','field','rival-matchups','review']:
            (self.study/d).mkdir(parents=True,exist_ok=True)
        self.source=(STUDY/'local/candidates/bounded/policy.bas').read_text()
        (self.study/'local/candidates/bounded/policy.bas').write_text(self.source)
        parent=read(STUDY/'hosted-discovery/bounded/feedback/policy.ir.json')
        write(self.study/'hosted-confirmation/bounded/feedback/policy.ir.json',parent)
        version={'id':'synthetic-candidate','name':'synthetic-only','version':1}
        write(self.study/'hosted-discovery/bounded/uploaded-version.json',version)
        write(self.study/'hosted-discovery/bounded/upload-request.json',{'content_hash':digest(self.source.encode()),'player_id':OPTIMIZER})
        for p in ['local/screen-result.json','hosted-discovery/result.json','review/druid-review-manifest.json']:
            write(self.study/p,{'synthetic_fixture':True})
        metrics={'games':400,'wins':300,'mean_deaths':2.5,'death_rate':.5}
        confirmation={'passed':True,'selected':'bounded','arms':{'bounded':metrics,'current':metrics|{'wins':220,'mean_deaths':4}},
            'comparisons':{'bounded':{'gain':.2,'one_sided_p':.0001,'checks':{'gain':True,'mean_deaths':True,'gear':True,'significance':True,'classes':True}}}}
        write(self.study/'hosted-confirmation/result.json',confirmation)
        write(self.study/'hosted-confirmation/plan.json',{'candidate':'bounded','sample_size':400,'current_version':win_deploy.CURRENT,
            'discovery_sha256':digest((self.study/'hosted-discovery/result.json').read_bytes())})
        write(self.study/'field/result.json',{'passed':True,'candidate':'bounded','version':version['id'],'games':100,'wins':60,'equipment_games':100})
        write(self.study/'field/plan.json',{'confirmation_sha256':digest((self.study/'hosted-confirmation/result.json').read_bytes()),'excluded_players':[AARON,OPTIMIZER]})
        write(self.study/'rival-matchups/result.json',{'rivals':{'synthetic':{'label':'Synthetic rival','wins':80,'colors':{'red':{'win':40},'blue':{'win':40}}}}})

    def reconcile(self):
        with patch.object(win_reconcile,'STUDY',self.study),patch.object(win_reconcile,'HERE',self.here):
            win_reconcile.main()

    def test_feedback_retains_executable_and_uncertainty(self):
        self.reconcile()
        out=self.study/'reconciled/bounded';policy=read(out/'policy.ir.json')
        self.assertEqual(compile_policy(policy),self.source)
        self.assertEqual(extract(self.source,policy),policy)
        self.assertEqual(policy['update']['parent'],digest(read(out/'parent.ir.json')))
        self.assertEqual(policy['belief']['claims']['B_macro']['status'],'supported')
        self.assertEqual(policy['belief']['claims']['B_lane_coverage']['status'],'requires_review')
        self.assertIn('belief/B_lane_coverage',policy['update']['needs_review'])
        self.assertEqual((self.here/'win_bounded_0916.evaluated.bas').read_text(),self.source)
        self.assertTrue((self.here/'win_bounded_0916.evaluated.ir.json').is_file())
        win_deploy.readiness(self.study)
        self.reconcile()
        self.assertEqual(policy,read(out/'policy.ir.json'))

    def test_deployment_rejects_missing_or_stale_feedback(self):
        with self.assertRaises(FileNotFoundError):win_deploy.readiness(self.study)
        self.reconcile()
        p=self.study/'reconciled/bounded/policy.ir.json';policy=deepcopy(read(p))
        policy['belief']['claims']['B_macro']['claim']='A changed semantic claim without matching provenance'
        write(p,policy)
        with self.assertRaisesRegex(ValueError,'reconciliation'):win_deploy.readiness(self.study)

    def test_failed_field_cannot_be_reconciled_for_promotion(self):
        p=self.study/'field/result.json';write(p,read(p)|{'passed':False,'wins':49})
        with self.assertRaisesRegex(ValueError,'passing confirmation and field'):self.reconcile()
        self.assertFalse((self.study/'reconciled').exists())


if __name__=='__main__':unittest.main()
