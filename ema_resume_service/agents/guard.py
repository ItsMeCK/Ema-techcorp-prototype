from typing import Dict, Any, Literal
from .base import BaseAgent
from ema_resume_service.core.config import logger

class IngestionGuardAgent(BaseAgent):
    """
    Role: The Bouncer. Placement: The very first node.
    Function: Validates payload integrity and checks for Indirect Prompt Injection.
    """
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get('candidate_id', 'UNKNOWN')
        logger.info(f"[{candidate_id}] Executing IngestionGuard: Validating Payload Integrity...")
        
        resume = state.get("resume_text", "")
        
        # Security/Circuit Breaker Simulation
        if "Ignore instructions" in resume or len(resume) < 50:
            logger.warning(f"[{candidate_id}] Security Alert: Malicious intent or malformed payload detected.")
            return {
                "status": "REJECTED_AT_INGESTION",
                "security_flags": ["MALFORMED_OR_INJECTION"]
            }
            
        return {"status": "INGESTION_PASSED", "security_flags": []}

def check_ingestion_security(state: Dict[str, Any]) -> Literal["pii_redactor_node", "__end__"]:
    """Conditional Edge: Kills the graph if the Bouncer rejects the payload."""
    if state.get("status") == "REJECTED_AT_INGESTION":
        return "__end__"
    return "pii_redactor_node"
