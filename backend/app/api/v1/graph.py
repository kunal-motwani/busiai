"""Decision Graph API routes."""
from fastapi import APIRouter, HTTPException
from app.graph.builder import decision_graph_builder
from app.graph.models import DecisionGraphResponse
from app.investigation.engine import investigation_engine
from app.investigation.models import InvestigationRequest


router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/build", response_model=DecisionGraphResponse)
async def build_decision_graph(req: InvestigationRequest):
    """Build interactive Decision Graph for a business question investigation."""
    try:
        inv_result = await investigation_engine.run_investigation(
            dataset_id=req.dataset_id,
            question=req.question,
            focus_metric=req.focus_metric,
        )
        return decision_graph_builder.build_graph(inv_result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
