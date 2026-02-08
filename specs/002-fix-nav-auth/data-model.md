# Data Model: Fix Navigation, Header UI, and Auth Persistence

**Feature**: Fix Navigation, Header UI, and Auth Persistence
**Branch**: 002-fix-nav-auth
**Date**: 2026-02-09

## Overview

This feature does not introduce any new data entities or modify existing data structures. It operates on existing UI state and navigation logic. This document describes the existing entities used by the feature and the state changes that occur during navigation and authentication.

---

## Existing Entities

### UserSession

**Description**: Represents the authenticated user's session state, including authentication token, user ID, and login status. This entity is managed by the AuthProvider context.

**Storage**: localStorage (client-side browser storage)

**Fields**:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| userId | string | Yes | Unique identifier for the authenticated user |
| username | string | Yes | User's display name |
| email | string | Yes | User's email address |
| isLoggedIn | boolean | No | Whether the user is currently authenticated |
| accessToken | string | Yes | JWT token for API authentication |
| expiryTime | Date | Yes | Token expiration timestamp |

**Relationships**:
- No direct relationships (frontend-only state)

**Validation Rules**:
- `isLoggedIn` must be true if `accessToken` is present
- `expiryTime` must be in the future for valid sessions
- `userId`, `username`, `email`, and `accessToken` must all be present or all be null

---

## State Transitions

### Authentication State Flow

```
[User Not Logged In]
    ↓
[User Logs In] → login() called
    ↓
[Session Created] → localStorage.setItem('userSession', ...)
    ↓
[isLoggedIn = true]
    ↓
[User Navigates] → No forced redirects
    ↓
[Page Reload] → checkAuthStatus() called
    ↓
[Session Restored] ← localStorage.getItem('userSession')
    ↓
[Check Token Expiry]
    ↓
[Valid Token] → [isLoggedIn = true]
[Expired Token] → [Logout] → [isLoggedIn = false]
```

### Navigation State Flow

```
[User on Any Page]
    ↓
[Clicks Navigation Link]
    ↓
[Next.js Router Navigation]
    ↓
[usePathname Hook Updates]
    ↓
[Header Re-renders]
    ↓
[Active Link Indicator Updates]
```

### Header Display State

```
[Header Component Renders]
    ↓
[Check session.isLoggedIn]
    ↓
[isLoggedIn = true]              [isLoggedIn = false]
    ↓                                ↓
[Show Logged-In Navigation]      [Show Logged-Out Navigation]
- Home                           - Home
- Dashboard                      - Login
- Add Task                       - Signup
- Username Display
- Logout Button
```

---

## Field Modification Rules

### UserSession Fields

**Editable via login()**:
- `userId` - Set from login response
- `username` - Set from login response
- `email` - Set from login response
- `accessToken` - Set from login response
- `expiryTime` - Calculated as current time + 1 hour
- `isLoggedIn` - Set to true

**Editable via logout()**:
- All fields set to null
- `isLoggedIn` set to false

**Auto-Updated**:
- `expiryTime` - Checked every minute by interval
- Session cleared automatically when token expires

**Read-Only**:
- None (all fields can be updated through login/logout)

---

## Validation Rules

### Frontend Validation

**Session Validation** (in checkAuthStatus):
```typescript
// Check if session exists in localStorage
if (storedSession) {
  const parsedSession = JSON.parse(storedSession);

  // Validate token expiry
  if (parsedSession.expiryTime && new Date(parsedSession.expiryTime) > new Date()) {
    // Valid session - restore it
    setSession(parsedSession);
  } else {
    // Expired session - clear it
    localStorage.removeItem('userSession');
  }
}
```

**Navigation Validation** (in WithAuth HOC):
```typescript
// Check if user is logged in before allowing access to protected routes
if (!session.isLoggedIn) {
  router.push('/login');
}
```

---

## TypeScript Interfaces

### Frontend Types

