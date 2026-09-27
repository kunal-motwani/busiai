"""What-If Simulation API routes."""
from fastapi import APIRouter, HTTPException
from app.simulation.engine import simulation_engine
from app.simulation.models import SimulationRequest, SimulationResult


router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run", response_model=SimulationResult)
async def run_simulation(req: SimulationRequest):
    """Execute grounded what-if business parameter simulation."""
    try:
        return simulation_engine.run_simulation(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
