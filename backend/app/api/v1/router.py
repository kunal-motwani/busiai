"""API v1 root router combining all analytical modules."""
from fastapi import APIRouter
from app.api.v1.datasets import router as datasets_router
from app.api.v1.profiling import router as profiling_router
from app.api.v1.insights import router as insights_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.investigation import router as investigation_router
from app.api.v1.graph import router as graph_router
from app.api.v1.simulation import router as simulation_router


api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(datasets_router)
api_v1_router.include_router(profiling_router)
api_v1_router.include_router(insights_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(investigation_router)
api_v1_router.include_router(graph_router)
api_v1_router.include_router(simulation_router)
