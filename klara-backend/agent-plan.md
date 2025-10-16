# Smart Task Decomposition with LangGraph

## Overview

This document outlines the implementation plan for adding AI agent-based task decomposition to the Klara backend. This feature will allow users to input complex tasks (e.g., "Plan Noah's birthday party") and have an AI agent automatically break them down into manageable subtasks.

## Goals

1. **Simple to start** - Basic decomposition that works well
2. **Easy to optimize** - Architecture that can be improved incrementally
3. **Frontend-friendly** - Clear, structured output for UI display
4. **Maintainable** - Separate concerns, testable components

## Architecture Overview

### Integration with Existing Brain Dump Flow

Instead of creating a separate endpoint, we'll enhance the existing `POST /brain-dumps` endpoint to intelligently handle task decomposition.

```
User Input: "Plan Noah's birthday party"
    ↓
[Brain Dump Request] → POST /brain-dumps
    ↓
[AIService] Step 1: Detect category → "task"
    ↓
[AIService] Step 2: Analyze task complexity
    ↓
Decision: Is this a complex task that needs decomposition?
    ├─ No → Process as single task (existing flow)
    │         ↓
    │      Save to tasks table
    │         ↓
    │      Return TaskResponse
    │
    └─ Yes → Use Task Decomposition Agent
              ↓
         [LangGraph Agent] → Generate subtasks
              ↓
         Save parent task + subtasks to database
              ↓
         Return TaskResponse (with subtasks)
```

### Why This Approach?

1. **Seamless UX** - Users don't need to know about decomposition, it just happens
2. **Smart defaults** - Agent decides when decomposition adds value
3. **Backward compatible** - Simple tasks still work as before
4. **Single endpoint** - Frontend only needs to handle one endpoint
5. **Consistent flow** - All brain dumps go through same categorization

## Data Models

### Agent Internal Model (not exposed to API)
```python
DecomposedTask:
  - should_decompose: bool        # Agent's decision
  - reasoning: str                # Why/how agent made decision
  - subtasks: List[SubTask]       # Empty if not decomposed
  - total_estimated_time: int     # Total time estimate in minutes

SubTask:
  - description: str              # What needs to be done
  - order: int                    # Sequence (1, 2, 3...)
  - estimated_time_minutes: int   # Time estimate (optional)
  - due_date: Optional[str]       # Due date if applicable
```

### Updated API Response Model (TaskResponse)
```python
TaskResponse:
  - id: int                       # Database ID
  - user_id: int
  - description: str              # Task description
  - due_date: Optional[str]       # Due date in YYYY-MM-DD format
  - estimated_time_minutes: Optional[int]  # NEW: Time estimate from LLM
  - completed: bool               # NEW: Task completion status
  - raw_input: str                # Original user input
  - subtasks: Optional[List[SubTaskResponse]]  # NEW: null if no decomposition
  - created_at: datetime

SubTaskResponse:
  - id: int                       # Database ID
  - parent_task_id: int           # Links to parent
  - description: str
  - order: int                    # Display order
  - estimated_time_minutes: Optional[int]
  - due_date: Optional[str]
  - completed: bool               # Task completion status
  - created_at: datetime
```

### Updated ShoppingItemResponse
```python
ShoppingItemResponse:
  - id: int
  - user_id: int
  - description: str
  - completed: bool               # NEW: Completion status
  - raw_input: str
  - created_at: datetime
```

## Database Schema Changes

### New Table: `subtasks`
```sql
CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    parent_task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    order INTEGER NOT NULL,
    estimated_time_minutes INTEGER,
    due_date DATE,
    completed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_subtasks_parent_task_id ON subtasks(parent_task_id);
```

### Updates to existing tables
```sql
-- Add completion status and time estimate to tasks
ALTER TABLE tasks ADD COLUMN completed BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE tasks ADD COLUMN estimated_time_minutes INTEGER;

-- Add completion status to shopping_items
ALTER TABLE shopping_items ADD COLUMN completed BOOLEAN DEFAULT FALSE NOT NULL;
```

**Note:** No `is_decomposed` column needed - presence of subtasks indicates decomposition.

## Agent Implementation

### Phase 1: Intelligent Agent with Decision-Making (MVP)

**File:** `app/task_decomposition_agent.py`

