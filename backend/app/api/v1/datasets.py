"""Dataset upload and management API routes."""
from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.ingestion.models import DatasetInfo, IngestionResponse
from app.ingestion.service import ingestion_service


router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=IngestionResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    sheet_name: Optional[str] = Form(None),
):
    """Upload a CSV or Excel dataset file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        dataset_info = await ingestion_service.process_file(
            filename=file.filename,
            content=content,
            sheet_name=sheet_name,
            custom_name=name,
        )
        return IngestionResponse(
            success=True,
            message="Dataset uploaded and ingested successfully.",
            dataset=dataset_info,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")


@router.get("", response_model=List[DatasetInfo])
async def list_datasets():
    """List all registered datasets."""
    return ingestion_service.get_all_datasets()


@router.get("/{dataset_id}", response_model=DatasetInfo)
async def get_dataset(dataset_id: str):
    """Get metadata for a specific dataset."""
    dataset = ingestion_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset and drop its table."""
    deleted = ingestion_service.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"success": True, "message": "Dataset deleted successfully."}
