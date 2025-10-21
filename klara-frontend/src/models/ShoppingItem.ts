import type { ShoppingItemResponse } from '@/types';

export class ShoppingItem {
  id: number;
  userId: number;
  description: string;
  completed: boolean;
  rawInput: string;
  createdAt: Date;

  constructor(data: ShoppingItemResponse) {
    this.id = data.id;
    this.userId = data.user_id;
    this.description = data.description;
    this.completed = data.completed;
    this.rawInput = data.raw_input;
    this.createdAt = new Date(data.created_at);
  }
}
