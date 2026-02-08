'use client';

import { useAuth } from '@/app/providers/auth-provider';
import { useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';

interface WithAuthProps {
  children: ReactNode;
}

export default function WithAuth({ children }: WithAuthProps) {
  const { session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!session.isLoggedIn) {
      router.push('/login');
    }
  }, [session.isLoggedIn, router]);

  if (!session.isLoggedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}