The agent will use LangGraph to:
1. **Analyze** the task description
2. **Decide** if decomposition is needed (using agent reasoning)
3. **Generate** subtasks if needed, OR estimate time if simple
4. **Structure** output with consistent format

**Agent Flow:**
```
Input: "Plan Noah's birthday party"
    ↓
Agent State:
  - task_description: str
  - should_decompose: bool
  - reasoning: str
  - subtasks: List[SubTask]
  - estimated_time_minutes: int
    ↓
Agent Node 1: Analyze & Decide
  LLM analyzes task and decides:
  - Is this a multi-step complex task? → should_decompose = True
  - Or a simple single-action task? → should_decompose = False
  - Estimate time in both cases
    ↓
Conditional Edge: should_decompose?
    ↓                           ↓
  YES                         NO
    ↓                           ↓
Agent Node 2a:              Agent Node 2b:
Generate Subtasks           Return Simple Task
  - Break down task           - Just estimated time
  - Create 3-7 subtasks       - No subtasks
  - Estimate each step
    ↓                           ↓
    └──────────┬────────────────┘
               ↓
            END Node
               ↓
Return DecomposedTask to AIService
```

### Phase 2: Future Optimizations (Not Implemented Yet)

**Smart Context Integration:**
- Check user's calendar for availability
- Consider existing tasks and priorities
- Use user preferences (morning person, batch similar tasks, etc.)

**Intelligent Ordering:**
- Identify dependencies between subtasks
- Suggest parallel vs sequential execution
- Optimize based on user's schedule

**Adaptive Complexity:**
- Simple tasks → don't decompose
- Medium tasks → 3-5 subtasks
- Complex tasks → nested decomposition

**Learning from User Behavior:**
- Track which subtasks users complete
- Learn typical time estimates per task type
- Personalize decomposition style

## API Endpoint Updates

### Updated Endpoint: `POST /brain-dumps`

**No changes to request format** - uses existing `BrainDumpRequest`

**Request:**
```json
{
  "text": "Plan Noah's birthday party",
  "user_id": 123
}
```

**Response (complex task with decomposition):**
```json
{
  "id": 456,
  "user_id": 123,
  "description": "Plan Noah's birthday party",
  "due_date": null,
  "estimated_time_minutes": 240,
  "completed": false,
  "raw_input": "Plan Noah's birthday party",
  "subtasks": [
    {
      "id": 789,
      "parent_task_id": 456,
      "description": "Create and send invitations",
      "order": 1,
      "estimated_time_minutes": 30,
      "due_date": "2025-10-18",
      "completed": false,
      "created_at": "2025-10-15T11:00:00Z"
    },
    {
      "id": 790,
      "parent_task_id": 456,
      "user_id": 123,
      "description": "Order birthday cake",
      "order": 2,
      "estimated_time_minutes": 15,
      "due_date": "2025-10-20",
      "completed": false,
      "created_at": "2025-10-15T11:00:00Z"
    },
    {
      "id": 791,
      "parent_task_id": 456,
      "user_id": 123,
      "description": "Buy decorations and party supplies",
      "order": 3,
      "estimated_time_minutes": 60,
      "due_date": "2025-10-22",
      "completed": false,
      "created_at": "2025-10-15T11:00:00Z"
    },
    {
      "id": 792,
      "parent_task_id": 456,
      "user_id": 123,
      "description": "Plan party activities and games",
      "order": 4,
      "estimated_time_minutes": 45,
      "due_date": "2025-10-23",
      "completed": false,
      "created_at": "2025-10-15T11:00:00Z"
    },
    {
      "id": 793,
      "parent_task_id": 456,
      "user_id": 123,
      "description": "Set up party space day-of",
      "order": 5,
      "estimated_time_minutes": 90,
      "due_date": "2025-10-25",
      "completed": false,
      "created_at": "2025-10-15T11:00:00Z"
    }
  ],
  "created_at": "2025-10-15T11:00:00Z"
}
```

**Response (simple task, no decomposition):**
```json
{
  "id": 457,
  "user_id": 123,
  "description": "Call the dentist to reschedule appointment",
  "due_date": null,
  "estimated_time_minutes": 5,
  "completed": false,
  "raw_input": "Call the dentist to reschedule appointment",
  "subtasks": null,
  "created_at": "2025-10-15T11:05:00Z"
}
```

## Frontend Display Recommendations

