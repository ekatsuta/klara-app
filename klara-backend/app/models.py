from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List, Union
from datetime import datetime


# User models
class UserLoginRequest(BaseModel):
    """Simple email login request"""
    email: EmailStr


class User(BaseModel):
    """User response"""
    id: int
    email: str
    created_at: datetime


# Brain dump models
class BrainDumpRequest(BaseModel):
    """Raw brain dump from user"""
    text: str
    user_id: int


# Category Detection
class CategoryDetection(BaseModel):
    """First step: Detect category only"""
    category: Literal["task", "shopping_list", "calendar_event"] = Field(
        description="Category: task, shopping_list, or calendar_event"
    )


# Category-specific processing models
class ProcessedTask(BaseModel):
    """AI-generated output for tasks"""
    title: str = Field(description="Succinct title (5-10 words max)")
    description: str = Field(description="Brief description (1-2 sentences)")
    due_date: Optional[str] = Field(
        default=None,
        description="Due date (YYYY-MM-DD format) if mentioned, null otherwise"
    )


class ShoppingItem(BaseModel):
    """Individual shopping item"""
    item_name: str = Field(description="Name of the item to purchase")
    quantity: Optional[str] = Field(
        default=None,
        description="Quantity if specified (e.g., '2', '1 gallon', '3 pounds'), null otherwise"
    )


class ProcessedShoppingList(BaseModel):
    """AI-generated output for shopping lists"""
    items: List[ShoppingItem] = Field(description="List of shopping items")
    title: str = Field(
        default="Shopping List",
        description="Title for the shopping list (e.g., 'Grocery Shopping', 'Weekly Groceries')"
    )


class ProcessedCalendarEvent(BaseModel):
    """AI-generated output for calendar events"""
    title: str = Field(description="Event title (5-10 words max)")
    description: str = Field(description="Brief description (1-2 sentences)")
    event_date: str = Field(description="Event date (YYYY-MM-DD format)")
    event_time: Optional[str] = Field(
        default=None,
        description="Event time (HH:MM 24-hour format) if mentioned, null otherwise"
    )


# Response models for frontend
class TaskResponse(BaseModel):
    """Response for task category"""
    id: int
    user_id: int
    category: Literal["task"]
    title: str
    description: str
    due_date: Optional[str] = None
    raw_input: str
    created_at: datetime


class ShoppingItemResponse(BaseModel):
    """Response for individual shopping item"""
    id: int
    item_name: str
    quantity: Optional[str] = None


class ShoppingListResponse(BaseModel):
    """Response for shopping list category"""
    id: int
    user_id: int
    category: Literal["shopping_list"]
    title: str
    items: List[ShoppingItemResponse]
    raw_input: str
    created_at: datetime


class CalendarEventResponse(BaseModel):
    """Response for calendar event category"""
    id: int
    user_id: int
    category: Literal["calendar_event"]
    title: str
    description: str
    event_date: str
    event_time: Optional[str] = None
    raw_input: str
    created_at: datetime


# Union type for all possible responses
BrainDumpResponse = Union[TaskResponse, ShoppingListResponse, CalendarEventResponse]
