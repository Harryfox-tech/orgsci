"""Finite Bayesian decision model. No random sampling or legacy imports.

All candidates enter with inadequate accepted proof. K=0 means both skill and
proof are insufficient; K=1 means proof alone is insufficient. Decision code
receives a posterior, never a realized K. L includes an end-of-training test;
V is a standalone test. Both tests use the same acceptance standard.
"""
from dataclasses import asdict, dataclass
from math import isfinite


@dataclass(frozen=True)
class Params:
    prior_deficient: float = 0.5
    hire_value: float = 1.0
    skill_value: float = 0.0
    learn_gain: float = 0.6
    verify_gain: float = 0.0
    learn_cost: float = 0.3
    verify_cost: float = 0.08
    test_tpr: float = 0.9
    test_fpr: float = 0.05
    no_action_hire: float = 0.0
    training_requires_verification_access: bool = False

    def __post_init__(self):
        for key, value in asdict(self).items():
            if not isfinite(value):
                raise ValueError(f"Non-finite parameter: {key}")
        for key in ("prior_deficient", "learn_gain", "verify_gain", "test_tpr",
                    "test_fpr", "no_action_hire"):
            if not 0 <= getattr(self, key) <= 1:
                raise ValueError(f"Probability out of bounds: {key}")
        if self.test_tpr < self.test_fpr:
            raise ValueError("Final test must be weakly informative")
        if min(self.hire_value, self.skill_value, self.learn_cost, self.verify_cost) < 0:
            raise ValueError("Values and costs must be nonnegative")


def action_gain(action, p):
    return {"N": 0.0, "L": p.learn_gain, "V": p.verify_gain}[action]


def action_cost(action, p):
    return {"N": 0.0, "L": p.learn_cost, "V": p.verify_cost}[action]


def hire_probability(action, final_skill, verification_available, p):
    if action == "N":
        return p.no_action_hire
    if action == "V" and not verification_available:
        raise ValueError("Standalone verification is unavailable")
    if (action == "L" and p.training_requires_verification_access
            and not verification_available):
        return p.no_action_hire
    return p.test_tpr if final_skill else p.test_fpr


def action_value(action, p_deficient, verification_available, p):
    """Expected value from a belief, not a known true state."""
    gain = action_gain(action, p)
    final_qualified = 1 - p_deficient + p_deficient * gain
    hire = (final_qualified * hire_probability(action, 1, verification_available, p)
            + (1 - final_qualified) * hire_probability(action, 0, verification_available, p))
    return (p.hire_value * hire + p.skill_value * p_deficient * gain
            - action_cost(action, p))


def choose_action(p_deficient, verification_available, p):
    if not 0 <= p_deficient <= 1:
        raise ValueError("Invalid posterior")
    # First maximizer wins: no action, then verification, then learning.
    feasible = ["N", "V", "L"] if verification_available else ["N", "L"]
    values = {a: action_value(a, p_deficient, verification_available, p) for a in feasible}
    best = max(values.values())
    chosen = next(a for a in feasible if values[a] >= best - 1e-12)
    return chosen, values


def signal_likelihood(signal, initial_skill, quality):
    # S indicates skill deficiency; E indicates existing skill / weak proof.
    correct_signal = "S" if initial_skill == 0 else "E"
    return quality if signal == correct_signal else 1 - quality


def posterior_deficient(signal, quality, p):
    joint0 = p.prior_deficient * signal_likelihood(signal, 0, quality)
    joint1 = (1 - p.prior_deficient) * signal_likelihood(signal, 1, quality)
    return None if joint0 + joint1 == 0 else joint0 / (joint0 + joint1)


RATE_KEYS = (
    "learn_rate", "verify_rate", "no_action_rate", "skill_gain",
    "final_qualified", "hire_rate", "true_hire", "false_hire",
    "qualified_not_hired", "unqualified_not_hired", "action_cost", "utility",
    "learning_initially_qualified", "verification_initially_deficient",
    "initially_qualified_hired_mass", "mass",
)


