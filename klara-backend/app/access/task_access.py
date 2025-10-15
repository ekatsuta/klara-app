"""
Task database access functions
"""

from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from app.db_models import Task
from app.models import TaskResponse


def create_task(
    session: Session,
    user_id: int,
    description: str,
    raw_input: str,
    due_date: Optional[date] = None,
) -> TaskResponse:
    """Create a new task"""
    task = Task(
        user_id=user_id, description=description, due_date=due_date, raw_input=raw_input
    )
    session.add(task)
    session.flush()

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        description=task.description,
        due_date=str(task.due_date) if task.due_date else None,
        raw_input=task.raw_input,
        created_at=task.created_at,
    )
