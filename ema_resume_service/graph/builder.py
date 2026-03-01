from langgraph.graph import StateGraph, END
import logging

from ema_resume_service.core.state import EnterpriseState
from ema_resume_service.agents.redactor import PIIRedactorAgent
from ema_resume_service.agents.evaluator import LLMEvaluatorAgent
from ema_resume_service.agents.router import RoutingAgent, HumanInterruptAgent, route_decision
from ema_resume_service.agents.guard import IngestionGuardAgent, check_ingestion_security
from ema_resume_service.agents.validator import ValidationAgent, route_validation_output

logger = logging.getLogger("EmaResumeService")

class EmaWorkflowEngine:
    """
    Compiles and constructs the LangGraph execution environment.
    Uses Dependency Injection to instantiate node services.
    """
    @classmethod
    def build_graph(cls) -> object:
        logger.info("Initializing LangGraph State Machine Compilation...")
        builder = StateGraph(EnterpriseState)

        # Instantiate Agent Services (Dependency Injection pattern)
        guard = IngestionGuardAgent()
        redactor = PIIRedactorAgent()
        evaluator = LLMEvaluatorAgent()
        validator = ValidationAgent()
        router = RoutingAgent()
        interrupt = HumanInterruptAgent()

        # Register Nodes (mapping class instances' process methods)
        builder.add_node("ingestion_guard_node", guard.process)
        builder.add_node("pii_redactor_node", redactor.process)
        builder.add_node("evaluator_node", evaluator.process)
        builder.add_node("validator_node", validator.process)
        builder.add_node("routing_node", router.process)
        builder.add_node("human_interrupt_node", interrupt.process)

        # Define Traversal Edges
        builder.set_entry_point("ingestion_guard_node")
        
        # Ingestion Guard conditional (Kill switch)
        builder.add_conditional_edges("ingestion_guard_node", check_ingestion_security)
        
        builder.add_edge("pii_redactor_node", "evaluator_node")
        builder.add_edge("evaluator_node", "validator_node")

        # Validator conditional (The Loop / Critic)
        builder.add_conditional_edges("validator_node", route_validation_output)
        
        # Business Logic Routing
        builder.add_conditional_edges("routing_node", route_decision)
        builder.add_edge("human_interrupt_node", END)

        logger.info("LangGraph Compiled Successfully.")
        return builder.compile()
