import LoginForm from '@/components/forms/login-form';
import Container from '@/components/layouts/container';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <Container className="flex items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Welcome Back</h1>
          <p className="text-gray-600 mt-2">
            Sign in to your account to continue
          </p>
        </div>

        <LoginForm />

        <div className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link href="/signup" className="underline underline-offset-4 hover:text-blue-600">
            Sign up
          </Link>
        </div>
      </div>
    </Container>
  );
}
