'use client';

import { useAuth } from './providers/auth-provider';
import Link from 'next/link';

export default function HomePage() {
  const { session } = useAuth();

  return (
    <>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');
        
        :root {
          --primary: #FF6B9D;
          --primary-dark: #C42C5C;
          --secondary: #4ECDC4;
          --accent: #FFE66D;
          --dark: #1A1A2E;
          --light: #F7F7FF;
          --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: 'DM Sans', sans-serif;
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
          min-height: 100vh;
          position: relative;
          overflow-x: hidden;
        }

        body::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: 
            radial-gradient(circle at 20% 50%, rgba(255, 107, 157, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(78, 205, 196, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(255, 230, 109, 0.1) 0%, transparent 50%);
          pointer-events: none;
          z-index: 0;
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

        .floating-shapes {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 0;
          overflow: hidden;
        }

        .shape {
          position: absolute;
          opacity: 0.1;
        }

        .shape-1 {
          top: 10%;
          left: 10%;
          width: 300px;
          height: 300px;
          background: var(--gradient-2);
          border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
          animation: float 25s ease-in-out infinite;
        }

        .shape-2 {
          bottom: 10%;
          right: 10%;
          width: 400px;
          height: 400px;
          background: var(--gradient-3);
          border-radius: 70% 30% 30% 70% / 60% 40% 60% 40%;
          animation: float 20s ease-in-out infinite reverse;
        }

        .shape-3 {
          top: 50%;
          left: 50%;
          width: 200px;
          height: 200px;
          background: var(--gradient-1);
          border-radius: 50%;
          animation: pulse 15s ease-in-out infinite;
          transform: translate(-50%, -50%);
        }

        @keyframes float {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          33% { transform: translate(50px, -50px) rotate(120deg); }
          66% { transform: translate(-30px, 30px) rotate(240deg); }
        }

        @keyframes pulse {
          0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.1; }
          50% { transform: translate(-50%, -50%) scale(1.3); opacity: 0.15; }
        }

        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(10px);
          padding: 8px 20px;
          border-radius: 50px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: rgba(255, 255, 255, 0.95);
          font-size: 0.9rem;
          font-weight: 500;
          margin-bottom: 2rem;
          animation: slideDown 0.8s ease-out;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .hero-badge::before {
          content: '✨';
          font-size: 1.2rem;
          animation: spin 3s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        h1.hero-title {
          font-family: 'Syne', sans-serif;
          font-size: clamp(3rem, 8vw, 5.5rem);
          font-weight: 800;
          line-height: 1.1;
          letter-spacing: -0.03em;
          background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 50%, #c7d2fe 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 1.5rem;
          animation: fadeInUp 0.8s ease-out 0.2s both;
          position: relative;
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .subtitle {
          font-size: clamp(1.2rem, 3vw, 1.5rem);
          color: rgba(255, 255, 255, 0.85);
          font-weight: 400;
          margin-bottom: 3rem;
          animation: fadeInUp 0.8s ease-out 0.4s both;
          line-height: 1.6;
        }

        .cta-group {
          display: flex;
          gap: 1.2rem;
          justify-content: center;
          flex-wrap: wrap;
          margin-bottom: 5rem;
          animation: fadeInUp 0.8s ease-out 0.6s both;
        }

        .btn-primary {
          position: relative;
          padding: 18px 42px;
          font-size: 1.1rem;
          font-weight: 700;
          color: #1A1A2E;
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          border: none;
          border-radius: 16px;
          cursor: pointer;
          overflow: hidden;
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          box-shadow: 0 10px 30px rgba(255, 107, 157, 0.3);
          text-decoration: none;
          display: inline-block;
        }

        .btn-primary::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, #FF6B9D 0%, #FFE66D 100%);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .btn-primary:hover::before {
          opacity: 1;
        }

        .btn-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(255, 107, 157, 0.5);
        }

        .btn-primary span {
          position: relative;
          z-index: 1;
        }

        .btn-secondary {
          padding: 18px 42px;
          font-size: 1.1rem;
          font-weight: 600;
          color: white;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.3s ease;
          text-decoration: none;
          display: inline-block;
        }

        .btn-secondary:hover {
          background: rgba(255, 255, 255, 0.2);
          border-color: rgba(255, 255, 255, 0.5);
          transform: translateY(-3px);
          box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 2rem;
          margin-top: 3rem;
          animation: fadeInUp 0.8s ease-out 0.8s both;
        }

        .feature-card {
          background: rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 24px;
          padding: 2.5rem;
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          position: relative;
          overflow: hidden;
        }

        .feature-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, rgba(255, 107, 157, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .feature-card:hover::before {
          opacity: 1;
        }

        .feature-card:hover {
          transform: translateY(-8px);
          border-color: rgba(255, 255, 255, 0.3);
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .feature-icon {
          width: 60px;
          height: 60px;
          background: var(--gradient-2);
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.8rem;
          margin-bottom: 1.5rem;
          transition: transform 0.3s ease;
        }

        .feature-card:hover .feature-icon {
          transform: scale(1.1) rotate(5deg);
        }

        .feature-card h3 {
          font-family: 'Syne', sans-serif;
          font-size: 1.3rem;
          font-weight: 700;
          color: white;
          margin-bottom: 0.8rem;
          position: relative;
        }

        .feature-card p {
          color: rgba(255, 255, 255, 0.75);
          line-height: 1.7;
          position: relative;
        }

        .section-title {
          font-family: 'Syne', sans-serif;
          font-size: 2.5rem;
          font-weight: 700;
          color: white;
          margin-bottom: 1rem;
          text-align: center;
          animation: fadeInUp 0.8s ease-out 0.6s both;
        }

        .container-custom {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 2rem;
          position: relative;
          z-index: 1;
        }

        @media (max-width: 768px) {
          .cta-group {
            flex-direction: column;
            align-items: stretch;
          }
          
          .features-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <div className="floating-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>

      <div className="container-custom" style={{ paddingTop: '6rem', paddingBottom: '6rem' }}>
        <header style={{ textAlign: 'center', marginBottom: '5rem' }}>
          <div className="hero-badge">
            Your Personal Productivity Hub
          </div>
          <h1 className="hero-title">
            Welcome to TaskMaster
            {session.isLoggedIn && (
              <span style={{ display: 'block', fontSize: '0.5em', marginTop: '0.5rem' }}>
                {session.username || session.email}
              </span>
            )}
          </h1>
          <p className="subtitle">
            Transform chaos into clarity. Manage your tasks with elegance and efficiency.
          </p>

          <div className="cta-group">
            <Link href="/signup" className="btn-primary">
              <span>Start Your Journey</span>
            </Link>
            <Link href="/login" className="btn-secondary">
              Sign In
            </Link>
          </div>
        </header>

        <main>
          <section>
            <h2 className="section-title">Powerful Features</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">📝</div>
                <h3>Smart Task Creation</h3>
                <p>Effortlessly create and organize your tasks with our intuitive interface</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">✅</div>
                <h3>Track Progress</h3>
                <p>Mark tasks as complete and watch your productivity soar</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">🗑️</div>
                <h3>Clean Workspace</h3>
                <p>Remove completed tasks to maintain a clutter-free environment</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">🔒</div>
                <h3>Secure & Private</h3>
                <p>Enterprise-grade authentication keeps your data safe</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">📱</div>
                <h3>Responsive Design</h3>
                <p>Access your tasks anywhere, on any device, seamlessly</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">⚡</div>
                <h3>Lightning Fast</h3>
                <p>Optimized performance for instant task management</p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </>
  );
}