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
    const isActive = pathname === path;
    return isActive 
      ? "nav-link nav-link-active" 
      : "nav-link";
  };

  return (
    <>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

        .header-wrapper {
          position: sticky;
          top: 0;
          z-index: 1000;
          background: rgba(26, 26, 46, 0.8);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        .header-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 2rem;
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          height: 80px;
        }

        /* Logo Section */
        .logo-section {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .logo-icon {
          width: 42px;
          height: 42px;
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.4rem;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
        }

        .logo-icon:hover {
          transform: rotate(-5deg) scale(1.05);
          box-shadow: 0 6px 20px rgba(255, 107, 157, 0.5);
        }

        .logo-text {
          font-family: 'Syne', sans-serif;
          font-size: 1.5rem;
          font-weight: 800;
          background: linear-gradient(135deg, #ffffff 0%, #FFE66D 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          letter-spacing: -0.02em;
          transition: all 0.3s ease;
          text-decoration: none;
        }

        .logo-section:hover .logo-text {
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        /* Navigation */
        .nav-section {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .nav-link {
          position: relative;
          padding: 0.75rem 1.25rem;
          font-size: 0.95rem;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.8);
          text-decoration: none;
          border-radius: 12px;
          transition: all 0.3s ease;
          overflow: hidden;
        }

        .nav-link::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(255, 255, 255, 0.05);
          opacity: 0;
          transition: opacity 0.3s ease;
          border-radius: 12px;
        }

        .nav-link:hover::before {
          opacity: 1;
        }

        .nav-link:hover {
          color: white;
          transform: translateY(-2px);
        }

        .nav-link-active {
          color: #FFE66D;
          background: rgba(255, 230, 109, 0.1);
          border: 1px solid rgba(255, 230, 109, 0.3);
        }

        .nav-link-active::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 30px;
          height: 3px;
          background: linear-gradient(90deg, #FFE66D, #FF6B9D);
          border-radius: 2px;
        }

        /* User Section */
        .user-section {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.5rem 1rem;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 50px;
          backdrop-filter: blur(10px);
        }

        .user-avatar {
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.9rem;
          font-weight: 700;
          color: white;
          text-transform: uppercase;
        }

        .user-name {
          font-size: 0.9rem;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.9);
          max-width: 150px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .logout-btn {
          padding: 0.75rem 1.5rem;
          font-size: 0.9rem;
          font-weight: 700;
          color: #1A1A2E;
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          border: none;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
          position: relative;
          overflow: hidden;
        }

        .logout-btn::before {
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

        .logout-btn:hover::before {
          opacity: 1;
        }

        .logout-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(255, 107, 157, 0.5);
        }

        .logout-btn span {
          position: relative;
          z-index: 1;
        }

        /* Mobile Menu Button */
        .mobile-menu-btn {
          display: none;
          flex-direction: column;
          gap: 5px;
          background: none;
          border: none;
          cursor: pointer;
          padding: 0.5rem;
        }

        .mobile-menu-btn span {
          width: 24px;
          height: 2px;
          background: white;
          border-radius: 2px;
          transition: all 0.3s ease;
        }

        .mobile-menu-btn:hover span {
          background: #FFE66D;
        }

        /* Responsive */
        @media (max-width: 1024px) {
          .nav-link {
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
          }

          .user-name {
            display: none;
          }
        }

        @media (max-width: 768px) {
          .header-container {
            padding: 0 1rem;
          }

          .header-content {
            height: 70px;
          }

          .logo-icon {
            width: 36px;
            height: 36px;
            font-size: 1.2rem;
          }

          .logo-text {
            font-size: 1.3rem;
          }

          .nav-section {
            position: absolute;
            top: 70px;
            left: 0;
            right: 0;
            background: rgba(26, 26, 46, 0.95);
            backdrop-filter: blur(20px);
            flex-direction: column;
            padding: 1rem;
            gap: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: none;
          }

          .nav-section.active {
            display: flex;
          }

          .nav-link {
            width: 100%;
            text-align: center;
          }

          .mobile-menu-btn {
            display: flex;
          }

          .user-section {
            gap: 0.5rem;
          }

          .user-info {
            padding: 0.4rem 0.8rem;
          }

          .logout-btn {
            padding: 0.6rem 1.2rem;
            font-size: 0.85rem;
          }
        }

        /* Authentication Buttons */
        .auth-buttons {
          display: flex;
          gap: 0.75rem;
        }

        .auth-link-login {
          padding: 0.75rem 1.5rem;
          font-size: 0.9rem;
          font-weight: 600;
          color: white;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 12px;
          text-decoration: none;
          transition: all 0.3s ease;
        }

        .auth-link-login:hover {
          background: rgba(255, 255, 255, 0.15);
          transform: translateY(-2px);
        }

        .auth-link-signup {
          padding: 0.75rem 1.5rem;
          font-size: 0.9rem;
          font-weight: 700;
          color: #1A1A2E;
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          border: none;
          border-radius: 12px;
          text-decoration: none;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
        }

        .auth-link-signup:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(255, 107, 157, 0.5);
        }
      `}</style>

      <header className="header-wrapper">
        <div className="header-container">
          <div className="header-content">
            {/* Logo */}
            <Link href="/" className="logo-section">
              <div className="logo-icon">✨</div>
              <span className="logo-text">TaskMaster</span>
            </Link>

            {/* Navigation Links */}
            <nav className="nav-section">
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
                <div className="auth-buttons">
                  <Link href="/login" className="auth-link-login">
                    Login
                  </Link>
                  <Link href="/signup" className="auth-link-signup">
                    Get Started
                  </Link>
                </div>
              )}
            </nav>

            {/* User Info & Logout */}
            {session.isLoggedIn && (
              <div className="user-section">
                <div className="user-info">
                  <div className="user-avatar">
                    {(session.username || session.email || 'U').charAt(0)}
                  </div>
                  <span className="user-name">
                    {session.username || session.email}
                  </span>
                </div>
                <button onClick={handleLogout} className="logout-btn">
                  <span>Logout</span>
                </button>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button className="mobile-menu-btn">
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </header>
    </>
  );
}