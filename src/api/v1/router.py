from fastapi import APIRouter

api_v3_router = APIRouter()

@api_v3_router.get("/status")
async def get_status():
    return {"status": "ok", "message": "API V1 is running"}
