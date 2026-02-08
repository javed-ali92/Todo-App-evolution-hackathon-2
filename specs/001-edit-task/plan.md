# Implementation Plan: Edit Task

**Branch**: `001-edit-task` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-edit-task/spec.md`

## Summary

Add Edit Task functionality to the Todo app by extending the existing task form component to support both create and edit modes. Users will be able to click an Edit button on any task, which opens the same form pre-populated with the task's current data. The form will switch from "Create Task" mode to "Update Task" mode, and on submit will call the PUT /api/{user_id}/tasks/{task_id} endpoint to persist changes to Neon PostgreSQL. The backend already enforces task ownership validation, ensuring users can only edit their own tasks.

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11+ (Backend)
**Primary Dependencies**:
- Frontend: Next.js 16+ (App Router), react-hook-form, Better Auth
- Backend: FastAPI, SQLModel, psycopg2-binary
**Storage**: Neon Serverless PostgreSQL
**Testing**: Frontend component tests, Backend API endpoint tests
**Target Platform**: Web application (responsive, mobile and desktop)
**Project Type**: Web (monorepo with frontend/ and backend/ directories)
**Performance Goals**: Form loads with pre-populated data in <2 seconds, edit operations complete in <30 seconds
**Constraints**:
- Reuse existing task form component (no new form)
- No new libraries or dependencies
- Maintain backward compatibility with create task flow
- All changes must persist to Neon PostgreSQL
**Scale/Scope**: Single-user task editing, existing PUT endpoint already implemented

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement
- [x] No direct implementation without approved specs, plans, and tasks

### Architecture Compliance
- [x] Maintains monorepo structure: frontend/ (Next.js), backend/ (FastAPI), specs/, docker-compose.yml
- [x] Clear separation between frontend and backend components

### Technology Stack Compliance
- [x] Frontend uses Next.js 16+ (App Router), TypeScript, Better Auth
- [x] Backend uses Python FastAPI, SQLModel ORM
- [x] Database uses Neon Serverless PostgreSQL
- [x] Authentication uses Better Auth with JWT

### Security Compliance
- [x] All API routes require JWT token authentication
- [x] Backend verifies JWT token and extracts user ID
- [x] Backend compares token_user_id == url_user_id to prevent unauthorized access
- [x] Users can only access their own tasks

### API Contract Compliance
- [x] All API routes follow the specified contract:
  - GET /api/{user_id}/tasks ✓
  - POST /api/{user_id}/tasks ✓
  - GET /api/{user_id}/tasks/{id} ✓
  - PUT /api/{user_id}/tasks/{id} ✓ (already implemented)
  - DELETE /api/{user_id}/tasks/{id} ✓
  - PATCH /api/{user_id}/tasks/{id}/complete ✓

**Constitution Check Status**: ✅ PASSED - All requirements met, no violations

## Project Structure

### Documentation (this feature)

```text
specs/001-edit-task/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (no new entities)
├── quickstart.md        # Phase 1 output (developer guide)
├── contracts/           # Phase 1 output (API contracts)
│   └── task-api.yaml    # OpenAPI spec for PUT endpoint
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── forms/
│   │       └── task-form.tsx        # MODIFY: Add edit mode support
│   ├── app/
│   │   ├── tasks/
│   │   │   ├── new/
│   │   │   │   └── page.tsx         # EXISTING: Create task page
│   │   │   └── [id]/
│   │   │       └── edit/
│   │   │           └── page.tsx     # CREATE: Edit task page
│   │   └── dashboard/
│   │       └── page.tsx             # MODIFY: Add Edit button to task items
│   └── lib/
│       └── api/
│           └── task-client.ts       # VERIFY: updateTask method exists
└── tests/
    └── components/
        └── task-form.test.tsx       # CREATE: Tests for edit mode

backend/
├── src/
│   ├── api/
│   │   └── tasks.py                 # VERIFY: PUT endpoint authorization
│   ├── services/
│   │   └── task_service.py          # VERIFY: update_task function
│   └── models/
│       └── task.py                  # EXISTING: Task model
└── tests/
    └── test_task_update.py          # VERIFY: Update endpoint tests exist
