# Quickstart Guide: Fix Navigation, Header UI, and Auth Persistence

**Feature**: Fix Navigation, Header UI, and Auth Persistence
**Branch**: 002-fix-nav-auth
**Date**: 2026-02-09

## Overview

This guide provides step-by-step instructions for implementing fixes to navigation redirects, header UI enhancements, and auth persistence verification. Follow these phases in order to ensure a smooth implementation with minimal risk.

---

## Prerequisites

Before starting implementation, ensure:

- [x] Feature specification reviewed and approved (`spec.md`)
- [x] Implementation plan reviewed (`plan.md`)
- [x] Technical decisions documented (`research.md`)
- [x] Development environment set up (frontend running)
- [x] Authentication working (can login and access dashboard)
- [x] Existing components located (page.tsx, header.tsx, auth-provider.tsx)

---

## Implementation Phases

### Phase 1: Fix Infinite Redirect Loop (30 minutes)

**Goal**: Remove forced dashboard redirect from home page to allow logged-in users to access it.

#### Step 1.1: Locate Home Page Component

**File**: `frontend/src/app/page.tsx`

Verify you're editing the correct file by checking for the redirect logic:
```typescript
useEffect(() => {
  if (session.isLoggedIn) {
    router.push('/dashboard');
  }
}, [session.isLoggedIn, router]);
```

#### Step 1.2: Remove Redirect Logic

Delete lines 12-16 (the useEffect hook that forces redirect):
```typescript
// DELETE THIS:
useEffect(() => {
  if (session.isLoggedIn) {
    router.push('/dashboard');
  }
}, [session.isLoggedIn, router]);
```

#### Step 1.3: Remove Loading Message

Delete lines 18-24 (the conditional loading message):
```typescript
// DELETE THIS:
if (session.isLoggedIn) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-gray-600">Redirecting to dashboard...</div>
    </div>
  );
}
```

#### Step 1.4: Update Home Page Content (Optional)

Optionally, you can add a welcome message for logged-in users:
```typescript
export default function HomePage() {
  const { session } = useAuth();

  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to Todo App
          {session.isLoggedIn && `, ${session.username || session.email}`}
        </h1>
        <p className="text-xl text-gray-600">Your personal task management system</p>
      </header>

      {/* Rest of existing content */}
    </div>
  );
}
```

#### Step 1.5: Test Redirect Fix

**Manual Test**:
1. Login to the application
2. Navigate to dashboard
3. Click browser back button or manually navigate to `/`
4. Verify you stay on home page (no redirect)
5. Click link to dashboard
6. Verify you can navigate back to home

**Expected**: No redirect loop, free navigation between home and dashboard.

---

### Phase 2: Verify Auth Persistence (15 minutes)

**Goal**: Confirm authentication state persists correctly across page reloads.

#### Step 2.1: Review Auth Provider Code

**File**: `frontend/src/app/providers/auth-provider.tsx`

Verify the following functions exist and look correct:
- `login()` - Stores session in localStorage (line 70)
- `logout()` - Removes session from localStorage (line 84)
- `checkAuthStatus()` - Restores session from localStorage (lines 90-112)
- `useEffect()` - Calls checkAuthStatus on mount (lines 37-39)

#### Step 2.2: Test Auth Persistence

**Manual Test**:
1. Login to the application
2. Navigate to dashboard
3. Refresh the page (F5 or Ctrl+R)
4. Verify you remain logged in
5. Verify you stay on dashboard (not redirected to login)

**Expected**: User remains logged in after refresh.

#### Step 2.3: Test Token Expiry

**Manual Test**:
1. Login to the application
2. Open browser DevTools → Application → Local Storage
3. Find `userSession` key
4. Modify `expiryTime` to a past date
5. Refresh the page
6. Verify you are logged out and redirected to login

**Expected**: Expired tokens are detected and user is logged out.

#### Step 2.4: Fix Issues (If Any)

If auth persistence is not working:

**Issue**: Session not restored after refresh
**Solution**: Check that `checkAuthStatus()` is called in useEffect on mount

**Issue**: Token expiry not detected
**Solution**: Verify expiry time comparison logic in `checkAuthStatus()`

**Issue**: localStorage not accessible
**Solution**: Check browser settings, ensure localStorage is enabled

---

### Phase 3: Enhance Header Navigation (1 hour)

**Goal**: Add comprehensive navigation links with auth-aware display and active page indicators.

#### Step 3.1: Import Required Hooks

**File**: `frontend/src/components/ui/header.tsx`

Add the usePathname import:
```typescript
'use client';

import { useAuth } from '@/app/providers/auth-provider';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
```

#### Step 3.2: Remove Logged-Out Return Null

Delete lines 16-18:
```typescript
// DELETE THIS:
if (!session.isLoggedIn) {
  return null;
}
```

#### Step 3.3: Add usePathname Hook

Add pathname detection:
```typescript
export default function Header() {
  const { session, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // ... rest of component
}
```

#### Step 3.4: Create Link Style Helper

Add a helper function for active link styling:
```typescript
const linkClass = (path: string) => {
  const baseClass = "px-3 py-2 rounded-md text-sm font-medium transition-colors";
  const activeClass = "bg-blue-100 text-blue-700";
  const inactiveClass = "text-gray-700 hover:bg-gray-100 hover:text-gray-900";

  return `${baseClass} ${pathname === path ? activeClass : inactiveClass}`;
};
```

#### Step 3.5: Implement New Header Structure

