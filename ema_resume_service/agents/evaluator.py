from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .base import BaseAgent
from ema_resume_service.core.config import logger, settings
from ema_resume_service.schemas.evaluation import EvaluationSchema

class LLMEvaluatorAgent(BaseAgent):
    """
    Tier 2 Inference: Core reasoning engine enforcing strict output validation via Pydantic.
    Demonstrates Dependency Injection by optionally accepting a pre-configured LLM instance.
    """

    def __init__(self, llm_override=None):
        self.api_key = settings.openai_api_key
        self.model_name = settings.evaluation_model
        
        # Determine if we should use the mock (if no API key or default demo key).
        self.use_mock = not self.api_key or self.api_key == "sk-demo-key-replace-me"

        if llm_override:
            self.llm = llm_override
        elif not self.use_mock:
            self.llm = ChatOpenAI(
                model=self.model_name, 
                temperature=0.0,
                api_key=self.api_key
            ).with_structured_output(EvaluationSchema)
        else:
            self.llm = None

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        candidate_id = state.get('candidate_id', 'UNKNOWN')
        logger.info(f"[{candidate_id}] Executing Core Evaluation Protocol...")
        
        jd = state.get("job_description", "")
        anon_resume = state.get("anonymized_resume", "")

        if self.llm and not self.use_mock:
            try:
                prompt = (
                    "You are an expert technical recruiter analyzing an applicant."
                    f"\\n\\nTarget Job Description:\\n{jd}\\n\\nAnonymized Resume Context:\\n{anon_resume}"
                )
                evaluation = self.llm.invoke([HumanMessage(content=prompt)])
                eval_dict = evaluation.model_dump()
                logger.info(f"[{candidate_id}] Live LLM Inference Completed.")
                
            except Exception as e:
                logger.error(f"[{candidate_id}] Inference Failure: {str(e)}")
                eval_dict = {"score": 50, "reasoning": f"API Error fallback: {str(e)}", "citations": []}
        else:
            eval_dict = self._mock_evaluation_logic(anon_resume, state.get("retry_count", 0))

        # IMPORTANT: Preserve Semantic Loop failure status if it tripped prior to entry or during evaluation
        # If the state is already strictly failed by the circuit breaker, do not overwrite it.
        final_status = state.get("status", "Evaluation_Complete")
        if final_status != "SEMANTIC_LOOP_DETECTED":
            final_status = "Evaluation_Complete"

        return {"evaluation": eval_dict, "status": final_status, "routing_decision": state.get("routing_decision", "")}

    def _mock_evaluation_logic(self, anon_resume: str, retry_count: int = 0) -> Dict[str, Any]:
        """Internal helper to provide structured mock data mapped against our new 10 resume file dataset."""
        if "# PASS" in anon_resume and "Score 95" in anon_resume:
            return {"score": 95, "reasoning": "Strong match: Meets all requirements.", "citations": ["Databridge Systems"]}
        elif "# PASS" in anon_resume and "Score 90" in anon_resume:
            return {"score": 90, "reasoning": "Strong match: Highly experienced React dev.", "citations": ["15+ responsive marketing sites"]}
        elif "# PASS" in anon_resume and "Score 92" in anon_resume:
            return {"score": 92, "reasoning": "Strong match: Excellent Kubernetes/IaC tenure.", "citations": ["Automated infrastructure provisioning"]}
        elif "# PASS" in anon_resume and "Score 88" in anon_resume:
            return {"score": 88, "reasoning": "Strong match: Solid FinTech Cloud engineering.", "citations": ["Orchestrated Docker containers"]}
            
        elif "# REJECT" in anon_resume and "Score 20" in anon_resume:
            # INTERVIEW DEMO: Simulate LLM Hallucination loops for Bob to trigger Semantic Breaker
            logger.warning(f"Mock LLM Hallucination (Pass {retry_count}): Evaluator forgot to pull citations and is repeating itself!")
            return {"score": 20, "reasoning": "Missing required Python experience.", "citations": []}
        elif "# REJECT" in anon_resume and "Score 15" in anon_resume:
            return {"score": 15, "reasoning": "Zero relevant frontend web architecture experience.", "citations": ["Zero experience with web frontend"]}
            
        elif "# HITL" in anon_resume and "Score 65" in anon_resume:
            return {"score": 65, "reasoning": "Borderline: Has Python, lacks LangGraph.", "citations": ["simple prompt wrapper"]}
        elif "# HITL" in anon_resume and "Score 75" in anon_resume:
            return {"score": 75, "reasoning": "Borderline: Good foundations, lacks enterprise React tenure.", "citations": ["Bootcamp Certificate"]}
        elif "# HITL" in anon_resume and "Score 55" in anon_resume:
            return {"score": 55, "reasoning": "Borderline: Lacks heavy IaC orchestration.", "citations": ["weekend project"]}
        elif "# HITL" in anon_resume and "Score 68" in anon_resume:
            return {"score": 68, "reasoning": "Borderline: Strong Python API, missing LangChain modules.", "citations": ["willing to learn agentic workflows"]}
        
        else:
            return {"score": 50, "reasoning": "Fallback evaluation triggered.", "citations": []}
