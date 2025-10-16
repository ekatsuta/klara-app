from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.models import TaskResponse, SubTask
from app.access import task_access
from app.database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    """Request to create a new task with optional subtasks"""

    user_id: int
    description: str
    due_date: Optional[str] = None
    estimated_time_minutes: int
    raw_input: str
    subtasks: List[SubTask] = []


@router.post("/", response_model=TaskResponse)
async def create_task(request: CreateTaskRequest, db: Session = Depends(get_db)):
    """Create a new task with optional subtasks after user approval"""
    try:
        # Create the parent task
        task = task_access.create_task(
            session=db,
            user_id=request.user_id,
            description=request.description,
            due_date=datetime.strptime(request.due_date, "%Y-%m-%d").date()
            if request.due_date
            else None,
            estimated_time_minutes=request.estimated_time_minutes,
            raw_input=request.raw_input,
        )

        # Create subtasks if provided
        if request.subtasks:
            subtasks_data = [
                {
                    "description": subtask.description,
                    "order": subtask.order,
                    "estimated_time_minutes": subtask.estimated_time_minutes,
                    "due_date": datetime.strptime(subtask.due_date, "%Y-%m-%d").date()
                    if subtask.due_date
                    else None,
                }
                for subtask in request.subtasks
            ]
            subtask_responses = task_access.create_subtasks(
                session=db,
                parent_task_id=task.id,
                subtasks=subtasks_data,
            )
            # Update task with subtasks
            task.subtasks = subtask_responses

        db.commit()
        return task

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")