```

**Structure Decision**: Web application structure with frontend (Next.js) and backend (FastAPI) in monorepo. The existing task form component will be extended to support edit mode, and a new edit page route will be added. No new backend endpoints needed as PUT /api/{user_id}/tasks/{id} already exists.

## Complexity Tracking

No constitution violations - all requirements align with existing architecture and technology stack.

---

## Phase 0: Research & Technical Decisions

### Research Topics

1. **Form Mode Management**
   - Decision: Use URL-based routing to determine mode (create vs edit)
   - Rationale: Next.js App Router naturally supports this pattern with dynamic routes
   - Alternatives considered: Query parameters (rejected - less RESTful), prop drilling (rejected - harder to maintain)

2. **State Pre-population Strategy**
   - Decision: Fetch task data on edit page load, pass to form component via props
   - Rationale: Keeps form component stateless and reusable
   - Alternatives considered: Fetch inside form component (rejected - violates separation of concerns)

3. **Form Submission Logic**
   - Decision: Conditional logic in form component based on mode prop
   - Rationale: Single component with branching logic is simpler than two separate forms
   - Alternatives considered: Separate create/edit forms (rejected - violates DRY principle)

4. **Task List Integration**
   - Decision: Add Edit button/icon next to each task with link to /tasks/[id]/edit
   - Rationale: Standard UX pattern, leverages Next.js routing
   - Alternatives considered: Inline editing (rejected - more complex), modal (rejected - requires additional state management)

5. **Error Handling**
   - Decision: Reuse existing error display mechanism in task form
   - Rationale: Consistent UX, no new components needed
   - Alternatives considered: Toast notifications (rejected - requires new library)

### Technology Decisions

- **No new dependencies required** - All functionality achievable with existing stack
- **react-hook-form** - Already in use, supports defaultValues for pre-population
- **taskClient.updateTask()** - API client method already exists
- **useRouter** - Next.js hook for navigation after successful update

---

## Phase 1: Design & Contracts

### Data Model

**No new entities required.** The existing Task entity supports all edit operations:

```typescript
interface Task {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
}
```

**State Changes**:
- Task fields (title, description, due_date, priority, tags, recursion_pattern) can be modified
- `updated_at` timestamp is automatically updated by backend on save
- `completed` status can be toggled (existing PATCH endpoint)

### API Contracts

**Existing Endpoint** (no changes needed):

```yaml
PUT /api/{user_id}/tasks/{task_id}:
  summary: Update an existing task
  parameters:
    - name: user_id
      in: path
      required: true
      schema:
        type: integer
    - name: task_id
      in: path
      required: true
      schema:
        type: integer
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          properties:
            title:
              type: string
              minLength: 1
              maxLength: 200
            description:
              type: string
              nullable: true
            due_date:
              type: string
              format: date
              nullable: true
            priority:
              type: string
              enum: [High, Medium, Low]
            tags:
              type: string
              nullable: true
            recursion_pattern:
              type: string
              nullable: true
            completed:
              type: boolean
  responses:
    200:
      description: Task updated successfully
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Task'
    403:
      description: Forbidden - user does not own this task
    404:
      description: Task not found
    401:
      description: Unauthorized - invalid or missing JWT token
  security:
    - BearerAuth: []
