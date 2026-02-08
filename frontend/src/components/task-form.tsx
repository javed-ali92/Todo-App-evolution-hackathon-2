import React, { useState } from 'react';
import { TaskCreate, taskClient } from '../lib/api/task-client';

interface TaskFormProps {
  userId: number;
  onTaskCreated: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ userId, onTaskCreated }) => {
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [dueDate, setDueDate] = useState<string>('');
  const [priority, setPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
  const [tags, setTags] = useState<string>('');
  const [recursionPattern, setRecursionPattern] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
        due_date: dueDate || undefined,
        priority,
        tags: tags || undefined,
        recursion_pattern: recursionPattern || undefined,
      };

      await taskClient.createTask(userId, taskData);
      // Reset form
      setTitle('');
      setDescription('');
      setDueDate('');
      setPriority('Medium');
      setTags('');
      setRecursionPattern('');
      onTaskCreated(); // Notify parent component to refresh tasks
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="task-form-container">
      <h3>Add New Task</h3>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit} className="task-form">
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter task title"
            disabled={submitting}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter task description (optional)"
            disabled={submitting}
            rows={3}
          />
        </div>

        <div className="form-group">
          <label htmlFor="dueDate">Due Date</label>
          <input
            type="date"
            id="dueDate"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            disabled={submitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as 'High' | 'Medium' | 'Low')}
            disabled={submitting}
          >
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="tags">Tags</label>
          <input
            type="text"
            id="tags"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="Enter tags separated by commas (optional)"
            disabled={submitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="recursionPattern">Recursion Pattern</label>
          <input
            type="text"
            id="recursionPattern"
            value={recursionPattern}
            onChange={(e) => setRecursionPattern(e.target.value)}
            placeholder="Enter recursion pattern (e.g., daily, weekly) (optional)"
            disabled={submitting}
          />
        </div>

        <button type="submit" disabled={submitting} className="submit-btn">
          {submitting ? 'Creating...' : 'Create Task'}
        </button>
      </form>
    </div>
  );
};

export default TaskForm;