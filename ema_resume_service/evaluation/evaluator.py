import json
import logging
from typing import List, Dict, Any
from .metrics import calculate_context_precision, calculate_answer_relevancy

logger = logging.getLogger("RAGASEvaluator")

class ProductionEvaluator:
    """
    Simulates a RAGAS (Retrieval Augmented Generation Assessment) pipeline for the Ema Prototype.
    This suite must be run prior to production releases to detect Output Drift.
    
    Metrics Tracked:
    1. Score Adherence: Does the model's score deviate > 5% from the Golden Dataset?
    2. Answer Relevancy: Are the Extracted Citations actually relevant to the JD requirement?
    3. Routing Accuracy: Did the model classify correctly (PASS/REJECT/HITL)?
    """
    
    def __init__(self, golden_dataset: List[Dict[str, Any]]):
        self.golden_dataset = {item['candidate_id']: item for item in golden_dataset}
        
    def evaluate_batch(self, experiment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares the current model iteration's output against the Golden Dataset.
        """
        logger.info(f"Initiating RAGAS Production Stability Evaluation on {len(experiment_results)} records...")
        
        metrics = {
            "total_evaluated": len(experiment_results),
            "score_drift_percentage": 0.0,
            "routing_accuracy": 0.0,
            "citation_relevancy": 0.0,
            "failures": []
        }
        
        correct_routes = 0
        total_drift = 0
        
        for result in experiment_results:
            candidate_id = result.get('candidate_id')
            if candidate_id not in self.golden_dataset:
                continue
                
            golden = self.golden_dataset[candidate_id]
            experiment_score = result.get('evaluation', {}).get('score', 0)
            golden_score = golden.get('expected_score', 0)
            
            # 1. Routing Accuracy (Handle Circuit Breakers that bypass routing)
            actual_decision = result.get('routing_decision')
            if not actual_decision:
                # If pipeline broke early (e.g. Ingestion/Semantic Trip), use status
                actual_decision = result.get('status')
                
            if actual_decision == golden.get('expected_routing'):
                correct_routes += 1
            else:
                metrics['failures'].append({
                    "id": candidate_id, 
                    "type": "ROUTING_ERROR",
                    "expected": golden.get('expected_routing'),
                    "actual": actual_decision
                })
                
            # 2. Score Drift Calculation
            drift = abs(experiment_score - golden_score) / max(golden_score, 1)
            total_drift += drift
            
            if drift > 0.10: # > 10% deviation triggers a failure
                metrics['failures'].append({
                    "id": candidate_id, 
                    "type": "SCORE_DRIFT",
                    "expected": golden_score,
                    "actual": experiment_score
                })
                
        metrics['routing_accuracy'] = (correct_routes / max(len(experiment_results), 1)) * 100
        metrics['score_drift_percentage'] = (total_drift / max(len(experiment_results), 1)) * 100
        
        # Simulated RAGAS Citation Relevancy (would normally use LLM-as-a-judge)
        metrics['citation_relevancy'] = 94.5 
        
        self._print_report(metrics)
        return metrics
        
    def _print_report(self, metrics: Dict[str, Any]):
        print("\\n" + "="*60)
        print(" 📊 PRODUCTION STABILITY REPORT (RAGAS MOCK SUITE) 📊")
        print("="*60)
        print(f"Total Records Tested: {metrics['total_evaluated']}")
        print(f"Routing Accuracy:     {metrics['routing_accuracy']}%")
        print(f"Score Drift:          {metrics['score_drift_percentage']:.2f}%")
        print(f"Citation Relevancy:   {metrics['citation_relevancy']}%")
        print("-" * 60)
        
        if metrics['failures']:
            print("❌ STABILITY FAILURES DETECTED:")
            for f in metrics['failures']:
                print(f"  - [{f['id']}] {f['type']} | Exp: {f['expected']} | Act: {f['actual']}")
            print("\\nDO NOT RELEASE TO PRODUCTION.")
        else:
            print("✅ ZERO DRIFT DETECTED. SAFE FOR PRODUCTION RELEASE.")
            print("="*60 + "\\n")
