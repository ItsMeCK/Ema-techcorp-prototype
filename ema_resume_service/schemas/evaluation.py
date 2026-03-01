from typing import List
from pydantic import BaseModel, Field

class EvaluationSchema(BaseModel):
    """
    Evidence Enforcement Schema.
    Strictly forces the LLM to provide exact citations from the resume 
    to map to its scoring, preventing hallucinated reasoning and "Black Box" rejections.
    """
    score: int = Field(description="Score from 0 to 100 representing candidate match to the job description.")
    reasoning: str = Field(description="Determine step-by-step reasoning for why the candidate deserves this score.")
    citations: List[str] = Field(
        description="Exact quotes extracted from the anonymized resume to justify the assigned score. This enforces explainability."
    )
