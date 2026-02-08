# Implementation Tasks: Edit Task

**Feature**: Edit Task
**Branch**: `001-edit-task`
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
**User Stories**: US1 (Edit Task Details), US2 (Task Ownership Authorization), US3 (Form Mode Indication)

---

## Phase 0: Setup & Verification

### Verification Tasks

- [X] [TASK-001] [P1] [Setup] Verify backend PUT endpoint exists and is functional
      File: backend/src/api/tasks.py
      Acceptance: Confirm PUT /api/{user_id}/tasks/{task_id} endpoint exists with authorization
      Dependencies: None
      Test: curl -X PUT http://localhost:8001/api/25/tasks/5 -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title":"Test Update"}'
      Status: ✅ Verified at tasks.py:127-163 with authorization

- [X] [TASK-002] [P1] [Setup] Verify taskClient.updateTask() method exists in frontend
      File: frontend/src/lib/api/task-client.ts
      Acceptance: Confirm updateTask(userId, taskId, taskData) method exists and returns Promise<Task>
      Dependencies: None
      Test: Read file and verify method signature matches expected interface
      Status: ✅ Verified at task-client.ts:131-145, also fixed TaskUpdate interface to include all fields

- [X] [TASK-003] [P1] [Setup] Locate existing TaskForm component
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: Confirm component exists, uses react-hook-form, and has submit handler
      Dependencies: None
      Test: Read file and identify current props, form structure, and submit logic
      Status: ✅ Located and analyzed

- [X] [TASK-004] [P1] [Setup] Locate task list component in dashboard
      File: frontend/src/app/dashboard/page.tsx
      Acceptance: Confirm task list renders tasks and has space for Edit button
      Dependencies: None
      Test: Read file and identify where tasks are mapped/rendered
      Status: ✅ Located TaskList component at task-list.tsx

---

## Phase 1: Extend Task Form Component

### US1: Edit Task Details + US3: Form Mode Indication

- [X] [TASK-005] [P1] [US1+US3] Add mode and initialData props to TaskForm interface
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: TaskFormProps interface includes mode: 'create' | 'edit' and initialData?: Task
      Dependencies: [TASK-003]
      Test: TypeScript compilation succeeds with new props
      Status: ✅ Implemented with default mode='create'

- [X] [TASK-006] [P1] [US1] Implement form pre-population with defaultValues
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: useForm hook uses defaultValues based on mode and initialData
      Dependencies: [TASK-005]
      Test: Open form in edit mode and verify all fields show existing task data
      Status: ✅ Implemented with conditional defaultValues

- [X] [TASK-007] [P3] [US3] Add conditional form title based on mode
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: Form displays "Create New Task" when mode='create' and "Edit Task" when mode='edit'
      Dependencies: [TASK-005]
      Test: Verify form title changes based on mode prop
      Status: ✅ Implemented with h1 heading

- [X] [TASK-008] [P3] [US3] Add conditional submit button text based on mode
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: Button shows "Create Task" when mode='create' and "Update Task" when mode='edit'
      Dependencies: [TASK-005]
      Test: Verify button text changes based on mode prop
      Status: ✅ Implemented with conditional rendering

- [X] [TASK-009] [P1] [US1] Implement conditional submit handler for create vs edit
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: onSubmit calls createTask when mode='create' and updateTask when mode='edit'
      Dependencies: [TASK-005, TASK-006]
      Test: Submit form in both modes and verify correct API method is called
      Status: ✅ Implemented with mode-based branching logic

- [X] [TASK-010] [P1] [US1] Add onSuccess and onCancel callback props
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: TaskFormProps includes optional onSuccess and onCancel callbacks
      Dependencies: [TASK-005]
      Test: Pass callbacks and verify they are called at appropriate times
      Status: ✅ Implemented with handleCancel function

