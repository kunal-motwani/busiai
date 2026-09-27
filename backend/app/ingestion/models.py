from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    """Metadata for a single column in a dataset."""
    name: str
    original_name: str
    data_type: str
    sample_values: list[Any] = Field(default_factory=list)


class DatasetInfo(BaseModel):
    """Overview metadata for an ingested dataset."""
    id: str
    name: str
    filename: str
    file_type: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: list[ColumnMetadata]
    table_name: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    preview_rows: list[dict[str, Any]] = Field(default_factory=list)


class IngestionResponse(BaseModel):
    """API response after dataset upload and registration."""
    success: bool
    message: str
    dataset: DatasetInfo
