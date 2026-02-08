'use client';

import WithAuth from '@/components/hoc/with-auth';
import Container from '@/components/layouts/container';
import TaskList from '@/components/lists/task-list';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <WithAuth>
      <Container>
        <div className="space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-2">Manage your tasks efficiently</p>
            </div>
            <Link
              href="/tasks/new"
              className="btn btn-primary"
            >
              Create New Task
            </Link>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-6 text-gray-900">Your Tasks</h2>
            <TaskList />
          </div>
        </div>
      </Container>
    </WithAuth>
  );
}