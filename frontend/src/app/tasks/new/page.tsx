'use client';

import WithAuth from '@/components/hoc/with-auth';
import Container from '@/components/layouts/container';
import TaskForm from '@/components/forms/task-form';

export default function NewTaskPage() {
  return (
    <WithAuth>
      <Container>
        <div className="max-w-2xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Create New Task</h1>
            <p className="text-gray-600 mt-2">Fill in the details to create a new task</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <TaskForm />
          </div>
        </div>
      </Container>
    </WithAuth>
  );
}