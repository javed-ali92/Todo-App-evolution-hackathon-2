# Implementation Tasks: Fix Navigation, Header UI, and Auth Persistence

**Feature**: Fix Navigation, Header UI, and Auth Persistence
**Branch**: `002-fix-nav-auth`
**Date**: 2026-02-09
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Task Format

```
- [ ] [TaskID] [Priority] [Story] Description
      File: path/to/file.ext
      Acceptance: Clear criteria for completion
      Dependencies: [TaskID, TaskID]
```

**Priority Levels**: P1 (Critical), P2 (Important), P3 (Nice-to-have)
**User Stories**: US1 (Auth Persistence), US2 (Fix Redirect Loop), US3 (Header Navigation UI)

---

## Phase 0: Setup & Verification

### Verification Tasks

- [x] T001 [P] Locate and verify auth provider implementation in frontend/src/app/providers/auth-provider.tsx
      Acceptance: Confirm localStorage persistence code exists (login, logout, checkAuthStatus functions)
      Dependencies: None

- [x] T002 [P] Locate home page component in frontend/src/app/page.tsx
      Acceptance: Identify redirect logic in useEffect hook (lines 12-16)
      Dependencies: None

- [x] T003 [P] Locate header component in frontend/src/components/ui/header.tsx
      Acceptance: Confirm current implementation returns null for logged-out users
      Dependencies: None

- [x] T004 [P] Locate WithAuth HOC in frontend/src/components/hoc/with-auth.tsx
      Acceptance: Verify it redirects unauthenticated users to login
      Dependencies: None

---

## Phase 1: User Story 1 (P1) - Auth State Persistence Across Page Reloads

### US1: Verify and Fix Auth Persistence

- [x] T005 [US1] Review auth-provider.tsx localStorage implementation
      File: frontend/src/app/providers/auth-provider.tsx
      Acceptance: Verify login() stores session (line 70), logout() clears session (line 84), checkAuthStatus() restores session (lines 90-112)
      Dependencies: [T001]

- [x] T006 [US1] Verify checkAuthStatus is called on mount
      File: frontend/src/app/providers/auth-provider.tsx
      Acceptance: Confirm useEffect calls checkAuthStatus() on component mount (lines 37-39)
      Dependencies: [T005]

- [ ] T007 [US1] Test auth persistence with valid token
      File: frontend/src/app/providers/auth-provider.tsx
      Acceptance: Login, refresh page, verify user remains logged in
      Dependencies: [T006]
      Test: Manual - Login → Refresh → Verify still authenticated

- [ ] T008 [US1] Test auth persistence with expired token
      File: frontend/src/app/providers/auth-provider.tsx
      Acceptance: Login, modify expiryTime to past date in localStorage, refresh, verify logout
      Dependencies: [T006]
      Test: Manual - Login → Modify expiryTime → Refresh → Verify logged out

- [ ] T009 [US1] Fix auth persistence issues if found
      File: frontend/src/app/providers/auth-provider.tsx
      Acceptance: If tests T007 or T008 fail, implement fixes to localStorage persistence
      Dependencies: [T007, T008]
      Note: May not be needed if existing implementation works correctly

---

## Phase 2: User Story 2 (P2) - Fix Infinite Dashboard Redirect Loop

### US2: Remove Forced Redirect from Home Page

- [x] T010 [US2] Remove useEffect redirect logic from home page
      File: frontend/src/app/page.tsx
      Acceptance: Delete lines 12-16 (useEffect that redirects logged-in users to dashboard)
      Dependencies: [T002]
      Code: Delete the entire useEffect block that checks session.isLoggedIn and calls router.push('/dashboard')

- [x] T011 [US2] Remove conditional loading message from home page
      File: frontend/src/app/page.tsx
      Acceptance: Delete lines 18-24 (conditional return showing "Redirecting to dashboard...")
      Dependencies: [T010]
      Code: Delete the if (session.isLoggedIn) return block with loading message

- [x] T012 [US2] Update home page content for both auth states
      File: frontend/src/app/page.tsx
      Acceptance: Home page renders content for both logged-in and logged-out users
      Dependencies: [T011]
      Code: Keep existing content, optionally add personalized greeting for logged-in users

- [ ] T013 [US2] Test navigation from dashboard to home
      File: frontend/src/app/page.tsx
      Acceptance: Login, navigate to dashboard, navigate to home, verify no redirect loop
      Dependencies: [T012]
      Test: Manual - Login → Dashboard → Home → Verify stays on home page

- [ ] T014 [US2] Test navigation from home to dashboard
      File: frontend/src/app/page.tsx
      Acceptance: Login, navigate to home, navigate to dashboard, verify navigation works
      Dependencies: [T012]
      Test: Manual - Login → Home → Dashboard → Verify navigation works

