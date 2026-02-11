'use client';

import { useEffect, useState } from 'react';
import WithAuth from '@/components/hoc/with-auth';
import Container from '@/components/layouts/container';
import TaskList from '@/components/lists/task-list';
import Link from 'next/link';
import { taskClient, Task } from '@/lib/api/task-client';
import { useAuth } from '@/app/providers/auth-provider';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const { session } = useAuth();

  useEffect(() => {
    const fetchTasks = async () => {
      if (!session.userId || !session.isLoggedIn) return;

      try {
        const userTasks = await taskClient.getUserTasks(parseInt(session.userId));
        setTasks(userTasks);
      } catch (err) {
        console.error('Failed to fetch tasks:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [session.userId, session.isLoggedIn]);

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.completed).length;
  const inProgressTasks = totalTasks - completedTasks;

  return (
    <>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

        .dashboard-wrapper {
          min-height: calc(100vh - 80px);
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
          position: relative;
          overflow: hidden;
        }

        .dashboard-wrapper::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: 
            radial-gradient(circle at 20% 30%, rgba(255, 107, 157, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(78, 205, 196, 0.1) 0%, transparent 50%);
          animation: morphDashboard 20s ease-in-out infinite;
          pointer-events: none;
        }

        @keyframes morphDashboard {
          0%, 100% { 
            background: 
              radial-gradient(circle at 20% 30%, rgba(255, 107, 157, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 70%, rgba(78, 205, 196, 0.1) 0%, transparent 50%);
          }
          50% { 
            background: 
              radial-gradient(circle at 80% 40%, rgba(255, 107, 157, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 20% 60%, rgba(78, 205, 196, 0.1) 0%, transparent 50%);
          }
        }

        .dashboard-container {
          position: relative;
          z-index: 1;
          padding: 3rem 0;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 2.5rem;
          flex-wrap: wrap;
          gap: 1.5rem;
        }

        .header-content {
          flex: 1;
          min-width: 250px;
        }

        .welcome-badge {
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
          margin-bottom: 1rem;
          animation: slideInLeft 0.6s ease-out;
        }

        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .welcome-badge::before {
          content: '👋';
          font-size: 1rem;
        }

        .dashboard-title {
          font-family: 'Syne', sans-serif;
          font-size: clamp(2rem, 5vw, 3rem);
          font-weight: 800;
          background: linear-gradient(135deg, #ffffff 0%, #FFE66D 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin-bottom: 0.5rem;
          letter-spacing: -0.02em;
          animation: slideInLeft 0.6s ease-out 0.1s both;
        }

        .dashboard-subtitle {
          color: rgba(255, 255, 255, 0.8);
          font-size: 1.1rem;
          font-weight: 400;
          animation: slideInLeft 0.6s ease-out 0.2s both;
        }

        .create-task-btn {
          padding: 1rem 2rem;
          font-size: 1rem;
          font-weight: 700;
          color: #1A1A2E;
          background: linear-gradient(135deg, #FFE66D 0%, #FF6B9D 100%);
          border: none;
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          position: relative;
          overflow: hidden;
          animation: slideInRight 0.6s ease-out 0.3s both;
        }

        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .create-task-btn::before {
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

        .create-task-btn:hover::before {
          opacity: 1;
        }

        .create-task-btn:hover {
          transform: translateY(-3px);
          box-shadow: 0 6px 20px rgba(255, 107, 157, 0.5);
        }

        .create-task-btn span {
          position: relative;
          z-index: 1;
        }

        .create-task-btn::after {
          content: '+';
          position: relative;
          z-index: 1;
          font-size: 1.3rem;
          font-weight: 700;
        }

        /* Stats Grid */
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2.5rem;
          animation: fadeInUp 0.6s ease-out 0.4s both;
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

        .stat-card {
          background: rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 20px;
          padding: 1.75rem;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .stat-card::before {
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

        .stat-card:hover::before {
          opacity: 1;
        }

        .stat-card:hover {
          transform: translateY(-5px);
          border-color: rgba(255, 255, 255, 0.25);
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .stat-icon {
          width: 50px;
          height: 50px;
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          margin-bottom: 1rem;
          position: relative;
          transition: transform 0.3s ease;
        }

        .stat-card:nth-child(2) .stat-icon {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        .stat-card:nth-child(3) .stat-icon {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        .stat-card:nth-child(4) .stat-icon {
          background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }

        .stat-card:hover .stat-icon {
          transform: scale(1.1) rotate(5deg);
        }

        .stat-label {
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.7);
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 0.5rem;
          position: relative;
        }

        .stat-value {
          font-family: 'Syne', sans-serif;
          font-size: 2rem;
          font-weight: 800;
          color: white;
          position: relative;
        }

        /* Tasks Section */
        .tasks-section {
          background: rgba(255, 255, 255, 0.08);
          backdrop-filter: blur(30px);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 24px;
          padding: 2.5rem;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
          animation: fadeInUp 0.6s ease-out 0.5s both;
          position: relative;
          overflow: hidden;
        }

        .tasks-section::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(90deg, transparent, rgba(255, 230, 109, 0.5), transparent);
          animation: shimmer 3s ease-in-out infinite;
        }

        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }

        .tasks-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .tasks-title {
          font-family: 'Syne', sans-serif;
          font-size: 1.75rem;
          font-weight: 700;
          color: white;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .tasks-title::before {
          content: '📋';
          font-size: 1.5rem;
        }

        .filter-pills {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .filter-pill {
          padding: 0.5rem 1rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 50px;
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .filter-pill:hover,
        .filter-pill.active {
          background: rgba(255, 230, 109, 0.2);
          border-color: rgba(255, 230, 109, 0.4);
          color: #FFE66D;
        }

        .tasks-content {
          position: relative;
        }

        /* Quick Actions */
        .quick-actions {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin-bottom: 2.5rem;
          animation: fadeInUp 0.6s ease-out 0.6s both;
        }

        .quick-action-card {
          background: rgba(255, 255, 255, 0.06);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          padding: 1.25rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          text-decoration: none;
        }

        .quick-action-card:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
          transform: translateY(-3px);
        }

        .quick-action-icon {
          font-size: 2rem;
          margin-bottom: 0.5rem;
          display: block;
        }

        .quick-action-label {
          color: rgba(255, 255, 255, 0.9);
          font-size: 0.9rem;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .dashboard-container {
            padding: 2rem 0;
          }

          .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .tasks-section {
            padding: 1.5rem;
          }

          .tasks-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .create-task-btn {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>

      <WithAuth>
        <div className="dashboard-wrapper">
          <Container className="dashboard-container">
            <div className="dashboard-header">
              <div className="header-content">
                <div className="welcome-badge">
                  Welcome back!
                </div>
                <h1 className="dashboard-title">Dashboard</h1>
                <p className="dashboard-subtitle">Manage your tasks efficiently and stay productive</p>
              </div>
              <Link href="/tasks/new" className="create-task-btn">
                <span>Create New Task</span>
              </Link>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📝</div>
                <div className="stat-label">Total Tasks</div>
                <div className="stat-value">{loading ? '...' : totalTasks}</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⏳</div>
                <div className="stat-label">In Progress</div>
                <div className="stat-value">{loading ? '...' : inProgressTasks}</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-label">Completed</div>
                <div className="stat-value">{loading ? '...' : completedTasks}</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🔥</div>
                <div className="stat-label">Completion Rate</div>
                <div className="stat-value">{loading ? '...' : totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0}%</div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
              <Link href="/tasks/new" className="quick-action-card">
                <span className="quick-action-icon">➕</span>
                <span className="quick-action-label">Add Task</span>
              </Link>
              <div className="quick-action-card">
                <span className="quick-action-icon">📊</span>
                <span className="quick-action-label">Analytics</span>
              </div>
              <div className="quick-action-card">
                <span className="quick-action-icon">⚙️</span>
                <span className="quick-action-label">Settings</span>
              </div>
              <div className="quick-action-card">
                <span className="quick-action-icon">🏆</span>
                <span className="quick-action-label">Achievements</span>
              </div>
            </div>

            {/* Tasks Section */}
            <div className="tasks-section">
              <div className="tasks-header">
                <h2 className="tasks-title">Your Tasks</h2>
                <div className="filter-pills">
                  <button className="filter-pill active">All</button>
                  <button className="filter-pill">Active</button>
                  <button className="filter-pill">Completed</button>
                </div>
              </div>
              <div className="tasks-content">
                <TaskList />
              </div>
            </div>
          </Container>
        </div>
      </WithAuth>
    </>
  );
}