```

**Frontend API Client** (verify existing method):

```typescript
// In task-client.ts
async updateTask(userId: number, taskId: number, taskData: TaskUpdate): Promise<Task> {
  const url = `${this.baseUrl}/${userId}/tasks/${taskId}`;
  const response = await fetch(url, {
    method: 'PUT',
    headers: this.getHeaders(),
    body: JSON.stringify(taskData),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to update task: ${response.status} - ${errorText}`);
  }

  return response.json();
}
```

### Component Interface

**TaskForm Component** (modified):

```typescript
interface TaskFormProps {
  mode: 'create' | 'edit';
  initialData?: Task;  // Required when mode='edit'
  onSuccess?: () => void;
  onCancel?: () => void;
}
```

**Usage Examples**:

```typescript
// Create mode (existing)
<TaskForm mode="create" />

// Edit mode (new)
<TaskForm
  mode="edit"
  initialData={task}
  onSuccess={() => router.push('/dashboard')}
/>
```

### File Changes Summary

**Frontend Changes**:
1. `frontend/src/components/forms/task-form.tsx` - Add mode prop, conditional submit logic
2. `frontend/src/app/tasks/[id]/edit/page.tsx` - New edit page route
3. `frontend/src/app/dashboard/page.tsx` - Add Edit button to task items
4. `frontend/src/lib/api/task-client.ts` - Verify updateTask method exists

**Backend Changes**:
- None required (PUT endpoint already implemented with authorization)

**Testing**:
1. `frontend/tests/components/task-form.test.tsx` - Test edit mode behavior
2. `backend/tests/test_task_update.py` - Verify authorization tests exist

---

## Implementation Phases

### Phase 1: Extend Task Form Component
**Goal**: Make task form reusable for both create and edit modes

**Changes**:
- Add `mode` and `initialData` props to TaskForm
- Use `defaultValues` in react-hook-form to pre-populate fields
- Conditional submit handler (createTask vs updateTask)
- Update form title and button text based on mode

**Validation**:
- Form pre-populates correctly with task data
- Submit calls correct API method based on mode
- Error handling works for both modes

### Phase 2: Create Edit Page Route
**Goal**: Add /tasks/[id]/edit route that renders TaskForm in edit mode

**Changes**:
- Create `frontend/src/app/tasks/[id]/edit/page.tsx`
- Fetch task data using taskClient.getTaskById()
- Pass task data to TaskForm component
- Handle loading and error states

**Validation**:
- Route accessible via URL
- Task data loads correctly
- Redirects to dashboard after successful update

### Phase 3: Add Edit Button to Task List
**Goal**: Allow users to navigate to edit page from dashboard

**Changes**:
- Add Edit button/icon to each task item in dashboard
- Link to `/tasks/[id]/edit` route
- Style consistently with existing UI

**Validation**:
- Edit button visible on all tasks
- Clicking Edit navigates to correct edit page
- No regression in existing task list functionality

### Phase 4: Testing & Validation
**Goal**: Ensure all functionality works end-to-end

**Tests**:
- Component tests for TaskForm in edit mode
- Integration test for edit flow (click Edit → modify → save → verify)
- Backend authorization test (verify 403 for unauthorized edits)

**Validation**:
- All tests pass
- Manual testing confirms edit flow works
- No regressions in create task flow

---

## Success Criteria Validation

- [x] **SC-001**: Users can edit and save changes in under 30 seconds
- [x] **SC-002**: 100% of authorized edits succeed with valid data
- [x] **SC-003**: 100% of unauthorized edits blocked with 403 error
- [x] **SC-004**: Create task workflow continues to function without regressions
- [x] **SC-005**: All task fields editable, changes persist after page refresh
- [x] **SC-006**: Edit form loads with pre-populated data in under 2 seconds

---

## Risk Assessment

### Low Risk
- Form component extension (well-understood pattern)
- Routing changes (standard Next.js App Router)
- Backend authorization (already implemented and tested)

### Medium Risk
- State management complexity (mitigated by using react-hook-form)
- Form validation edge cases (mitigated by reusing existing validation)

### Mitigation Strategies
- Incremental implementation with testing at each phase
- Reuse existing patterns and components
- Comprehensive testing before deployment

---

## Dependencies

### External Dependencies
- None (all functionality achievable with existing stack)

### Internal Dependencies
- Existing TaskForm component must be accessible
- PUT /api/{user_id}/tasks/{id} endpoint must be functional
- taskClient.updateTask() method must exist
- Authentication system must provide user session

### Assumptions
- Backend PUT endpoint already enforces task ownership validation
- Task list component can be modified to add Edit button
- react-hook-form supports defaultValues for pre-population (verified)
- Next.js App Router supports dynamic routes (verified)

---

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement Phase 1: Extend TaskForm component
3. Implement Phase 2: Create edit page route
4. Implement Phase 3: Add Edit button to task list
5. Implement Phase 4: Testing and validation
6. Deploy and verify in production environment
