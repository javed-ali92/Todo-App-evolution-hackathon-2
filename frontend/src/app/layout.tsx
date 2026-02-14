import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from './providers/auth-provider';
import Header from '../components/ui/header';
import FloatingChatButton from '../components/chat/floating-chat-button';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Todo App - Manage Your Tasks',
  description: 'A clean and minimal task management application built with Next.js',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <Header />
          <main className="min-h-screen">
            {children}
          </main>
          <FloatingChatButton />
        </AuthProvider>
      </body>
    </html>
  );
}