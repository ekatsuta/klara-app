import type { TaskResponse, SubTaskResponse } from '@/types';

export class SubTask {
  id: number;
  parentTaskId: number;
  description: string;
  estimatedTimeMinutes?: number;
  dueDate?: string;
  order: number;
  completed: boolean;
  createdAt: Date;

  constructor(data: SubTaskResponse) {
    this.id = data.id;
    this.parentTaskId = data.parent_task_id;
    this.description = data.description;
    this.estimatedTimeMinutes = data.estimated_time_minutes;
    this.dueDate = data.due_date;
    this.order = data.order;
    this.completed = data.completed;
    this.createdAt = new Date(data.created_at);
  }
}

export class Task {
  id: number;
  userId: number;
  description: string;
  dueDate?: string;
  estimatedTimeMinutes?: number;
  completed: boolean;
  rawInput: string;
  subtasks: SubTask[];
  createdAt: Date;

  constructor(data: TaskResponse) {
    this.id = data.id;
    this.userId = data.user_id;
    this.description = data.description;
    this.dueDate = data.due_date;
    this.estimatedTimeMinutes = data.estimated_time_minutes;
    this.completed = data.completed;
    this.rawInput = data.raw_input;
    this.subtasks = data.subtasks?.map(st => new SubTask(st)) ?? [];
    this.createdAt = new Date(data.created_at);
  }
}
