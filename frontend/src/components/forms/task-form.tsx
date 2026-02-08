'use client';

import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { taskClient, Task } from '@/lib/api/task-client';
import { useAuth } from '@/app/providers/auth-provider';

interface TaskFormData {
  title: string;
  description?: string;
  due_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
}

interface TaskFormProps {
  mode?: 'create' | 'edit';
  initialData?: Task;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function TaskForm({
  mode = 'create',
  initialData,
  onSuccess,
  onCancel
}: TaskFormProps) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<TaskFormData>({
    defaultValues: mode === 'edit' && initialData ? {
      title: initialData.title,
      description: initialData.description || '',
      due_date: initialData.due_date || '',
      priority: initialData.priority,
      tags: initialData.tags || '',
      recursion_pattern: initialData.recursion_pattern || '',
    } : {
      priority: 'Medium'
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const router = useRouter();
  const { session } = useAuth();

  const onSubmit = async (data: TaskFormData) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (!session.userId) {
        throw new Error('User not authenticated');
      }

      const userId = parseInt(session.userId);

      if (mode === 'create') {
        await taskClient.createTask(userId, {
          title: data.title,
          description: data.description || undefined,
          due_date: data.due_date || undefined,
          priority: data.priority,
          tags: data.tags || undefined,
          recursion_pattern: data.recursion_pattern || undefined,
        });
        setSuccess('Task created successfully!');
      } else {
        if (!initialData?.id) {
          throw new Error('Task ID is required for editing');
        }
        await taskClient.updateTask(userId, initialData.id, {
          title: data.title,
          description: data.description || undefined,
          due_date: data.due_date || undefined,
          priority: data.priority,
          tags: data.tags || undefined,
          recursion_pattern: data.recursion_pattern || undefined,
        });
        setSuccess('Task updated successfully!');
      }

      reset();

      if (onSuccess) {
        setTimeout(() => onSuccess(), 1500);
      } else {
        setTimeout(() => router.push('/dashboard'), 1500);
      }
    } catch (err: any) {
      const errorMessage = err.message || `Failed to ${mode} task. Please try again.`;
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <h1 className="text-2xl font-bold mb-6">
        {mode === 'create' ? 'Create New Task' : 'Edit Task'}
      </h1>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="title"
          type="text"
          {...register('title', {
            required: 'Title is required',
            maxLength: {
              value: 200,
              message: 'Title must be less than 200 characters'
            }
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter task title"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          rows={4}
          {...register('description', {
            maxLength: {
              value: 1000,
              message: 'Description must be less than 1000 characters'
            }
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter task description (optional)"
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-1">
          Due Date
        </label>
        <input
          id="due_date"
          type="date"
          {...register('due_date')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
          Priority <span className="text-red-500">*</span>
        </label>
        <select
          id="priority"
          {...register('priority', { required: 'Priority is required' })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
        {errors.priority && (
          <p className="mt-1 text-sm text-red-600">{errors.priority.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
          Tags
        </label>
        <input
          id="tags"
          type="text"
          {...register('tags')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter tags separated by commas (optional)"
        />
        <p className="mt-1 text-xs text-gray-500">Example: work, urgent, personal</p>
      </div>

      <div>
        <label htmlFor="recursion_pattern" className="block text-sm font-medium text-gray-700 mb-1">
          Recursion Pattern
        </label>
        <input
          id="recursion_pattern"
          type="text"
          {...register('recursion_pattern')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter recursion pattern (optional)"
        />
        <p className="mt-1 text-xs text-gray-500">Example: daily, weekly, monthly</p>
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Saving...' : (mode === 'create' ? 'Create Task' : 'Update Task')}
        </button>
        <button
          type="button"
          onClick={handleCancel}
          className="px-6 py-3 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}