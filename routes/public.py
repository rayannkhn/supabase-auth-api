from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/info")
async def public_info():
    return {"message": "Welcome stranger! This info is public."}
