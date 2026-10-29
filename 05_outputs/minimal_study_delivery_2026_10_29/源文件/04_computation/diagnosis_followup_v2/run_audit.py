import csv
import hashlib
import itertools
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from bridge_model import Params, choose_action, enumerate_group, mix, posterior, v1

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1 = HERE.parent / "minimal_diagnosis_2026_10_28"
OUT = HERE / "results"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected():
    old = json.loads((V1 / "results/protected_files_sha256.json").read_text(encoding="utf-8"))["before"]
    for name, value in old.items():
        if digest(ROOT / name) != value:
            raise AssertionError(f"Legacy archive changed: {name}")
    for path in V1.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            old[path.relative_to(ROOT).as_posix()] = digest(path)
    return old


def dump_csv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(exist_ok=True)
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    config_hash = digest(HERE / "config.json")
    assert digest(V1 / "config.json") == cfg["base_config_sha256"]
    before = protected()
    tests = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_bridge"],
                           cwd=HERE, capture_output=True, text=True)
    (OUT / "test_output.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    if tests.returncode:
        raise RuntimeError("Bridge verification failed")
    base_params = v1.Params(**json.loads((V1 / "config.json").read_text(encoding="utf-8"))["base"])
    states = {}
    for q, r, b, mu in itertools.product(cfg["diagnostic_qualities"], cfg["private_information_qualities"],
                                        cfg["high_type_learning_productivity_gains"],
                                        cfg["private_values_of_productivity_gain"]):
        p = Params(base=base_params, low_output=cfg["base_productivity_below_threshold"],
                   high_output=cfg["base_productivity_above_threshold"], high_learn_gain=b,
                   high_verify_gain=cfg["high_type_verification_productivity_gain"], productivity_value=mu)
        states[q, r, b, mu] = {a: enumerate_group(p, q, r, a)[0] for a in (0, 1)}
    rows, contrasts, branches = [], [], []
    formula_cases, max_formula_error = 0, 0.0
    for (q, r, b, mu), values in states.items():
        p = Params(base=base_params, low_output=cfg["base_productivity_below_threshold"],
                   high_output=cfg["base_productivity_above_threshold"], high_learn_gain=b,
                   high_verify_gain=cfg["high_type_verification_productivity_gain"], productivity_value=mu)
        if r == .5:
            pattern = all(choose_action(posterior(h, z, r, q, p), False, p)[0] == "L"
                          and choose_action(posterior(h, z, r, q, p), True, p)[0] == ("L" if z == "S" else "V")
                          for h, z in itertools.product(("S", "E"), repeat=2))
            if pattern:
                formula_cases += 1
                prediction = -.5 * (base_params.learn_gain * (1 - q) * p.output_gap + q * b)
                actual = values[1]["potential_productivity_gain"] - values[0]["potential_productivity_gain"]
                max_formula_error = max(max_formula_error, abs(prediction - actual))
        for label, access in cfg["access_regimes"].items():
            groups = {g: mix([(a, values[1]), (1 - a, values[0])]) for g, a in access.items()}
            groups["overall"] = mix([(cfg["group_shares"][g], groups[g]) for g in cfg["group_shares"]])
            baseline_values = states[.5, r, b, mu]
            total_access = sum(cfg["group_shares"][g] * access[g] for g in access)
            baseline = mix([(total_access, baseline_values[1]), (1 - total_access, baseline_values[0])])
            prefix = {"quality": q, "private_quality": r, "high_learning_output_gain": b,
                      "private_productivity_value": mu, "regime": label}
            for g, m in groups.items():
                rows.append({**prefix, "group": g, **m})
            m = groups["overall"]
            contrasts.append({**prefix,
                              **{"delta_" + k: m[k] - baseline[k] for k in
                                 ("utility", "skill_gain", "potential_productivity_gain", "hire_rate", "true_hire")},
                              "action_change_from_no_diagnostic": m["action_change_from_no_diagnostic"]})
        if q == .8 and r in (.5, .9, 1) and b in (0, .3) and mu == 0:
            _, detail = enumerate_group(p, q, r, .5, keep_branches=True)
            branches.extend({"quality": q, "private_quality": r, "high_learning_output_gain": b, **row} for row in detail)
    dump_csv("all_cases.csv", rows)
    dump_csv("diagnostic_contrasts.csv", contrasts)
    dump_csv("illustrative_branches.csv", branches)

    q_checks = r_checks = q_bad = r_bad = option_bad = 0
    for r, b, mu, a in itertools.product(cfg["private_information_qualities"],
            cfg["high_type_learning_productivity_gains"], cfg["private_values_of_productivity_gain"], (0, 1)):
        values = [states[q, r, b, mu][a]["utility"] for q in cfg["diagnostic_qualities"]]
        q_checks += len(values) - 1
        q_bad += sum(y < x - 1e-10 for x, y in zip(values, values[1:]))
    for q, b, mu, a in itertools.product(cfg["diagnostic_qualities"],
            cfg["high_type_learning_productivity_gains"], cfg["private_values_of_productivity_gain"], (0, 1)):
        values = [states[q, r, b, mu][a]["utility"] for r in cfg["private_information_qualities"]]
        r_checks += len(values) - 1
        r_bad += sum(y < x - 1e-10 for x, y in zip(values, values[1:]))
    option_bad = sum(v[1]["utility"] < v[0]["utility"] - 1e-10 for v in states.values())
    mass_error = max(abs(m["mass"] - 1) for state in states.values() for m in state.values())
    perfect_private_error = max(abs(m[key] - states[.5, 1.0, b, mu][a][key])
                                for (q, r, b, mu), state in states.items() if r == 1
                                for a, m in state.items() for key in m)
    after = protected()
    checks = {"tests_passed": True, "parameter_cells": len(states), "reported_group_cells": len(rows),
              "ai_information_comparisons": q_checks, "ai_information_violations": q_bad,
              "private_information_comparisons": r_checks, "private_information_violations": r_bad,
              "option_value_violations": option_bad, "formula_cases": formula_cases,
              "max_formula_absolute_error": max_formula_error,
              "max_probability_mass_error": mass_error,
              "max_diagnostic_effect_with_perfect_private_information": perfect_private_error,
              "v1_and_legacy_files_unchanged": before == after,
              "protected_files_count": len(before), "config_unchanged": digest(HERE / "config.json") == config_hash}
    assert q_bad == r_bad == option_bad == 0
    assert checks["v1_and_legacy_files_unchanged"] and checks["config_unchanged"]
    assert max_formula_error < 1e-10
    assert mass_error < 1e-10 and perfect_private_error < 1e-10
    (OUT / "checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    (OUT / "protected_files_sha256.json").write_text(
        json.dumps({"before": before, "after": after}, indent=2) + "\n", encoding="utf-8")
    manifest = {"version": cfg["version"], "run_time_utc": datetime.now(timezone.utc).isoformat(),
                "python_version": platform.python_version(), "config_sha256": config_hash,
                "unit": cfg["unit"], "seed_policy": cfg["seed_policy"],
                "command": "python -X utf8 04_computation/diagnosis_followup_v2/run_audit.py",
                "source_sha256": {n: digest(HERE / n) for n in
                                  ("config.json", "bridge_model.py", "test_bridge.py", "run_audit.py")},
                "output_sha256": {p.name: digest(p) for p in OUT.iterdir() if p.is_file() and p.name != "manifest.json"}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()
