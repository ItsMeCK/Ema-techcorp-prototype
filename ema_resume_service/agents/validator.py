from typing import Dict, Any, Literal
from .base import BaseAgent
from ema_resume_service.core.config import logger
import hashlib

class ValidationAgent(BaseAgent):
    """
    Role: The Critic (Quality Assurance).
    Function: Checks constraints (e.g., "Are citations present?"). Source of the Loop Back.
    """
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get('candidate_id', 'UNKNOWN')
        logger.info(f"[{candidate_id}] Executing Validation Protocol (The Critic)...")
        
        eval_data = state.get("evaluation", {})
        citations = eval_data.get("citations", [])
        score = eval_data.get("score", 0)
        
        # Increment retry counter
        current_retries = state.get("retry_count", 0) + 1
        
        # 1. Semantic Circuit Breaker: Enforce Evidence Rule
        if score < 40 and not citations:
             logger.warning(f"[{candidate_id}] Validation Failed: Rejection missing citations.")
             # If we've exhausted retries on this, it's a semantic loop.
             if current_retries > 3:
                  return {"quality_score": 0.5, "retry_count": current_retries, "status": "SEMANTIC_LOOP_DETECTED"}
             return {"quality_score": 0.5, "retry_count": current_retries, "status": "VALIDATION_FAILED"}
             
        # 2. Semantic Circuit Breaker: Diversity Sampling (Prevent Logical Loops)
        reasoning = eval_data.get("reasoning", "")
        current_hash = hashlib.md5(reasoning.encode('utf-8')).hexdigest()
        
        thought_hashes = state.get("thought_hashes", [])
        
        if current_hash in thought_hashes:
            logger.error(f"[{candidate_id}] SEMANTIC CIRCUIT BREAKER TRIPPED: LLM is repeating identical thoughts. Hash Collision: {current_hash}")
            return {
                "quality_score": 0.1, # Extremely low to force edge trip
                "retry_count": current_retries, 
                "status": "SEMANTIC_LOOP_DETECTED",
                "needs_human_review": True
            }
            
        thought_hashes.append(current_hash)
             
        # Passed Constraints
        return {
            "quality_score": 1.0, 
            "retry_count": current_retries, 
            "status": "VALIDATION_PASSED",
            "thought_hashes": thought_hashes
        }

def route_validation_output(state: Dict[str, Any]) -> Literal["evaluator_node", "human_interrupt_node", "routing_node"]:
    """
    The Conditional Edge Logic (Managerial Decision)
    Determines if we loop back, escalate to human, or proceed to final routing.
    """
    retries = state.get("retry_count", 0)
    quality = state.get("quality_score", 1.0)
    
    # 1. Semantic Circuit Breaker (Identical Thoughts / Diversity Sampling issue)
    if quality <= 0.2:
        logger.error(f"[{state.get('candidate_id')}] Routing to HumanInterrupt. Semantic integrity compromised.")
        return "human_interrupt_node"
        
    # 2. Safety Circuit Breaker (Kill Zombie Threads)
    if retries > 3:
        logger.error(f"[{state.get('candidate_id')}] Circuit Breaker Triggered: Escaping Infinite Loop via Retry Exhaustion.")
        return "human_interrupt_node"
        
    # 3. Validation Gate (Loop Back for correction)
    if quality < 0.8:
        return "evaluator_node"
        
    # 4. Happy Path
    return "routing_node"
