import os
import sys

# Ensure Python can resolve the local package structure
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ema_resume_service.core.config import logger, settings
from ema_resume_service.graph.builder import EmaWorkflowEngine
from ema_resume_service.graph.traceability import TraceabilityReportGenerator
from ema_resume_service.evaluation.evaluator import ProductionEvaluator
import concurrent.futures
import time
import random

def load_text_file(filepath: str) -> str:
    with open(filepath, 'r') as f:
        return f.read().strip()

def run_prototype_simulation():
    """
    Executes a simulated batch of applicants through the compiled LangGraph logic
    by ingesting dynamic profiles from the data folder.
    Generates a Traceability Audit Report to satisfy TechCorp compliance requirements.
    """
    print("\\n" + "="*80)
    print(" 🚀 Ema AI: TechCorp Enterprise Agentic Capability API (File Ingestion Mode)")
    print("="*80 + "\\n")
    
    if not settings.openai_api_key or settings.openai_api_key == "sk-demo-key-replace-me":
        logger.warning(
            "OPENAI_API_KEY environment variable not detected. "
            "Proceeding with intelligent deterministic mock strategy for demonstration."
        )

    # Compile the engine
    graph = EmaWorkflowEngine.build_graph()

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    jd_dir = os.path.join(base_dir, "data", "job_descriptions")
    resume_dir = os.path.join(base_dir, "data", "resumes")

    # Load resources
    try:
        jds = {
            "JD_1": load_text_file(os.path.join(jd_dir, "jd_1_senior_ai_engineer.txt")),
            "JD_2": load_text_file(os.path.join(jd_dir, "jd_2_frontend_developer.txt")),
            "JD_3": load_text_file(os.path.join(jd_dir, "jd_3_devops_engineer.txt"))
        }
    except FileNotFoundError as e:
        logger.error(f"Missing Data Directories: {e}")
        return

    # Evaluation Matrix mapping Resume to the JD they applied for
    # In a real environment, this operates as our Golden Dataset for RAGAS evaluation.
    test_matrix = [
        {"id": "RES-01 (Sarah)", "file": "res_01_sarah_connor.txt", "jd_key": "JD_1", "expected": "PASS", "expected_score": 95, "expected_routing": "Auto-Shortlist 🟢"},
        {"id": "RES-02 (Bob)", "file": "res_02_bob_wilson.txt", "jd_key": "JD_1", "expected": "REJECT", "expected_score": 20, "expected_routing": "SEMANTIC_LOOP_DETECTED"}, # Now expects failing Semantic Hash Breaker
        {"id": "RES-03 (Alice)", "file": "res_03_alice_chen.txt", "jd_key": "JD_1", "expected": "HITL", "expected_score": 65, "expected_routing": "Route to HITL 🟡"},
        {"id": "RES-04 (David)", "file": "res_04_david_park.txt", "jd_key": "JD_2", "expected": "PASS", "expected_score": 90, "expected_routing": "Auto-Shortlist 🟢"},
        {"id": "RES-05 (Carl)", "file": "res_05_carl_jenkins.txt", "jd_key": "JD_2", "expected": "REJECT", "expected_score": 15, "expected_routing": "Auto-Reject 🔴"},
        {"id": "RES-06 (Emily)", "file": "res_06_emily_davis.txt", "jd_key": "JD_2", "expected": "HITL", "expected_score": 75, "expected_routing": "Route to HITL 🟡"},
        {"id": "RES-07 (Frank)", "file": "res_07_frank_miller.txt", "jd_key": "JD_3", "expected": "PASS", "expected_score": 92, "expected_routing": "Auto-Shortlist 🟢"},
        {"id": "RES-08 (Gina)", "file": "res_08_gina_torres.txt", "jd_key": "JD_3", "expected": "PASS", "expected_score": 88, "expected_routing": "Auto-Shortlist 🟢"},
        {"id": "RES-09 (Henry)", "file": "res_09_henry_clark.txt", "jd_key": "JD_3", "expected": "HITL", "expected_score": 55, "expected_routing": "Route to HITL 🟡"},
        {"id": "RES-10 (Ian)", "file": "res_10_ian_white.txt", "jd_key": "JD_1", "expected": "HITL", "expected_score": 68, "expected_routing": "Route to HITL 🟡"},
    ]

    print(f"Loaded {len(test_matrix)} Applicant Profiles against {len(jds)} Job Descriptions.\\n")
    
    # Track final states for the traceability report
    final_states = []
    
    def process_candidate(profile):
        """Worker function for ThreadPoolExecutor"""
        # Simulate network latency of pulling from Azure Service Bus
        time.sleep(random.uniform(0.1, 0.5))
        
        logger.info(f"[ASB Queue] Dequeued Profile: {profile['id']}")
        
        resume_text = load_text_file(os.path.join(resume_dir, profile["file"]))
        jd_text = jds[profile["jd_key"]]
        
        initial_state = {
            "candidate_id": profile["id"],
            "resume_text": resume_text,
            "job_description": jd_text,
            "anonymized_resume": "",
            "evaluation": {},
            "routing_decision": "",
            "retry_count": 0,
            "global_step_count": 0,
            "execution_trace": [],
            "thought_hashes": [],
            "quality_score": 0.0,
            "citations": [],
            "security_flags": [],
            "needs_human_review": False,
            "status": "Initialized"
        }
        
        final_state_for_candidate = initial_state.copy()
        
        try:
            for step in graph.stream(initial_state):
                for node_name, state in step.items():
                    final_state_for_candidate.update(state)
                    # If any node explicitly triggered SEMANTIC_LOOP_DETECTED, hard-lock the routing decision
                    if state.get("status") == "SEMANTIC_LOOP_DETECTED":
                        final_state_for_candidate["routing_decision"] = "SEMANTIC_LOOP_DETECTED"
        except Exception as e:
             logger.error(f"[{profile['id']}] Graph execution failed: {e}")
             
        return final_state_for_candidate

    print("================================================================================")
    print(" ⚡ Initiating Concurrent Processing (Mock Azure Service Bus Ingestion) ⚡")
    print("================================================================================\\n")

    # Simulate Enterprise Scaling (ThreadPoolExecutor)
    # Using max_workers=5 to demonstrate concurrent processing without overwhelming local stdout
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks to the thread pool
        future_to_profile = {executor.submit(process_candidate, profile): profile for profile in test_matrix}
        
        for future in concurrent.futures.as_completed(future_to_profile):
            profile = future_to_profile[future]
            try:
                result_state = future.result()
                final_states.append(result_state)
                
                # Print completion summary for this thread
                score = result_state.get('evaluation', {}).get('score', 'N/A')
                verdict = result_state.get('routing_decision', 'ERROR')
                print(f"✅ Completed: {profile['id']} | JD: {profile['jd_key']} | Score: {score} | Verdict: {verdict}")
                
            except Exception as exc:
                print(f"❌ {profile['id']} generated an exception: {exc}")

    # Generate the Traceability Audit Report
    print("\\n" + "="*80)
    print(" Generating Traceability & Compliance Audit Report...")
    TraceabilityReportGenerator.generate_report(final_states)
    
    # -------------------------------------------------------------
    # Final Production Release Gate: RAGAS Drift Evaluation
    # -------------------------------------------------------------
    golden_proxy = [{"candidate_id": t["id"], "expected_score": t["expected_score"], "expected_routing": t["expected_routing"]} for t in test_matrix]
    evaluator = ProductionEvaluator(golden_dataset=golden_proxy)
    evaluator.evaluate_batch(final_states)
    print("="*80 + "\\n")

if __name__ == '__main__':
    run_prototype_simulation()
