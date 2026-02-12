'use client';

import LoginForm from '@/components/forms/login-form';
import Container from '@/components/layouts/container';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');

        .login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
          position: relative;
          overflow: hidden;
        }

        .login-background {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
          z-index: -2;
        }

        .login-background::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: 
            radial-gradient(circle at 20% 50%, rgba(255, 107, 157, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(78, 205, 196, 0.15) 0%, transparent 50%);
          animation: morph 20s ease-in-out infinite;
        }

        @keyframes morph {
          0%, 100% { 
            background: 
              radial-gradient(circle at 20% 50%, rgba(255, 107, 157, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(78, 205, 196, 0.15) 0%, transparent 50%);
          }
          50% { 
            background: 
              radial-gradient(circle at 80% 30%, rgba(255, 107, 157, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 20% 70%, rgba(78, 205, 196, 0.15) 0%, transparent 50%);
          }
        }

        .floating-orbs {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: -1;
        }

        .orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(80px);
          opacity: 0.3;
          animation: float 20s ease-in-out infinite;
        }

        .orb-1 {
          top: 10%;
          left: 20%;
          width: 400px;
          height: 400px;
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          animation-delay: 0s;
        }

        .orb-2 {
          bottom: 20%;
          right: 10%;
          width: 500px;
          height: 500px;
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          animation-delay: 5s;
        }

        .orb-3 {
          top: 50%;
          left: 50%;
          width: 300px;
          height: 300px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          animation-delay: 10s;
          transform: translate(-50%, -50%);
        }

        @keyframes float {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(50px, -50px); }
          66% { transform: translate(-30px, 30px); }
        }

        .login-card {
          background: rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(30px);
          border: 1px solid rgba(255, 255, 255, 0.18);
          border-radius: 32px;
          padding: 3rem 2.5rem;
          width: 100%;
          max-width: 480px;
          box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.37),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
          position: relative;
          overflow: hidden;
          animation: slideUp 0.6s ease-out;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(50px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .login-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
          animation: shimmer 3s ease-in-out infinite;
        }

        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }

        .login-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }

        .login-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: rgba(255, 255, 255, 0.12);
          backdrop-filter: blur(10px);
          padding: 6px 16px;
          border-radius: 50px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: rgba(255, 255, 255, 0.9);
          font-size: 0.85rem;
          font-weight: 500;
          margin-bottom: 1.5rem;
          animation: fadeIn 0.8s ease-out 0.2s both;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .login-badge::before {
          content: '🔐';
          font-size: 1rem;
        }

        .login-title {
          font-family: 'Syne', sans-serif;
          font-size: 2.5rem;
          font-weight: 800;
          background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.75rem;
          letter-spacing: -0.02em;
          animation: fadeIn 0.8s ease-out 0.3s both;
        }

        .login-subtitle {
          color: rgba(255, 255, 255, 0.8);
          font-size: 1.05rem;
          font-weight: 400;
          line-height: 1.6;
          animation: fadeIn 0.8s ease-out 0.4s both;
        }

        .form-wrapper {
          animation: fadeIn 0.8s ease-out 0.5s both;
        }

        .login-footer {
          margin-top: 2rem;
          text-align: center;
          color: rgba(255, 255, 255, 0.75);
          font-size: 0.95rem;
          animation: fadeIn 0.8s ease-out 0.6s both;
        }

        .login-footer a {
          color: #FFE66D;
          text-decoration: none;
          font-weight: 600;
          transition: all 0.3s ease;
          position: relative;
        }

        .login-footer a::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(90deg, #FFE66D, #FF6B9D);
          transform: scaleX(0);
          transform-origin: right;
          transition: transform 0.3s ease;
        }

        .login-footer a:hover::after {
          transform: scaleX(1);
          transform-origin: left;
        }

        .login-footer a:hover {
          color: #FF6B9D;
        }

        .decorative-dots {
          position: absolute;
          width: 100%;
          height: 100%;
          top: 0;
          left: 0;
          pointer-events: none;
          opacity: 0.1;
          z-index: 0;
        }

        .decorative-dots::before,
        .decorative-dots::after {
          content: '';
          position: absolute;
          width: 150px;
          height: 150px;
          background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 1px, transparent 1px);
          background-size: 15px 15px;
        }

        .decorative-dots::before {
          top: -20px;
          right: -20px;
          transform: rotate(15deg);
        }

        .decorative-dots::after {
          bottom: -20px;
          left: -20px;
          transform: rotate(-15deg);
        }

        @media (max-width: 640px) {
          .login-card {
            padding: 2rem 1.5rem;
            border-radius: 24px;
          }

          .login-title {
            font-size: 2rem;
          }

          .login-subtitle {
            font-size: 0.95rem;
          }
        }
      `}</style>

      <div className="login-background"></div>
      <div className="floating-orbs">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <Container className="login-container">
        <div className="login-card">
          <div className="decorative-dots"></div>
          
          <div className="login-header">
            <div className="login-badge">
              Secure Login
            </div>
            <h1 className="login-title">Welcome Back</h1>
            <p className="login-subtitle">
              Sign in to your account to continue your productivity journey
            </p>
          </div>

          <div className="form-wrapper">
            <LoginForm />
          </div>

          <div className="login-footer">
            Don't have an account?{' '}
            <Link href="/signup">
              Sign up
            </Link>
          </div>
        </div>
      </Container>
    </>
  );
}