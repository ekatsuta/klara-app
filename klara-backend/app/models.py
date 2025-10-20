from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List
from datetime import datetime


# User models
class UserLoginRequest(BaseModel):
    """Simple email login request"""

    email: EmailStr


class UserResponse(BaseModel):
    """User response"""

    id: int
    email: str
    first_name: str


# Brain dump models
class BrainDumpRequest(BaseModel):
    """Raw brain dump from user"""

    text: str
    user_id: int


# AI Processing models
class ProcessedBrainDump(BaseModel):
    """Result of processing a brain dump - can contain multiple categories"""

    tasks: List["ProcessedTask"] = Field(
        default_factory=list, description="Tasks extracted from the brain dump"
    )
    shopping_items: List["ProcessedShoppingItem"] = Field(
        default_factory=list, description="Shopping items extracted from the brain dump"
    )
    calendar_events: List["ProcessedCalendarEvent"] = Field(
        default_factory=list,
        description="Calendar events extracted from the brain dump",
    )


class ProcessedTask(BaseModel):
    """AI-processed task data with optional decomposition"""

    description: str
    due_date: Optional[str] = None
    estimated_time_minutes: int = Field(
        description="Estimated time to complete in minutes"
    )
    should_decompose: bool = Field(
        description="Whether the task should be decomposed into subtasks"
    )
    reasoning: Optional[str] = Field(
        None, description="Agent's reasoning for decomposition decision"
    )
    subtasks: List["SubTask"] = Field(
        default_factory=list, description="List of subtasks (empty if not decomposed)"
    )


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
    completed: bool = False
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
    estimated_time_minutes: Optional[int] = None
    completed: bool = False
    raw_input: str
    subtasks: Optional[List["SubTaskResponse"]] = None
    created_at: datetime


# Task Decomposition models
class SubTask(BaseModel):
    """A subtask created by the agent"""

    description: str
    estimated_time_minutes: Optional[int] = Field(
        None, description="Estimated time to complete in minutes"
    )
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    order: int = Field(description="Order in which subtask should be completed")


class SubTaskResponse(BaseModel):
    """Subtask saved in database"""

    id: int
    parent_task_id: int
    description: str
    estimated_time_minutes: Optional[int]
    due_date: Optional[str]
    order: int
    completed: bool
    created_at: datetime


class BrainDumpResponse(BaseModel):
    """Response after processing and saving a brain dump"""

    tasks: List[TaskResponse] = Field(default_factory=list)
    shopping_items: List[ShoppingItemResponse] = Field(default_factory=list)
    calendar_events: List[CalendarEventResponse] = Field(default_factory=list)