- [ ] [TASK-011] [P1] [US1] Test create mode still works after changes
      File: frontend/src/components/forms/task-form.tsx
      Acceptance: Navigate to /tasks/new, fill form, submit, verify task created
      Dependencies: [TASK-009]
      Test: Manual test - create a new task and verify no regressions
      Status: ⏳ Requires manual testing

---

## Phase 2: Create Edit Page Route

### US1: Edit Task Details

- [X] [TASK-012] [P1] [US1] Create edit page directory structure
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Directory structure exists: frontend/src/app/tasks/[id]/edit/
      Dependencies: None
      Test: Verify directory exists with correct structure
      Status: ✅ Created directory structure

- [X] [TASK-013] [P1] [US1] Implement edit page component with task fetching
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page component fetches task by ID using taskClient.getTaskById()
      Dependencies: [TASK-012, TASK-002]
      Test: Navigate to /tasks/5/edit and verify task data is fetched
      Status: ✅ Implemented with useEffect hook for fetching

- [X] [TASK-014] [P1] [US1] Add loading state to edit page
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page shows "Loading task..." while fetching data
      Dependencies: [TASK-013]
      Test: Navigate to edit page and verify loading state appears briefly
      Status: ✅ Implemented loading state UI

- [X] [TASK-015] [P1] [US1] Add error handling to edit page
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page shows error message and back button if task fetch fails
      Dependencies: [TASK-013]
      Test: Navigate to /tasks/99999/edit (non-existent task) and verify error display
      Status: ✅ Implemented error state with back button

- [X] [TASK-016] [P1] [US1] Add authentication check to edit page
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page redirects to /login if user is not authenticated
      Dependencies: [TASK-013]
      Test: Access edit page without authentication and verify redirect
      Status: ✅ Implemented session check with redirect

