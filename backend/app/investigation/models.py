"""Investigation models and schemas."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.evidence.models import EvidenceItem


class HypothesisStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


class Hypothesis(BaseModel):
    id: str
    statement: str
    rationale: str
    target_metric: str
    target_dimension: Optional[str] = None
    status: HypothesisStatus = HypothesisStatus.PENDING
    confidence_score: float = 0.0  # 0 to 100
    impact_magnitude: Optional[float] = None
    evidence_ids: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None


class InvestigationPlan(BaseModel):
    dataset_id: str
    business_question: str
    target_metric: str
    target_period: Optional[str] = None
    hypotheses: List[Hypothesis] = Field(default_factory=list)


class InvestigationRequest(BaseModel):
    dataset_id: str
    question: str
    focus_metric: Optional[str] = None


class RecommendationAction(BaseModel):
    id: str
    title: str
    description: str
    projected_impact: str
    priority: str  # "high", "medium", "low"
    supporting_evidence: List[str] = Field(default_factory=list)


class InvestigationResult(BaseModel):
    id: str
    dataset_id: str
    question: str
    target_metric: str
    executive_summary: str
    key_findings: List[str] = Field(default_factory=list)
    hypotheses_tested: List[Hypothesis] = Field(default_factory=list)
    evidence_package: List[EvidenceItem] = Field(default_factory=list)
    primary_drivers: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[RecommendationAction] = Field(default_factory=list)
