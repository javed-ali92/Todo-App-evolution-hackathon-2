# Research & Technical Decisions: Edit Task

**Feature**: Edit Task
**Branch**: 001-edit-task
**Date**: 2026-02-09

## Overview

This document captures the technical research and decisions made during the planning phase for the Edit Task feature. All decisions prioritize reusing existing components and patterns to minimize complexity and maintain consistency.

---

## Research Topic 1: Form Mode Management

### Question
How should the application determine whether the task form is in "create" or "edit" mode?

### Options Evaluated

1. **URL-based routing** (dynamic routes)
   - Create: `/tasks/new`
   - Edit: `/tasks/[id]/edit`
   - Pros: RESTful, leverages Next.js App Router, clear separation
   - Cons: Requires new route file

2. **Query parameters**
   - Create: `/tasks/form`
   - Edit: `/tasks/form?id=123&mode=edit`
   - Pros: Single route file
   - Cons: Less RESTful, harder to bookmark, query param parsing

3. **Prop drilling from parent**
   - Pass mode as prop from various entry points
   - Pros: Flexible
   - Cons: Harder to maintain, unclear source of truth

### Decision: URL-based routing

**Rationale**: Next.js App Router naturally supports dynamic routes with `[id]` segments. This approach is RESTful, provides clear URLs for bookmarking, and makes the mode determination explicit and maintainable.

**Implementation**:
- Existing: `frontend/src/app/tasks/new/page.tsx` (create mode)
- New: `frontend/src/app/tasks/[id]/edit/page.tsx` (edit mode)

---

## Research Topic 2: State Pre-population Strategy

### Question
How should task data be loaded and passed to the form component for editing?

### Options Evaluated

1. **Fetch in page component, pass via props**
   - Page fetches task data using `taskClient.getTaskById()`
   - Pass task object to TaskForm as `initialData` prop
   - Pros: Separation of concerns, form remains stateless
   - Cons: Additional prop passing

2. **Fetch inside form component**
   - TaskForm receives task ID, fetches data internally
   - Pros: Self-contained component
   - Cons: Violates single responsibility, harder to test

3. **Global state management**
   - Store task in Redux/Context
   - Form reads from global state
   - Pros: Accessible anywhere
   - Cons: Overkill for this use case, adds complexity

### Decision: Fetch in page component, pass via props

**Rationale**: Keeps the TaskForm component stateless and reusable. The page component is responsible for data fetching, while the form component focuses solely on presentation and user interaction. This aligns with React best practices and makes testing easier.

**Implementation**:
```typescript
// In edit page
const task = await taskClient.getTaskById(userId, taskId);
<TaskForm mode="edit" initialData={task} />
```

---

## Research Topic 3: Form Submission Logic

### Question
How should the form handle different submission logic for create vs edit modes?

### Options Evaluated

1. **Conditional logic in single component**
   - Single TaskForm with `if (mode === 'edit')` branching
   - Pros: DRY principle, single source of truth
   - Cons: Slightly more complex logic

2. **Separate CreateTaskForm and EditTaskForm**
   - Two distinct components
   - Pros: Clear separation, simpler individual components
   - Cons: Code duplication, harder to maintain consistency

3. **Higher-order component (HOC)**
   - Wrap base form with mode-specific behavior
   - Pros: Composition pattern
   - Cons: Over-engineering for this use case

### Decision: Conditional logic in single component

**Rationale**: The form fields and validation are identical for create and edit modes. Only the submission handler differs (createTask vs updateTask). Using conditional logic maintains DRY principles while keeping the code simple and maintainable.

**Implementation**:
```typescript
const onSubmit = async (data: TaskFormData) => {
  if (mode === 'create') {
    await taskClient.createTask(userId, data);
  } else {
    await taskClient.updateTask(userId, initialData.id, data);
  }
};
```

---

## Research Topic 4: Task List Integration

### Question
How should users access the edit functionality from the task list?

### Options Evaluated

1. **Edit button/icon with navigation**
   - Add Edit button next to each task
   - Link to `/tasks/[id]/edit`
   - Pros: Standard UX pattern, clear action
   - Cons: Requires UI space

2. **Inline editing**
   - Click task to edit in place
   - Pros: Seamless UX
   - Cons: Complex state management, harder to implement

3. **Modal/dialog**
   - Edit button opens modal with form
   - Pros: No navigation, stays on same page
   - Cons: Requires modal state management, new component

4. **Context menu (right-click)**
   - Right-click task for edit option
   - Pros: Saves UI space
   - Cons: Not discoverable, poor mobile support

### Decision: Edit button/icon with navigation

**Rationale**: This is the most standard and discoverable UX pattern. It leverages Next.js routing naturally and doesn't require additional state management. Users expect this pattern from other todo applications.

**Implementation**:
```typescript
<Link href={`/tasks/${task.id}/edit`}>
  <button>Edit</button>
</Link>
```

---

