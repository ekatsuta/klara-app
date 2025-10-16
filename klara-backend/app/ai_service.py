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
    SubTask,
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
        """Step 2: Process a task and analyze for decomposition"""
        # Use ProcessedTask directly for LLM parsing
        parser = PydanticOutputParser(pydantic_object=ProcessedTask)
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI task planning assistant helping busy parents manage their mental load.

Your job is to:
1. Extract a clear, concise task description (5-10 words max)
2. Extract a due date if mentioned (YYYY-MM-DD format)
3. Decide whether to decompose the task into subtasks
4. If decomposing, create 3-7 concrete, actionable subtasks
5. Estimate time for the task (or sum of subtasks if decomposed)

DECISION CRITERIA for decomposition:
- Decompose if the task is complex and involves multiple distinct steps
- Decompose if the task would take more than 30 minutes to complete
- Decompose if breaking it down would make it less overwhelming
- DO NOT decompose simple, straightforward tasks that can be done in one action
- DO NOT decompose if the task is already specific and clear

EXAMPLES:

Simple tasks (DO NOT decompose):
- "Call the dentist to reschedule appointment" → Single 5-minute action
- "Update emergency contact form for school" → Already specific
- "Send email to teacher about field trip" → Single action

Complex tasks (SHOULD decompose):
- "Plan Noah's birthday party" → Multiple steps: guest list, venue, cake, decorations, invitations
- "Organize garage for spring cleaning" → Multiple steps: sort items, donate, clean, reorganize
- "Prepare for Mae's school presentation" → Research, create slides, practice

TIME ESTIMATION GUIDELINES:
- Simple phone calls: 5-15 minutes
- Quick errands: 15-30 minutes
- Planning tasks: 30-120 minutes
- Research tasks: 30-90 minutes
- Organization tasks: 60-180 minutes

SUBTASK GUIDELINES (if decomposing):
- Create 3-7 subtasks (not too many, not too few)
- Order subtasks logically (what needs to happen first)
- Each subtask should be a concrete, actionable step
- Estimate time for each subtask realistically

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
            Category-specific processed result - task (with optional subtasks), list of shopping items, or calendar event
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
            # Fallback to simple task without decomposition
            return ProcessedTask(
                description=text[:100] + ("..." if len(text) > 100 else ""),
                due_date=None,
                estimated_time_minutes=15,
                should_decompose=False,
                reasoning="Error occurred during processing",
                subtasks=[],
            )
