from typing import TypedDict, Dict, Any, List, Optional
from pydantic import BaseModel, Field

# ==============================================================================
# LangGraph Design Mastery: "State, Verbs, and Decisions"
# Step 1: Define the State (The "Noun")
# Concept: The State is the "File Folder" that gets passed around the office.
# ==============================================================================

class EnterpriseState(TypedDict):
    """
    The Ultimate "Enterprise State" Schema (Must-Have Fields)
    To survive production, your State object needs more than just messages.
    It needs fields for Control, Safety, and Auditability.
    """
    
    # --- 1. CORE INPUT/OUTPUT ---
    # The raw user intent or document payload
    candidate_id: str
    resume_text: str
    job_description: str
    # The final, sanitized response read for downstream consumers
    anonymized_resume: str
    evaluation: Dict[str, Any]
    routing_decision: str
    
    # --- 3. CONTROL FLOW & LOOP SAFETY ---
    # Tracks how many times a specific node has retried (prevent infinite loops)
    retry_count: int 
    # Tracks total steps to kill "Zombie Threads"
    global_step_count: int 
    # The path of nodes visited (e.g., ["IngestionGuard", "Redactor", "Evaluator"])
    execution_trace: List[str] 
    
    # --- 4. SEMANTIC CIRCUIT BREAKERS ---
    # List of hashes of previous 'Thoughts'. Used to detect "Logical Loops"
    thought_hashes: List[str] 
    # Score from the Validator/Critic agent. If < 0.8, loop back.
    quality_score: float 
    
    # --- 5. AUDIT & COMPLIANCE ---
    # "Evidence Enforcement Rule": Logic fails if this is empty.
    citations: List[str] 
    # Flags if PII was detected/redacted during execution
    security_flags: List[str] 
    # For HITL: If true, the graph pauses and serializes to Postgres
    needs_human_review: bool 
    
    status: str
