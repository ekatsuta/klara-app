import type { CalendarEventResponse } from '@/types';

export class CalendarEvent {
  id: number;
  userId: number;
  description: string;
  eventDate: string;
  eventTime?: string;
  rawInput: string;
  createdAt: Date;

  constructor(data: CalendarEventResponse) {
    this.id = data.id;
    this.userId = data.user_id;
    this.description = data.description;
    this.eventDate = data.event_date;
    this.eventTime = data.event_time;
    this.rawInput = data.raw_input;
    this.createdAt = new Date(data.created_at);
  }
}
