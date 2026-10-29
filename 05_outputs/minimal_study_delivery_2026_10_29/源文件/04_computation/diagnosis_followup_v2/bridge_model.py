"""Auditable extension of v1, without changing any v1 file.

Adds a candidate-private signal and potential productivity gains above the
qualification threshold. The candidate may value those gains. No oracle enters
choice; hiring still uses the same minimum-qualification test as v1.
"""
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "minimal_diagnosis_2026_10_28"
v1_manifest = json.loads((V1 / "results/run_manifest.json").read_text(encoding="utf-8"))
v1_source = V1 / "model.py"
if hashlib.sha256(v1_source.read_bytes()).hexdigest() != v1_manifest["sources_sha256"]["model.py"]:
    raise RuntimeError("v1 source has changed; do not silently use a different baseline")
spec = importlib.util.spec_from_file_location("_locked_diagnosis_v1", v1_source)
v1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v1
spec.loader.exec_module(v1)


@dataclass(frozen=True)
class Params:
    base: v1.Params = v1.Params()
    low_output: float = 1.0
    high_output: float = 2.0
    high_learn_gain: float = 0.0
    high_verify_gain: float = 0.0
    productivity_value: float = 0.0

    def __post_init__(self):
        values = (self.low_output, self.high_output, self.high_learn_gain,
                  self.high_verify_gain, self.productivity_value)
        if not all(isfinite(x) for x in values):
            raise ValueError("Nonfinite productivity parameter")
        if self.high_output <= self.low_output or min(values) < 0:
            raise ValueError("Invalid productivity levels or gains")
        if self.base.skill_value != 0:
            raise ValueError("Avoid double counting: use productivity_value, not v1.skill_value")

    @property
    def output_gap(self):
        return self.high_output - self.low_output


def likelihood(signal, k, quality):
    return quality if (signal == "S") == (k == 0) else 1 - quality


def posterior(h, z, private_quality, diagnostic_quality, p):
    a = (p.base.prior_deficient * likelihood(h, 0, private_quality)
         * likelihood(z, 0, diagnostic_quality))
    b = ((1 - p.base.prior_deficient) * likelihood(h, 1, private_quality)
         * likelihood(z, 1, diagnostic_quality))
    return None if a + b == 0 else a / (a + b)


def high_type_gain(action, p):
    return {"N": 0.0, "L": p.high_learn_gain, "V": p.high_verify_gain}[action]


def expected_productivity_gain(action, deficient_probability, p):
    return (deficient_probability * v1.action_gain(action, p.base) * p.output_gap
            + (1 - deficient_probability) * high_type_gain(action, p))


def value(action, belief, access, p):
    return (v1.action_value(action, belief, access, p.base)
            + p.productivity_value * expected_productivity_gain(action, belief, p))


def choose_action(belief, access, p):
    if belief is None or not 0 <= belief <= 1:
        raise ValueError("Choice must receive a valid posterior, never a true type")
    feasible = ("N", "V", "L") if access else ("N", "L")
    vals = {a: value(a, belief, access, p) for a in feasible}
    maximum = max(vals.values())
    return next(a for a in feasible if vals[a] >= maximum - 1e-12), vals


METRICS = ("mass", "learn_rate", "verify_rate", "no_action_rate", "skill_gain",
           "final_qualified", "hire_rate", "true_hire", "false_hire", "action_cost",
           "utility", "potential_productivity_gain", "final_potential_productivity",
           "hired_output_per_initial_candidate", "learning_initially_qualified",
           "action_change_from_no_diagnostic")


def enumerate_group(p, q, r, access_probability, keep_branches=False):
    if not (.5 <= q <= 1 and .5 <= r <= 1 and 0 <= access_probability <= 1):
        raise ValueError("Invalid signal quality or access probability")
    totals = {key: 0.0 for key in METRICS}
    branches = []
    for access, pa in ((False, 1 - access_probability), (True, access_probability)):
        for k0, pk in ((0, p.base.prior_deficient), (1, 1 - p.base.prior_deficient)):
            for h in ("S", "E"):
                for z in ("S", "E"):
                    mass0 = pa * pk * likelihood(h, k0, r) * likelihood(z, k0, q)
                    if mass0 == 0:
                        continue
                    belief = posterior(h, z, r, q, p)
                    action, vals = choose_action(belief, access, p)
                    without_diagnostic = choose_action(posterior(h, z, r, .5, p), access, p)[0]
                    chance_qualified = 1 if k0 else v1.action_gain(action, p.base)
                    for k1, chance in ((0, 1 - chance_qualified), (1, chance_qualified)):
                        growth = ((k1 - k0) * p.output_gap if not k0
                                  else high_type_gain(action, p))
                        output = p.low_output + k0 * p.output_gap + growth
                        hire_chance = v1.hire_probability(action, k1, access, p.base)
                        for hire, ph in ((0, 1 - hire_chance), (1, hire_chance)):
                            m = mass0 * chance * ph
                            if m == 0:
                                continue
                            totals["mass"] += m
                            totals[{"N": "no_action_rate", "V": "verify_rate", "L": "learn_rate"}[action]] += m
                            totals["skill_gain"] += m * (k1 - k0)
                            totals["final_qualified"] += m * k1
                            totals["hire_rate"] += m * hire
                            totals["true_hire"] += m * hire * k1
                            totals["false_hire"] += m * hire * (1 - k1)
                            totals["action_cost"] += m * v1.action_cost(action, p.base)
                            totals["learning_initially_qualified"] += m * k0 * (action == "L")
                            totals["action_change_from_no_diagnostic"] += m * (action != without_diagnostic)
                            totals["potential_productivity_gain"] += m * growth
                            totals["final_potential_productivity"] += m * output
                            totals["hired_output_per_initial_candidate"] += m * output * hire
                            if keep_branches:
                                branches.append({"access": access, "initial_skill": k0,
                                                 "private_signal": h, "diagnostic_signal": z,
                                                 "posterior_deficient": belief, "action": action,
                                                 "decision_value": vals[action], "final_skill": k1,
                                                 "productivity_gain": growth, "hired": hire, "mass": m})
    totals["utility"] = (p.base.hire_value * totals["hire_rate"]
                         + p.productivity_value * totals["potential_productivity_gain"]
                         - totals["action_cost"])
    return totals, branches


def mix(weighted):
    if abs(sum(w for w, _ in weighted) - 1) > 1e-10:
        raise ValueError("Weights must sum to one")
    return {key: sum(w * m[key] for w, m in weighted) for key in METRICS}