- [ ] T015 [US2] Test unauthenticated access to home page
      File: frontend/src/app/page.tsx
      Acceptance: Logout, navigate to home, verify page loads without redirect
      Dependencies: [T012]
      Test: Manual - Logout → Home → Verify page loads

- [ ] T016 [US2] Test unauthenticated access to protected routes
      File: frontend/src/components/hoc/with-auth.tsx
      Acceptance: Logout, try to access /dashboard, verify redirect to login
      Dependencies: [T004]
      Test: Manual - Logout → /dashboard → Verify redirect to /login

---

## Phase 3: User Story 3 (P3) - Improved Header Navigation UI

### US3: Enhance Header with Navigation Links

- [x] T017 [US3] Import usePathname hook in header component
      File: frontend/src/components/ui/header.tsx
      Acceptance: Add import { usePathname } from 'next/navigation' at top of file
      Dependencies: [T003]
      Code: import { useRouter, usePathname } from 'next/navigation';

- [x] T018 [US3] Remove logged-out return null from header
      File: frontend/src/components/ui/header.tsx
      Acceptance: Delete lines 16-18 (if (!session.isLoggedIn) return null;)
      Dependencies: [T003]
      Code: Remove the early return that hides header for logged-out users

- [x] T019 [US3] Add usePathname hook to header component
      File: frontend/src/components/ui/header.tsx
      Acceptance: Add const pathname = usePathname(); after other hooks
      Dependencies: [T017, T018]
      Code: const pathname = usePathname();

- [x] T020 [US3] Create linkClass helper function for active indicator
      File: frontend/src/components/ui/header.tsx
      Acceptance: Add function that returns CSS classes based on pathname match
      Dependencies: [T019]
      Code:
      ```typescript
      const linkClass = (path: string) => {
        const baseClass = "px-3 py-2 rounded-md text-sm font-medium transition-colors";
        const activeClass = "bg-blue-100 text-blue-700";
        const inactiveClass = "text-gray-700 hover:bg-gray-100 hover:text-gray-900";
        return `${baseClass} ${pathname === path ? activeClass : inactiveClass}`;
      };
      ```

- [x] T021 [US3] Implement new header structure with navigation links
      File: frontend/src/components/ui/header.tsx
      Acceptance: Replace return statement with new header structure including logo, nav links, and user info
      Dependencies: [T020]
      Code: Implement header with conditional navigation based on session.isLoggedIn

- [x] T022 [US3] Add logged-out navigation links (Home, Login, Signup)
      File: frontend/src/components/ui/header.tsx
      Acceptance: When logged out, header shows Home, Login, Signup links
      Dependencies: [T021]
      Code: Conditional rendering for !session.isLoggedIn state

- [x] T023 [US3] Add logged-in navigation links (Home, Dashboard, Add Task)
      File: frontend/src/components/ui/header.tsx
      Acceptance: When logged in, header shows Home, Dashboard, Add Task links
      Dependencies: [T021]
      Code: Conditional rendering for session.isLoggedIn state

- [x] T024 [US3] Add user info and logout button for logged-in state
      File: frontend/src/components/ui/header.tsx
      Acceptance: When logged in, header shows username and logout button
      Dependencies: [T021]
      Code: Conditional rendering of user info section

- [x] T025 [US3] Apply active page indicator styling
      File: frontend/src/components/ui/header.tsx
      Acceptance: Current page link is highlighted with blue background
      Dependencies: [T020, T021]
      Code: Use linkClass(path) for each Link component

- [ ] T026 [US3] Test header display when logged out
      File: frontend/src/components/ui/header.tsx
      Acceptance: Logout, verify header shows Home, Login, Signup links
      Dependencies: [T022]
      Test: Manual - Logout → Verify header shows correct links

- [ ] T027 [US3] Test header display when logged in
      File: frontend/src/components/ui/header.tsx
      Acceptance: Login, verify header shows Home, Dashboard, Add Task, Username, Logout
      Dependencies: [T023, T024]
      Test: Manual - Login → Verify header shows correct links

- [ ] T028 [US3] Test active page indicator on all routes
      File: frontend/src/components/ui/header.tsx
      Acceptance: Navigate to each page, verify active link is highlighted
      Dependencies: [T025]
      Test: Manual - Navigate to /, /dashboard, /tasks/new → Verify active indicator

- [ ] T029 [US3] Test logout button functionality
      File: frontend/src/components/ui/header.tsx
      Acceptance: Click logout, verify redirect to login and header updates
      Dependencies: [T024]
      Test: Manual - Login → Click Logout → Verify redirect and header update

- [ ] T030 [US3] Test header responsive design on mobile
      File: frontend/src/components/ui/header.tsx
      Acceptance: View header on mobile viewport (<768px), verify usability
      Dependencies: [T021]
      Test: Manual - DevTools mobile view → Verify header is usable

