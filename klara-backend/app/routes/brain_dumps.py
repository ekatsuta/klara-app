from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Union, List
from sqlalchemy.orm import Session
from app.models import (
    BrainDumpRequest,
    ProcessedTask,
    ProcessedCalendarEvent,
    ProcessedShoppingItem,
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
        ProcessedTask, List[ProcessedShoppingItem], ProcessedCalendarEvent
    ],
)
async def process_brain_dump(request: BrainDumpRequest):
    """Process a brain dump using AI and return suggestions for user approval"""
    try:
        # Process the brain dump with AI and return suggestions (not saved to DB)
        processed = await ai_service.process_brain_dump(request.text)
        return processed

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
