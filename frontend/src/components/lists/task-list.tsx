'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { taskClient, Task } from '@/lib/api/task-client';
import { useAuth } from '@/app/providers/auth-provider';

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const { session } = useAuth();

  const fetchTasks = async () => {
    if (!session.userId) return;

    setLoading(true);
    setError('');

    try {
      const userTasks = await taskClient.getUserTasks(parseInt(session.userId));
      setTasks(userTasks);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load tasks';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (session.isLoggedIn && session.userId) {
      fetchTasks();
    }
  }, [session.isLoggedIn, session.userId]);

  const handleToggleComplete = async (taskId: number) => {
    if (!session.userId) return;

    try {
      await taskClient.toggleTaskCompletion(parseInt(session.userId), taskId);
      // Refresh tasks after toggling
      await fetchTasks();
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update task';
      setError(errorMessage);
    }
  };

  const handleDelete = async (taskId: number) => {
    if (!session.userId) return;

    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await taskClient.deleteTask(parseInt(session.userId), taskId);
      // Refresh tasks after deletion
      await fetchTasks();
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete task';
      setError(errorMessage);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-600">Loading tasks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        {error}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">No tasks yet. Create your first task to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <div
          key={task.id}
          className={`bg-white border rounded-lg p-4 transition-all ${
            task.completed ? 'bg-green-50 border-green-200' : 'border-gray-200'
          }`}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => handleToggleComplete(task.id)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <h3
                  className={`text-lg font-semibold ${
                    task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                  }`}
                >
                  {task.title}
                </h3>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded ${
                    task.priority === 'High'
                      ? 'bg-red-100 text-red-800'
                      : task.priority === 'Medium'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  {task.priority}
                </span>
              </div>

              {task.description && (
                <p className="text-gray-600 mb-2 ml-8">{task.description}</p>
              )}

              <div className="flex flex-wrap gap-4 text-sm text-gray-500 ml-8">
                {task.due_date && (
                  <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                )}
                {task.tags && (
                  <span>Tags: {task.tags}</span>
                )}
                {task.recursion_pattern && (
                  <span>Recurs: {task.recursion_pattern}</span>
                )}
              </div>
            </div>

            <div className="flex gap-2">
              <Link href={`/tasks/${task.id}/edit`}>
                <button
                  className="px-3 py-1 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
                >
                  Edit
                </button>
              </Link>
              <button
                onClick={() => handleDelete(task.id)}
                className="px-3 py-1 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}