## Research Topic 5: Error Handling

### Question
How should edit-specific errors be handled and displayed?

### Options Evaluated

1. **Reuse existing form error display**
   - Use same error state and UI as create mode
   - Pros: Consistent UX, no new components
   - Cons: None

2. **Toast notifications**
   - Show errors in toast/snackbar
   - Pros: Non-blocking, modern UX
   - Cons: Requires new library (react-toastify, etc.)

3. **Error boundary**
   - Catch errors at page level
   - Pros: Centralized error handling
   - Cons: Less granular control

### Decision: Reuse existing form error display

**Rationale**: The existing TaskForm already has error handling with state variables (`error`, `success`) and UI display. Reusing this mechanism ensures consistency and avoids adding new dependencies.

**Implementation**: No changes needed - existing error handling works for both modes.

---

## Technology Stack Verification

### Frontend Dependencies (Existing)
- **Next.js 16+**: App Router with dynamic routes ✓
- **react-hook-form**: Supports `defaultValues` for pre-population ✓
- **TypeScript**: Type safety for props and interfaces ✓
- **Better Auth**: Provides user session for authorization ✓

### Backend Dependencies (Existing)
- **FastAPI**: PUT endpoint already implemented ✓
- **SQLModel**: Task model supports all fields ✓
- **JWT verification**: Authorization already enforced ✓
- **Neon PostgreSQL**: Database persistence working ✓

### New Dependencies Required
**None** - All functionality achievable with existing stack.

---

## API Verification

### Existing Endpoints Used

1. **GET /api/{user_id}/tasks/{id}**
   - Status: ✓ Implemented
   - Purpose: Fetch task data for editing
   - Authorization: JWT token required, user_id validation

2. **PUT /api/{user_id}/tasks/{id}**
   - Status: ✓ Implemented
   - Purpose: Update task data
   - Authorization: JWT token required, ownership validation
   - Request body: TaskUpdate (title, description, due_date, priority, tags, recursion_pattern, completed)

### Frontend API Client Methods

1. **taskClient.getTaskById(userId, taskId)**
   - Status: ✓ Exists in task-client.ts
   - Returns: Promise<Task>

2. **taskClient.updateTask(userId, taskId, taskData)**
   - Status: ✓ Exists in task-client.ts
   - Returns: Promise<Task>

---

## Performance Considerations

### Load Time
- **Target**: Form loads with pre-populated data in <2 seconds
- **Strategy**: Single API call to fetch task data, no additional requests
- **Validation**: Measure with browser DevTools Network tab

### Update Time
- **Target**: Edit operations complete in <30 seconds
- **Strategy**: Direct PUT request, no complex processing
- **Validation**: Measure end-to-end from form submit to dashboard refresh

---

## Security Considerations

### Authorization
- **Backend validation**: Already enforces token_user_id == url_user_id
- **Frontend protection**: Session check before allowing edit navigation
- **Error handling**: 403 Forbidden for unauthorized attempts

### Data Validation
- **Frontend**: react-hook-form validation (required fields, max lengths)
- **Backend**: SQLModel validation (field constraints, types)
- **Consistency**: Same validation rules as create mode

---

## Testing Strategy

### Unit Tests
- TaskForm component with mode='edit'
- Form pre-population with initialData
- Conditional submit logic

### Integration Tests
- Full edit flow: navigate → load → modify → save → verify
- Authorization: attempt to edit another user's task
- Error handling: network failures, validation errors

### Manual Testing
- Cross-browser compatibility
- Mobile responsiveness
- Keyboard navigation
- Screen reader accessibility

---

## Risks & Mitigation

### Risk: Form state conflicts between create and edit modes
**Mitigation**: Use react-hook-form's `reset()` with defaultValues to ensure clean state

### Risk: Stale data when editing
**Mitigation**: Fetch fresh task data on edit page load, not from cached list

### Risk: Race conditions with concurrent edits
**Mitigation**: Backend uses database transactions, last-write-wins strategy (acceptable for MVP)

---

## Alternatives Considered & Rejected

1. **GraphQL instead of REST**
   - Rejected: Existing API is REST, no need to change

2. **Optimistic UI updates**
   - Rejected: Adds complexity, not required for MVP

3. **Real-time collaboration**
   - Rejected: Out of scope, single-user editing sufficient

4. **Undo/redo functionality**
   - Rejected: Out of scope, can be added later if needed

---

## References

- Next.js App Router: https://nextjs.org/docs/app
- react-hook-form defaultValues: https://react-hook-form.com/api/useform
- FastAPI PUT endpoints: https://fastapi.tiangolo.com/tutorial/body-updates/
- RESTful routing conventions: https://restfulapi.net/resource-naming/

---

## Conclusion

All technical decisions prioritize simplicity and reuse of existing patterns. No new dependencies are required, and all functionality can be implemented with the current technology stack. The approach is well-understood, low-risk, and aligns with React and Next.js best practices.
