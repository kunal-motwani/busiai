"""Decision Graph models for React Flow visualization."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphNodePosition(BaseModel):
    x: float
    y: float


class DecisionGraphNode(BaseModel):
    id: str
    type: str  # "question", "hypothesis", "analysis", "evidence", "action", "simulation"
    data: Dict[str, Any] = Field(default_factory=dict)
    position: GraphNodePosition


class DecisionGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: bool = False
    style: Dict[str, Any] = Field(default_factory=dict)


class DecisionGraphResponse(BaseModel):
    nodes: List[DecisionGraphNode] = Field(default_factory=list)
    edges: List[DecisionGraphEdge] = Field(default_factory=list)
    summary: str
