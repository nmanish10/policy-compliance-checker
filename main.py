from agent import ComplianceAgent

if __name__ == "__main__":
    sample_policy = """
    This policy includes data protection and access control.
    It also explains retention and incident reporting.
    """

    agent = ComplianceAgent()
    output = agent.run(sample_policy, seed=123)

    print("\nRUN ID:", output["run_id"])
    print("\nMETRICS:", output["metrics"])
    print("\nSTATE TRANSITIONS:")
    for entry in output["state_history"]:
        print(entry)