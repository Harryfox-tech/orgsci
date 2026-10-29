"""Independent decision-policy checks, analytic identities and boundary tests."""
import itertools
import unittest
from dataclasses import replace
from model import (Params, action_cost, action_gain, choose_action, enumerate_group,
                   hire_probability, learning_cutoff, posterior_deficient)


class MinimalResearchTests(unittest.TestCase):
    def test_total_probability_and_accounting(self):
        for prior, q, access in itertools.product((0, .25, .5, 1), (.5, .8, 1), (0, .5, 1)):
            p = Params(prior_deficient=prior)
            m, rows = enumerate_group(p, q, access)
            self.assertAlmostEqual(sum(r["mass"] for r in rows), 1)
            self.assertAlmostEqual(m["hire_rate"], m["true_hire"] + m["false_hire"])
            self.assertAlmostEqual(m["final_qualified"], 1 - prior + m["skill_gain"])
            self.assertAlmostEqual(m["final_qualified"], m["true_hire"] + m["qualified_not_hired"])
            self.assertAlmostEqual(m["learn_rate"] + m["verify_rate"] + m["no_action_rate"], 1)

    def test_bayes_likelihoods(self):
        p = Params(prior_deficient=.25)
        self.assertAlmostEqual(posterior_deficient("S", .8, p), .2 / .35)
        self.assertAlmostEqual(posterior_deficient("E", .8, p), .05 / .65)

    def test_analytic_interior_formula(self):
        p = Params()
        self.assertAlmostEqual(learning_cutoff(p), 22 / 51)
        for q in (.6, .65, .8, .95, 1):
            available, _ = enumerate_group(p, q, 1)
            unavailable, _ = enumerate_group(p, q, 0)
            self.assertAlmostEqual(available["skill_gain"] - unavailable["skill_gain"],
                                   -.5 * p.learn_gain * (1 - q))
            self.assertAlmostEqual(available["true_hire"] - unavailable["true_hire"],
                                   -.5 * p.learn_gain * p.test_tpr * (1 - q))
            self.assertAlmostEqual(available["utility"] - unavailable["utility"],
                                   .5 * (p.learn_cost - p.verify_cost
                                   - p.learn_gain * (p.test_tpr - p.test_fpr) * (1 - q)))

    def test_optimal_against_all_signal_contingent_policies(self):
        # Independent brute force over all policies; does not call choose_action.
        for cost, q, access in itertools.product((.1, .3, .65), (.5, .65, .95), (0, 1)):
            p = Params(learn_cost=cost)
            actions = ("N", "V", "L") if access else ("N", "L")
            policy_values = []
            for policy in itertools.product(actions, repeat=2):
                value = 0
                for k0, pk in ((0, p.prior_deficient), (1, 1 - p.prior_deficient)):
                    for index, signal in enumerate(("S", "E")):
                        likelihood = q if (signal == "S") == (k0 == 0) else 1 - q
                        a = policy[index]
                        final_one = 1 if k0 else action_gain(a, p)
                        hire = (final_one * hire_probability(a, 1, access, p)
                                + (1 - final_one) * hire_probability(a, 0, access, p))
                        value += pk * likelihood * (p.hire_value * hire
                                 + p.skill_value * (final_one - k0) - action_cost(a, p))
                policy_values.append(value)
            actual, _ = enumerate_group(p, q, access)
            self.assertAlmostEqual(actual["utility"], max(policy_values))

    def test_value_of_information(self):
        for cost, prior, access in itertools.product((.1, .3, .65), (.25, .5, .75), (0, .5, 1)):
            p = Params(learn_cost=cost, prior_deficient=prior)
            values = [enumerate_group(p, q, access)[0]["utility"] for q in (.5, .6, .8, .95, 1)]
            self.assertTrue(all(y >= x - 1e-12 for x, y in zip(values, values[1:])))

    def test_no_forced_participation(self):
        self.assertEqual(choose_action(1, True, Params(learn_cost=.65))[0], "N")
        self.assertEqual(choose_action(1, False, Params(learn_cost=.65))[0], "N")

    def test_no_verification_and_low_cost_makes_information_irrelevant(self):
        baseline = enumerate_group(Params(), .5, 0)[0]
        for q in (.65, .8, 1):
            actual = enumerate_group(Params(), q, 0)[0]
            for key in baseline:
                self.assertAlmostEqual(actual[key], baseline[key])

    def test_same_total_slots_same_aggregate_joint_rates(self):
        for q in (.5, .65, .8, 1):
            high = enumerate_group(Params(), q, .75)[0]
            low = enumerate_group(Params(), q, .25)[0]
            equal = enumerate_group(Params(), q, .5)[0]
            for key in ("utility", "skill_gain", "true_hire", "false_hire", "hire_rate"):
                self.assertAlmostEqual((high[key] + low[key]) / 2, equal[key])

    def test_shared_bottleneck_does_not_give_training_free_proof(self):
        p = Params(training_requires_verification_access=True)
        m, _ = enumerate_group(p, .8, 0)
        self.assertEqual(m["no_action_rate"], 1)
        self.assertEqual(m["hire_rate"], 0)

    def test_equal_learning_effects_remove_skill_tradeoff(self):
        p = Params(verify_gain=.6)
        for q in (.5, .8, 1):
            yes, _ = enumerate_group(p, q, 1)
            no, _ = enumerate_group(p, q, 0)
            self.assertAlmostEqual(yes["skill_gain"], no["skill_gain"])
            self.assertAlmostEqual(yes["true_hire"], no["true_hire"])

    def test_partial_teaching_can_crowd_out_more_effective_training(self):
        # Analytic counterexample prompted by the fixed boundary comparison:
        # baseline S->L,E->V gives .5*.8*.6=.24; at verify_gain=.3, V is
        # optimal under both signals and gives .5*.3=.15 instead.
        initial = enumerate_group(Params(), .8, 1)[0]
        partial = enumerate_group(Params(verify_gain=.3), .8, 1)[0]
        self.assertAlmostEqual(initial["skill_gain"], .24)
        self.assertAlmostEqual(partial["skill_gain"], .15)
        self.assertAlmostEqual(partial["verify_rate"], 1)
        self.assertGreater(partial["utility"], initial["utility"])

    def test_more_options_cannot_lower_candidate_value(self):
        for q in (.5, .6, .8, 1):
            yes = enumerate_group(Params(), q, 1)[0]
            no = enumerate_group(Params(), q, 0)[0]
            self.assertGreaterEqual(yes["utility"] + 1e-12, no["utility"])


if __name__ == "__main__":
    unittest.main()
