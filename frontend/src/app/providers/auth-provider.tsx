'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface UserSession {
  userId: string | null;
  username: string | null;
  email: string | null;
  isLoggedIn: boolean;
  accessToken: string | null;
  expiryTime: Date | null;
}

interface AuthContextType {
  session: UserSession;
  login: (userData: { userId: string; username: string; email: string; accessToken: string }) => void;
  logout: () => void;
  checkAuthStatus: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [session, setSession] = useState<UserSession>({
    userId: null,
    username: null,
    email: null,
    isLoggedIn: false,
    accessToken: null,
    expiryTime: null,
  });

  const router = useRouter();

  // Check auth status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Check for token expiration
  useEffect(() => {
    if (session.isLoggedIn && session.expiryTime) {
      const interval = setInterval(() => {
        if (new Date() >= session.expiryTime!) {
          logout();
        }
      }, 60000); // Check every minute

      return () => clearInterval(interval);
    }
  }, [session]);

  const login = (userData: { userId: string; username: string; email: string; accessToken: string }) => {
    const expiryTime = new Date();
    expiryTime.setHours(expiryTime.getHours() + 1); // Token expires in 1 hour

    const newSession: UserSession = {
      userId: userData.userId,
      username: userData.username,
      email: userData.email,
      isLoggedIn: true,
      accessToken: userData.accessToken,
      expiryTime: expiryTime,
    };

    setSession(newSession);

    // Store in localStorage
    localStorage.setItem('userSession', JSON.stringify(newSession));
  };

  const logout = () => {
    setSession({
      userId: null,
      username: null,
      email: null,
      isLoggedIn: false,
      accessToken: null,
      expiryTime: null,
    });

    // Remove from localStorage
    localStorage.removeItem('userSession');

    // Redirect to login
    router.push('/login');
  };

  const checkAuthStatus = () => {
    const storedSession = localStorage.getItem('userSession');

    if (storedSession) {
      const parsedSession: UserSession = JSON.parse(storedSession);

      // Check if token is expired
      if (parsedSession.expiryTime && new Date(parsedSession.expiryTime) > new Date()) {
        setSession(parsedSession);
      } else {
        // Token expired, remove it
        localStorage.removeItem('userSession');
        setSession({
          userId: null,
          username: null,
          email: null,
          isLoggedIn: false,
          accessToken: null,
          expiryTime: null,
        });
      }
    }
  };

  return (
    <AuthContext.Provider value={{ session, login, logout, checkAuthStatus }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};