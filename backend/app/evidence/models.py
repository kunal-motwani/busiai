"""Evidence Layer models and schemas."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalculationProof(BaseModel):
    """Verifiable mathematical proof for an analytical claim."""
    metric: str
    formula: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    calculated_value: Any
    confidence_pct: float = 100.0


class EvidenceItem(BaseModel):
    """An individual piece of verifiable data evidence."""
    id: str
    title: str
    hypothesis_id: Optional[str] = None
    sql_query: str
    executed_at: str
    execution_time_ms: float
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    proof: CalculationProof
    summary: str


class EvidencePackage(BaseModel):
    """Container for all evidence gathered during an investigation."""
    dataset_id: str
    question_id: str
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    total_queries_run: int = 0
    verification_score: float = 100.0  # Percentage of claims mathematically verified
