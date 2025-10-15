from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models import UserLoginRequest, UserResponse
from app.access import user_access
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=UserResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Simple email-based login - creates user if doesn't exist"""
    try:
        user = user_access.get_or_create_user(session=db, email=request.email)
        db.commit()
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
