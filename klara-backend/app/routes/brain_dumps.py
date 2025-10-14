from fastapi import APIRouter, HTTPException
from typing import Union, List
from app.models import (
    BrainDumpRequest,
    TaskResponse,
    ShoppingListResponse,
    CalendarEventResponse,
    ProcessedTask,
    ProcessedShoppingList,
    ProcessedCalendarEvent
)
from app.database import db
from app.ai_service import AIService

router = APIRouter(prefix="/brain-dumps", tags=["brain-dumps"])

# Initialize AI service
ai_service = AIService()


@router.post("/", response_model=Union[TaskResponse, ShoppingListResponse, CalendarEventResponse])
async def create_reminder(request: BrainDumpRequest):
    """Process a brain dump using AI and save to database"""
    try:
        # Process the brain dump with AI
        processed = await ai_service.process_brain_dump(request.text)

        # Save to database based on type
        if isinstance(processed, ProcessedTask):
            return db.create_task(
                user_id=request.user_id,
                title=processed.title,
                description=processed.description,
                due_date=processed.due_date,
                raw_input=request.text
            )
        elif isinstance(processed, ProcessedShoppingList):
            return db.create_shopping_list(
                user_id=request.user_id,
                title=processed.title,
                items=processed.items,
                raw_input=request.text
            )
        elif isinstance(processed, ProcessedCalendarEvent):
            return db.create_calendar_event(
                user_id=request.user_id,
                title=processed.title,
                description=processed.description,
                event_date=processed.event_date,
                event_time=processed.event_time,
                raw_input=request.text
            )
        else:
            raise ValueError(f"Unknown processed type: {type(processed)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/user/{user_id}", response_model=List[Union[TaskResponse, ShoppingListResponse, CalendarEventResponse]])
async def get_user_brain_dumps(user_id: int):
    """Get all brain dumps for a specific user"""
    try:
        brain_dumps = db.get_user_brain_dumps(user_id)
        return brain_dumps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch brain dumps: {str(e)}")
