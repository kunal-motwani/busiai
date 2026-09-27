"""Profiling API routes."""
from fastapi import APIRouter, HTTPException
from app.ingestion.service import ingestion_service
from app.profiling.models import DatasetProfile
from app.profiling.service import profiling_service


router = APIRouter(prefix="/profile", tags=["profiling"])


@router.get("/{dataset_id}", response_model=DatasetProfile)
async def get_dataset_profile(dataset_id: str):
    """Generate or retrieve statistical profile for a dataset."""
    dataset = ingestion_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    try:
        profile = profiling_service.profile_dataset(dataset)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to profile dataset: {str(e)}"
        )
