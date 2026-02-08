# Research & Technical Decisions: Fix Navigation, Header UI, and Auth Persistence

**Feature**: Fix Navigation, Header UI, and Auth Persistence
**Branch**: 002-fix-nav-auth
**Date**: 2026-02-09

## Overview

This document captures the technical research and decisions made during the planning phase for fixing navigation redirects, enhancing header UI, and ensuring auth persistence. All decisions prioritize minimal changes to existing code while fixing critical user experience issues.

---

## Research Topic 1: Root Cause of Infinite Redirect Loop

### Question
Why are logged-in users stuck in an infinite redirect loop when trying to access the home page?

### Investigation

**Code Analysis** (frontend/src/app/page.tsx):
```typescript
useEffect(() => {
  if (session.isLoggedIn) {
    router.push('/dashboard');
  }
}, [session.isLoggedIn, router]);
```

**Root Cause**: The home page unconditionally redirects logged-in users to the dashboard. When a logged-in user tries to navigate to the home page, they are immediately redirected back to the dashboard, creating a loop.

### Options Evaluated

1. **Remove forced redirect entirely**
   - Pros: Simple, allows logged-in users to access home page
   - Cons: None identified
   - Implementation: Delete lines 12-24 from page.tsx

2. **Conditional redirect based on route history**
   - Pros: Could redirect only on initial login
   - Cons: Complex, requires tracking navigation history, fragile
   - Implementation: Use Next.js router history API

3. **Add "skip redirect" query parameter**
   - Pros: Allows explicit control
   - Cons: Ugly URLs, poor UX, requires manual parameter management
   - Implementation: Check for ?skipRedirect=true in URL

### Decision: Remove forced redirect entirely

**Rationale**: The home page should be accessible to all users, regardless of authentication state. Forcing logged-in users away from the home page is not a standard pattern and creates poor UX. The redirect should only happen after successful login (which is already handled by the login page), not every time a logged-in user visits home.

**Implementation**:
- Remove useEffect redirect logic (lines 12-16)
- Remove conditional loading message (lines 18-24)
- Keep existing content that shows for both logged-in and logged-out users

---

## Research Topic 2: Auth Persistence Verification

### Question
Is authentication state correctly persisting across page reloads, or does it need fixes?

### Investigation

**Code Analysis** (frontend/src/app/providers/auth-provider.tsx):

**Login function** (lines 54-71):
```typescript
const login = (userData) => {
  // ... set session state ...
  localStorage.setItem('userSession', JSON.stringify(newSession));
};
```

**Logout function** (lines 73-88):
```typescript
const logout = () => {
  // ... clear session state ...
  localStorage.removeItem('userSession');
  router.push('/login');
};
```

**checkAuthStatus function** (lines 90-112):
```typescript
const checkAuthStatus = () => {
  const storedSession = localStorage.getItem('userSession');
  if (storedSession) {
    const parsedSession = JSON.parse(storedSession);
    if (parsedSession.expiryTime && new Date(parsedSession.expiryTime) > new Date()) {
      setSession(parsedSession);
    } else {
      localStorage.removeItem('userSession');
    }
  }
};
```

**Initialization** (lines 37-39):
```typescript
useEffect(() => {
  checkAuthStatus();
}, []);
```

### Options Evaluated

1. **Keep existing implementation**
   - Pros: Code looks correct, localStorage is properly used
   - Cons: Needs testing to verify it works
   - Implementation: No changes, just verify through testing

2. **Switch to sessionStorage**
   - Pros: More secure (cleared on tab close)
   - Cons: Loses persistence across tabs, worse UX
   - Implementation: Replace localStorage with sessionStorage

3. **Add token refresh mechanism**
   - Pros: Better security, longer sessions
   - Cons: Out of scope, requires backend changes
   - Implementation: Add refresh token endpoint and logic

### Decision: Keep existing implementation

**Rationale**: The code analysis shows that localStorage persistence is already correctly implemented. The auth provider stores the session on login, restores it on mount, and checks for expiration. This should work correctly. The issue reported by the user may be due to the redirect loop preventing proper testing, not an actual persistence problem.

**Implementation**: No changes needed, but will verify through manual testing after fixing the redirect loop.

---

## Research Topic 3: Header Navigation Structure

### Question
How should the header display navigation links for logged-in vs logged-out users?

### Investigation

**Current Implementation** (frontend/src/components/ui/header.tsx):
- Returns null if user is not logged in (line 16-18)
- Shows only username and logout button for logged-in users
- No navigation links to other pages

**Requirements**:
- Logged-out: Home, Login, Signup
- Logged-in: Home, Dashboard, Add Task, Logout

### Options Evaluated

1. **Conditional rendering in single component**
   - Pros: Single source of truth, easy to maintain
   - Cons: Slightly more complex JSX
   - Implementation: Use ternary or conditional blocks

2. **Separate HeaderLoggedIn and HeaderLoggedOut components**
   - Pros: Clear separation, simpler individual components
   - Cons: Code duplication, harder to maintain consistency
   - Implementation: Create two separate components

3. **Higher-order component (HOC)**
   - Pros: Composition pattern
   - Cons: Over-engineering for this use case
   - Implementation: Wrap base header with auth-specific behavior

