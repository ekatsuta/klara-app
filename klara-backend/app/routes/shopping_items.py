from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.models import ShoppingItemResponse
from app.access import shopping_item_access
from app.database import get_db

router = APIRouter(prefix="/shopping-items", tags=["shopping-items"])


class CreateShoppingItemsRequest(BaseModel):
    """Request to create shopping items"""

    user_id: int
    items: List[str]  # List of item descriptions
    raw_input: str


@router.post("/", response_model=List[ShoppingItemResponse])
async def create_shopping_items(
    request: CreateShoppingItemsRequest, db: Session = Depends(get_db)
):
    """Create shopping items after user approval"""
    try:
        result = []
        for description in request.items:
            shopping_item = shopping_item_access.create_shopping_item(
                session=db,
                user_id=request.user_id,
                description=description,
                raw_input=request.raw_input,
            )
            result.append(shopping_item)

        db.commit()
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create shopping items: {str(e)}"
        )