```typescript
// User session state
interface UserSession {
  userId: string | null;
  username: string | null;
  email: string | null;
  isLoggedIn: boolean;
  accessToken: string | null;
  expiryTime: Date | null;
}

// Auth context interface
interface AuthContextType {
  session: UserSession;
  login: (userData: { userId: string; username: string; email: string; accessToken: string }) => void;
  logout: () => void;
  checkAuthStatus: () => void;
}

// Navigation route types
type PublicRoute = '/' | '/login' | '/signup';
type ProtectedRoute = '/dashboard' | '/tasks/new' | '/tasks/[id]/edit';
type Route = PublicRoute | ProtectedRoute;
```

---

## localStorage Schema

### Storage Key: 'userSession'

**Format**: JSON string

**Structure**:
```json
{
  "userId": "123",
  "username": "john_doe",
  "email": "john@example.com",
  "isLoggedIn": true,
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiryTime": "2026-02-09T05:00:00.000Z"
}
```

**Size**: Typically 200-500 bytes (well within localStorage limits)

**Persistence**: Survives page reloads and browser restarts until manually cleared or expired

---

## State Management

### React Context (AuthProvider)

**Provider Location**: `frontend/src/app/providers/auth-provider.tsx`

**State Management**:
- Uses React useState for session state
- Uses React useEffect for initialization and expiry checking
- Provides context to all child components via AuthContext

**State Updates**:
- `login()` - Updates state and localStorage
- `logout()` - Clears state and localStorage
- `checkAuthStatus()` - Restores state from localStorage on mount

---

## Data Flow Diagrams

### Login Flow

```
User                    AuthProvider              localStorage
  |                          |                          |
  |-- login(userData) ------>|                          |
  |                          |-- setSession(newSession) |
  |                          |                          |
  |                          |-- setItem('userSession') ->|
  |                          |                          |
  |<-- session updated ------|                          |
```

### Page Reload Flow

```
Browser                 AuthProvider              localStorage
  |                          |                          |
  |-- page reload ---------->|                          |
  |                          |-- useEffect() mount      |
  |                          |                          |
  |                          |-- checkAuthStatus() ---->|
  |                          |                          |
  |                          |<-- getItem('userSession')|
  |                          |                          |
  |                          |-- parse JSON             |
  |                          |-- check expiry           |
  |                          |-- setSession()           |
  |                          |                          |
  |<-- session restored -----|                          |
```

### Logout Flow

```
User                    AuthProvider              localStorage
  |                          |                          |
  |-- logout() ------------->|                          |
  |                          |-- setSession(empty)      |
  |                          |                          |
  |                          |-- removeItem('userSession')->|
  |                          |                          |
  |                          |-- router.push('/login')  |
  |                          |                          |
  |<-- redirected to login --|                          |
```

---

## Performance Considerations

### localStorage Operations

**Read Performance**:
- Single read on app initialization (checkAuthStatus)
- Synchronous operation, typically <1ms
- No performance impact

**Write Performance**:
- Single write on login
- Single delete on logout
- Synchronous operations, typically <1ms
- No performance impact

### State Updates

**React Re-renders**:
- Header re-renders when session state changes
- Navigation re-renders when pathname changes
- Both are lightweight operations with no performance impact

---

## Security Considerations

### localStorage Security

**Risks**:
- XSS attacks can access localStorage
- JWT tokens stored in plain text

**Mitigations**:
- Tokens have 1-hour expiry
- Backend validates all tokens
- No sensitive data beyond token stored
- Standard practice for JWT storage in SPAs

**Not Implemented** (out of scope):
- HttpOnly cookies (would require backend changes)
- Token refresh mechanism
- Encrypted storage

---

## Summary

This feature operates entirely on existing data structures with no schema changes required. The UserSession entity is well-defined, validation rules are clear, and state management is straightforward. The data model is simple, well-understood, and sufficient for the feature requirements.
