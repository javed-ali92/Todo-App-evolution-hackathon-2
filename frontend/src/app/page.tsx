'use client';

import { useAuth } from './providers/auth-provider';
import Link from 'next/link';

export default function HomePage() {
  const { session } = useAuth();

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to Todo App{session.isLoggedIn && `, ${session.username || session.email}`}
        </h1>
        <p className="text-xl text-gray-600">Your personal task management system</p>
      </header>

      <main>
        <section className="text-center mb-16">
          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/signup" className="btn btn-primary">
              Sign Up
            </Link>
            <Link href="/login" className="btn btn-secondary">
              Log In
            </Link>
          </div>
        </section>

        <section className="bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Features</h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Create and manage your personal tasks
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Mark tasks as complete/incomplete
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Delete tasks when completed
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Secure authentication
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Responsive design for all devices
            </li>
          </ul>
        </section>
      </main>
    </div>
  );
}