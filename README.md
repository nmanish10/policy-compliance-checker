# 🛡️ Policy Compliance Intelligence

An AI-powered **policy compliance analysis system** that evaluates organizational policies against a predefined compliance checklist.  
The system combines **LLM-based policy extraction** with a **deterministic rule-based validation engine** to identify compliance violations and generate actionable improvement suggestions.

The application provides an interactive dashboard, benchmarking analytics, run replay capabilities, and exportable compliance reports.

---

# 📊 System Overview

The system analyzes policy documents and determines whether they satisfy key compliance requirements.

It performs the following pipeline:

1. Accept a policy as input
2. Extract structured compliance sections using an LLM
3. Validate extracted sections using a rule-based compliance engine
4. Detect violations and compute a compliance score
5. Generate improvement suggestions
6. Display results in a dashboard
7. Export a professional compliance report

---

# 🏗️ System Architecture

![Architecture](architecture.png)

The architecture consists of the following components:

**Streamlit Dashboard**
- User interface for policy analysis
- Displays metrics, violations, and suggestions

**Compliance Agent**
- Orchestrates the workflow
- Manages state transitions
- Invokes tools and LLM parsing

**LLM Policy Parser**
- Extracts structured policy sections from unstructured text

**Compliance Engine**
- Validates extracted sections against rule definitions
- Calculates compliance score and risk level

**Rules Configuration**
- JSON-based compliance rules
- Includes severity levels and rule weights

**Run Logs / Observability**
- Stores execution traces and results
- Enables replay and system observability

**Replay Runs Viewer**
- Allows inspection of previous executions
- Reconstructs system decisions and state transitions

**PDF Report Generator**
- Produces exportable compliance reports

---

# 🔄 State Machine

![State Machine](state_machine.png)

The system follows an explicit state machine during execution.

IDLE → POLICY_RECEIVED → PARSING_POLICY → VALIDATING → REPORT_GENERATED → COMPLETED

Each state transition is logged and visible in the dashboard.

---

# 🚀 Features

## Policy Analysis
- LLM-based extraction of policy sections
- Rule-based compliance validation
- Violation detection
- Weighted compliance scoring
- Risk level classification

## Dashboard
- Compliance score visualization
- Violation severity distribution
- Policy improvement suggestions
- Execution metrics
- State transition history

## Benchmark Evaluation
- Evaluation across **10 policy scenarios**
- Comparison with naive keyword baseline
- Critical detection rate metric
- Structured vs baseline score analysis

## Observability
- Run IDs for every execution
- Execution timestamps
- State transition logs
- LLM output visibility

## Replay System
- Browse previous runs
- Reconstruct execution results
- Inspect system decisions

## Reporting
- Exportable **PDF compliance reports**
- Includes violations, risk level, and suggestions

---

# 🧠 Compliance Rules

The validation engine uses a configurable rule set defined in:

config/rules.json

Each rule specifies:

- Compliance field
- Severity level
- Weight
- Description

Example rule:

```json
{
  "id": "rule_data_protection",
  "field": "data_protection",
  "description": "Data protection section must be defined",
  "severity": "critical",
  "weight": 30
}
```

---

# 📈 Evaluation Framework

The system includes an evaluation harness with 10 benchmark scenarios, including:

- Fully compliant policy

- Missing retention policy

- Only keyword mentions

- Empty policy

- Partial compliance


Metrics reported:

- Structured compliance score

- Baseline keyword score

- Violation counts

- Critical detection rate


This demonstrates the effectiveness of structured validation compared to naive keyword detection.


---

# 🛠️ Tech Stack

**Backend**

- Python


**AI Integration**

- Mistral LLM API


**Frontend**

- Streamlit


**Visualization**

- Plotly

- Matplotlib


**Data Handling**

- Pandas


**PDF Reporting**

- ReportLab


**Schema Validation**

- Pydantic



---

# 📂 Project Structure

```
policy-compliance-checker/
│
├── app.py
├── agent.py
├── state_machine.py
├── evaluation.py
├── report_generator.py
├── models.py
│
├── tools/
│   └── compliance_engine.py
│
├── config/
│   └── rules.json
│
├── runs/
│   └── run logs
│
├── architecture.png
├── state_machine.png
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository:
```
git clone <repository-url>
cd policy-compliance-checker
```
Create a virtual environment:
```
python -m venv venv
```
Activate the environment:

Windows:
```
venv\Scripts\activate
```
Install dependencies:
```
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a .env file:
```
MISTRAL_API_KEY=your_api_key
MISTRAL_MODEL=mistral-large-latest
MISTRAL_API_URL=https://api.mistral.ai/v1/chat/completions
```

---

# ▶️ Running the Application

Start the dashboard:
```
streamlit run app.py
```

The dashboard will open in the browser.


---

# 🧪 Running Evaluation

To run the benchmark evaluation:
```
python evaluation.py
```
This will execute all test scenarios and display evaluation results.


---

# 📄 Exporting Reports

After analyzing a policy in the dashboard, you can download a PDF compliance report that includes:

- Compliance score

- Risk classification

- Detected violations

- Improvement suggestions

- Rule version metadata



---

# 🧩 Guardrails

The system implements several safeguards:

- Tool allowlist enforcement

- Maximum execution steps

- API timeouts

- Schema validation for LLM output

- Deterministic rule validation


These ensure reliable and safe agent execution.


---

# 🎯 Demo Workflow

Typical demo flow:

1. Enter a policy into the dashboard


2. Run the compliance analysis


3. View violations and compliance score


4. Inspect state transitions


5. Review improvement suggestions


6. Download the compliance report


7. Compare results using the benchmark analytics




---

# 📜 License

This project is intended for educational and research purposes.

---

