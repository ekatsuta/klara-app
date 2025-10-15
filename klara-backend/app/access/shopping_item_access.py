"""
Shopping item database access functions
"""

from sqlalchemy.orm import Session
from app.db_models import ShoppingItem
from app.models import ShoppingItemResponse


def create_shopping_item(
    session: Session, user_id: int, description: str, raw_input: str
) -> ShoppingItemResponse:
    """Create a new shopping item"""
    shopping_item = ShoppingItem(
        user_id=user_id, description=description, raw_input=raw_input
    )
    session.add(shopping_item)
    session.flush()

    return ShoppingItemResponse(
        id=shopping_item.id,
        user_id=shopping_item.user_id,
        description=shopping_item.description,
        raw_input=shopping_item.raw_input,
        created_at=shopping_item.created_at,
    )
