"""Profiling models and schemas."""
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ColumnType(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    IDENTIFIER = "identifier"
    TEXT = "text"


class NumericStats(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    outlier_count: int = 0
    zero_count: int = 0


class CategoricalStats(BaseModel):
    unique_count: int = 0
    cardinality_ratio: float = 0.0
    top_values: List[dict[str, Any]] = Field(default_factory=list)


class TemporalStats(BaseModel):
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    date_range_days: Optional[int] = None
    inferred_frequency: Optional[str] = None


class ColumnProfile(BaseModel):
    name: str
    original_name: str
    inferred_type: ColumnType
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    is_primary_key_candidate: bool = False
    numeric_stats: Optional[NumericStats] = None
    categorical_stats: Optional[CategoricalStats] = None
    temporal_stats: Optional[TemporalStats] = None


class DatasetProfile(BaseModel):
    dataset_id: str
    total_rows: int
    total_columns: int
    quality_score: float  # 0 to 100
    columns: List[ColumnProfile]
    primary_date_column: Optional[str] = None
    key_metrics: List[str] = Field(default_factory=list)
    key_dimensions: List[str] = Field(default_factory=list)
    issues_detected: List[str] = Field(default_factory=list)
