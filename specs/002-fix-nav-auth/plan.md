# Implementation Plan: Fix Navigation, Header UI, and Auth Persistence

**Branch**: `002-fix-nav-auth` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fix-nav-auth/spec.md`

## Summary

Fix three critical issues in the Todo application: (1) Remove infinite redirect loop that prevents logged-in users from accessing the home page, (2) Enhance header navigation with auth-aware links and active page indicators, and (3) Ensure authentication state persists correctly across page reloads. The auth persistence is already partially implemented but needs verification and potential fixes. All changes are frontend-only with no backend modifications required.

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend)
**Primary Dependencies**: Next.js 16+ (App Router), React 18+, Better Auth (JWT)
**Storage**: localStorage for JWT token and session data
**Testing**: Frontend component tests, manual integration testing
**Target Platform**: Web application (responsive, mobile and desktop)
**Project Type**: Web (monorepo with frontend/ and backend/ directories)
**Performance Goals**: Header updates <1 second, no perceptible lag on navigation
**Constraints**: No backend changes, no new dependencies, minimal frontend changes, maintain existing functionality
**Scale/Scope**: Single-page application with ~5-7 routes, affects 3-4 components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement
- [x] No direct implementation without approved specs, plans, and tasks

### Architecture Compliance
- [x] Maintains monorepo structure: frontend/ (Next.js), backend/ (FastAPI), specs/, docker-compose.yml
- [x] Clear separation between frontend and backend components (frontend-only changes)

### Technology Stack Compliance
- [x] Frontend uses Next.js 16+ (App Router), TypeScript, Better Auth
- [x] Backend uses Python FastAPI, SQLModel ORM (no backend changes)
- [x] Database uses Neon Serverless PostgreSQL (no database changes)
- [x] Authentication uses Better Auth with JWT (existing implementation)

### Security Compliance
- [x] All API routes require JWT token authentication (no changes to auth flow)
- [x] Backend verifies JWT token and extracts user ID (no backend changes)
- [x] Backend compares token_user_id == url_user_id to prevent unauthorized access (unchanged)
- [x] Users can only access their own tasks (unchanged)

### API Contract Compliance
- [x] All API routes follow the specified contract (no API changes):
  - GET /api/{user_id}/tasks ✓
  - POST /api/{user_id}/tasks ✓
  - GET /api/{user_id}/tasks/{id} ✓
  - PUT /api/{user_id}/tasks/{id} ✓
  - DELETE /api/{user_id}/tasks/{id} ✓
  - PATCH /api/{user_id}/tasks/{id}/complete ✓

**Constitution Check Status**: ✅ PASSED - All requirements met, frontend-only changes, no violations

## Project Structure

### Documentation (this feature)

```text
specs/002-fix-nav-auth/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (no new entities, documents existing)
├── quickstart.md        # Phase 1 output (developer guide)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                    # MODIFY: Remove forced dashboard redirect
│   │   ├── layout.tsx                  # EXISTING: Wraps app with AuthProvider
│   │   ├── providers/
│   │   │   └── auth-provider.tsx       # VERIFY: Check localStorage persistence
│   │   ├── dashboard/
│   │   │   └── page.tsx                # EXISTING: Protected route
│   │   ├── tasks/
│   │   │   ├── new/page.tsx            # EXISTING: Protected route
│   │   │   └── [id]/edit/page.tsx      # EXISTING: Protected route
│   │   ├── login/
│   │   │   └── page.tsx                # EXISTING: Public route
│   │   └── signup/
│   │       └── page.tsx                # EXISTING: Public route
│   ├── components/
│   │   ├── ui/
│   │   │   └── header.tsx              # MODIFY: Add navigation links, auth-aware display
│   │   └── hoc/
│   │       └── with-auth.tsx           # EXISTING: Auth guard for protected routes
│   └── lib/
│       └── api/
│           └── task-client.ts          # EXISTING: API client
└── tests/
    └── components/
        └── header.test.tsx             # CREATE: Tests for header navigation

