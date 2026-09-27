"""Deterministic Analysis API routes."""
from fastapi import APIRouter, HTTPException, Query
from app.analysis.engine import analysis_engine
from app.analysis.models import (
    ContributionResult,
    PeriodComparisonRequest,
    PeriodComparisonResult,
    SQLQueryRequest,
    SQLQueryResult,
)


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/query", response_model=SQLQueryResult)
async def run_sql_query(req: SQLQueryRequest):
    """Execute a safe, validated analytical SQL query."""
    return analysis_engine.execute_custom_sql(req.dataset_id, req.query)


@router.post("/compare-periods", response_model=PeriodComparisonResult)
async def compare_periods(req: PeriodComparisonRequest):
    """Compute period-over-period differences for a metric."""
    try:
        return analysis_engine.compare_periods(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contribution", response_model=ContributionResult)
async def get_contribution(
    dataset_id: str = Query(..., description="Dataset ID"),
    metric: str = Query(..., description="Metric column name"),
    dimension: str = Query(..., description="Dimension column name"),
):
    """Calculate segment contribution and concentration shares."""
    try:
        return analysis_engine.analyze_contribution(dataset_id, metric, dimension)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