### Option 1: Expandable Card (Recommended for MVP)
```
┌─────────────────────────────────────────┐
│ 🎉 Plan Noah's birthday party          │
│ ⏱️  Total: 4 hours                      │
│                                         │
│ [Show Subtasks ▼]                      │
└─────────────────────────────────────────┘

When expanded:
┌─────────────────────────────────────────┐
│ 🎉 Plan Noah's birthday party          │
│ ⏱️  Total: 4 hours                      │
│                                         │
│ [Hide Subtasks ▲]                      │
│                                         │
│ Why this breakdown:                     │
│ "This is a multi-faceted event..."     │
│                                         │
│ ☐ 1. Create and send invitations       │
│      📅 Due: Oct 18 | ⏱️  30 min        │
│                                         │
│ ☐ 2. Order birthday cake                │
│      📅 Due: Oct 20 | ⏱️  15 min        │
│                                         │
│ ☐ 3. Buy decorations and supplies      │
│      📅 Due: Oct 22 | ⏱️  1 hour        │
│                                         │
│ ☐ 4. Plan party activities              │
│      📅 Due: Oct 23 | ⏱️  45 min        │
│                                         │
│ ☐ 5. Set up party space                 │
│      📅 Due: Oct 25 | ⏱️  1.5 hours     │
└─────────────────────────────────────────┘
```

### Option 2: Timeline View
Show subtasks on a timeline based on due dates

### Option 3: Kanban Board
Drag subtasks through "To Do", "In Progress", "Done"

## Implementation Steps

### Step 1: Update Data Models ✅ (First)
- Update `TaskResponse` in `app/models.py` (add `estimated_time_minutes`, `completed`, `subtasks`)
- Update `ShoppingItemResponse` in `app/models.py` (add `completed`)
- Add task decomposition models to `app/models.py` (DecomposedTask, SubTask, SubTaskResponse)
- Update SQLAlchemy models in `app/db_models.py`:
  - Add `completed` and `estimated_time_minutes` to Task model
  - Add `completed` to ShoppingItem model
  - Create new SubTask model

### Step 2: Database Migration ✅ (Second)
- Create `subtasks` table
- Add `completed` and `estimated_time_minutes` columns to `tasks`
- Add `completed` column to `shopping_items`
- Create necessary indexes

### Step 3: Database Access Layer
- Create `app/access/subtask_access.py`
- CRUD operations for subtasks

### Step 4: Agent Service
- Create `app/task_decomposition_agent.py`
- Implement LangGraph agent
- Define agent nodes and workflow
- Add prompt templates

### Step 5: Update Existing AI Service
- Modify `app/ai_service.py`:
  - Call task decomposition agent for all tasks
  - Agent decides whether to decompose internally
  - Return DecomposedTask result

### Step 6: Update Brain Dumps Endpoint
- Modify `app/routes/brain_dumps.py`:
  - Handle saving parent task with optional subtasks
  - Update task creation logic to save estimated_time_minutes and completed fields
  - No response type changes needed (still returns TaskResponse)

### Step 7: Testing
- Test with simple tasks (should work as before)
- Test with complex tasks (should decompose)
- Verify database operations
- Check response formats

## LangGraph Agent Details

### Agent State
```python
class TaskDecompositionState(TypedDict):
    task_description: str
    context: dict
    subtasks: List[SubTask]
    reasoning: str
    should_decompose: bool
```

### Agent Nodes

**Node 1: Analyze Task**
- Input: Task description
- Logic: Determine if task is complex enough to decompose
- Output: `should_decompose` boolean

**Node 2: Decompose Task**
- Input: Task description, context
- LLM Call: Generate subtasks with Claude
- Output: List of SubTask objects + reasoning

**Node 3: End**
- Return final state

### Agent Graph (Phase 1 - With Intelligent Decision Making)
```
START → analyze_and_decide → [should_decompose?]
                                    ↓ yes               ↓ no
                            generate_subtasks     estimate_simple_task
                                    ↓                    ↓
                                    └──────┬─────────────┘
                                           ↓
                                         END
```

**Node Details:**

1. **analyze_and_decide**: Agent uses LLM to analyze task complexity
   - Input: task_description
   - Output: should_decompose (bool), reasoning (str)
   - Decision criteria:
     - Multi-step? → decompose
     - Single action? → simple
   - Examples:
     - "Call dentist" → should_decompose = False
     - "Plan birthday party" → should_decompose = True

