import json

MIN_POLICY_WORDS = 5


def load_rules():
    with open("config/rules.json", "r") as f:
       data = json.load(f)
       return data["rules"], data["version"]


def validate_structured_policy(parsed_policy: dict):
    rules, rule_version = load_rules()

    violations = []
    total_weight = sum(rule["weight"] for rule in rules)
    deducted_weight = 0

    severity_count = {"critical": 0, "minor": 0}

    for rule in rules:

        value = parsed_policy.get(rule["field"], "")

        # Enforce meaningful policy definition
        if not value or len(value.strip().split()) < MIN_POLICY_WORDS:

            violations.append({
                "rule_id": rule["id"],
                "field": rule["field"],
                "description": rule["description"],
                "severity": rule["severity"],
                "weight": rule["weight"]
            })

            deducted_weight += rule["weight"]
            severity_count[rule["severity"]] += 1

    score = round(((total_weight - deducted_weight) / total_weight) * 100, 2)

    if score >= 80:
        risk = "Low"
    elif score >= 50:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "rule_version": rule_version,
        "total_rules": len(rules),
        "violations": violations,
        "violation_count": len(violations),
        "severity_breakdown": severity_count,
        "compliance_score": score,
        "risk_level": risk
    }