from fastapi import APIRouter, HTTPException
from app.models import UserLoginRequest, User
from app.database import db

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=User)
async def login(request: UserLoginRequest):
    """Simple email-based login - creates user if doesn't exist"""
    try:
        user = db.get_or_create_user(request.email)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
