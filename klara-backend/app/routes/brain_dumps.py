from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Union, List
from sqlalchemy.orm import Session
from app.models import (
    BrainDumpRequest,
    BrainDumpResponse,
)
from app.access import task_access, shopping_item_access, calendar_event_access
from app.database import get_db
from app.ai_service import AIService

router = APIRouter(prefix="/brain-dumps", tags=["brain-dumps"])

# Initialize AI service
ai_service = AIService()


@router.post("/", response_model=BrainDumpResponse)
async def process_brain_dump(request: BrainDumpRequest, db: Session = Depends(get_db)):
    """Process a brain dump using AI and save all extracted items to database"""
    try:
        # Process the brain dump with AI
        processed = await ai_service.process_brain_dump(request.text)

        # Save all tasks
        saved_tasks = []
        for task in processed.tasks:
            # Create the parent task
            saved_task = task_access.create_task(
                session=db,
                user_id=request.user_id,
                description=task.description,
                due_date=datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if task.due_date
                else None,
                estimated_time_minutes=task.estimated_time_minutes,
                raw_input=request.text,
            )

            # If task was decomposed, create subtasks
            if task.should_decompose and task.subtasks:
                subtasks_data = [
                    {
                        "description": subtask.description,
                        "order": subtask.order,
                        "estimated_time_minutes": subtask.estimated_time_minutes,
                        "due_date": datetime.strptime(
                            subtask.due_date, "%Y-%m-%d"
                        ).date()
                        if subtask.due_date
                        else None,
                    }
                    for subtask in task.subtasks
                ]
                subtask_responses = task_access.create_subtasks(
                    session=db,
                    parent_task_id=saved_task.id,
                    subtasks=subtasks_data,
                )
                # Update task with subtasks
                saved_task.subtasks = subtask_responses

            saved_tasks.append(saved_task)

        # Save all shopping items
        saved_shopping_items = []
        for item in processed.shopping_items:
            saved_item = shopping_item_access.create_shopping_item(
                session=db,
                user_id=request.user_id,
                description=item.description,
                raw_input=request.text,
            )
            saved_shopping_items.append(saved_item)

        # Save all calendar events
        saved_calendar_events = []
        for event in processed.calendar_events:
            # Convert event_date string to date object
            event_date_obj = datetime.strptime(event.event_date, "%Y-%m-%d").date()

            # Convert event_time string to time object if provided
            event_time_obj = None
            if event.event_time:
                # Handle both HH:MM and HH:MM:SS formats
                time_format = (
                    "%H:%M:%S" if event.event_time.count(":") == 2 else "%H:%M"
                )
                event_time_obj = datetime.strptime(event.event_time, time_format).time()

            saved_event = calendar_event_access.create_calendar_event(
                session=db,
                user_id=request.user_id,
                description=event.description,
                event_date=event_date_obj,
                event_time=event_time_obj,
                raw_input=request.text,
            )
            saved_calendar_events.append(saved_event)

        db.commit()

        return BrainDumpResponse(
            tasks=saved_tasks,
            shopping_items=saved_shopping_items,
            calendar_events=saved_calendar_events,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
