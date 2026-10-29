"""Reproduce finite-state mechanism checks and all numerical report tables.

Run from anywhere. Standard-library only; never imports the legacy ABM.
The grid is an illustrative design space, not a sample of workers or markets.
"""
import csv
import hashlib
import itertools
import json
import platform
import subprocess
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from model import Params, enumerate_group, learning_cutoff, mix_metrics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "results"
TOL = 1e-10


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def protected_hashes():
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "01_manuscript", "04_computation/replication_archive"],
        cwd=ROOT).decode("utf-8").split("\0")
    return {n: sha256(ROOT / n) for n in names if n and (ROOT / n).is_file()}


def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_regime(p, q, regime, shares):
    groups = {g: enumerate_group(p, q, access)[0] for g, access in regime.items()}
    groups["overall"] = mix_metrics([(shares[g], groups[g]) for g in shares], p)
    return groups


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    config_path = HERE / "config.json"
    config_digest = sha256(config_path)
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    p = Params(**cfg["base"])
    before = protected_hashes()
    test = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_model"],
                          cwd=HERE, capture_output=True, text=True)
    (OUT / "test_output.txt").write_text(test.stdout + test.stderr, encoding="utf-8")
    if test.returncode:
        raise RuntimeError("Unit / analytic checks failed; see results/test_output.txt")
    shares = cfg["group_shares"]

    base_rows, decisions = [], []
    for q in cfg["qualities"]:
        for label, access in cfg["access_regimes"].items():
            for group, m in run_regime(p, q, access, shares).items():
                base_rows.append({"quality": q, "regime": label, "group": group, **m})
        for available in (False, True):
            _, rows = enumerate_group(p, q, int(available))
            for r in rows:
                decisions.append({"quality": q, **r})
    write_csv("base_cases.csv", base_rows)
    write_csv("base_branches.csv", decisions)

    boundary_rows = []
    for label, override in cfg["boundaries"].items():
        bp = replace(p, **override)
        for q in cfg["qualities"]:
            for access_label in ("unequal", "equal_same_slots"):
                groups = run_regime(bp, q, cfg["access_regimes"][access_label], shares)
                for group, m in groups.items():
                    boundary_rows.append({"boundary": label, "quality": q,
                                          "regime": access_label, "group": group, **m})
    write_csv("boundary_cases.csv", boundary_rows)

    hetero_rows = []
    costs = cfg["heterogeneous_learning_costs"]
    for q in cfg["qualities"]:
        for label in ("unequal", "equal_same_slots"):
            segments = [run_regime(replace(p, learn_cost=c), q,
                        cfg["access_regimes"][label], shares) for c in costs]
            for group in (*shares, "overall"):
                m = mix_metrics([(1 / len(costs), s[group]) for s in segments], p)
                hetero_rows.append({"quality": q, "regime": label, "group": group, **m})
    write_csv("heterogeneous_costs.csv", hetero_rows)

    grid_rows = []
    voi_violations = option_violations = 0
    voi_comparisons = formula_cases = 0
    max_formula_error = max_same_slots_error = 0.0
    grid = cfg["grid"]
    for prior, gain, cl, cv in itertools.product(grid["prior_deficient"], grid["learn_gain"],
                                               grid["learn_cost"], grid["verify_cost"]):
        gp = replace(p, prior_deficient=prior, learn_gain=gain, learn_cost=cl, verify_cost=cv)
        previous = {}
        for q in grid["quality"]:
            yes = enumerate_group(gp, q, 1)[0]
            no = enumerate_group(gp, q, 0)[0]
            for access, m in ((0, no), (1, yes)):
                if access in previous:
                    voi_comparisons += 1
                    voi_violations += m["utility"] < previous[access] - TOL
                previous[access] = m["utility"]
            option_violations += yes["utility"] < no["utility"] - TOL
            # Independent mixture identities; group shares and total slots fixed.
            high = enumerate_group(gp, q, .75)[0]
            low = enumerate_group(gp, q, .25)[0]
            equal = enumerate_group(gp, q, .5)[0]
            for key in ("utility", "skill_gain", "hire_rate", "true_hire", "false_hire"):
                max_same_slots_error = max(max_same_slots_error,
                    abs((high[key] + low[key]) / 2 - equal[key]))
            cutoff = learning_cutoff(gp)
            interior = (prior == .5 and cv < cl
                        and cl < min(gp.hire_value * gp.test_tpr,
                                     gp.hire_value * (gp.test_fpr + gain * (gp.test_tpr - gp.test_fpr)))
                        and 0 < cutoff < 1 and q > max(cutoff, 1 - cutoff) + TOL)
            du = yes["utility"] - no["utility"]
            dg = yes["skill_gain"] - no["skill_gain"]
            dt = yes["true_hire"] - no["true_hire"]
            if interior:
                formula_cases += 1
                predicted = (-.5 * gain * (1 - q),
                             -.5 * gain * gp.test_tpr * (1 - q),
                             .5 * (cl - cv - gp.hire_value * gain
                                   * (gp.test_tpr - gp.test_fpr) * (1 - q)))
                max_formula_error = max(max_formula_error,
                    *(abs(a - b) for a, b in zip((dg, dt, du), predicted)))
            grid_rows.append({"prior_deficient": prior, "learn_gain": gain,
                              "learn_cost": cl, "verify_cost": cv, "quality": q,
                              "cutoff": cutoff, "interior_formula_applies": interior,
                              "utility_with_access": yes["utility"], "utility_without_access": no["utility"],
                              "delta_utility": du, "delta_skill_gain": dg, "delta_true_hire": dt,
                              "delta_hire_rate": yes["hire_rate"] - no["hire_rate"],
                              "delta_false_hire": yes["false_hire"] - no["false_hire"],
                              "private_value_up_skill_gain_down": du > TOL and dg < -TOL})
    write_csv("parameter_grid.csv", grid_rows)

    after = protected_hashes()
    checks = {
        "unit_tests_passed": test.returncode == 0,
        "value_of_information_comparisons": voi_comparisons,
        "value_of_information_violations": int(voi_violations),
        "additional_option_comparisons": len(grid_rows),
        "additional_option_violations": int(option_violations),
        "closed_form_cases": formula_cases,
        "max_closed_form_absolute_error": max_formula_error,
        "max_same_slot_aggregate_absolute_error": max_same_slots_error,
        "protected_files_count": len(before),
        "protected_files_unchanged": before == after,
        "config_unchanged_during_run": config_digest == sha256(config_path),
        "tolerance": TOL,
    }
    write_json("checks.json", checks)
    write_json("protected_files_sha256.json", {"before": before, "after": after})
    assert not voi_violations and not option_violations
    assert max_formula_error < TOL and max_same_slots_error < TOL
    assert before == after and checks["config_unchanged_during_run"]
    manifest = {
        "design_version": cfg["design_version"],
        "run_time_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
        "config_sha256": config_digest, "base_parameters": asdict(p),
        "unit": "Exact expected probability mass per initial low-score candidate; not sampled people",
        "seed_policy": cfg["seed_policy"],
        "method": "Finite probability enumeration with floating arithmetic, no Monte Carlo",
        "p_values_or_confidence_intervals": "Not applicable: no empirical sample or Monte Carlo error",
        "sources_sha256": {name: sha256(HERE / name) for name in
                           ("model.py", "run_study.py", "test_model.py", "config.json")},
    }

    sample = [r for r in base_rows if r["regime"] == "unequal" and r["group"] == "overall"]
    lines = ["# 最小研究：自动生成的数值摘要", "", "结果属于未校准模型，不是现实估计或原创性证明。", "",
             "| 诊断精度 | 个人期望效用 | 能力新增比例 | 真正合格且录用 | 总录用比例 | 行动成本 |",
             "|---|---|---|---|---|---|"]
    for r in sample:
        lines.append(f"| {r['quality']:.2f} | {r['utility']:.6f} | {r['skill_gain']:.6f} | "
                     f"{r['true_hire']:.6f} | {r['hire_rate']:.6f} | {r['action_cost']:.6f} |")
    tradeoffs = sum(r["private_value_up_skill_gain_down"] for r in grid_rows)
    lines += ["", f"扫描 {len(grid_rows)} 个参数单元，其中 {tradeoffs} 个单元满足“可用验证提高个人效用、同时降低新增能力”。",
              "这个计数仅描述所选网格，不代表现实中的发生比例。", "",
              f"解析式适用单元：{formula_cases}；最大误差：{max_formula_error:.3g}。",
              f"信息价值检查：{voi_comparisons} 次；违反次数：{voi_violations}。",
              f"验证选项检查：{len(grid_rows)} 次；违反次数：{option_violations}。",
              f"锁定稿件与旧复制包 {len(before)} 个已跟踪文件：运行前后哈希一致。", "",
              "完整设定、条件推导、反例解释与文献边界见项目管理目录的同日研究包。"]
    (OUT / "数值摘要.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest["output_sha256"] = {f.name: sha256(f) for f in sorted(OUT.iterdir())
                                 if f.is_file() and f.name != "run_manifest.json"}
    write_json("run_manifest.json", manifest)
    print(json.dumps({"output_directory": str(OUT), "grid_cells": len(grid_rows),
                      "tradeoff_cells": tradeoffs, "checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
