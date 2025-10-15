import os
from datetime import datetime
from typing import Union, List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from app.models import (
    CategoryDetection,
    ProcessedTask,
    ProcessedShoppingItem,
    ProcessedCalendarEvent,
)


class AIService:
    """Service for processing brain dumps using two-step categorization with Anthropic"""

    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Initialize ChatAnthropic model
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            anthropic_api_key=self.anthropic_api_key,
            temperature=0.3,
            max_tokens=2048,
        )

    async def _detect_category(self, text: str) -> str:
        """Step 1: Detect the category of the brain dump"""
        parser = PydanticOutputParser(pydantic_object=CategoryDetection)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI categorization expert helping parents organize their mental load.

Your ONLY task is to categorize the user's input into ONE of these categories:

Categories:
- task: Something that needs to be done, a to-do item, an action to complete
  Examples: "buy birthday present", "schedule dentist appointment", "call the plumber"

- shopping_list: Items to purchase, groceries, things to buy
  Examples: "need milk and eggs", "get bread, cheese, and butter", "buy new pants for Mae"

- calendar_event: Time-specific events, appointments, scheduled activities
  Examples: "Noah's party next Saturday at 2pm", "doctor appointment on the 15th", "soccer practice Thursday"

Focus ONLY on categorization.

{format_instructions}""",
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm | parser
        result = await chain.ainvoke(
            {"input": text, "format_instructions": parser.get_format_instructions()}
        )

        return result.category

    async def _process_task(self, text: str) -> ProcessedTask:
        """Step 2: Process a task"""
        parser = PydanticOutputParser(pydantic_object=ProcessedTask)
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI assistant helping to structure task information.

Extract the following from the user's input:
1. A clear, concise description (5-10 words max)
2. A due date if mentioned (YYYY-MM-DD format)

Current date is {today}. Use this to calculate relative dates like "tomorrow", "next week", etc.

{format_instructions}""",
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm | parser
        result = await chain.ainvoke(
            {
                "input": text,
                "today": today,
                "format_instructions": parser.get_format_instructions(),
            }
        )

        return result

    async def _process_shopping_items(self, text: str) -> List[ProcessedShoppingItem]:
        """Step 2: Process shopping items"""

        # Helper model for parsing multiple items
        class ShoppingItemsList(BaseModel):
            items: List[ProcessedShoppingItem]

        parser = PydanticOutputParser(pydantic_object=ShoppingItemsList)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                You are an AI assistant helping to structure shopping list information.

                Extract ALL items mentioned in the user's input as separate shopping items.
                For each item, create a clear description that includes quantity if specified.

                Examples:
                - Input: "milk, eggs, and bread"
                  Output: [{{"description": "milk"}}, {{"description": "eggs"}}, {{"description": "bread"}}]

                - Input: "2 gallons of milk and 3 pounds of cheese"
                  Output: [{{"description": "2 gallons of milk"}}, {{"description": "3 pounds of cheese"}}]

                IMPORTANT: Extract EVERY item mentioned, even if they're in a comma-separated list.

                {format_instructions}
                """,
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm | parser
        result = await chain.ainvoke(
            {"input": text, "format_instructions": parser.get_format_instructions()}
        )
        return result.items

    async def _process_calendar_event(self, text: str) -> ProcessedCalendarEvent:
        """Step 2: Process a calendar event"""
        parser = PydanticOutputParser(pydantic_object=ProcessedCalendarEvent)
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI assistant helping to structure calendar event information.

Extract the following from the user's input:
1. A clear event title (5-10 words max)
2. A brief description (1-2 sentences)
3. Event date (YYYY-MM-DD format) - REQUIRED
4. Event time (HH:MM 24-hour format) if mentioned

Current date is {today}. Use this to calculate relative dates like "tomorrow", "next Saturday", etc.

{format_instructions}""",
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm | parser
        result = await chain.ainvoke(
            {
                "input": text,
                "today": today,
                "format_instructions": parser.get_format_instructions(),
            }
        )

        return result

    async def process_brain_dump(
        self, text: str
    ) -> Union[ProcessedTask, List[ProcessedShoppingItem], ProcessedCalendarEvent]:
        """
        Process a brain dump using two-step categorization

        Args:
            text: The user's brain dump text

        Returns:
            Category-specific processed result - single task/event or list of shopping items
        """
        try:
            # Step 1: Detect category
            category = await self._detect_category(text)
            print(f"Detected category: {category}")

            # Step 2: Process based on category
            if category == "task":
                return await self._process_task(text)
            elif category == "shopping_list":
                return await self._process_shopping_items(text)
            elif category == "calendar_event":
                return await self._process_calendar_event(text)
            else:
                raise ValueError(f"Unknown category: {category}")

        except Exception as e:
            print(f"Error processing brain dump: {e}")
            # Fallback to task
            return ProcessedTask(
                description=text[:100] + ("..." if len(text) > 100 else ""),
                due_date=None,
            )
