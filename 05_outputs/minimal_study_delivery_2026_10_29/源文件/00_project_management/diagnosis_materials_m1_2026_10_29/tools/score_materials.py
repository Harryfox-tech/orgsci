"""Score transparent research fixtures. Never infers latent ability or reads a model truth state."""
from collections import Counter
from decimal import Decimal, InvalidOperation

DOMAINS = {
    "record_handling": ("duplicate_ids", "duplicate_policy"),
    "scope": ("eligible_ids", "excluded_ids"),
    "missingness": ("incomplete_eligible_ids", "missing_treatment"),
    "aggregation": ("known_subtotal", "full_total_status"),
}


def number(value):
    if value is None or isinstance(value, bool):
        return None
    if str(value).strip() == "":
        return None
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Expected a finite nonnegative task value")
    return result


def derive_key(task):
    rows = [tuple(row) for row in task["rows"]]
    if any(len(row) != 4 for row in rows):
        raise ValueError("Expected exactly four columns")
    counts = Counter(rows)
    unique = list(dict.fromkeys(rows))
    by_id = {}
    for row in unique:
        if row[0] in by_id and by_id[row[0]] != row:
            raise ValueError("Conflicting records for one ID need an additional rule")
        by_id[row[0]] = row
    duplicates = sorted({row[0] for row, count in counts.items() if count > 1})
    eligible = [row for row in unique if row[1] == task["target_status"]]
    excluded = [row[0] for row in unique if row[1] != task["target_status"]]
    incomplete, subtotal = [], Decimal(0)
    for row in eligible:
        qty, unit = number(row[2]), number(row[3])
        if qty is None or unit is None:
            incomplete.append(row[0])
        else:
            subtotal += qty * unit
    return {
        "duplicate_ids": duplicates, "duplicate_policy": "keep_one_identical",
        "eligible_ids": sorted(row[0] for row in eligible), "excluded_ids": sorted(excluded),
        "incomplete_eligible_ids": sorted(incomplete),
        "missing_treatment": "unknown_do_not_impute" if incomplete else "not_applicable",
        "known_subtotal": str(subtotal),
        "full_total_status": "undetermined" if incomplete else "complete",
    }


def equal_ids(value, expected):
    return (isinstance(value, list) and all(isinstance(x, str) for x in value)
            and len(value) == len(set(value)) and set(value) == set(expected))


def grade(answer, key):
    """Only explicit answers and the public task key determine a score."""
    if not isinstance(answer, dict):
        raise ValueError("Answer must be an object")
    checks = {}
    for field, expected in key.items():
        actual = answer.get(field)
        if field.endswith("_ids"):
            checks[field] = equal_ids(actual, expected)
        elif field == "known_subtotal":
            try:
                checks[field] = number(actual) is not None and number(actual) == number(expected)
            except (InvalidOperation, ValueError, TypeError):
                checks[field] = False
        else:
            checks[field] = actual == expected
    domain_scores = {name: sum(int(checks[field]) for field in fields)
                     for name, fields in DOMAINS.items()}
    score = sum(domain_scores.values())
    submitted = [field for field in key if field in answer and answer[field] is not None]
    response_status = "empty" if not submitted else ("complete" if len(submitted) == len(key) else "partial")
    criterion = (response_status == "complete" and score >= 6
                 and domain_scores["missingness"] == 2 and domain_scores["aggregation"] == 2)
    return {"checks": checks, "domain_scores": domain_scores, "score": score,
            "max_score": 8, "response_status": response_status, "submitted_fields": submitted,
            "illustrative_criterion_met": criterion}


def feedback(result, personalized):
    """No forced route, capability probability, confidence estimate, or true type."""
    if not personalized:
        return [
            "本任务检查重复记录、纳入范围、缺失信息与汇总表述四个环节。",
            "这些环节的检查结果不直接等于你的完整能力。",
            "学习可以帮助你练习；验证可以为资料卡增加本次认可的记录。",
            "请结合自己的判断，在当前开放的行动中自主选择。",
        ]
    names = {"record_handling": "重复记录", "scope": "纳入范围",
             "missingness": "缺失信息", "aggregation": "汇总表述"}
    lines = []
    for name, score in result["domain_scores"].items():
        count = sum(field in result["submitted_fields"] for field in DOMAINS[name])
        if count < 2:
            lines.append(f"{names[name]}：记录未完整作答，当前不足以作完整判断；不推断真实能力。")
        else:
            lines.append(f"{names[name]}：本次符合{score}/2项评分规则；不代表潜在能力已确定。")
    return lines


def profile_record(action, verification_result=None):
    """A private diagnostic score and the independent post-test never grant a certificate."""
    if action not in {"L", "V", "N"}:
        raise ValueError("Unknown action")
    if action == "N" or verification_result is None:
        return {"recognized_pass": False, "verified_domains": []}
    domains = [d for d, score in verification_result["domain_scores"].items() if score == 2]
    return {"recognized_pass": verification_result["illustrative_criterion_met"],
            "verified_domains": domains}

