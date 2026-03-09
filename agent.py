import time
import os
import requests
import json
from dotenv import load_dotenv

from state_machine import State, StateMachine
from tools.compliance_engine import validate_structured_policy
from logger import generate_run_id, log_run, get_timestamp
from models import PolicySections

load_dotenv()

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise Exception("MISTRAL_API_KEY not set in environment variables")

# =========================
# MISTRAL CONFIG
# =========================

MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-large-latest")
MISTRAL_API_URL = os.environ.get(
    "MISTRAL_API_URL",
    "https://api.mistral.ai/v1/chat/completions"
)

_DEFAULT_MODEL_CHAIN = [MISTRAL_MODEL, "open-mistral-nemo", "mistral-small-latest"]

MODEL_CHAIN = []
for m in _DEFAULT_MODEL_CHAIN:
    if m and m not in MODEL_CHAIN:
        MODEL_CHAIN.append(m)


# =========================
# AGENT
# =========================

class ComplianceAgent:

    # Tool allowlist (Guardrail)
    ALLOWED_TOOLS = ["validate_structured_policy"]

    def __init__(self, max_steps: int = 10):
        self.state_machine = StateMachine()
        self.max_steps = max_steps
        self.step_count = 0

    # -------------------------
    # STEP GUARDRAIL
    # -------------------------
    def _increment_step(self):
        self.step_count += 1
        if self.step_count > self.max_steps:
            raise Exception("Max step limit exceeded")

    # -------------------------
    # LLM PARSING (STRICT JSON)
    # -------------------------
    def parse_with_llm(self, policy_text: str):

        prompt = f"""
You are a compliance policy extraction engine.

Your task is to extract structured compliance sections from a policy document.

IMPORTANT RULES:

1. Only extract a section if the policy explicitly defines a real rule,
requirement, or procedure.

2. If the text only mentions a concept without defining a policy
(example: "this policy includes access control" or "mentions encryption"),
you MUST return null for that section.

3. NEVER invent, expand, rewrite, or improve policy text.

4. Only copy sentences that appear in the policy.

5. If the policy does not contain a full sentence describing the rule,
return null.

6. Extracted text should be copied verbatim from the policy when possible.

Return ONLY valid JSON with these keys:

- data_protection
- access_control
- retention
- incident_reporting

If a section is missing or insufficiently defined, return null.

Example output:

{{
 "data_protection": "All sensitive data must be encrypted using AES-256.",
 "access_control": null,
 "retention": "Customer data must be retained for 7 years before deletion.",
 "incident_reporting": null
}}

Policy:
{policy_text}
"""

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }

        for model in MODEL_CHAIN:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0,  # deterministic
                }

                response = requests.post(
                    MISTRAL_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30,
                )

                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]

                    try:
                        parsed_json = json.loads(content)
                        validated = PolicySections(**parsed_json)
                        return validated.model_dump()
                    except json.JSONDecodeError:
                        continue  # Try fallback model

            except requests.exceptions.Timeout:
                continue  # Try fallback model on timeout
            except Exception:
                continue  # Try fallback model on other errors

        raise Exception("All Mistral models failed or returned invalid JSON")
    
    def generate_suggestions(self, violations):

        if not violations:
            return []

        violation_text = "\n".join([v["description"] for v in violations])

        prompt = f"""
You are a compliance advisor.

The following policy violations were detected:

{violation_text}

Your task:
Provide EXACTLY ONE improvement suggestion for EACH violation.

Requirements:
- Each suggestion must directly address the specific missing policy rule.
- Each suggestion should be written as a clear, detailed paragraph.
- The suggestion should explain what needs to be implemented and what it should include.
- Do NOT break suggestions into multiple bullet points.
- Do NOT generate multiple suggestions for the same violation.

Output Rules:
- Return ONLY a valid JSON array of strings.
- The number of suggestions MUST equal the number of violations.

Example:
[
"Define a comprehensive data retention policy that specifies retention periods for different categories of data, outlines secure storage practices, and includes clear procedures for archival and deletion in accordance with applicable regulatory requirements.",
"Implement role-based access control with clearly defined permission levels, enforce strong authentication mechanisms such as multi-factor authentication, and establish regular access reviews to ensure the principle of least privilege."
]
"""

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }

        for model in MODEL_CHAIN:

            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                }

                response = requests.post(
                    MISTRAL_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:

                    content = response.json()["choices"][0]["message"]["content"]

                    content = content.strip()

                    # remove markdown if model adds it
                    if content.startswith("```"):
                        content = content.replace("```json", "").replace("```", "").strip()

                    parsed = json.loads(content)

                    if isinstance(parsed, list):
                        return parsed
    
            except Exception:
                continue

        return []

    # -------------------------
    # MAIN RUN
    # -------------------------
    def run(self, policy_text: str, seed: int = 42):

        self.state_machine = StateMachine()
        run_id = generate_run_id()
        start_time = time.time()
        self.step_count = 0

        try:
            # STATE 1
            self._increment_step()
            self.state_machine.transition("policy_uploaded", State.POLICY_RECEIVED)

            # STATE 2
            self._increment_step()
            self.state_machine.transition("parse_policy", State.PARSING_POLICY)

            llm_output = self.parse_with_llm(policy_text)

            # STATE 3
            self._increment_step()
            self.state_machine.transition("start_validation", State.VALIDATING)

            tool_name = "validate_structured_policy"

            # Tool allowlist guardrail
            if tool_name not in self.ALLOWED_TOOLS:
                raise Exception(f"Tool {tool_name} not allowed")

            result = validate_structured_policy(llm_output)
            suggestions = self.generate_suggestions(result["violations"])

            # STATE 4
            self._increment_step()
            self.state_machine.transition("generate_report", State.REPORT_GENERATED)

            self._increment_step()
            self.state_machine.transition("finish", State.COMPLETED)

            end_time = time.time()
            execution_time_ms = round((end_time - start_time) * 1000, 2)

            run_data = {
                "run_id": run_id,
                "seed": seed,
                "timestamp": get_timestamp(),
                "state_history": self.state_machine.get_history(),
                "llm_output": llm_output,
                "suggestions": suggestions,
                "metrics": {
                    "execution_time_ms": execution_time_ms,
                    "violation_count": result["violation_count"],
                    "compliance_score": result["compliance_score"]
                },
                "result": result
            }

            log_run(run_id, run_data)
            return run_data

        except Exception as e:
            self.state_machine.transition("error_occurred", State.ERROR)

            error_data = {
                "run_id": run_id,
                "timestamp": get_timestamp(),
                "error": str(e),
                "state_history": self.state_machine.get_history()
            }

            log_run(run_id, error_data)
            return error_data