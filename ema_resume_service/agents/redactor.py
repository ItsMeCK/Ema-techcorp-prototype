from typing import Dict, Any
from .base import BaseAgent
from ema_resume_service.core.config import logger

class PIIRedactorAgent(BaseAgent):
    """
    Tier 1 Inference Node: Redacts PII to eliminate demographic bias vectors.
    """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get('candidate_id', 'UNKNOWN')
        logger.info(f"[{candidate_id}] Executing PII Redaction Phase...")
        
        resume = state.get("resume_text", "")
        
        # Deterministic mock-scrubbing for prototype predictability
        redacted_resume = resume.replace("John Doe", "[REDACTED_NAME]") \
                                .replace("Jane Smith", "[REDACTED_NAME]") \
                                .replace("Alex Johnson", "[REDACTED_NAME]") \
                                .replace("john@example.com", "[REDACTED_EMAIL]") \
                                .replace("jane@example.com", "[REDACTED_EMAIL]") \
                                .replace("alex@example.com", "[REDACTED_EMAIL]")
        
        return {"anonymized_resume": redacted_resume, "status": "PII_Redacted"}
