'use client';

import { useAuth } from '@/app/providers/auth-provider';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

export default function Header() {
  const { session, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const linkClass = (path: string) => {
    const baseClass = "px-3 py-2 rounded-md text-sm font-medium transition-colors";
    const activeClass = "bg-blue-100 text-blue-700";
    const inactiveClass = "text-gray-700 hover:bg-gray-100 hover:text-gray-900";
    return `${baseClass} ${pathname === path ? activeClass : inactiveClass}`;
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/">
              <h1 className="text-xl font-semibold text-gray-900">Todo App</h1>
            </Link>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1">
            <Link href="/" className={linkClass('/')}>
              Home
            </Link>

            {session.isLoggedIn ? (
              <>
                <Link href="/dashboard" className={linkClass('/dashboard')}>
                  Dashboard
                </Link>
                <Link href="/tasks/new" className={linkClass('/tasks/new')}>
                  Add Task
                </Link>
              </>
            ) : (
              <>
                <Link href="/login" className={linkClass('/login')}>
                  Login
                </Link>
                <Link href="/signup" className={linkClass('/signup')}>
                  Signup
                </Link>
              </>
            )}
          </nav>

          {/* User Info & Logout (Logged-in only) */}
          {session.isLoggedIn && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {session.username || session.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}