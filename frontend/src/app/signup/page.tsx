import SignupForm from '@/components/forms/signup-form';
import Container from '@/components/layouts/container';
import Link from 'next/link';

export default function SignupPage() {
  return (
    <Container className="flex items-center justify-center min-h-[60vh]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Create an Account</h1>
          <p className="text-gray-600 mt-2">
            Get started with your free account today
          </p>
        </div>

        <SignupForm />

        <div className="mt-6 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link href="/login" className="underline underline-offset-4 hover:text-blue-600">
            Sign in
          </Link>
        </div>
      </div>
    </Container>
  );
}
