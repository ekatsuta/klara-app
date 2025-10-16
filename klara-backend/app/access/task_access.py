"""
Task database access functions
"""

from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from app.db_models import Task, SubTask
from app.models import TaskResponse, SubTaskResponse


def create_task(
    session: Session,
    user_id: int,
    description: str,
    raw_input: str,
    due_date: Optional[date] = None,
    estimated_time_minutes: Optional[int] = None,
) -> TaskResponse:
    """Create a new task"""
    task = Task(
        user_id=user_id,
        description=description,
        due_date=due_date,
        estimated_time_minutes=estimated_time_minutes,
        raw_input=raw_input,
    )
    session.add(task)
    session.flush()

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        description=task.description,
        due_date=str(task.due_date) if task.due_date else None,
        estimated_time_minutes=task.estimated_time_minutes,
        completed=task.completed,
        raw_input=task.raw_input,
        subtasks=None,
        created_at=task.created_at,
    )


def create_subtasks(
    session: Session,
    parent_task_id: int,
    subtasks: List[dict],
) -> List[SubTaskResponse]:
    """Create multiple subtasks for a parent task"""
    subtask_objects = [
        SubTask(
            parent_task_id=parent_task_id,
            description=subtask_data["description"],
            order=subtask_data["order"],
            estimated_time_minutes=subtask_data.get("estimated_time_minutes"),
            due_date=subtask_data.get("due_date"),
        )
        for subtask_data in subtasks
    ]

    session.add_all(subtask_objects)
    session.flush()

    # Convert to response models
    # TODO: use pydantic's model_validate
    return [
        SubTaskResponse(
            id=subtask.id,
            parent_task_id=subtask.parent_task_id,
            description=subtask.description,
            order=subtask.order,
            estimated_time_minutes=subtask.estimated_time_minutes,
            due_date=str(subtask.due_date) if subtask.due_date else None,
            completed=subtask.completed,
            created_at=subtask.created_at,
        )
        for subtask in subtask_objects
    ]
