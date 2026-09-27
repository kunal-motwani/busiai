"""Auto-insights API routes."""
from typing import List
from fastapi import APIRouter, HTTPException
from app.analysis.insights import BusinessInsight, insights_service
from app.ingestion.service import ingestion_service
from app.profiling.service import profiling_service


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{dataset_id}", response_model=List[BusinessInsight])
async def get_dataset_insights(dataset_id: str):
    """Retrieve automated business insights discovered for a dataset."""
    dataset = ingestion_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    try:
        profile = profiling_service.profile_dataset(dataset)
        insights = insights_service.generate_insights(dataset, profile)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate insights: {str(e)}"
        )
