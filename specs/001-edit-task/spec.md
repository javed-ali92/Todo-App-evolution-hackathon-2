# Feature Specification: Edit Task

**Feature Branch**: `001-edit-task`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Add an Edit Task feature to the Todo app. Requirements: Show an Edit button on each task. When clicked, open the existing task form. Auto-fill the form with the selected task's data. Switch the form from Create Task to Update Task. On submit, call the update task API (PUT /api/{user_id}/tasks/{task_id}). Save changes in Neon PostgreSQL. Only allow the task owner to edit. Do not create a new form or break existing features. Keep the implementation clean and minimal."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Edit Task Details (Priority: P1)

A user wants to modify an existing task's information (title, description, due date, priority, tags) to keep their task list accurate and up-to-date.

**Why this priority**: This is the core functionality of the feature. Without the ability to edit and save task changes, the feature has no value. This represents the minimum viable product.

**Independent Test**: Can be fully tested by clicking an Edit button on any task, modifying the task details in the form, saving the changes, and verifying the updated task appears in the task list with the new information.

**Acceptance Scenarios**:

1. **Given** a user is viewing their task list with at least one task, **When** they click the Edit button on a task, **Then** the task form opens with all fields pre-filled with the current task data
2. **Given** the task form is open in edit mode, **When** the user modifies the title and clicks Save, **Then** the task is updated with the new title and the user sees the updated task in their list
3. **Given** the task form is open in edit mode, **When** the user modifies multiple fields (title, description, due date, priority) and clicks Save, **Then** all modified fields are updated and persisted
4. **Given** the task form is open in edit mode, **When** the user clicks Cancel or closes the form without saving, **Then** no changes are saved and the task retains its original values

---

### User Story 2 - Task Ownership Authorization (Priority: P2)

A user should only be able to edit their own tasks, ensuring data security and preventing unauthorized modifications.

**Why this priority**: Security and data integrity are critical, but the basic edit functionality must work first. This can be tested independently by attempting to edit tasks with different user accounts.

**Independent Test**: Can be fully tested by logging in as User A, attempting to edit User B's task (via direct URL manipulation or API call), and verifying the system rejects the request with an authorization error.

**Acceptance Scenarios**:

1. **Given** a user is logged in and viewing their own tasks, **When** they click Edit on any of their tasks, **Then** the edit form opens successfully
2. **Given** a user attempts to edit a task they don't own (via URL manipulation), **When** the system validates the request, **Then** the system returns a 403 Forbidden error and prevents the edit
3. **Given** a user's session expires while editing a task, **When** they attempt to save changes, **Then** the system prompts them to re-authenticate before allowing the update

---

### User Story 3 - Form Mode Indication (Priority: P3)

A user should clearly understand whether they are creating a new task or editing an existing one to avoid confusion.

**Why this priority**: This improves user experience but is not critical for functionality. The feature works without it, but it enhances usability.

**Independent Test**: Can be fully tested by opening the form in create mode and edit mode, and verifying the form title, button text, and visual indicators correctly reflect the current mode.

**Acceptance Scenarios**:

1. **Given** a user clicks "New Task" or "Create Task", **When** the form opens, **Then** the form title displays "Create Task" and the submit button shows "Create" or "Save"
2. **Given** a user clicks Edit on an existing task, **When** the form opens, **Then** the form title displays "Edit Task" or "Update Task" and the submit button shows "Update" or "Save Changes"
3. **Given** the form is open in edit mode, **When** the user views the form, **Then** all fields are pre-populated with the current task data

---

### Edge Cases

- What happens when a user tries to edit a task that has been deleted by another session?
- How does the system handle concurrent edits (two users editing the same task simultaneously)?
- What happens if the network connection is lost while submitting the edit?
- How does the system handle validation errors (e.g., empty title, invalid date format)?
- What happens if the user navigates away from the edit form without saving?
- How does the system handle editing a task with a due date that has already passed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display an Edit button or action on each task in the task list
- **FR-002**: System MUST reuse the existing task creation form for editing tasks (no new form component)
- **FR-003**: System MUST pre-populate all form fields with the selected task's current data when opening in edit mode
- **FR-004**: System MUST clearly indicate when the form is in "edit mode" vs "create mode" (e.g., form title, button text)
- **FR-005**: System MUST call the PUT /api/{user_id}/tasks/{task_id} endpoint when saving edited task data
- **FR-006**: System MUST validate that the authenticated user owns the task before allowing edits (token user_id must match task owner_id)
- **FR-007**: System MUST return a 403 Forbidden error if a user attempts to edit a task they don't own
- **FR-008**: System MUST persist all task changes to Neon PostgreSQL database
- **FR-009**: System MUST update the task list to reflect changes immediately after successful save
- **FR-010**: System MUST validate required fields (title) before allowing save
- **FR-011**: System MUST handle and display appropriate error messages for failed updates (network errors, validation errors, authorization errors)
- **FR-012**: System MUST allow users to cancel editing and return to the task list without saving changes
- **FR-013**: System MUST preserve all existing task creation functionality without breaking changes

### Key Entities

- **Task**: Represents a todo item with attributes including id, title, description, due_date, priority, tags, recursion_pattern, completed status, owner_id, created_at, and updated_at timestamps
- **User**: Represents the authenticated user who owns tasks and has permission to edit only their own tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully edit and save changes to any of their tasks in under 30 seconds
- **SC-002**: 100% of edit attempts by task owners result in successful updates when valid data is provided
- **SC-003**: 100% of unauthorized edit attempts (editing another user's task) are blocked with appropriate error messages
- **SC-004**: The existing task creation workflow continues to function without any regressions or breaking changes
- **SC-005**: Users can edit all task fields (title, description, due date, priority, tags, completion status) and changes persist after page refresh
- **SC-006**: The edit form loads with pre-populated data in under 2 seconds for tasks with standard data sizes

## Assumptions *(optional)*

- The PUT /api/{user_id}/tasks/{task_id} endpoint already exists and is functional
- The existing task form component is designed to be reusable for both create and edit modes
- Users are authenticated and have valid JWT tokens before accessing the edit functionality
- The frontend has access to the current user's ID from the authentication context
- Network connectivity is generally reliable (offline editing is not in scope)
- The task list component can be refreshed or updated after successful edits

## Out of Scope *(optional)*

- Bulk editing of multiple tasks simultaneously
- Undo/redo functionality for task edits
- Edit history or audit trail showing who changed what and when
- Real-time collaborative editing (multiple users editing the same task)
- Offline editing with sync when connection is restored
- Drag-and-drop reordering of tasks
- Advanced validation rules beyond basic required field checks
- Optimistic UI updates (changes reflected before server confirmation)

## Dependencies *(optional)*

- Existing task creation form component must be accessible and reusable
- PUT /api/{user_id}/tasks/{task_id} API endpoint must be available
- Authentication system must provide current user ID
- Task list component must support refresh or update after edits
- Neon PostgreSQL database must be accessible and operational
