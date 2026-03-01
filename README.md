# Ema AI: TechCorp Resume Matching Prototype

**Author:** TechCorp AI Engineering

## 1. Executive Summary
This repository contains the production-ready prototype for the **Ema "Universal AI Employee"**, systematically designed to replace TechCorp's legacy resume screening vendor. 

The primary business objectives center on ethical AI adoption, stability, transparency, and operational efficiency:
- **Zero Bias Inference:** Removal of demographic and Partially Identifiable Information (PII) vector data prior to evaluation.
- **Enforced Explainability:** Eradication of "Black Box" reasoning; the agent is programmatically forced to extract exact quotes (Evidence Citations) to justify any scoring.
- **Intelligent Triage (HITL):** Reduction of false rejections by routing borderline candidates to a Human-in-the-Loop (HITL) workflow.
- **Guaranteed Output Stability:** Integration of a strict RAGAS evaluation pipeline to measure output drift and ensure mathematical routing accuracy before production release.

## 2. Advanced Architectural Paradigm
This system is engineered using **LangGraph** to construct a deterministic, enterprise-grade state machine. It explicitly moves away from fragile prompt-chaining paradigms towards a heavily fortified agentic workflow.

### VP-Level Engineering Principles Implemented
- **Enterprise State Schema (`TypedDict`):** The data payload is tracked through a strict `EnterpriseState` object. It governs core I/O, control flow (`retry_count`, `thought_hashes`), and safety (`security_flags`).
- **Semantic Circuit Breakers (Self-Healing):** To prevent catastrophic LLM hallucination loops, the `ValidationAgent` (The Critic) utilizes `hashlib` diversity sampling. If the LLM repeats identical reasoning (hash collision) without resolving citation constraints, the system trips a `SEMANTIC_LOOP_DETECTED` state, bypasses automated routing, and safely checkpoints for human review.
- **Synchronous & Asynchronous Checkpointing:** Utilizing the `HumanInterruptAgent`, the LangGraph topology supports pausing execution at exact state milestones. In a production environment, this integrates with Postgres `checkpointer` to persist state across distributed clusters while waiting for asynchronous human inputs (e.g., Slack interactions).
- **Dependency Injection & Mocks:** Core agent logic accepts overridable LLM instances, allowing the repository to run an automated, structured mock process for rapid, deterministic testing without requiring API keys.

## 3. Logical Node Workflow (Orchestrator Topology)
1. `ingestion_guard_node`: Validates payload schema integrity (Kill Switch).
2. `pii_redactor_node`: Deterministic pre-processing that scrubs bias vectors.
3. `evaluator_node`: The core LLM reasoning engine comparing the anonymized payload against the Job Description.
4. `validator_node`: The Critic. Enforces citation evidence rules and detects semantic reasoning loops. (Loops back to `evaluator_node` or trips the Semantic Breaker).
5. `routing_node`: Dynamic edge mapping based on scoring thresholds (Score > 85 = Auto-Shortlist, Score < 40 = Auto-Reject, 40-84 = Route to HITL).
6. `human_interrupt_node`: A safe checkpointing node used for HITL routing and capturing Semantic Trip failures.

---

## 4. Production Stability (RAGAS Evaluator)
To satisfy TechCorp compliance requirements and prevent vendor failure recurrence, this repository ships with a dedicated `evaluation` module reflecting best practices in Retrieval Augmented Generation Assessment (RAGAS).

- **The Golden Dataset:** `main.py` utilizes a baseline validation matrix comprising 10 Resumes and 3 Job Descriptions, each strictly mapped to expected scores and correct internal routing vectors.
- **Zero Drift Tolerance:** After processing the LangGraph execution block, the `ProductionEvaluator` class parses the final graph output to compute `Routing Accuracy` and `Score Drift`. A release is blocked if any deviations or unhandled circuit trips occur.

---

## 5. Setup & Installation Prerequisites
**Requirements:** `Python 3.9+`, `OpenAI API Key` (Optional for code review; intelligent mock fallback deterministic mode included).

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/ema-techcorp-prototype.git
cd ema-techcorp-prototype

# 2. Setup Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 3. Environment Variables
export OPENAI_API_KEY="sk-your-api-key-here"
```

## 6. Execution Prototype
The architecture simulates an Azure Service Bus polling architecture using Python's `ThreadPoolExecutor` for concurrent ingestion. 

To execute the compliance suite and generate the Traceability Report, run:
```bash
python main.py
```
*Note: Without a valid `OPENAI_API_KEY`, the script falls back to an intelligent deterministic simulation designed specifically to trigger and test the self-healing and semantic circuit breaker topologies automatically.*
