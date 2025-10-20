-- Klara Backend Database Schema
-- Migration 002: Add subtask model and completion tracking
-- Date: 2025-10-16
-- Alembic Revision: 3aab0895a699

-- Create subtasks table
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

-- Add completion tracking and time estimates to tasks
ALTER TABLE tasks ADD COLUMN estimated_time_minutes INTEGER;
ALTER TABLE tasks ADD COLUMN completed BOOLEAN DEFAULT FALSE NOT NULL;

-- Add completion tracking to shopping items
ALTER TABLE shopping_items ADD COLUMN completed BOOLEAN DEFAULT FALSE NOT NULL;

-- Comments
COMMENT ON TABLE subtasks IS 'Subtasks decomposed from complex parent tasks by AI agent';
COMMENT ON COLUMN tasks.estimated_time_minutes IS 'Estimated time to complete in minutes (from LLM or sum of subtasks)';
COMMENT ON COLUMN tasks.completed IS 'Whether the task has been completed';
COMMENT ON COLUMN shopping_items.completed IS 'Whether the shopping item has been purchased';
