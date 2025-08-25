from fastapi import APIRouter
from fastapi.responses import JSONResponse
router = APIRouter()
@router.get("/chart")
async def get_chart_data():
    # Clean dummy chart data
    data = {
        "status": "success",
        "chart": {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "values": [12, 34, 56, 23, 45]
        }
    }
    return JSONResponse(content=data)
