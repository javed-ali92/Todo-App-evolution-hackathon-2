'use client';

import SignupForm from '@/components/forms/signup-form';
import Container from '@/components/layouts/container';
import Link from 'next/link';

export default function SignupPage() {
  return (
    <>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');

        .signup-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
          position: relative;
          overflow: hidden;
        }

        .signup-background {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
          z-index: -2;
        }

        .signup-background::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: 
            radial-gradient(circle at 30% 40%, rgba(255, 230, 109, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 70% 70%, rgba(255, 107, 157, 0.15) 0%, transparent 50%);
          animation: morphSignup 20s ease-in-out infinite;
        }

        @keyframes morphSignup {
          0%, 100% { 
            background: 
              radial-gradient(circle at 30% 40%, rgba(255, 230, 109, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 70% 70%, rgba(255, 107, 157, 0.15) 0%, transparent 50%);
          }
          50% { 
            background: 
              radial-gradient(circle at 70% 30%, rgba(255, 230, 109, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 30% 80%, rgba(255, 107, 157, 0.15) 0%, transparent 50%);
          }
        }

        .floating-orbs-signup {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: -1;
        }

        .orb-signup {
          position: absolute;
          border-radius: 50%;
          filter: blur(80px);
          opacity: 0.3;
          animation: floatSignup 20s ease-in-out infinite;
        }

        .orb-signup-1 {
          top: 15%;
          right: 15%;
          width: 450px;
          height: 450px;
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          animation-delay: 0s;
        }

        .orb-signup-2 {
          bottom: 15%;
          left: 10%;
          width: 500px;
          height: 500px;
          background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
          animation-delay: 7s;
        }

        .orb-signup-3 {
          top: 45%;
          left: 45%;
          width: 350px;
          height: 350px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          animation-delay: 14s;
          transform: translate(-50%, -50%);
        }

        @keyframes floatSignup {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(-40px, 60px); }
          66% { transform: translate(40px, -40px); }
        }

        .signup-card {
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
          animation: slideUpSignup 0.6s ease-out;
        }

        @keyframes slideUpSignup {
          from {
            opacity: 0;
            transform: translateY(50px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .signup-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(90deg, transparent, rgba(255, 230, 109, 0.6), transparent);
          animation: shimmerSignup 3s ease-in-out infinite;
        }

        @keyframes shimmerSignup {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }

        .signup-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }

        .signup-badge {
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
          animation: fadeInSignup 0.8s ease-out 0.2s both;
        }

        @keyframes fadeInSignup {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .signup-badge::before {
          content: '✨';
          font-size: 1rem;
          animation: spinSlow 4s linear infinite;
        }

        @keyframes spinSlow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .signup-title {
          font-family: 'Syne', sans-serif;
          font-size: 2.5rem;
          font-weight: 800;
          background: linear-gradient(135deg, #ffffff 0%, #FFE66D 50%, #ffffff 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.75rem;
          letter-spacing: -0.02em;
          animation: fadeInSignup 0.8s ease-out 0.3s both;
        }

        .signup-subtitle {
          color: rgba(255, 255, 255, 0.8);
          font-size: 1.05rem;
          font-weight: 400;
          line-height: 1.6;
          animation: fadeInSignup 0.8s ease-out 0.4s both;
        }

        .form-wrapper-signup {
          animation: fadeInSignup 0.8s ease-out 0.5s both;
        }

        .signup-footer {
          margin-top: 2rem;
          text-align: center;
          color: rgba(255, 255, 255, 0.75);
          font-size: 0.95rem;
          animation: fadeInSignup 0.8s ease-out 0.6s both;
        }

        .signup-footer a {
          color: #4ECDC4;
          text-decoration: none;
          font-weight: 600;
          transition: all 0.3s ease;
          position: relative;
        }

        .signup-footer a::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(90deg, #4ECDC4, #44A08D);
          transform: scaleX(0);
          transform-origin: right;
          transition: transform 0.3s ease;
        }

        .signup-footer a:hover::after {
          transform: scaleX(1);
          transform-origin: left;
        }

        .signup-footer a:hover {
          color: #44A08D;
        }

        .decorative-circles-signup {
          position: absolute;
          width: 100%;
          height: 100%;
          top: 0;
          left: 0;
          pointer-events: none;
          opacity: 0.08;
          z-index: 0;
        }

        .decorative-circles-signup::before,
        .decorative-circles-signup::after {
          content: '';
          position: absolute;
          border-radius: 50%;
          border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .decorative-circles-signup::before {
          top: -50px;
          right: -50px;
          width: 200px;
          height: 200px;
          animation: pulse 8s ease-in-out infinite;
        }

        .decorative-circles-signup::after {
          bottom: -60px;
          left: -60px;
          width: 250px;
          height: 250px;
          animation: pulse 8s ease-in-out infinite reverse;
        }

        @keyframes pulse {
          0%, 100% { 
            transform: scale(1);
            opacity: 0.08;
          }
          50% { 
            transform: scale(1.1);
            opacity: 0.12;
          }
        }

        .feature-highlights {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.75rem;
          margin-top: 2rem;
          animation: fadeInSignup 0.8s ease-out 0.7s both;
        }

        .feature-item {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 0.75rem;
          text-align: center;
          transition: all 0.3s ease;
        }

        .feature-item:hover {
          background: rgba(255, 255, 255, 0.1);
          transform: translateY(-3px);
          border-color: rgba(255, 255, 255, 0.2);
        }

        .feature-item-icon {
          font-size: 1.5rem;
          margin-bottom: 0.25rem;
          display: block;
        }

        .feature-item-text {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.8);
          font-weight: 500;
        }

        @media (max-width: 640px) {
          .signup-card {
            padding: 2rem 1.5rem;
            border-radius: 24px;
          }

          .signup-title {
            font-size: 2rem;
          }

          .signup-subtitle {
            font-size: 0.95rem;
          }

          .feature-highlights {
            grid-template-columns: 1fr;
            gap: 0.5rem;
          }
        }
      `}</style>

      <div className="signup-background"></div>
      <div className="floating-orbs-signup">
        <div className="orb-signup orb-signup-1"></div>
        <div className="orb-signup orb-signup-2"></div>
        <div className="orb-signup orb-signup-3"></div>
      </div>

      <Container className="signup-container">
        <div className="signup-card">
          <div className="decorative-circles-signup"></div>
          
          <div className="signup-header">
            <div className="signup-badge">
              Start Your Journey
            </div>
            <h1 className="signup-title">Create Account</h1>
            <p className="signup-subtitle">
              Join thousands of productive users and transform how you work
            </p>
          </div>

          <div className="form-wrapper-signup">
            <SignupForm />
          </div>

          <div className="feature-highlights">
            <div className="feature-item">
              <span className="feature-item-icon">🚀</span>
              <span className="feature-item-text">Fast Setup</span>
            </div>
            <div className="feature-item">
              <span className="feature-item-icon">🔒</span>
              <span className="feature-item-text">Secure</span>
            </div>
            <div className="feature-item">
              <span className="feature-item-icon">💯</span>
              <span className="feature-item-text">Free Forever</span>
            </div>
          </div>

          <div className="signup-footer">
            Already have an account?{' '}
            <Link href="/login">
              Sign in
            </Link>
          </div>
        </div>
      </Container>
    </>
  );
}