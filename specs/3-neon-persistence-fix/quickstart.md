# Quickstart Guide: Neon Persistence Fix Implementation

## Overview
This guide provides quick setup and implementation steps for fixing the task creation form, enforcing dashboard redirect after login, and ensuring user & task persistence in Neon PostgreSQL.

## Prerequisites
- Node.js 16+ for frontend
- Python 3.9+ for backend
- Neon PostgreSQL database with connection string
- Backend server running on http://localhost:8000
- Frontend server running on http://localhost:5173

## Environment Setup
1. Ensure DATABASE_URL in backend/.env points to your Neon PostgreSQL
2. Confirm both backend and frontend servers are running
3. Verify API endpoints are accessible at http://localhost:8000/api/*

## Implementation Steps

### 1. Database Layer
- Verify Neon connection in backend/src/database/database.py
- Confirm SQLModel engine uses Neon connection string
- Test table creation during startup

### 2. Authentication Flow
- Check auth endpoints: /api/auth/login, /api/auth/register
- Update frontend login to redirect to /dashboard after success
- Verify JWT token handling

### 3. Task Management
- Verify task endpoints: /api/{user_id}/tasks/*
- Ensure user_id is properly associated with tasks
- Test CRUD operations with proper user filtering

### 4. Frontend Components
- Update LoginPage.jsx to redirect after successful login
- Create/update TodoForm.jsx with proper field validation
- Ensure DashboardPage.jsx fetches and displays tasks correctly

## Common Issues & Solutions

### Issue: 404 on API endpoints
**Solution**: Check that backend is running and endpoints are prefixed with /api

### Issue: Redirect not happening after login
**Solution**: Update AuthContext.jsx to navigate to /dashboard after successful login

### Issue: Task form not submitting
**Solution**: Verify form data matches backend schema and has proper user_id association

### Issue: Tasks not showing on dashboard
**Solution**: Ensure dashboard fetches tasks for the authenticated user only

## Testing Commands
- `curl -X POST "http://localhost:8000/api/auth/login" -H "Content-Type: application/json" -d "{...}"`
- Verify database tables exist: users, tasks with proper relationships
- Test full flow: signup → login → redirect → task creation → persistence