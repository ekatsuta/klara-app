"""
Calendar event database access functions
"""

from typing import Optional
from datetime import date, time
from sqlalchemy.orm import Session
from app.db_models import CalendarEvent
from app.models import CalendarEventResponse


def create_calendar_event(
    session: Session,
    user_id: int,
    description: str,
    event_date: date,
    raw_input: str,
    event_time: Optional[time] = None,
) -> CalendarEventResponse:
    """Create a new calendar event"""
    calendar_event = CalendarEvent(
        user_id=user_id,
        description=description,
        event_date=event_date,
        event_time=event_time,
        raw_input=raw_input,
    )
    session.add(calendar_event)
    session.flush()

    return CalendarEventResponse(
        id=calendar_event.id,
        user_id=calendar_event.user_id,
        description=calendar_event.description,
        event_date=str(calendar_event.event_date),
        event_time=str(calendar_event.event_time)
        if calendar_event.event_time
        else None,
        raw_input=calendar_event.raw_input,
        created_at=calendar_event.created_at,
    )