Replace the entire return statement with:
```typescript
return (
  <header className="bg-white shadow-sm border-b border-gray-200">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        {/* Logo */}
        <div className="flex items-center">
          <Link href="/">
            <h1 className="text-xl font-semibold text-gray-900">Todo App</h1>
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="flex items-center gap-1">
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
            <>
              <Link href="/login" className={linkClass('/login')}>
                Login
              </Link>
              <Link href="/signup" className={linkClass('/signup')}>
                Signup
              </Link>
            </>
          )}
        </nav>

        {/* User Info & Logout (Logged-in only) */}
        {session.isLoggedIn && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {session.username || session.email}
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </div>
  </header>
);
```

#### Step 3.6: Test Header Navigation

**Manual Test**:
1. Logout (if logged in)
2. Verify header shows: Home, Login, Signup
3. Login to the application
4. Verify header shows: Home, Dashboard, Add Task, Username, Logout
5. Click each navigation link
6. Verify active page is highlighted with blue background
7. Verify navigation works correctly

**Expected**: Header displays correct links, active indicator works, all navigation functional.

#### Step 3.7: Test Mobile Responsiveness

**Manual Test**:
1. Open browser DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device (iPhone, Pixel, etc.)
4. Verify header is readable and usable
5. Test all navigation links on mobile

**Expected**: Header works on mobile devices.

---

### Phase 4: Testing & Validation (30 minutes)

**Goal**: Ensure all functionality works end-to-end with no regressions.

#### Step 4.1: Comprehensive Navigation Testing

**Test as Logged-Out User**:
- [ ] Visit home page - should load without redirect
- [ ] Click Login link - should navigate to login page
- [ ] Click Signup link - should navigate to signup page
- [ ] Try to access /dashboard directly - should redirect to login
- [ ] Try to access /tasks/new directly - should redirect to login

**Test as Logged-In User**:
- [ ] Visit home page - should load without redirect
- [ ] Click Dashboard link - should navigate to dashboard
- [ ] Click Add Task link - should navigate to task creation
- [ ] Click Home link - should navigate back to home
- [ ] Navigate between all pages freely - no redirect loops

#### Step 4.2: Auth Persistence Testing

- [ ] Login and refresh page - should remain logged in
- [ ] Login and close/reopen tab - should remain logged in
- [ ] Login, wait for token expiry, refresh - should be logged out
- [ ] Logout - should clear session and redirect to login

#### Step 4.3: Header Display Testing

- [ ] Header shows correct links when logged out
- [ ] Header shows correct links when logged in
- [ ] Active page indicator highlights current page
- [ ] Active indicator updates when navigating
- [ ] Username displays correctly
- [ ] Logout button works

#### Step 4.4: Regression Testing

- [ ] Login flow still works
- [ ] Task creation still works
- [ ] Task editing still works
- [ ] Task deletion still works
- [ ] Task completion toggle still works

#### Step 4.5: Cross-Browser Testing

Test in multiple browsers:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (if available)

#### Step 4.6: Mobile Testing

Test on mobile viewport:
- [ ] Header is readable
- [ ] Navigation links are tappable
- [ ] All functionality works

---

## Common Issues & Solutions

### Issue 1: Redirect Loop Still Occurs

**Symptom**: Logged-in users still redirected from home page

**Solution**: Verify you completely removed the useEffect redirect logic from page.tsx. Check for any other redirect logic in layout.tsx or middleware.

### Issue 2: Auth Not Persisting

**Symptom**: User logged out after page refresh

**Solution**:
1. Check browser console for localStorage errors
2. Verify `checkAuthStatus()` is called on mount
3. Check that localStorage is enabled in browser
4. Verify JSON parsing doesn't fail

### Issue 3: Active Indicator Not Working

**Symptom**: Active page not highlighted in header

**Solution**:
1. Verify usePathname is imported and called
2. Check pathname value in console: `console.log(pathname)`
3. Verify path comparison logic in linkClass function
4. Check CSS classes are applied correctly

### Issue 4: Header Not Showing for Logged-Out Users

**Symptom**: Header disappears when logged out

**Solution**: Verify you removed the `if (!session.isLoggedIn) return null;` check from header.tsx

### Issue 5: Mobile Header Broken

**Symptom**: Header not usable on mobile

**Solution**:
1. Check Tailwind responsive classes are correct
2. Verify viewport meta tag in layout
3. Test with actual mobile device, not just DevTools

---

## Performance Optimization

### Memoization (Optional)

If header re-renders are causing performance issues:
```typescript
import { useMemo } from 'react';

const linkClass = useMemo(() => (path: string) => {
  // ... linkClass logic
}, [pathname]);
```

### Code Splitting (Not Needed)

Header is small and used on every page, so code splitting is not beneficial.

---

## Deployment Checklist

Before deploying to production:

- [ ] All manual tests passed
- [ ] No console errors in browser
- [ ] Auth persistence works correctly
- [ ] No redirect loops
- [ ] Header displays correctly in all states
- [ ] Mobile responsive
- [ ] Cross-browser tested
- [ ] No regressions in existing functionality

---

## Next Steps

After completing implementation:

1. Run `/sp.tasks` to generate detailed task breakdown (if not already done)
2. Create pull request with changes
3. Request code review
4. Deploy to staging environment
5. Perform QA testing
6. Deploy to production

---

## Support & Resources

- **Specification**: `specs/002-fix-nav-auth/spec.md`
- **Implementation Plan**: `specs/002-fix-nav-auth/plan.md`
- **Technical Decisions**: `specs/002-fix-nav-auth/research.md`
- **Data Model**: `specs/002-fix-nav-auth/data-model.md`

For questions or issues, refer to the specification and plan documents first.