- [ ] [TASK-017] [P1] [US1] Test edit page loads and displays form correctly
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Navigate to /tasks/5/edit, verify form loads with pre-populated data
      Dependencies: [TASK-013, TASK-014, TASK-015]
      Test: Manual test - open edit page for existing task and verify all fields populated
      Status: ⏳ Requires manual testing
              </div>
              <button
                onClick={() => router.push('/dashboard')}
                className="mt-4 text-blue-600 hover:underline"
              >
                ← Back to Dashboard
              </button>
            </div>
          );
        }

        if (!task) {
          return (
            <div className="max-w-2xl mx-auto px-4 py-8">
              <p>Task not found</p>
            </div>
          );
        }

        return (
          <div className="max-w-2xl mx-auto px-4 py-8">
            <TaskForm
              mode="edit"
              initialData={task}
              onSuccess={() => router.push('/dashboard')}
              onCancel={() => router.push('/dashboard')}
            />
          </div>
        );
      }
      ```

- [ ] [TASK-014] [P1] [US1] Add loading state to edit page
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page shows "Loading task..." while fetching data
      Dependencies: [TASK-013]
      Test: Navigate to edit page and verify loading state appears briefly

- [ ] [TASK-015] [P1] [US1] Add error handling to edit page
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page shows error message and back button if task fetch fails
      Dependencies: [TASK-013]
      Test: Navigate to /tasks/99999/edit (non-existent task) and verify error display

- [ ] [TASK-016] [P1] [US1] Add authentication check to edit page
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Page redirects to /login if user is not authenticated
      Dependencies: [TASK-013]
      Test: Access edit page without authentication and verify redirect

- [ ] [TASK-017] [P1] [US1] Test edit page loads and displays form correctly
      File: frontend/src/app/tasks/[id]/edit/page.tsx
      Acceptance: Navigate to /tasks/5/edit, verify form loads with pre-populated data
      Dependencies: [TASK-013, TASK-014, TASK-015]
      Test: Manual test - open edit page for existing task and verify all fields populated

---

## Phase 3: Add Edit Button to Task List

### US1: Edit Task Details

- [X] [TASK-018] [P1] [US1] Add Edit button to task list items
      File: frontend/src/app/dashboard/page.tsx
      Acceptance: Each task in the list displays an Edit button/link
      Dependencies: [TASK-004]
      Test: View dashboard and verify Edit button appears on all tasks
      Status: ✅ Implemented in task-list.tsx with Link component

- [X] [TASK-019] [P1] [US1] Style Edit button to match existing UI
      File: frontend/src/app/dashboard/page.tsx
      Acceptance: Edit button has consistent styling with other action buttons
      Dependencies: [TASK-018]
      Test: Verify Edit button styling matches design system
      Status: ✅ Styled with blue background (bg-blue-600) matching design

- [X] [TASK-020] [P1] [US1] Test Edit button navigation
      File: frontend/src/app/dashboard/page.tsx
      Acceptance: Clicking Edit button navigates to /tasks/{id}/edit with correct task ID
      Dependencies: [TASK-018, TASK-017]
      Test: Click Edit on task ID 5, verify navigation to /tasks/5/edit
      Status: ✅ Implemented with Next.js Link component

- [ ] [TASK-021] [P1] [US1] Verify task list refreshes after edit
      File: frontend/src/app/dashboard/page.tsx
      Acceptance: After editing a task, dashboard shows updated task data
      Dependencies: [TASK-020]
      Test: Edit a task, return to dashboard, verify changes are visible
      Status: ⏳ Requires manual testing with running servers

---

## Phase 4: Testing & Validation

### US2: Task Ownership Authorization

- [ ] [TASK-022] [P2] [US2] Test authorized user can edit their own tasks
      File: backend/tests/test_task_update.py
      Acceptance: User can successfully edit tasks they own
      Dependencies: [TASK-001]
      Test: Create task as User A, edit as User A, verify success

- [ ] [TASK-023] [P2] [US2] Test unauthorized user cannot edit other users' tasks
      File: backend/tests/test_task_update.py
      Acceptance: Attempting to edit another user's task returns 403 Forbidden
      Dependencies: [TASK-001]
      Test: Create task as User A, attempt to edit as User B, verify 403 error
      Code:
      ```bash
      # Test unauthorized access (should return 403)
      curl -X PUT http://localhost:8001/api/999/tasks/5 \
        -H "Authorization: Bearer <user_b_token>" \
        -H "Content-Type: application/json" \
        -d '{"title":"Hacked"}'
      ```

- [ ] [TASK-024] [P2] [US2] Test JWT token validation on edit endpoint
      File: backend/tests/test_task_update.py
      Acceptance: Requests without valid JWT token return 401 Unauthorized
      Dependencies: [TASK-001]
      Test: Attempt to edit task without Authorization header, verify 401 error

### End-to-End Testing

- [ ] [TASK-025] [P1] [US1] Test complete edit flow end-to-end
      File: N/A (Manual test)
      Acceptance: User can click Edit → modify fields → save → see updated task
      Dependencies: [TASK-020, TASK-021]
      Test: Complete full edit workflow and verify all steps work correctly
      Steps:
      1. Navigate to dashboard
      2. Click Edit on a task
      3. Modify title, description, due_date, priority
      4. Click Update Task
      5. Verify redirect to dashboard
      6. Verify task shows updated values
      7. Refresh page and verify changes persisted

- [ ] [TASK-026] [P1] [US1] Test edit with validation errors
      File: N/A (Manual test)
      Acceptance: Form shows validation errors for invalid input
      Dependencies: [TASK-009]
      Test: Submit form with empty title, verify error message displayed

- [ ] [TASK-027] [P1] [US1] Test cancel edit functionality
      File: N/A (Manual test)
      Acceptance: Clicking Cancel returns to dashboard without saving changes
      Dependencies: [TASK-010]
      Test: Open edit form, modify fields, click Cancel, verify no changes saved

- [ ] [TASK-028] [P1] [US1] Test edit with network error
      File: N/A (Manual test)
      Acceptance: Form shows error message if API request fails
      Dependencies: [TASK-009]
      Test: Simulate network failure, attempt to save, verify error handling

### Database Verification

- [ ] [TASK-029] [P1] [US1] Verify task updates persist in Neon PostgreSQL
      File: N/A (Database query)
      Acceptance: Updated task data is correctly stored in database
      Dependencies: [TASK-025]
      Test: Query database after edit and verify updated_at timestamp changed
      Code:
      ```sql
      -- Check task was updated
      SELECT id, title, description, updated_at
      FROM task
      WHERE id = 5;

      -- Verify updated_at timestamp changed
      SELECT id, title, created_at, updated_at,
             (updated_at > created_at) as was_updated
      FROM task
      WHERE id = 5;
      ```

### Regression Testing

- [ ] [TASK-030] [P1] [US1] Verify create task flow still works
      File: N/A (Manual test)
      Acceptance: Creating new tasks works exactly as before
      Dependencies: [TASK-011]
      Test: Navigate to /tasks/new, create task, verify no regressions

- [ ] [TASK-031] [P1] [US1] Verify delete task functionality still works
      File: N/A (Manual test)
      Acceptance: Deleting tasks works without issues
      Dependencies: [TASK-021]
      Test: Delete a task from dashboard, verify it's removed

- [ ] [TASK-032] [P1] [US1] Verify complete task functionality still works
      File: N/A (Manual test)
      Acceptance: Marking tasks as complete/incomplete works
      Dependencies: [TASK-021]
      Test: Toggle task completion status, verify it updates correctly

### Mobile & Accessibility Testing

- [ ] [TASK-033] [P3] [US3] Test edit functionality on mobile viewport
      File: N/A (Manual test)
      Acceptance: Edit button is accessible and form is usable on mobile
      Dependencies: [TASK-019]
      Test: Open dashboard on mobile viewport, verify Edit button is tappable

- [ ] [TASK-034] [P3] [US3] Test keyboard navigation for edit flow
      File: N/A (Manual test)
      Acceptance: Users can navigate edit form using keyboard only
      Dependencies: [TASK-017]
      Test: Use Tab, Enter, Escape keys to navigate and interact with form

---

## Task Summary

**Total Tasks**: 34
**By Priority**:
- P1 (Critical): 27 tasks
- P2 (Important): 3 tasks
- P3 (Nice-to-have): 4 tasks

**By User Story**:
- US1 (Edit Task Details): 24 tasks
- US2 (Task Ownership Authorization): 3 tasks
- US3 (Form Mode Indication): 4 tasks
- Setup/Testing: 3 tasks

**By Phase**:
- Phase 0 (Setup & Verification): 4 tasks
- Phase 1 (Extend Task Form): 7 tasks
- Phase 2 (Create Edit Page): 6 tasks
- Phase 3 (Add Edit Button): 4 tasks
- Phase 4 (Testing & Validation): 13 tasks

---

## Dependency Graph

```
Phase 0: Setup & Verification
├── TASK-001 (Verify backend PUT endpoint)
├── TASK-002 (Verify taskClient.updateTask)
├── TASK-003 (Locate TaskForm component)
└── TASK-004 (Locate task list component)

