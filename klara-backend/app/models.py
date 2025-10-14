from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


# User models
class UserLoginRequest(BaseModel):
    """Simple email login request"""
    email: EmailStr


class UserResponse(BaseModel):
    """User response"""
    id: int
    email: str
    created_at: datetime


# Brain dump models
class BrainDumpRequest(BaseModel):
    """Raw brain dump from user"""
    text: str
    user_id: int


# AI Processing models
class CategoryDetection(BaseModel):
    """AI category detection result"""
    category: Literal["task", "shopping_list", "calendar_event"]


class ProcessedTask(BaseModel):
    """AI-processed task data"""
    description: str
    due_date: Optional[str] = None


class ProcessedShoppingItem(BaseModel):
    """AI-processed shopping list data"""
    description: str


class ProcessedCalendarEvent(BaseModel):
    """AI-processed calendar event data"""
    description: str
    event_date: str
    event_time: Optional[str] = None


# Response models for API endpoints
class ShoppingItemResponse(BaseModel):
    """Shopping item response"""
    id: int
    user_id: int
    description: str
    raw_input: str
    created_at: datetime


class CalendarEventResponse(BaseModel):
    """Calendar event response"""
    id: int
    user_id: int
    description: str
    event_date: str
    event_time: Optional[str] = None
    raw_input: str
    created_at: datetime


class TaskResponse(BaseModel):
    id: int
    user_id: int
    description: str
    due_date: Optional[str] = None
    raw_input: str
    created_at: datetime