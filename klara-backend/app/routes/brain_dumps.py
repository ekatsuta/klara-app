from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Union, List
from sqlalchemy.orm import Session
from app.models import (
    BrainDumpRequest,
    TaskResponse,
    ShoppingItemResponse,
    CalendarEventResponse,
    ProcessedTask,
    ProcessedCalendarEvent,
)
from app.access import task_access, shopping_item_access, calendar_event_access
from app.database import get_db
from app.ai_service import AIService

router = APIRouter(prefix="/brain-dumps", tags=["brain-dumps"])

# Initialize AI service
ai_service = AIService()


@router.post(
    "/",
    response_model=Union[
        TaskResponse, List[ShoppingItemResponse], CalendarEventResponse
    ],
)
async def process_brain_dump(request: BrainDumpRequest, db: Session = Depends(get_db)):
    """Process a brain dump using AI and save to database"""
    try:
        # Process the brain dump with AI
        processed = await ai_service.process_brain_dump(request.text)

        result: Union[TaskResponse, List[ShoppingItemResponse], CalendarEventResponse]

        # Save to database based on type
        if isinstance(processed, ProcessedTask):
            result = task_access.create_task(
                session=db,
                user_id=request.user_id,
                description=processed.description,
                due_date=datetime.strptime(processed.due_date, "%Y-%m-%d").date()
                if processed.due_date
                else None,
                raw_input=request.text,
            )
        elif isinstance(processed, list):  # List of ProcessedShoppingItem
            # Create a shopping item in DB for each processed item
            result = []
            for item in processed:
                shopping_item = shopping_item_access.create_shopping_item(
                    session=db,
                    user_id=request.user_id,
                    description=item.description,
                    raw_input=request.text,
                )
                result.append(shopping_item)
        elif isinstance(processed, ProcessedCalendarEvent):
            # Convert event_date string to date object
            event_date_obj = datetime.strptime(processed.event_date, "%Y-%m-%d").date()

            # Convert event_time string to time object if provided
            event_time_obj = None
            if processed.event_time:
                # Handle both HH:MM and HH:MM:SS formats
                time_format = (
                    "%H:%M:%S" if processed.event_time.count(":") == 2 else "%H:%M"
                )
                event_time_obj = datetime.strptime(
                    processed.event_time, time_format
                ).time()

            result = calendar_event_access.create_calendar_event(
                session=db,
                user_id=request.user_id,
                description=processed.description,
                event_date=event_date_obj,
                event_time=event_time_obj,
                raw_input=request.text,
            )
        else:
            raise ValueError(f"Unknown processed type: {type(processed)}")

        db.commit()
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
