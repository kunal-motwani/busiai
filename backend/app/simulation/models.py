"""What-If Simulation models and schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationScenario(BaseModel):
    name: str  # "conservative", "base_case", "optimistic"
    projected_value: float
    delta_value: float
    delta_percentage: float
    description: str


class TimelinePoint(BaseModel):
    month: str
    baseline: float
    projected_base: float
    projected_conservative: float
    projected_optimistic: float


class SimulationRequest(BaseModel):
    dataset_id: str
    target_metric: Optional[str] = None
    price_change_pct: float = Field(default=0.0, ge=-50.0, le=100.0)
    churn_reduction_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    conversion_boost_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    cost_reduction_pct: float = Field(default=0.0, ge=0.0, le=100.0)


class SimulationResult(BaseModel):
    dataset_id: str
    target_metric: str
    baseline_value: float
    projected_value: float
    net_delta: float
    net_delta_pct: float
    confidence_score: float
    scenarios: List[SimulationScenario] = Field(default_factory=list)
    timeline_curve: List[TimelinePoint] = Field(default_factory=list)
    key_takeaways: List[str] = Field(default_factory=list)
