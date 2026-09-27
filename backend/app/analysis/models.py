"""Deterministic Analysis Models and Schemas."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    PERIOD_OVER_PERIOD = "period_over_period"
    CONTRIBUTION = "contribution"
    DRILLDOWN = "drilldown"
    CORRELATION = "correlation"
    SQL_QUERY = "sql_query"


class SQLQueryRequest(BaseModel):
    dataset_id: str
    query: str


class SQLQueryResult(BaseModel):
    success: bool
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class PeriodComparisonRequest(BaseModel):
    dataset_id: str
    date_column: str
    metric_column: str
    period_type: str = "month"  # "month", "quarter", "year", "day"
    dimension_column: Optional[str] = None


class PeriodComparisonRow(BaseModel):
    period: str
    current_value: float
    previous_value: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None


class PeriodComparisonResult(BaseModel):
    metric: str
    date_column: str
    periods: List[PeriodComparisonRow]
    overall_change_pct: Optional[float] = None
    highest_growth_period: Optional[str] = None
    largest_drop_period: Optional[str] = None


class ContributionItem(BaseModel):
    segment: str
    value: float
    percentage_share: float
    rank: int


class ContributionResult(BaseModel):
    metric: str
    dimension: str
    total_value: float
    items: List[ContributionItem]
    top_3_concentration_pct: float
