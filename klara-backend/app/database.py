from datetime import datetime
from typing import Optional, List, Union
from app.models import (
    User,
    TaskResponse,
    ShoppingListResponse,
    ShoppingItemResponse,
    CalendarEventResponse,
    ShoppingItem
)


class Database:
    """Simple in-memory database (replace with PostgreSQL later)"""

    def __init__(self):
        self.users = {}  # {id: {email, created_at}}
        self.tasks = {}  # {id: {user_id, title, description, ...}}
        self.shopping_lists = {}  # {id: {user_id, title, items, ...}}
        self.shopping_items = {}  # {id: {shopping_list_id, item_name, quantity}}
        self.calendar_events = {}  # {id: {user_id, title, description, event_date, ...}}

        self.user_id_counter = 1
        self.task_id_counter = 1
        self.shopping_list_id_counter = 1
        self.shopping_item_id_counter = 1
        self.calendar_event_id_counter = 1

    def get_or_create_user(self, email: str) -> User:
        """Get existing user or create new one by email"""
        # Check if user exists
        for user_id, user_data in self.users.items():
            if user_data["email"] == email:
                return User(
                    id=user_id,
                    email=user_data["email"],
                    created_at=user_data["created_at"]
                )

        # Create new user
        user_id = self.user_id_counter
        self.user_id_counter += 1

        user_data = {
            "email": email,
            "created_at": datetime.now()
        }
        self.users[user_id] = user_data

        return User(
            id=user_id,
            email=user_data["email"],
            created_at=user_data["created_at"]
        )

    def create_task(
        self,
        user_id: int,
        title: str,
        description: str,
        raw_input: str,
        due_date: Optional[str] = None
    ) -> TaskResponse:
        """Save a task"""
        task_id = self.task_id_counter
        self.task_id_counter += 1

        task_data = {
            "user_id": user_id,
            "category": "task",
            "title": title,
            "description": description,
            "due_date": due_date,
            "raw_input": raw_input,
            "created_at": datetime.now()
        }
        self.tasks[task_id] = task_data

        return TaskResponse(id=task_id, **task_data)

    def create_shopping_list(
        self,
        user_id: int,
        title: str,
        items: List[ShoppingItem],
        raw_input: str
    ) -> ShoppingListResponse:
        """Save a shopping list with items"""
        shopping_list_id = self.shopping_list_id_counter
        self.shopping_list_id_counter += 1

        # Create shopping list items
        item_responses = []
        for item in items:
            item_id = self.shopping_item_id_counter
            self.shopping_item_id_counter += 1

            item_data = {
                "shopping_list_id": shopping_list_id,
                "item_name": item.item_name,
                "quantity": item.quantity
            }
            self.shopping_items[item_id] = item_data
            item_responses.append(ShoppingItemResponse(id=item_id, **item_data))

        # Create shopping list
        shopping_list_data = {
            "user_id": user_id,
            "category": "shopping_list",
            "title": title,
            "items": item_responses,
            "raw_input": raw_input,
            "created_at": datetime.now()
        }
        self.shopping_lists[shopping_list_id] = shopping_list_data

        return ShoppingListResponse(id=shopping_list_id, **shopping_list_data)

    def create_calendar_event(
        self,
        user_id: int,
        title: str,
        description: str,
        event_date: str,
        raw_input: str,
        event_time: Optional[str] = None
    ) -> CalendarEventResponse:
        """Save a calendar event"""
        event_id = self.calendar_event_id_counter
        self.calendar_event_id_counter += 1

        event_data = {
            "user_id": user_id,
            "category": "calendar_event",
            "title": title,
            "description": description,
            "event_date": event_date,
            "event_time": event_time,
            "raw_input": raw_input,
            "created_at": datetime.now()
        }
        self.calendar_events[event_id] = event_data

        return CalendarEventResponse(id=event_id, **event_data)

    def get_user_brain_dumps(
        self, user_id: int
    ) -> List[Union[TaskResponse, ShoppingListResponse, CalendarEventResponse]]:
        """Get all brain dumps (tasks, shopping lists, events) for a user"""
        results = []

        # Get tasks
        for task_id, task_data in self.tasks.items():
            if task_data["user_id"] == user_id:
                results.append(TaskResponse(id=task_id, **task_data))

        # Get shopping lists
        for list_id, list_data in self.shopping_lists.items():
            if list_data["user_id"] == user_id:
                results.append(ShoppingListResponse(id=list_id, **list_data))

        # Get calendar events
        for event_id, event_data in self.calendar_events.items():
            if event_data["user_id"] == user_id:
                results.append(CalendarEventResponse(id=event_id, **event_data))

        # Sort by created_at
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results


# Global database instance
db = Database()
