from fastapi import APIRouter, Query, HTTPException
from services.storage import get_json

router = APIRouter(prefix="/api", tags=["telemetry"])


@router.get("/sessions/{year}/{round_num}/telemetry")
async def driver_telemetry(
    year: int,
    round_num: int,
    type: str = Query("R", pattern=r"^(R|Q|S|SQ|FP1|FP2|FP3)$"),
    driver: str = Query(..., pattern=r"^[A-Z]{2,4}$"),
    lap: int = Query(...),
):
    data = get_json(f"sessions/{year}/{round_num}/{type}/telemetry/{driver}.json")
    if data is None:
        raise HTTPException(status_code=404, detail="Telemetry not available for this driver")

    lap_data = data.get(str(lap))
    if lap_data is None:
        raise HTTPException(status_code=404, detail="Telemetry not available for this lap")
    return lap_data
