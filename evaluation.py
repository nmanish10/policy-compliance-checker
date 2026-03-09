from agent import ComplianceAgent

# --------------------------------------------------
# TEST SCENARIOS
# --------------------------------------------------

SCENARIOS = [

{
"name": "Fully Compliant",
"policy": """
Data Protection:
All sensitive and personal data is encrypted using AES-256 encryption both at rest and in transit.

Access Control:
Role-based access control is enforced and all privileged access requires multi-factor authentication.

Retention:
Customer and operational data is retained for a period of 7 years in accordance with regulatory requirements.

Incident Reporting:
Security incidents must be reported to the security team within 24 hours and documented in the incident management system.
""",
"expected_critical": 0
},

{
"name": "Missing Retention",
"policy": """
Data Protection:
All user data is encrypted using industry standard encryption.

Access Control:
Role-based access control is implemented across all systems.

Incident Reporting:
All incidents must be reported within 24 hours.
""",
"expected_critical": 0
},

{
"name": "Policy Mentions Only",
"policy": "We follow data protection and access control standards across the organization.",
"expected_critical": 3
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
All personal and sensitive data is encrypted both at rest and during transmission.
""",
"expected_critical": 3
},

{
"name": "Only Access Control",
"policy": """
Access Control:
Access to internal systems is controlled through role-based permissions and authentication mechanisms.
""",
"expected_critical": 3
},

{
"name": "Only Retention",
"policy": """
Retention:
Operational and customer data is retained for five years before secure deletion.
""",
"expected_critical": 3
},

{
"name": "Only Incident Reporting",
"policy": """
Incident Reporting:
Security incidents must be documented and reported to the security operations team within 24 hours.
""",
"expected_critical": 3
},

{
"name": "Partial Structured",
"policy": """
Data Protection:
All sensitive data is encrypted.

Retention:
Customer data is retained for 3 years.
""",
"expected_critical": 2
},

{
"name": "Verbose Policy",
"policy": """
The organization maintains strict security and governance controls. All personal and operational data is encrypted,
access to internal systems is restricted using role-based permissions,
data retention is defined for a minimum of seven years,
and all security incidents must be reported to the security team within 24 hours.
""",
"expected_critical": 0
},

{
"name": "Ambiguous Policy",
"policy": """
Security and privacy are important to the organization.
Appropriate measures are taken to ensure data protection.
""",
"expected_critical": 3
}, 

{
"name": "Misleading Statement",
"policy": """
The company takes security very seriously and follows best practices to ensure data safety.
""",
"expected_critical": 4
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