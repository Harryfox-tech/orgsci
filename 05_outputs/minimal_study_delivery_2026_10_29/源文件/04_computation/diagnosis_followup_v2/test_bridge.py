import itertools
import unittest
from dataclasses import replace
from bridge_model import (Params, choose_action, enumerate_group, likelihood,
                          posterior, v1)


class BridgeTests(unittest.TestCase):
    def test_v1_is_nested_with_uninformative_private_signal(self):
        for q, mu, a in itertools.product((.5, .8, 1), (0, .5, 1), (0, .5, 1)):
            p = Params(productivity_value=mu)
            old = v1.enumerate_group(replace(p.base, skill_value=mu), q, a)[0]
            new = enumerate_group(p, q, .5, a)[0]
            for key in ("learn_rate", "verify_rate", "utility", "skill_gain", "true_hire", "hire_rate", "action_cost"):
                self.assertAlmostEqual(new[key], old[key])
            self.assertAlmostEqual(new["potential_productivity_gain"], old["skill_gain"])

    def test_bayes_combines_only_available_information(self):
        p = Params()
        self.assertAlmostEqual(posterior("S", "E", .9, .8, p), .18 / (.18 + .08))
        self.assertIsNone(posterior("S", "E", 1, 1, p))

    def test_accounting_and_mass(self):
        for q, r, a in itertools.product((.5, 1), (.5, .9, 1), (0, .5, 1)):
            p = Params(high_learn_gain=.3)
            m, _ = enumerate_group(p, q, r, a)
            self.assertAlmostEqual(m["mass"], 1)
            self.assertAlmostEqual(m["final_qualified"], .5 + m["skill_gain"])
            self.assertAlmostEqual(m["hire_rate"], m["true_hire"] + m["false_hire"])
            self.assertAlmostEqual(m["final_potential_productivity"], 1.5 + m["potential_productivity_gain"])

    def test_positive_post_threshold_growth_is_measured(self):
        p = Params(high_learn_gain=.3)
        m = enumerate_group(p, .5, .5, 0)[0]
        self.assertAlmostEqual(m["skill_gain"], .3)
        self.assertAlmostEqual(m["potential_productivity_gain"], .45)

    def test_fixed_policy_analytic_difference(self):
        for b, q in itertools.product((0, .3, 1.2), (.6, .8, 1)):
            p = Params(high_learn_gain=b)
            yes = enumerate_group(p, q, .5, 1)[0]
            no = enumerate_group(p, q, .5, 0)[0]
            self.assertAlmostEqual(yes["potential_productivity_gain"] - no["potential_productivity_gain"],
                                   -.5 * (.6 * (1 - q) + q * b))

    def test_perfect_self_knowledge_removes_incremental_diagnostic_effect(self):
        for b, mu, a in itertools.product((0, .3, 1.2), (0, .5, 1), (0, .5, 1)):
            p = Params(high_learn_gain=b, productivity_value=mu)
            base = enumerate_group(p, .5, 1, a)[0]
            for q in (.8, .95, 1):
                m = enumerate_group(p, q, 1, a)[0]
                for key in m:
                    self.assertAlmostEqual(m[key], base[key])

    def test_strong_but_imperfect_private_information_can_make_ai_inactive(self):
        baseline = enumerate_group(Params(), .5, .9, .5)[0]
        diagnostic = enumerate_group(Params(), .8, .9, .5)[0]
        self.assertAlmostEqual(diagnostic["utility"], baseline["utility"])
        self.assertAlmostEqual(diagnostic["action_change_from_no_diagnostic"], 0)

    def test_population_action_rate_can_hide_policy_switches(self):
        p = Params()
        baseline = enumerate_group(p, .5, .7, 1)[0]
        diagnostic = enumerate_group(p, .8, .7, 1)[0]
        self.assertAlmostEqual(baseline["learn_rate"], diagnostic["learn_rate"])
        self.assertAlmostEqual(diagnostic["action_change_from_no_diagnostic"], .38)

    def test_future_productivity_value_can_restore_learning(self):
        p = Params(high_learn_gain=1.2, productivity_value=.5)
        m = enumerate_group(p, .8, .5, 1)[0]
        self.assertAlmostEqual(m["learn_rate"], 1)
        self.assertAlmostEqual(m["potential_productivity_gain"], .9)

    def test_exact_policy_enumeration_optimality(self):
        for r, b, mu, access in ((.5, .3, 0, True), (.7, .3, .25, True), (.9, 1.2, .5, False)):
            p = Params(high_learn_gain=b, productivity_value=mu)
            observations = list(itertools.product(("S", "E"), repeat=2))
            feasible = ("N", "V", "L") if access else ("N", "L")
            policy_values = []
            q = .8
            for policy in itertools.product(feasible, repeat=4):
                expected = 0
                for k, pk in ((0, .5), (1, .5)):
                    for index, (h, z) in enumerate(observations):
                        weight = pk * likelihood(h, k, r) * likelihood(z, k, q)
                        action = policy[index]
                        qualified = 1 if k else v1.action_gain(action, p.base)
                        hired = (qualified * v1.hire_probability(action, 1, access, p.base)
                                 + (1 - qualified) * v1.hire_probability(action, 0, access, p.base))
                        growth = ((qualified - k) * p.output_gap if k == 0
                                  else {"L": b, "V": 0, "N": 0}[action])
                        expected += weight * (hired + mu * growth - v1.action_cost(action, p.base))
                policy_values.append(expected)
            m = enumerate_group(p, q, r, int(access))[0]
            self.assertAlmostEqual(m["utility"], max(policy_values))


if __name__ == "__main__":
    unittest.main()