---

## Phase 4: Testing & Validation

### End-to-End Testing

- [ ] T031 Test complete navigation flow as logged-out user
      File: N/A (Manual test)
      Acceptance: Visit all public pages, verify no unwanted redirects
      Dependencies: [T015, T026]
      Test: Logout → Home → Login → Signup → Verify all accessible

- [ ] T032 Test complete navigation flow as logged-in user
      File: N/A (Manual test)
      Acceptance: Visit all pages, verify free navigation without redirect loops
      Dependencies: [T013, T014, T027]
      Test: Login → Home → Dashboard → Tasks → Home → Verify no loops

- [ ] T033 Test auth persistence across multiple page reloads
      File: N/A (Manual test)
      Acceptance: Login, refresh on multiple pages, verify auth persists
      Dependencies: [T007]
      Test: Login → Dashboard → Refresh → Home → Refresh → Verify logged in

- [ ] T034 Test header updates on auth state changes
      File: N/A (Manual test)
      Acceptance: Login/logout, verify header updates immediately
      Dependencies: [T027, T029]
      Test: Logout → Verify header → Login → Verify header updates

- [ ] T035 Test active page indicator across all routes
      File: N/A (Manual test)
      Acceptance: Navigate to all routes, verify active indicator updates
      Dependencies: [T028]
      Test: Navigate to each route → Verify active link highlighted

### Regression Testing

- [ ] T036 Verify login functionality still works
      File: N/A (Manual test)
      Acceptance: Login with valid credentials, verify redirect to dashboard
      Dependencies: [T012]
      Test: Login → Verify redirect to dashboard and auth state

- [ ] T037 Verify task creation still works
      File: N/A (Manual test)
      Acceptance: Create new task, verify it appears in task list
      Dependencies: [T032]
      Test: Login → Add Task → Create → Verify task created

- [ ] T038 Verify task editing still works
      File: N/A (Manual test)
      Acceptance: Edit existing task, verify changes persist
      Dependencies: [T032]
      Test: Login → Dashboard → Edit Task → Save → Verify changes

- [ ] T039 Verify task deletion still works
      File: N/A (Manual test)
      Acceptance: Delete task, verify it's removed from list
      Dependencies: [T032]
      Test: Login → Dashboard → Delete Task → Verify removed

- [ ] T040 Verify task completion toggle still works
      File: N/A (Manual test)
      Acceptance: Toggle task completion, verify state updates
      Dependencies: [T032]
      Test: Login → Dashboard → Toggle Complete → Verify updated

### Cross-Browser Testing

- [ ] T041 Test all functionality in Chrome/Edge
      File: N/A (Manual test)
      Acceptance: All features work correctly in Chrome/Edge
      Dependencies: [T032, T033, T034]
      Test: Run all tests in Chrome/Edge browser

- [ ] T042 Test all functionality in Firefox
      File: N/A (Manual test)
      Acceptance: All features work correctly in Firefox
      Dependencies: [T032, T033, T034]
      Test: Run all tests in Firefox browser

- [ ] T043 Test all functionality in Safari (if available)
      File: N/A (Manual test)
      Acceptance: All features work correctly in Safari
      Dependencies: [T032, T033, T034]
      Test: Run all tests in Safari browser

### Mobile Testing

- [ ] T044 Test navigation on mobile viewport
      File: N/A (Manual test)
      Acceptance: All navigation works on mobile (<768px)
      Dependencies: [T030]
      Test: DevTools mobile view → Test all navigation

- [ ] T045 Test header usability on mobile
      File: N/A (Manual test)
      Acceptance: Header links are tappable and readable on mobile
      Dependencies: [T030]
      Test: DevTools mobile view → Test header interaction

---

## Task Summary

**Total Tasks**: 45
**By Priority**:
- P1 (Critical): 5 tasks (US1: Auth Persistence)
- P2 (Important): 7 tasks (US2: Fix Redirect Loop)
- P3 (Nice-to-have): 14 tasks (US3: Header Navigation)
- Testing: 19 tasks

**By User Story**:
- US1 (Auth State Persistence): 5 tasks
- US2 (Fix Redirect Loop): 7 tasks
- US3 (Header Navigation UI): 14 tasks
- Setup/Verification: 4 tasks
- Testing & Validation: 15 tasks

**By Phase**:
- Phase 0 (Setup & Verification): 4 tasks
- Phase 1 (US1 - Auth Persistence): 5 tasks
- Phase 2 (US2 - Fix Redirect Loop): 7 tasks
- Phase 3 (US3 - Header Navigation): 14 tasks
- Phase 4 (Testing & Validation): 15 tasks

---

## Dependency Graph