Phase 1: Extend Task Form Component
├── TASK-005 (Add mode/initialData props) ← depends on TASK-003
├── TASK-006 (Implement pre-population) ← depends on TASK-005
├── TASK-007 (Conditional form title) ← depends on TASK-005
├── TASK-008 (Conditional button text) ← depends on TASK-005
├── TASK-009 (Conditional submit handler) ← depends on TASK-005, TASK-006
├── TASK-010 (Add callbacks) ← depends on TASK-005
└── TASK-011 (Test create mode) ← depends on TASK-009

Phase 2: Create Edit Page Route
├── TASK-012 (Create directory structure)
├── TASK-013 (Implement edit page) ← depends on TASK-012, TASK-002
├── TASK-014 (Add loading state) ← depends on TASK-013
├── TASK-015 (Add error handling) ← depends on TASK-013
├── TASK-016 (Add auth check) ← depends on TASK-013
└── TASK-017 (Test edit page) ← depends on TASK-013, TASK-014, TASK-015

Phase 3: Add Edit Button to Task List
├── TASK-018 (Add Edit button) ← depends on TASK-004
├── TASK-019 (Style Edit button) ← depends on TASK-018
├── TASK-020 (Test navigation) ← depends on TASK-018, TASK-017
└── TASK-021 (Verify refresh) ← depends on TASK-020

