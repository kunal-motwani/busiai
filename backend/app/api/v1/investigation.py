"""AI Investigation API routes."""
from fastapi import APIRouter, HTTPException
from app.investigation.engine import investigation_engine
from app.investigation.models import InvestigationRequest, InvestigationResult


router = APIRouter(prefix="/investigation", tags=["investigation"])


@router.post("/run", response_model=InvestigationResult)
async def run_investigation(req: InvestigationRequest):
    """Run an AI business investigation on a dataset with verified deterministic evidence."""
    try:
        return await investigation_engine.run_investigation(
            dataset_id=req.dataset_id,
            question=req.question,
            focus_metric=req.focus_metric,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
