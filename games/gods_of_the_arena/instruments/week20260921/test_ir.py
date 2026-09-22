"""Boundary checks for the isolated Bassy migration and reverse conversion."""
from copy import deepcopy
import unittest
import build
from policy_ir import compile_policy, extract, refresh_grounding
import basic_syntax

class NewWeekIR(unittest.TestCase):
    def test_exact_roundtrip(self):
        p=build.policy()
        self.assertEqual(extract(compile_policy(p),p),p)

    def test_decimal_and_integer_division_are_distinct(self):
        self.assertNotEqual(basic_syntax.expression('7 / 2'),basic_syntax.expression('7 \\ 2'))
        self.assertEqual(basic_syntax.expression('0.25'),('decimal','0.25'))

    def test_extract_parameter_change_marks_claims_for_review(self):
        parent=build.policy()
        changed=deepcopy(parent)
        changed['skill']['recover']['parameters']['retreat_hp']=30
        refresh_grounding(changed)
        lifted=extract(compile_policy(changed),parent)
        self.assertEqual(lifted['skill']['recover']['parameters']['retreat_hp'],30)
        self.assertEqual(lifted['belief']['claims']['NewWeekBundle']['status'],'requires_review')

    def test_unaccounted_command_rejected(self):
        p=build.policy()
        with self.assertRaises(ValueError):
            extract(compile_policy(p)+'\nbuyItem(18)\n',p)

    def test_out_of_bounds_parameters_rejected(self):
        p=build.policy();p['skill']['observe']['parameters']['scan_limit']=1000
        with self.assertRaises(ValueError):compile_policy(p)

    def test_old_engine_binding_rejected(self):
        p=build.policy();p['execution']['game_version']='2026.9.16.5'
        with self.assertRaises(ValueError):compile_policy(p)

if __name__=='__main__':unittest.main()