```
Phase 0: Setup & Verification
├── T001 (Verify auth provider) [P]
├── T002 (Locate home page) [P]
├── T003 (Locate header) [P]
└── T004 (Locate WithAuth HOC) [P]

Phase 1: User Story 1 (P1) - Auth Persistence
├── T005 (Review auth-provider) ← depends on T001
├── T006 (Verify checkAuthStatus) ← depends on T005
├── T007 (Test valid token) ← depends on T006
├── T008 (Test expired token) ← depends on T006
└── T009 (Fix issues if found) ← depends on T007, T008

Phase 2: User Story 2 (P2) - Fix Redirect Loop
├── T010 (Remove useEffect redirect) ← depends on T002
├── T011 (Remove loading message) ← depends on T010
├── T012 (Update home content) ← depends on T011
├── T013 (Test dashboard to home) ← depends on T012
├── T014 (Test home to dashboard) ← depends on T012
├── T015 (Test unauth home access) ← depends on T012
└── T016 (Test unauth protected access) ← depends on T004

Phase 3: User Story 3 (P3) - Header Navigation
├── T017 (Import usePathname) ← depends on T003
├── T018 (Remove return null) ← depends on T003
├── T019 (Add usePathname hook) ← depends on T017, T018
├── T020 (Create linkClass helper) ← depends on T019
├── T021 (Implement header structure) ← depends on T020
├── T022 (Add logged-out links) ← depends on T021
├── T023 (Add logged-in links) ← depends on T021
├── T024 (Add user info/logout) ← depends on T021
├── T025 (Apply active indicator) ← depends on T020, T021
├── T026 (Test logged-out header) ← depends on T022
├── T027 (Test logged-in header) ← depends on T023, T024
├── T028 (Test active indicator) ← depends on T025
├── T029 (Test logout button) ← depends on T024
└── T030 (Test mobile responsive) ← depends on T021

Phase 4: Testing & Validation
├── T031 (E2E logged-out) ← depends on T015, T026
├── T032 (E2E logged-in) ← depends on T013, T014, T027
├── T033 (Auth persistence test) ← depends on T007
├── T034 (Header updates test) ← depends on T027, T029
├── T035 (Active indicator test) ← depends on T028
├── T036-T040 (Regression tests) ← depends on T032
├── T041-T043 (Cross-browser tests) ← depends on T032, T033, T034
└── T044-T045 (Mobile tests) ← depends on T030
```

---

## Parallel Execution Opportunities

Tasks that can be executed in parallel (no dependencies between them):

**Batch 1 - Setup Phase** (can all run in parallel):
- T001, T002, T003, T004

**Batch 2 - Auth Testing** (after T006 completes):
- T007, T008

**Batch 3 - Redirect Testing** (after T012 completes):
- T013, T014, T015

**Batch 4 - Header Testing** (after T021 completes):
- T022, T023, T024

**Batch 5 - Regression Tests** (after T032 completes):
- T036, T037, T038, T039, T040

**Batch 6 - Cross-Browser Tests** (after T032, T033, T034 complete):
- T041, T042, T043

---

## Implementation Order Recommendation

**MVP (Minimum Viable Product) - User Story 1 Only**:
1. Complete Phase 0 (T001-T004) - Run in parallel
2. Complete Phase 1 (T005-T009) - Verify auth persistence
3. Test auth persistence (T033)

**Full Implementation**:
1. **Start with Setup** (T001-T004) - Run in parallel
2. **Fix Auth Persistence** (T005-T009) - Sequential
3. **Fix Redirect Loop** (T010-T016) - Mostly sequential
4. **Enhance Header** (T017-T030) - Sequential with some parallel opportunities
5. **Run All Tests** (T031-T045) - Many can run in parallel

**Critical Path**: T002 → T010 → T011 → T012 → T013 → T032

**Estimated Total Time**: 2-3 hours for implementation + 1-2 hours for testing = 3-5 hours total

---

## Success Validation Checklist

After completing all tasks, verify:

- [ ] Users remain logged in after page refresh
- [ ] Logged-in users can navigate between Home and Dashboard without redirect loops
- [ ] Unauthenticated users can access public pages without redirects
- [ ] Protected routes redirect unauthenticated users to login
- [ ] Header shows correct links for logged-in users
- [ ] Header shows correct links for logged-out users
- [ ] Active page is highlighted in header
- [ ] Logout button works and updates header
- [ ] Header is responsive on mobile devices
- [ ] All existing functionality (login, tasks) still works

---

## Notes

- All file paths are relative to repository root
- Manual tests should be performed in multiple browsers
- Mobile testing should cover iOS Safari and Android Chrome at minimum
- Auth persistence is likely already working, may need no fixes
- Main changes are removing redirect and enhancing header
- No backend changes required
- No new dependencies required