def summarize(rows, p):
    m = {key: 0.0 for key in RATE_KEYS}
    for r in rows:
        weight, action = r["mass"], r["action"]
        k0, k1, h = r["initial_skill"], r["final_skill"], r["hired"]
        m["mass"] += weight
        m[{"L": "learn_rate", "V": "verify_rate", "N": "no_action_rate"}[action]] += weight
        m["skill_gain"] += weight * (k1 - k0)
        m["final_qualified"] += weight * k1
        m["hire_rate"] += weight * h
        m["true_hire"] += weight * h * k1
        m["false_hire"] += weight * h * (1 - k1)
        m["qualified_not_hired"] += weight * (1 - h) * k1
        m["unqualified_not_hired"] += weight * (1 - h) * (1 - k1)
        m["action_cost"] += weight * action_cost(action, p)
        m["learning_initially_qualified"] += weight * (action == "L") * k0
        m["verification_initially_deficient"] += weight * (action == "V") * (1 - k0)
        m["initially_qualified_hired_mass"] += weight * k0 * h
    m["utility"] = (p.hire_value * m["hire_rate"] + p.skill_value * m["skill_gain"]
                    - m["action_cost"])
    m["qualified_share_of_hires"] = m["true_hire"] / m["hire_rate"] if m["hire_rate"] else None
    m["initially_qualified_recognition"] = (
        m["initially_qualified_hired_mass"] / (1 - p.prior_deficient)
        if p.prior_deficient < 1 else None)
    return m


def enumerate_group(p, quality, access_probability):
    """Exact joint mass over availability, initial K, signal, final K, hire.

    Conditional independence of access and K is an explicit design assumption.
    Diagnostics are private and cannot change the fixed final-test rule.
    """
    if not 0.5 <= quality <= 1 or not 0 <= access_probability <= 1:
        raise ValueError("Invalid signal quality or access probability")
    rows = []
    for available, pa in ((False, 1 - access_probability), (True, access_probability)):
        if pa == 0:
            continue
        for k0, pk in ((0, p.prior_deficient), (1, 1 - p.prior_deficient)):
            for signal in ("S", "E"):
                probability = pa * pk * signal_likelihood(signal, k0, quality)
                if probability == 0:
                    continue
                posterior = posterior_deficient(signal, quality, p)
                action, values = choose_action(posterior, available, p)
                probability_k1 = 1.0 if k0 else action_gain(action, p)
                for k1, pf in ((0, 1 - probability_k1), (1, probability_k1)):
                    ph = hire_probability(action, k1, available, p)
                    for hired, py in ((0, 1 - ph), (1, ph)):
                        mass = probability * pf * py
                        if mass == 0:
                            continue
                        rows.append({"verification_available": available,
                                     "initial_skill": k0, "signal": signal,
                                     "posterior_deficient": posterior, "action": action,
                                     "decision_value": values[action], "final_skill": k1,
                                     "hired": hired, "mass": mass})
    return summarize(rows, p), rows


def mix_metrics(weighted_metrics, p):
    """Mix joint rates first; do not average conditional ratios."""
    total = sum(w for w, _ in weighted_metrics)
    if abs(total - 1) > 1e-10:
        raise ValueError("Mixture weights must sum to one")
    m = {key: sum(w * x[key] for w, x in weighted_metrics) for key in RATE_KEYS}
    m["qualified_share_of_hires"] = m["true_hire"] / m["hire_rate"] if m["hire_rate"] else None
    m["initially_qualified_recognition"] = (
        m["initially_qualified_hired_mass"] / (1 - p.prior_deficient)
        if p.prior_deficient < 1 else None)
    return m


def learning_cutoff(p):
    denominator = (p.learn_gain - p.verify_gain) * (
        p.hire_value * (p.test_tpr - p.test_fpr) + p.skill_value)
    return None if denominator <= 0 else (p.learn_cost - p.verify_cost) / denominator
