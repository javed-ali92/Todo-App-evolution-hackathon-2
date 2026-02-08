# Quickstart Guide: Clean Next.js Frontend with App Router

**Feature**: 004-clean-frontend
**Date**: 2026-02-07
**Purpose**: Step-by-step guide to set up and run the clean Next.js frontend

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Backend API running on port 8000 (or configured port)
- Git for version control

---

## Initial Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Verify Configuration Files

Ensure these files exist and are properly configured:

**package.json** - Should include:
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-hook-form": "^7.49.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0"
  }
}
```

**next.config.js** - Should include proxy configuration:
```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};
```

**tsconfig.json** - Should include path aliases:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## Development Workflow

### 1. Start Backend Server

In a separate terminal:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/api/health
```

### 2. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The application should be available at: `http://localhost:3000`

### 3. Verify Frontend is Running

Open browser and navigate to:
- Landing page: `http://localhost:3000`
- Login page: `http://localhost:3000/login`
- Signup page: `http://localhost:3000/signup`

---

## Testing the Application

### 1. Test User Registration

1. Navigate to `http://localhost:3000/signup`
2. Fill in the form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
3. Click "Create Account"
4. Should redirect to dashboard at `http://localhost:3000/dashboard`

### 2. Test User Login

1. Navigate to `http://localhost:3000/login`
2. Fill in the form:
   - Email: `test@example.com`
   - Password: `password123`
3. Click "Sign in"
4. Should redirect to dashboard at `http://localhost:3000/dashboard`

### 3. Test Task Creation

1. Ensure you're logged in and on the dashboard
2. Navigate to `http://localhost:3000/tasks/new` or use the task form on dashboard
3. Fill in the form:
   - Title: `Test Task`
   - Description: `This is a test task`
   - Due Date: Select a future date
   - Priority: `High`
   - Tags: `test,demo`
4. Click "Create Task"
5. Task should appear in the task list

### 4. Test Task Management

1. On the dashboard, view your task list
2. Click to mark a task as complete
3. Verify the task status updates
4. Try deleting a task
5. Verify the task is removed from the list

---

## Project Structure

After cleanup, the frontend structure should look like:

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page
│   │   ├── globals.css          # Global styles
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── signup/
│   │   │   └── page.tsx         # Signup page
│   │   ├── dashboard/
│   │   │   ├── layout.tsx       # Dashboard layout
│   │   │   └── page.tsx         # Dashboard page
│   │   ├── tasks/
│   │   │   └── new/
│   │   │       └── page.tsx     # Task creation page
│   │   └── providers/
│   │       └── auth-provider.tsx # Auth context provider
│   ├── components/
│   │   ├── forms/
│   │   │   ├── login-form.tsx
│   │   │   ├── signup-form.tsx
│   │   │   ├── task-form.tsx
│   │   │   └── filter-controls.tsx
│   │   ├── lists/
│   │   │   └── task-list.tsx
│   │   ├── layouts/
│   │   │   └── container.tsx
│   │   ├── hoc/
│   │   │   └── with-auth.tsx
│   │   └── ui/
│   │       ├── header.tsx
│   │       └── footer.tsx
│   ├── lib/
│   │   └── api/
│   │       ├── auth-client.ts
│   │       └── task-client.ts
│   └── styles/
│       └── globals.css
├── public/                       # Static assets
├── package.json
├── next.config.js
├── tsconfig.json
└── tailwind.config.js
```

---

## Common Issues and Solutions

### Issue 1: "Module not found" errors

**Solution**: Ensure all dependencies are installed
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue 2: API calls failing with CORS errors

**Solution**: Verify next.config.js has proper proxy configuration and backend is running

### Issue 3: Authentication not persisting

**Solution**: Check browser localStorage for 'auth_token' or 'userSession'. Clear and try logging in again.

### Issue 4: Pages not found (404 errors)

**Solution**: Ensure you're using App Router structure (`app/` directory) and files are named correctly (`page.tsx`)

### Issue 5: TypeScript errors

**Solution**: Ensure all TypeScript interfaces are properly imported from `lib/api/` files

---

## Environment Variables

Create a `.env.local` file in the frontend directory if needed:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: With the proxy configuration in next.config.js, you can use relative paths (`/api`) instead of absolute URLs.

---

## Building for Production

### 1. Build the Application

```bash
npm run build
```

### 2. Start Production Server

```bash
npm start
```

### 3. Verify Production Build

Navigate to `http://localhost:3000` and test all functionality.

---

## Development Tips

### Hot Reload
- Next.js automatically reloads when you save files
- If changes don't appear, try refreshing the browser

### Debugging
- Use browser DevTools Console for JavaScript errors
- Use Network tab to inspect API calls
- Check terminal for Next.js server errors

### Code Quality
- Run TypeScript type checking: `npm run type-check` (if configured)
- Format code consistently
- Keep components small and focused

---

## Next Steps

After completing the setup:

1. Review the implementation plan in `specs/004-clean-frontend/plan.md`
2. Follow the tasks in `specs/004-clean-frontend/tasks.md`
3. Start with Phase 1: Cleanup
4. Proceed through each phase sequentially
5. Test thoroughly after each phase

---

## Support

If you encounter issues:

1. Check the console for error messages
2. Verify backend is running and accessible
3. Review the API contracts in `specs/004-clean-frontend/contracts/`
4. Check the data model in `specs/004-clean-frontend/data-model.md`

---

## Validation Checklist

Before considering the setup complete, verify:

- [ ] Frontend dev server starts without errors
- [ ] Backend API is accessible from frontend
- [ ] Can navigate to all routes (/, /login, /signup, /dashboard)
- [ ] Can register a new user
- [ ] Can login with existing user
- [ ] Can create a new task
- [ ] Can view tasks on dashboard
- [ ] Can mark tasks as complete
- [ ] Can delete tasks
- [ ] Authentication persists across page reloads
- [ ] Logout works correctly