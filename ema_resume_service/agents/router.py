from typing import Dict, Any, Literal
from .base import BaseAgent
from ema_resume_service.core.config import logger

class RoutingAgent(BaseAgent):
    """
    Business Logic Tier: Applies deterministic organizational thresholds to AI outputs.
    """
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get('candidate_id', 'UNKNOWN')
        logger.info(f"[{candidate_id}] Applying Organizational Routing Protocol...")
        
        score = state.get("evaluation", {}).get("score", 0)
        
        if state.get("status") == "SEMANTIC_LOOP_DETECTED":
            decision = "SEMANTIC_LOOP_DETECTED"
        elif score >= 85:
            decision = "Auto-Shortlist 🟢"
        elif score <= 40:
            decision = "Auto-Reject 🔴"
        else:
            decision = "Route to HITL 🟡"
            
        return {"routing_decision": decision, "status": decision}

class HumanInterruptAgent(BaseAgent):
    """
    Stub for asynchronous system pauses.
    In production, LangGraph's checkpointer (Postgres) persists state here.
    """
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get('candidate_id', 'UNKNOWN')
        logger.info(f"[{candidate_id}] Checkpointing State. Awaiting Human Recruiter Review.")
        
        # When bypassing the router directly (like Semantic Loop breakers), we ensure
        # the routing_decision state variable carries the status forward for RAGAS output evaluation.
        decision = state.get("routing_decision", "")
        
        if state.get("status") == "SEMANTIC_LOOP_DETECTED":
             decision = "SEMANTIC_LOOP_DETECTED"
             logger.warning(f"[{candidate_id}] Human routing flagged specifically for SEMANTIC_LOOP_DETECTED.")
        elif not decision:
             decision = "Route to HITL 🟡"
             
        return {"routing_decision": decision, "status": "Awaiting_Human_Review"}

def route_decision(state: Dict[str, Any]) -> Literal["human_interrupt_node", "__end__"]:
    """Conditional logic edge router."""
    if "Route to HITL" in state.get("routing_decision", ""):
        return "human_interrupt_node"
    return "__end__"