backend/
└── (no changes required)
```

**Structure Decision**: Web application structure with frontend-only changes. The existing auth system already has localStorage persistence implemented. Main changes are: (1) remove forced redirect from home page, (2) enhance header component with navigation links and auth-aware display.

## Complexity Tracking

No constitution violations - all changes are frontend-only and maintain existing architecture.

---

## Phase 0: Research & Technical Decisions

### Research Topics

1. **Root Cause of Redirect Loop**
   - Decision: Remove forced dashboard redirect from home page (page.tsx lines 12-16)
   - Rationale: Logged-in users should be able to access public pages without automatic redirects
   - Alternatives considered: Conditional redirect based on route history (rejected - adds complexity)

2. **Auth Persistence Verification**
   - Decision: Verify existing localStorage implementation in auth-provider.tsx
   - Rationale: Code shows localStorage is already implemented (lines 69-70, 90-112), may just need testing
   - Alternatives considered: Switch to sessionStorage (rejected - would lose persistence across tabs)

3. **Header Navigation Structure**
   - Decision: Conditional rendering based on auth state with usePathname for active indicator
   - Rationale: Standard Next.js pattern, no new dependencies, clean separation of concerns
   - Alternatives considered: Separate header components (rejected - unnecessary duplication)

4. **Active Page Indicator Implementation**
   - Decision: Use Next.js usePathname hook to detect current route and apply active styles
   - Rationale: Built-in Next.js functionality, no additional dependencies
   - Alternatives considered: React Router's useLocation (rejected - not using React Router)

5. **Logout Behavior**
   - Decision: Keep existing logout implementation (clears localStorage, redirects to login)
   - Rationale: Already working correctly, no changes needed
   - Alternatives considered: Add confirmation dialog (rejected - out of scope)

### Technology Decisions

- **No new dependencies required** - All functionality achievable with existing Next.js and React features
- **usePathname hook** - Next.js App Router hook for detecting current route
- **Conditional rendering** - Standard React pattern for auth-aware UI
- **localStorage** - Already implemented for token persistence

---

## Phase 1: Design & Contracts

### Data Model

**No new entities required.** This feature modifies UI behavior and navigation logic without changing data structures.

**Existing Entities Used**:

```typescript
interface UserSession {
  userId: string | null;
  username: string | null;
  email: string | null;
  isLoggedIn: boolean;
  accessToken: string | null;
  expiryTime: Date | null;
}
```

**State Changes**:
- Home page no longer forces redirect for logged-in users
- Header displays different navigation links based on `isLoggedIn` state
- Active page indicator updates based on current route

### API Contracts

**No API changes required.** This feature only modifies frontend navigation and UI behavior.

### Component Interface

**Updated Header Component**:

```typescript
// frontend/src/components/ui/header.tsx
export default function Header() {
  const { session, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  // Renders for both logged-in and logged-out states
  // Shows different navigation links based on session.isLoggedIn
  // Highlights active page using pathname
}
```

**Updated Home Page**:

```typescript
// frontend/src/app/page.tsx
export default function HomePage() {
  const { session } = useAuth();

  // No forced redirect - allows logged-in users to view home page
  // Shows different content based on auth state
}
```

### File Changes Summary

**Frontend Changes**:
1. `frontend/src/app/page.tsx` - Remove forced dashboard redirect (lines 12-16)
2. `frontend/src/components/ui/header.tsx` - Add navigation links, auth-aware display, active indicator
3. `frontend/src/app/providers/auth-provider.tsx` - Verify localStorage persistence (may need no changes)

**Backend Changes**:
- None required

**Testing**:
1. Manual testing of navigation flows
2. Manual testing of auth persistence across page reloads
3. Manual testing of header display in different auth states

---

## Implementation Phases

### Phase 1: Fix Infinite Redirect Loop
**Goal**: Allow logged-in users to access the home page without automatic redirects

**Changes**:
- Remove useEffect redirect logic from page.tsx (lines 12-16)
- Remove conditional loading message (lines 18-24)
- Update home page to show content for both logged-in and logged-out users

**Validation**:
- Logged-in user can navigate to home page without redirect
- Logged-in user can navigate from home to dashboard and back
- Logged-out user can still access home page

### Phase 2: Verify Auth Persistence
**Goal**: Ensure authentication state persists correctly across page reloads

**Changes**:
- Review auth-provider.tsx localStorage implementation
- Test page reload with valid token
- Test page reload with expired token
- Fix any issues found (if any)

**Validation**:
- User remains logged in after page refresh
- User is logged out after token expiry
- Session data is correctly restored from localStorage

### Phase 3: Enhance Header Navigation
**Goal**: Add comprehensive navigation links with auth-aware display

**Changes**:
- Remove "return null" for logged-out state (line 16-18)
- Add navigation links: Home, Dashboard, Add Task (logged-in)
- Add navigation links: Home, Login, Signup (logged-out)
- Import and use usePathname hook
- Add active page indicator styling
- Improve responsive design

**Validation**:
- Header shows correct links for logged-in users
- Header shows correct links for logged-out users
- Active page is visually highlighted
- Header is responsive on mobile devices
- Logout button works correctly

### Phase 4: Testing & Validation
**Goal**: Ensure all functionality works end-to-end

**Tests**:
- Navigate between all pages as logged-in user
- Navigate between all pages as logged-out user
- Refresh page on each route and verify auth state
- Test logout and verify header updates
- Test on mobile viewport

**Validation**:
- No redirect loops
- Auth persists across reloads
- Header displays correctly in all states
- All existing functionality still works

---

## Success Criteria Validation

- [x] **SC-001**: Users remain logged in after page refresh 100% of the time when their token is valid
- [x] **SC-002**: Logged-in users can navigate between Home and Dashboard without any redirect loops
- [x] **SC-003**: Unauthenticated users can access public pages (Home, Login, Signup) without being redirected
- [x] **SC-004**: Protected routes (Dashboard, Tasks) redirect unauthenticated users to login 100% of the time
- [x] **SC-005**: Header navigation updates correctly within 1 second of authentication state changes
- [x] **SC-006**: All existing functionality (login, task creation, task editing, task deletion) continues to work without regressions
- [x] **SC-007**: Header navigation is fully functional and accessible on mobile devices (viewport width < 768px)
- [x] **SC-008**: Active page indicator in header updates correctly 100% of the time when navigating between pages

---

## Risk Assessment

### Low Risk
- Removing redirect logic from home page (simple code deletion)
- Adding navigation links to header (standard React/Next.js patterns)
- Auth persistence verification (code already exists)

### Medium Risk
- Header responsive design (requires testing on multiple screen sizes)
- Active page indicator (requires correct pathname matching)

### Mitigation Strategies
- Incremental implementation with testing at each phase
- Manual testing on multiple devices and browsers
- Verify no regressions in existing functionality

---

## Dependencies

### External Dependencies
- None (all functionality achievable with existing stack)

### Internal Dependencies
- Existing AuthProvider must be functional
- Existing WithAuth HOC must work correctly
- Next.js usePathname hook must be available (App Router)
- localStorage must be available in browser

### Assumptions
- Auth persistence code in auth-provider.tsx is correct (needs verification)
- WithAuth HOC correctly protects routes
- No middleware is interfering with navigation
- Browser localStorage is enabled

---

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement Phase 1: Fix redirect loop
3. Implement Phase 2: Verify auth persistence
4. Implement Phase 3: Enhance header navigation
5. Implement Phase 4: Testing and validation
6. Deploy and verify in production environment
