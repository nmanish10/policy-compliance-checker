from agent import ComplianceAgent

# --------------------------------------------------
# TEST SCENARIOS
# --------------------------------------------------

SCENARIOS = [
    {
        "name": "Fully Compliant",
        "policy": """
        Data Protection:
        All user data is encrypted using AES-256.

        Access Control:
        Role-based access control is enforced.

        Retention:
        Data is retained for 7 years.

        Incident Reporting:
        Incidents must be reported within 24 hours.
        """,
        "expected_critical": 0
    },
    {
        "name": "Missing Retention",
        "policy": """
        Data Protection:
        All user data is encrypted.

        Access Control:
        Role-based access control is enforced.

        Incident Reporting:
        Incidents must be reported within 24 hours.
        """,
        "expected_critical": 1
    },
    {
        "name": "Only Mentions",
        "policy": "We follow data protection and access control standards.",
        "expected_critical": 4
    },
    {
        "name": "Empty Policy",
        "policy": "",
        "expected_critical": 4
    },
    {
        "name": "Only Data Protection",
        "policy": """
        Data Protection:
        Data is encrypted.
        """,
        "expected_critical": 3
    },
    {
        "name": "Only Access Control",
        "policy": """
        Access Control:
        Role-based access control.
        """,
        "expected_critical": 3
    },
    {
        "name": "Only Retention",
        "policy": """
        Retention:
        Data retained for 5 years.
        """,
        "expected_critical": 3
    },
    {
        "name": "Only Incident Reporting",
        "policy": """
        Incident Reporting:
        Report within 24 hours.
        """,
        "expected_critical": 3
    },
    {
        "name": "Partial Structured",
        "policy": """
        Data Protection:
        Encrypted.

        Retention:
        3 years.
        """,
        "expected_critical": 2
    },
    {
        "name": "Verbose Policy",
        "policy": """
        This organization ensures comprehensive data protection mechanisms
        including encryption, strict access control policies, defined retention
        timelines of 7 years, and mandatory incident reporting procedures
        within 24 hours of detection.
        """,
        "expected_critical": 0
    }
]

# --------------------------------------------------
# NAIVE BASELINE
# --------------------------------------------------

def naive_baseline(policy_text: str):

    keywords = [
        "data protection",
        "access control",
        "retention",
        "incident reporting"
    ]

    policy_lower = policy_text.lower()

    found = sum(1 for k in keywords if k in policy_lower)

    score = round((found / len(keywords)) * 100, 2)

    return score


# --------------------------------------------------
# RUN EVALUATION
# --------------------------------------------------

def run_evaluation():

    agent = ComplianceAgent()

    results = []

    total_critical_rules = 0
    detected_critical_rules = 0

    for scenario in SCENARIOS:

        output = agent.run(scenario["policy"], seed=42)

        baseline_score = naive_baseline(scenario["policy"])

        violations = output["result"]["violations"]

        # count critical violations
        detected_critical = sum(
            1 for v in violations
            if v["severity"] == "critical"
        )

        expected_critical = scenario["expected_critical"]

        detected_critical_rules += min(detected_critical, expected_critical)
        total_critical_rules += expected_critical

        results.append({
            "scenario": scenario["name"],
            "structured_score": output["metrics"]["compliance_score"],
            "baseline_score": baseline_score,
            "violations": output["metrics"]["violation_count"],
            "expected_critical": expected_critical,
            "detected_critical": detected_critical
        })

    # --------------------------------------------------
    # CRITICAL DETECTION RATE
    # --------------------------------------------------

    if total_critical_rules == 0:
        critical_detection_rate = 0
    else:
        critical_detection_rate = round(
            (detected_critical_rules / total_critical_rules) * 100,
            2
        )

    return {
        "results": results,
        "critical_detection_rate": critical_detection_rate
    }


# --------------------------------------------------
# CLI TEST
# --------------------------------------------------

if __name__ == "__main__":

    evaluation = run_evaluation()

    results = evaluation["results"]
    critical_rate = evaluation["critical_detection_rate"]

    print("\nScenario Results\n")

    for r in results:
        print(r)

    print("\nCritical Detection Rate:", critical_rate, "%")