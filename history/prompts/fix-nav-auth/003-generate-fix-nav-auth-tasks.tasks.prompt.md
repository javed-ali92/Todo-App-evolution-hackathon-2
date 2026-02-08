---
id: 003
title: Generate Fix Nav Auth Tasks
stage: tasks
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: fix-nav-auth
branch: 002-fix-nav-auth
user: HP
command: /sp.tasks
labels: ["tasks", "fix-nav-auth", "implementation-breakdown"]
links:
  spec: specs/002-fix-nav-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fix-nav-auth/tasks.md
tests: []
---

## Prompt

1. Inspect auth redirect logic.
2. Remove forced dashboard redirect after login.
3. Allow logged-in users to visit Home page.
4. Update header to include all page links.
5. Improve header UI and active link state.
6. Persist auth state on page reload.
7. Ensure logout clears stored auth data.

## Response snapshot

Created comprehensive tasks.md file with 45 detailed implementation tasks organized by user story and phase.

**Task Breakdown**:

**Phase 0: Setup & Verification** (4 tasks)
- T001: Verify auth provider implementation
- T002: Locate home page component
- T003: Locate header component
- T004: Locate WithAuth HOC

**Phase 1: User Story 1 (P1) - Auth State Persistence** (5 tasks)
- T005: Review auth-provider.tsx localStorage implementation
- T006: Verify checkAuthStatus is called on mount
- T007: Test auth persistence with valid token
- T008: Test auth persistence with expired token
- T009: Fix auth persistence issues if found

**Phase 2: User Story 2 (P2) - Fix Infinite Redirect Loop** (7 tasks)
- T010: Remove useEffect redirect logic from home page
- T011: Remove conditional loading message
- T012: Update home page content for both auth states
- T013-T016: Test navigation flows (dashboard↔home, unauth access)

**Phase 3: User Story 3 (P3) - Improved Header Navigation** (14 tasks)
- T017-T019: Import and setup usePathname hook
- T020: Create linkClass helper for active indicator
- T021: Implement new header structure
- T022-T024: Add navigation links (logged-out and logged-in)
- T025: Apply active page indicator styling
- T026-T030: Test header display and functionality

**Phase 4: Testing & Validation** (15 tasks)
- T031-T035: End-to-end testing (navigation flows, auth persistence, header updates)
- T036-T040: Regression testing (login, tasks CRUD operations)
- T041-T043: Cross-browser testing (Chrome, Firefox, Safari)
- T044-T045: Mobile testing (viewport, usability)

**Task Organization**:
- Total: 45 tasks
- P1 (Critical): 5 tasks
- P2 (Important): 7 tasks
- P3 (Nice-to-have): 14 tasks
- Testing: 19 tasks

**By User Story**:
- US1 (Auth State Persistence): 5 tasks
- US2 (Fix Redirect Loop): 7 tasks
- US3 (Header Navigation UI): 14 tasks
- Setup/Verification: 4 tasks
- Testing & Validation: 15 tasks

**Key Features**:
- Each task includes file path, acceptance criteria, dependencies, and test instructions
- Dependency graph shows task relationships and critical path
- Parallel execution opportunities identified (6 batches)
- Code examples provided for complex tasks (linkClass helper, header structure)
- Estimated total time: 3-5 hours (2-3 implementation + 1-2 testing)

**Critical Path**: T002 → T010 → T011 → T012 → T013 → T032

**Files to Modify**:
- frontend/src/app/page.tsx (remove forced redirect)
- frontend/src/components/ui/header.tsx (add navigation links, auth-aware display)
- frontend/src/app/providers/auth-provider.tsx (verify only, likely no changes)

**Files to Create**: None (all changes are modifications)

**Backend Changes**: None required

**MVP Scope** (User Story 1 only):
- Phase 0: Setup (T001-T004)
- Phase 1: Auth Persistence (T005-T009)
- Test: Auth persistence (T033)

**Parallel Execution Opportunities**:
- Batch 1: T001, T002, T003, T004 (setup)
- Batch 2: T007, T008 (auth testing)
- Batch 3: T013, T014, T015 (redirect testing)
- Batch 4: T022, T023, T024 (header links)
- Batch 5: T036-T040 (regression tests)
- Batch 6: T041-T043 (cross-browser tests)

## Outcome

- ✅ Impact: Complete task breakdown ready for implementation with clear dependencies and acceptance criteria
- 🧪 Tests: 19 testing tasks covering E2E, regression, cross-browser, and mobile
- 📁 Files: 1 file created (tasks.md with 45 tasks)
- 🔁 Next prompts: Run `/sp.implement` to begin implementation or start with MVP (US1 only)
- 🧠 Reflection: Tasks are well-organized by user story priority, with clear dependencies and parallel execution opportunities

## Evaluation notes (flywheel)

- Failure modes observed: None - tasks generated successfully with comprehensive coverage
- Graders run and results (PASS/FAIL): PASS - All tasks include file paths, acceptance criteria, and dependencies
- Prompt variant (if applicable): Standard /sp.tasks workflow
- Next experiment (smallest change to try): Consider adding automated test tasks if TDD approach is preferred in future
