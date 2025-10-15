"""
User database access functions
"""

from sqlalchemy.orm import Session
from app.db_models import User
from app.models import UserResponse


def get_or_create_user(session: Session, email: str) -> UserResponse:
    """Get existing user or create new one by email"""
    # Check if user exists
    user = session.query(User).filter(User.email == email).first()

    if user:
        return UserResponse(id=user.id, email=user.email, first_name=user.first_name)

    # Create new user
    user = User(email=email)
    session.add(user)
    session.flush()

    return UserResponse(id=user.id, email=user.email, first_name=user.first_name)
