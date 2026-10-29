"""Check authored task arithmetic and the meaning of illustrative records; no study run."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from score_materials import derive_key, feedback, grade, profile_record

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]


def main():
    data = json.loads((HERE / "task_data.json").read_text(encoding="utf-8"))
    manual = json.loads((HERE / "answer_key.json").read_text(encoding="utf-8"))
    tasks = {task["id"]: task for task in data["tasks"]}
    passed = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    gold = {}
    for name, task in tasks.items():
        key = derive_key(task)
        check(name + "_authored_key_matches_independent_arithmetic", key == manual[name])
        gold[name] = grade(manual[name], key)
        check(name + "_correct_answer_gets_eight", gold[name]["score"] == 8)
    bad = deepcopy(manual["A"])
    bad["known_subtotal"], bad["full_total_status"] = "750", "complete"
    bad["missing_treatment"] = "fill_zero"
    incorrect = grade(bad, manual["A"])
    check("double_count_and_zero_imputation_do_not_pass", not incorrect["illustrative_criterion_met"])
    check("empty_answer_is_zero", grade({}, manual["A"])["score"] == 0)
    check("empty_answer_is_marked_missing", grade({}, manual["A"])["response_status"] == "empty")
    check("missing_feedback_does_not_infer_low_ability",
          all("不足以" in line for line in feedback(grade({}, manual["A"]), True)))
    partial = deepcopy(manual["A"])
    partial.pop("duplicate_ids")
    check("partial_verification_not_a_pass", not grade(partial, manual["A"])["illustrative_criterion_met"])
    bad = deepcopy(manual["A"])
    bad["known_subtotal"] = True
    check("boolean_is_not_numeric_answer", not grade(bad, manual["A"])["checks"]["known_subtotal"])
    bad["known_subtotal"] = "NaN"
    check("nonfinite_is_not_numeric_answer", not grade(bad, manual["A"])["checks"]["known_subtotal"])
    bad = deepcopy(manual["A"])
    bad["eligible_ids"].append(bad["eligible_ids"][0])
    check("duplicate_answer_ids_rejected", not grade(bad, manual["A"])["checks"]["eligible_ids"])
    zero = deepcopy(tasks["A"])
    zero["rows"][-1][2] = "0"
    zkey = derive_key(zero)
    check("zero_is_not_missing", zkey["incomplete_eligible_ids"] == [] and zkey["full_total_status"] == "complete")
    conflict = deepcopy(tasks["A"])
    conflict["rows"].append(["S101", "paid", "9", "120"])
    conflict_rejected = False
    try:
        derive_key(conflict)
    except ValueError:
        conflict_rejected = True
    check("conflicting_duplicate_requires_rule", conflict_rejected)
    check("L_and_V_have_same_recognition_rule", profile_record("L", gold["B"]) == profile_record("V", gold["B"]))
    check("private_or_posttest_result_not_automatically_recognized", not profile_record("N", gold["C"])["recognized_pass"])
    check("missing_verification_not_a_pass", not profile_record("V")["recognized_pass"])
    check("both_feedback_forms_four_lines", len(feedback(gold["A"], True)) == len(feedback(gold["A"], False)) == 4)
    examples = {
        "correct_A": {"answer": manual["A"], "scoring": gold["A"], "feedback": feedback(gold["A"], True)},
        "incorrect_A": {"scoring": incorrect, "feedback": feedback(incorrect, True)},
        "generic": feedback(gold["A"], False),
        "no_response": feedback(grade({}, manual["A"]), True),
        "record_L_pass": profile_record("L", gold["B"]),
        "record_V_pass": profile_record("V", gold["B"]),
        "record_N_even_if_posttest_high": profile_record("N", gold["C"]),
    }
    out = HERE / "checks"
    out.mkdir(exist_ok=True)
    (out / "scoring_examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hashes = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [HERE / "task_data.json", HERE / "answer_key.json",
                        HERE / "tools/score_materials.py", HERE / "tools/check_materials.py"]}
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "passed_checks": passed,
              "check_count": len(passed), "status": "passed", "hashes": hashes,
              "participants": 0, "random_draws": 0, "new_model_parameter_cells": 0,
              "unit": "Authored task fixtures, not participants or experimental observations",
              "limitations": ["Difficulty, reliability, learning effects and external validity untested.",
                             "Eight checks are scoring items, not four validated latent traits.",
                             "No diagnostic accuracy or theoretical novelty established."]}
    (out / "materials_checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks_passed": len(passed), "gold_subtotals": {k: v["known_subtotal"] for k,v in manual.items()},
                      "participants": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()