2. **generate_subtasks**: LLM breaks down complex task
   - Input: task_description
   - Output: subtasks (List[SubTask]), estimated_time_minutes (int)
   - Creates 3-7 ordered subtasks with individual time estimates
   - Total time = sum of all subtask times

3. **estimate_simple_task**: LLM estimates time for simple task
   - Input: task_description
   - Output: estimated_time_minutes (int)
   - No subtasks created
   - Returns single time estimate

### Integration Point in AIService

The existing `ai_service.py` flow will be updated:

```python
async def process_brain_dump(self, text: str):
    # Step 1: Detect category (EXISTING)
    category = await self._detect_category(text)

    # Step 2: Process based on category
    if category == "task":
        # Use agent for all tasks - agent decides whether to decompose
        from app.task_decomposition_agent import TaskDecompositionAgent
        agent = TaskDecompositionAgent()
        return await agent.analyze_and_process(text)

    elif category == "shopping_list":
        # Process shopping items
        return await self._process_shopping_items(text)

    elif category == "calendar_event":
        # Process calendar event
        return await self._process_calendar_event(text)
```

### Prompt Template (Node 2)
```
You are an AI assistant helping busy parents manage their mental load.

Your task is to break down a complex task into 3-7 concrete, actionable subtasks.

Task: {task_description}
Context: {context}

Guidelines:
1. Create subtasks that are specific and actionable
2. Order them logically (what needs to happen first)
3. Estimate realistic time for each (in minutes)
4. Suggest due dates if the task has time sensitivity
5. Keep descriptions concise (5-10 words)

Format your response as JSON matching this structure:
{{
  "reasoning": "Brief explanation of your breakdown approach",
  "subtasks": [
    {{
      "description": "First action to take",
      "order": 1,
      "estimated_time_minutes": 30,
      "due_date": "2025-10-18"
    }},
    ...
  ]
}}
```

## Cost Considerations

**Per Decomposition:**
- 1 LLM call to Claude (~500-1000 tokens input, ~500-1500 tokens output)
- Estimated cost: $0.005-0.015 per decomposition

**Optimization Strategies:**
1. Cache common task patterns
2. Use smaller model for simple tasks
3. Implement rate limiting per user
4. Add "smart decomposition" toggle (user can disable)

## Error Handling

1. **LLM fails to generate valid JSON**
   - Retry with stricter prompt
   - Fallback: Create single subtask with original description

2. **Database error**
   - Roll back transaction
   - Return error to user with clear message

3. **Agent timeout**
   - Set 30-second timeout
   - Fallback to basic task creation

4. **Invalid input**
   - Validate task description length (min 10 chars)
   - Return 400 error with helpful message

## Success Metrics

1. **User Engagement**
   - % of users who try decomposition
   - % who complete decomposed tasks vs regular tasks

2. **Quality**
   - User ratings of decomposition quality
   - % of subtasks that users modify/delete

3. **Performance**
   - Average response time (<3 seconds target)
   - Error rate (<1% target)

## Future Enhancements

### Phase 2
- [ ] Smart context: Check user's calendar
- [ ] Learn from user edits to subtasks
- [ ] Suggest decomposition for likely complex tasks

### Phase 3
- [ ] Multi-agent collaboration (planning agent + scheduling agent)
- [ ] Integration with external APIs (recipes, stores, etc.)
- [ ] Nested decomposition for very complex tasks

### Phase 4
- [ ] Proactive suggestions: "I noticed you haven't started the party planning. Want me to break it down?"
- [ ] Smart reminders based on subtask urgency
- [ ] Family coordination: Assign subtasks to family members

## Technical Debt to Monitor

1. **Agent state management** - Currently stateless; may need persistence for complex flows
2. **Prompt versioning** - Track prompt changes and performance
3. **Model selection** - Currently hardcoded to Claude Sonnet; may want dynamic selection
4. **Caching layer** - No caching yet; consider Redis for repeated patterns

## Questions for Future Consideration

1. Should we allow users to manually trigger decomposition on existing tasks?
2. How should we handle tasks that are already partially complete?
3. Should subtasks be independently editable/deletable?
4. Do we want a "suggest more subtasks" feature?
5. Should we support nested subtasks (subtask of a subtask)?

---

**Status:** Ready for implementation
**Author:** Claude Code
**Date:** 2025-10-15
**Version:** 1.0
