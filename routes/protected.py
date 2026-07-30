from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/profile")
async def profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


@router.get("/dashboard")
async def dashboard(user=Depends(get_current_user)):
    # Demo route only, to prove get_current_user is reusable across
    # unrelated endpoints without re-implementing token verification.
    return {"message": f"Welcome back, {user.email}."}
