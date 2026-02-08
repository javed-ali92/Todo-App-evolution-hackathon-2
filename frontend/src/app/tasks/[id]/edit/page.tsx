'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import TaskForm from '@/components/forms/task-form';
import { taskClient, Task } from '@/lib/api/task-client';
import { useAuth } from '@/app/providers/auth-provider';

export default function EditTaskPage() {
  const router = useRouter();
  const params = useParams();
  const { session } = useAuth();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchTask() {
      try {
        if (!session?.userId) {
          router.push('/login');
          return;
        }

        const taskId = parseInt(params.id as string);
        const userId = parseInt(session.userId);

        const fetchedTask = await taskClient.getTaskById(userId, taskId);
        setTask(fetchedTask);
      } catch (err: any) {
        setError(err.message || 'Failed to load task');
      } finally {
        setLoading(false);
      }
    }

    fetchTask();
  }, [params.id, session, router]);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <p>Loading task...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
        <button
          onClick={() => router.push('/dashboard')}
          className="mt-4 text-blue-600 hover:underline"
        >
          ← Back to Dashboard
        </button>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <p>Task not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <TaskForm
        mode="edit"
        initialData={task}
        onSuccess={() => router.push('/dashboard')}
        onCancel={() => router.push('/dashboard')}
      />
    </div>
  );
}