### Decision: Conditional rendering in single component

**Rationale**: The header needs to show different links based on auth state, but the overall structure (logo, navigation, actions) is the same. Using conditional rendering keeps the code DRY while being easy to understand and maintain.

**Implementation**:
```typescript
export default function Header() {
  const { session, logout } = useAuth();

  return (
    <header>
      <Logo />
      <nav>
        {session.isLoggedIn ? (
          // Logged-in navigation
          <><Link href="/">Home</Link>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/tasks/new">Add Task</Link></>
        ) : (
          // Logged-out navigation
          <><Link href="/">Home</Link>
            <Link href="/login">Login</Link>
            <Link href="/signup">Signup</Link></>
        )}
      </nav>
      {session.isLoggedIn && (
        <div>
          <span>{session.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </header>
  );
}
```

---

## Research Topic 4: Active Page Indicator Implementation

### Question
How should the header indicate which page is currently active?

### Investigation

**Next.js App Router Options**:
- `usePathname()` hook - Returns current pathname
- `useSelectedLayoutSegment()` - Returns active segment
- `useParams()` - Returns route parameters

### Options Evaluated

1. **usePathname hook**
   - Pros: Simple, direct, works for all routes
   - Cons: None
   - Implementation: `const pathname = usePathname(); const isActive = pathname === '/dashboard';`

2. **useSelectedLayoutSegment hook**
   - Pros: Works with nested layouts
   - Cons: More complex, not needed for flat navigation
   - Implementation: More complex segment matching

3. **CSS :active pseudo-class**
   - Pros: No JavaScript needed
   - Cons: Only works for click state, not current page
   - Implementation: Not applicable

### Decision: usePathname hook

**Rationale**: The usePathname hook is the standard Next.js App Router way to detect the current route. It's simple, reliable, and works perfectly for our flat navigation structure.

**Implementation**:
```typescript
import { usePathname } from 'next/navigation';

export default function Header() {
  const pathname = usePathname();

  const linkClass = (path: string) =>
    pathname === path
      ? 'text-blue-600 font-semibold'
      : 'text-gray-600 hover:text-gray-900';

  return (
    <Link href="/dashboard" className={linkClass('/dashboard')}>
      Dashboard
    </Link>
  );
}
```

---

## Research Topic 5: Responsive Header Design

### Question
How should the header adapt to mobile devices?

### Investigation

**Current Implementation**:
- Uses Tailwind CSS utility classes
- Has basic responsive classes (sm:, lg:)
- No mobile menu/hamburger

**Requirements**:
- Must work on mobile (< 768px)
- Must be accessible
- Must not require new dependencies

### Options Evaluated

1. **Horizontal scrolling on mobile**
   - Pros: Simple, no JavaScript needed
   - Cons: Poor UX, hard to discover all links
   - Implementation: `overflow-x-auto` class

2. **Hamburger menu with state**
   - Pros: Standard mobile pattern, good UX
   - Cons: Requires state management, more complex
   - Implementation: useState for menu open/close

3. **Stacked layout on mobile**
   - Pros: Simple, accessible, no JavaScript
   - Cons: Takes more vertical space
   - Implementation: `flex-col` on mobile, `flex-row` on desktop

### Decision: Stacked layout on mobile (with potential hamburger in future)

**Rationale**: For MVP, a stacked layout is the simplest solution that works well on mobile without requiring additional state management. The navigation has only 3-4 links, so vertical stacking is acceptable. If needed in the future, a hamburger menu can be added.

**Implementation**:
```typescript
<nav className="flex flex-col md:flex-row gap-4">
  {/* Navigation links */}
</nav>
```

---

## Technology Stack Verification

### Frontend Dependencies (Existing)
- **Next.js 16+**: App Router with usePathname hook ✓
- **React 18+**: Conditional rendering, hooks ✓
- **TypeScript**: Type safety for props ✓
- **Tailwind CSS**: Utility classes for styling ✓
- **Better Auth**: JWT authentication ✓

### New Dependencies Required
**None** - All functionality achievable with existing stack.

---

## Performance Considerations

### Header Rendering
- **Target**: No perceptible lag when auth state changes
- **Strategy**: React's automatic re-rendering on state change
- **Validation**: Manual testing with Chrome DevTools Performance tab

### Navigation Updates
- **Target**: Active indicator updates instantly on route change
- **Strategy**: usePathname hook automatically updates on navigation
- **Validation**: Visual inspection during navigation

---

## Security Considerations

### No Security Changes
- Auth flow remains unchanged
- localStorage usage is existing pattern
- No new attack vectors introduced
- JWT token handling unchanged

### Verification
- No backend changes means no new security risks
- Frontend changes are UI-only
- Existing auth guards (WithAuth HOC) remain in place

---

## Conclusion

All technical decisions prioritize simplicity and minimal changes to existing code. No new dependencies are required, and all functionality can be implemented with the current technology stack. The approach is well-understood, low-risk, and aligns with React and Next.js best practices.

**Key Decisions Summary**:
1. Remove forced redirect from home page
2. Keep existing localStorage auth persistence
3. Use conditional rendering for header navigation
4. Use usePathname hook for active page indicator
5. Use stacked layout for mobile responsiveness
