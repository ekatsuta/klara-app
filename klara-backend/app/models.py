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


class DecomposedTask(BaseModel):
    """Result of task decomposition by agent"""

    task_description: str = Field(description="The original task description")
    should_decompose: bool = Field(
        description="Whether the agent decided to decompose the task"
    )
    reasoning: str = Field(description="Agent's reasoning for the decision")
    subtasks: List[SubTask] = Field(
        default_factory=list, description="List of subtasks (empty if not decomposed)"
    )
    estimated_time_minutes: int = Field(
        description="Total estimated time for task or sum of subtasks"
    )


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