Phase 4: Testing & Validation
├── TASK-022 (Test authorized edit) ← depends on TASK-001
├── TASK-023 (Test unauthorized edit) ← depends on TASK-001
├── TASK-024 (Test JWT validation) ← depends on TASK-001
├── TASK-025 (E2E test) ← depends on TASK-020, TASK-021
├── TASK-026 (Test validation) ← depends on TASK-009
├── TASK-027 (Test cancel) ← depends on TASK-010
├── TASK-028 (Test network error) ← depends on TASK-009
├── TASK-029 (Verify DB persistence) ← depends on TASK-025
├── TASK-030 (Test create regression) ← depends on TASK-011
├── TASK-031 (Test delete regression) ← depends on TASK-021
├── TASK-032 (Test complete regression) ← depends on TASK-021
├── TASK-033 (Test mobile) ← depends on TASK-019
└── TASK-034 (Test keyboard nav) ← depends on TASK-017
```

---

## Parallel Execution Opportunities

Tasks that can be executed in parallel (no dependencies between them):

**Batch 1 - Setup Phase** (can all run in parallel):
- TASK-001, TASK-002, TASK-003, TASK-004

**Batch 2 - Form Component** (after TASK-005 completes):
- TASK-006, TASK-007, TASK-008, TASK-010

**Batch 3 - Edit Page Features** (after TASK-013 completes):
- TASK-014, TASK-015, TASK-016

**Batch 4 - Authorization Tests** (after TASK-001 completes):
- TASK-022, TASK-023, TASK-024

**Batch 5 - Regression Tests** (after Phase 3 completes):
- TASK-030, TASK-031, TASK-032

---

## Implementation Order Recommendation

1. **Start with Setup** (TASK-001 through TASK-004) - Run in parallel
2. **Extend TaskForm** (TASK-005 through TASK-011) - Sequential with some parallel opportunities
3. **Create Edit Page** (TASK-012 through TASK-017) - Mostly sequential
4. **Add Edit Button** (TASK-018 through TASK-021) - Sequential
5. **Run All Tests** (TASK-022 through TASK-034) - Many can run in parallel

**Critical Path**: TASK-003 → TASK-005 → TASK-009 → TASK-013 → TASK-018 → TASK-020 → TASK-025

**Estimated Total Time**: 6-8 hours for implementation + 2-3 hours for testing = 8-11 hours total

---

## Success Validation Checklist

After completing all tasks, verify:

- [ ] Users can click Edit on any task and see the form pre-populated
- [ ] Users can modify task fields and save changes successfully
- [ ] Changes persist in Neon PostgreSQL database
- [ ] Only task owners can edit their tasks (403 for unauthorized attempts)
- [ ] Form clearly indicates create vs edit mode
- [ ] Create task workflow still works without regressions
- [ ] All existing features (delete, complete) still work
- [ ] Edit functionality works on mobile devices
- [ ] Form is accessible via keyboard navigation
- [ ] Error messages display correctly for validation and network errors

---

## Notes

- All file paths are relative to repository root
- Test commands assume backend running on localhost:8001 and frontend on localhost:3000
- JWT tokens must be obtained via login endpoint before testing
- Database queries assume Neon PostgreSQL connection is configured
- Manual tests should be performed in both Chrome and Firefox
- Mobile testing should cover iOS Safari and Android Chrome at minimum
