import os
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.models import (
    ProcessedTask,
    ProcessedBrainDump,
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

    async def process_brain_dump(self, text: str) -> ProcessedBrainDump:
        """
        Process a brain dump and extract all tasks, shopping items, and calendar events

        Args:
            text: The user's brain dump text

        Returns:
            ProcessedBrainDump containing lists of tasks, shopping items, and calendar events
        """
        parser = PydanticOutputParser(pydantic_object=ProcessedBrainDump)
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI assistant helping busy parents organize their mental load.

Your job is to extract ALL items from the user's brain dump and categorize them into:
1. **Tasks** - Things to do, actions to complete
2. **Shopping Items** - Things to buy, groceries
3. **Calendar Events** - Time-specific appointments, scheduled activities

IMPORTANT: A single brain dump can contain MULTIPLE categories and MULTIPLE items.

BRAIN DUMP EXAMPLES:
- "Call the babysitter and buy milk" → 1 task + 1 shopping item
- "Buy eggs, milk, and bread" → 3 shopping items
- "Call dentist, schedule car appointment, and pick up dry cleaning" → 3 tasks
- "Soccer practice Thursday at 4pm and dentist appointment Friday at 2pm" → 2 calendar events

TASK PROCESSING:
For each task:
1. Extract a clear, concise description (5-10 words max)
2. Extract due date if mentioned (YYYY-MM-DD format)
3. Decide whether to decompose into subtasks
4. If decomposing, create 3-7 concrete subtasks
5. Estimate time for the task (or sum of subtasks if decomposed)

TASK DECOMPOSITION CRITERIA:
- Decompose if the task is complex and involves multiple distinct steps
- Decompose if the task would take more than 30 minutes to complete
- Decompose if breaking it down would make it less overwhelming
- DO NOT decompose simple, straightforward tasks that can be done in one action
- DO NOT decompose if the task is already specific and clear

TASK DECOMPOSITION EXAMPLES:

Simple tasks (DO NOT decompose):
- "Call the dentist to reschedule appointment" → Single 5-minute action
- "Update emergency contact form for school" → Already specific
- "Send email to teacher about field trip" → Single action
- "Pick up dry cleaning" → Simple errand
- "Call the babysitter" → Single phone call

Complex tasks (SHOULD decompose):
- "Plan Noah's birthday party" → Multiple steps:
  * Create guest list
  * Book venue or plan location
  * Order birthday cake
  * Buy decorations
  * Send invitations
  * Plan activities/games

- "Organize garage for spring cleaning" → Multiple steps:
  * Sort items into keep/donate/trash
  * Take donation items to charity
  * Clean garage floor and walls
  * Reorganize remaining items
  * Install new storage solutions

- "Prepare for Mae's school presentation" → Multiple steps:
  * Research presentation topic
  * Create slides or poster
  * Practice presentation
  * Prepare materials needed

SUBTASK GUIDELINES (if decomposing):
- Create 3-7 subtasks (not too many, not too few)
- Order subtasks logically (what needs to happen first)
- Each subtask should be a concrete, actionable step
- Estimate time for each subtask realistically
- Distribute parent task's due_date across subtasks if provided

TIME ESTIMATION GUIDELINES:
- Simple phone calls: 5-15 minutes
- Quick errands: 15-30 minutes
- Planning tasks: 30-120 minutes
- Research tasks: 30-90 minutes
- Organization tasks: 60-180 minutes

SHOPPING ITEMS:
- Extract each item separately
- Include quantities if specified
- Keep descriptions concise

CALENDAR EVENTS:
- Extract description (5-10 words max)
- Event date (YYYY-MM-DD format) - REQUIRED
- Event time (HH:MM 24-hour format) if mentioned

Current date: {today}

{format_instructions}""",
                ),
                ("human", "{input}"),
            ]
        )

        try:
            chain = prompt | self.llm | parser
            result = await chain.ainvoke(
                {
                    "input": text,
                    "today": today,
                    "format_instructions": parser.get_format_instructions(),
                }
            )
            return result

        except Exception as e:
            print(f"Error processing brain dump: {e}")
            # Fallback: treat as simple task
            return ProcessedBrainDump(
                tasks=[
                    ProcessedTask(
                        description=text[:100] + ("..." if len(text) > 100 else ""),
                        due_date=None,
                        estimated_time_minutes=15,
                        should_decompose=False,
                        reasoning="Error occurred during processing",
                        subtasks=[],
                    )
                ],
                shopping_items=[],
                calendar_events=[],
            )
