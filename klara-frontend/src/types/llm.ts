export interface SubTaskResponse {
  id: number;
  parent_task_id: number;
  description: string;
  estimated_time_minutes?: number;
  due_date?: string;
  order: number;
  completed: boolean;
  created_at: string;
}

export interface TaskResponse {
  id: number;
  user_id: number;
  description: string;
  due_date?: string;
  estimated_time_minutes?: number;
  completed: boolean;
  raw_input: string;
  subtasks?: SubTaskResponse[];
  created_at: string;
}

export interface ShoppingItemResponse {
  id: number;
  user_id: number;
  description: string;
  completed: boolean;
  raw_input: string;
  created_at: string;
}

export interface CalendarEventResponse {
  id: number;
  user_id: number;
  description: string;
  event_date: string;
  event_time?: string;
  raw_input: string;
  created_at: string;
}

export interface BrainDumpResponse {
  tasks: TaskResponse[];
  shopping_items: ShoppingItemResponse[];
  calendar_events: CalendarEventResponse[];
}
