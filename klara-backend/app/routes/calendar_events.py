from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models import CalendarEventResponse
from app.access import calendar_event_access
from app.database import get_db

router = APIRouter(prefix="/calendar-events", tags=["calendar-events"])


class CreateCalendarEventRequest(BaseModel):
    """Request to create a calendar event"""

    user_id: int
    description: str
    event_date: str  # YYYY-MM-DD format
    event_time: Optional[str] = None  # HH:MM format
    raw_input: str


@router.post("/", response_model=CalendarEventResponse)
async def create_calendar_event(
    request: CreateCalendarEventRequest, db: Session = Depends(get_db)
):
    """Create a calendar event after user approval"""
    try:
        # Convert event_date string to date object
        event_date_obj = datetime.strptime(request.event_date, "%Y-%m-%d").date()

        # Convert event_time string to time object if provided
        event_time_obj = None
        if request.event_time:
            # Handle both HH:MM and HH:MM:SS formats
            time_format = "%H:%M:%S" if request.event_time.count(":") == 2 else "%H:%M"
            event_time_obj = datetime.strptime(request.event_time, time_format).time()

        result = calendar_event_access.create_calendar_event(
            session=db,
            user_id=request.user_id,
            description=request.description,
            event_date=event_date_obj,
            event_time=event_time_obj,
            raw_input=request.raw_input,
        )

        db.commit()
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create calendar event: {str(e)}"
        )
