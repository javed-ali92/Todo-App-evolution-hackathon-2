# Quickstart Guide: Edit Task Feature

**Feature**: Edit Task
**Branch**: 001-edit-task
**Date**: 2026-02-09

## Overview

This guide provides step-by-step instructions for implementing the Edit Task feature. Follow these phases in order to ensure a smooth implementation with minimal risk.

---

## Prerequisites

Before starting implementation, ensure:

- [x] Feature specification reviewed and approved (`spec.md`)
- [x] Implementation plan reviewed (`plan.md`)
- [x] Technical decisions documented (`research.md`)
- [x] Development environment set up (frontend and backend running)
- [x] Authentication working (can create and view tasks)
- [x] Existing task form component located (`frontend/src/components/forms/task-form.tsx`)

---

## Implementation Phases

### Phase 1: Extend Task Form Component (2-3 hours)

**Goal**: Make the existing task form reusable for both create and edit modes.

#### Step 1.1: Update TaskForm Props

**File**: `frontend/src/components/forms/task-form.tsx`

Add new props to the component:

```typescript
interface TaskFormProps {
  mode: 'create' | 'edit';
  initialData?: Task;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function TaskForm({
  mode = 'create',
  initialData,
  onSuccess,
  onCancel
}: TaskFormProps) {
  // Component implementation
}
```

#### Step 1.2: Pre-populate Form with Initial Data

Update the `useForm` hook to use `defaultValues`:

```typescript
const { register, handleSubmit, reset, formState: { errors } } = useForm<TaskFormData>({
  defaultValues: mode === 'edit' && initialData ? {
    title: initialData.title,
    description: initialData.description || '',
    due_date: initialData.due_date || '',
    priority: initialData.priority,
    tags: initialData.tags || '',
    recursion_pattern: initialData.recursion_pattern || '',
  } : {
    priority: 'Medium'
  }
});
```

#### Step 1.3: Update Form Title and Button Text

Add conditional rendering based on mode:

```typescript
<h1 className="text-2xl font-bold mb-6">
  {mode === 'create' ? 'Create New Task' : 'Edit Task'}
</h1>

// ... in the form ...

<button type="submit" disabled={loading}>
  {loading ? 'Saving...' : (mode === 'create' ? 'Create Task' : 'Update Task')}
</button>
```

#### Step 1.4: Update Submit Handler

Add conditional logic to call the correct API method:

```typescript
const onSubmit = async (data: TaskFormData) => {
  setLoading(true);
  setError('');
  setSuccess('');

  try {
    if (!session.userId) {
      throw new Error('User not authenticated');
    }

    const userId = parseInt(session.userId);

    if (mode === 'create') {
      await taskClient.createTask(userId, {
        title: data.title,
        description: data.description || undefined,
        due_date: data.due_date || undefined,
        priority: data.priority,
        tags: data.tags || undefined,
        recursion_pattern: data.recursion_pattern || undefined,
      });
      setSuccess('Task created successfully!');
    } else {
      if (!initialData?.id) {
        throw new Error('Task ID is required for editing');
      }
      await taskClient.updateTask(userId, initialData.id, {
        title: data.title,
        description: data.description || undefined,
        due_date: data.due_date || undefined,
        priority: data.priority,
        tags: data.tags || undefined,
        recursion_pattern: data.recursion_pattern || undefined,
      });
      setSuccess('Task updated successfully!');
    }

    reset();

    // Call onSuccess callback if provided, otherwise redirect
    if (onSuccess) {
      setTimeout(() => onSuccess(), 1500);
    } else {
      setTimeout(() => router.push('/dashboard'), 1500);
    }
  } catch (err: any) {
    const errorMessage = err.message || `Failed to ${mode} task. Please try again.`;
    setError(errorMessage);
  } finally {
    setLoading(false);
  }
};
```

#### Step 1.5: Test Create Mode Still Works

**Manual Test**:
1. Navigate to `/tasks/new`
2. Fill out the form
3. Submit and verify task is created
4. Confirm no regressions

**Expected**: Create functionality works exactly as before.

---

### Phase 2: Create Edit Page Route (1-2 hours)

**Goal**: Add a new route that renders the TaskForm in edit mode.

#### Step 2.1: Create Edit Page File

**File**: `frontend/src/app/tasks/[id]/edit/page.tsx`

Create the directory structure and file:

```bash
mkdir -p frontend/src/app/tasks/[id]/edit
```

#### Step 2.2: Implement Edit Page Component

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import TaskForm from '@/components/forms/task-form';
import { taskClient, Task } from '@/lib/api/task-client';
import { useAuth } from '@/app/providers/auth-provider';

export default function EditTaskPage() {
  const router = useRouter();
  const params = useParams();
  const { session } = useAuth();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchTask() {
      try {
        if (!session?.userId) {
          router.push('/login');
          return;
        }

        const taskId = parseInt(params.id as string);
        const userId = parseInt(session.userId);

        const fetchedTask = await taskClient.getTaskById(userId, taskId);
        setTask(fetchedTask);
      } catch (err: any) {
        setError(err.message || 'Failed to load task');
      } finally {
        setLoading(false);
      }
    }

    fetchTask();
  }, [params.id, session, router]);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <p>Loading task...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
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

#### Step 2.3: Test Edit Page

**Manual Test**:
1. Navigate to `/tasks/5/edit` (use an existing task ID)
2. Verify form loads with task data pre-populated
3. Modify a field and submit
4. Verify redirect to dashboard
5. Confirm task was updated

**Expected**: Edit page loads, form is pre-populated, updates work.

---

### Phase 3: Add Edit Button to Task List (1 hour)

**Goal**: Allow users to navigate to the edit page from the dashboard.

#### Step 3.1: Locate Task List Component

**File**: `frontend/src/app/dashboard/page.tsx`

Find where tasks are rendered in the list.

#### Step 3.2: Add Edit Button

Add an Edit button/link next to each task:

```typescript
import Link from 'next/link';

// Inside the task list mapping
{tasks.map((task) => (
  <div key={task.id} className="task-item">
    {/* Existing task display */}
    <h3>{task.title}</h3>
    <p>{task.description}</p>

    {/* Add Edit button */}
    <div className="task-actions">
      <Link href={`/tasks/${task.id}/edit`}>
        <button className="btn-edit">
          Edit
        </button>
      </Link>

      {/* Existing buttons (delete, complete, etc.) */}
    </div>
  </div>
))}
```

#### Step 3.3: Style Edit Button

Add appropriate styling to match existing UI:

```css
.btn-edit {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-edit:hover {
  background-color: #2563eb;
}
```

#### Step 3.4: Test Edit Button

**Manual Test**:
1. Go to dashboard
2. Verify Edit button appears on all tasks
3. Click Edit on a task
4. Verify navigation to `/tasks/{id}/edit`
5. Verify correct task data loads

**Expected**: Edit button visible, clicking navigates to edit page.

---

### Phase 4: Testing & Validation (1-2 hours)

**Goal**: Ensure all functionality works end-to-end with no regressions.

#### Step 4.1: Manual Testing Checklist

- [ ] **Create Task Flow**
  - [ ] Navigate to `/tasks/new`
  - [ ] Fill form and submit
  - [ ] Verify task created
  - [ ] Confirm no regressions

- [ ] **Edit Task Flow**
  - [ ] Click Edit on a task
  - [ ] Verify form pre-populated
  - [ ] Modify title only
  - [ ] Submit and verify update
  - [ ] Verify updated_at timestamp changed

- [ ] **Edit Multiple Fields**
  - [ ] Edit a task
  - [ ] Change title, description, due_date, priority
  - [ ] Submit and verify all changes persisted

- [ ] **Cancel Edit**
  - [ ] Click Edit on a task
  - [ ] Modify fields
  - [ ] Click Cancel
  - [ ] Verify no changes saved

- [ ] **Authorization**
  - [ ] Try to edit another user's task (via URL manipulation)
  - [ ] Verify 403 Forbidden error

- [ ] **Error Handling**
  - [ ] Submit form with empty title
  - [ ] Verify validation error displayed
  - [ ] Submit with invalid date format
  - [ ] Verify error handling

- [ ] **Mobile Responsiveness**
  - [ ] Test on mobile viewport
  - [ ] Verify Edit button accessible
  - [ ] Verify form usable on mobile

#### Step 4.2: Backend Verification

Verify the backend is handling requests correctly:

```bash
# Test GET endpoint
curl -X GET http://localhost:8001/api/25/tasks/5 \
  -H "Authorization: Bearer <token>"

# Test PUT endpoint
curl -X PUT http://localhost:8001/api/25/tasks/5 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title"}'

# Test unauthorized access (should return 403)
curl -X PUT http://localhost:8001/api/999/tasks/5 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hacked"}'
```

#### Step 4.3: Database Verification

Check that updates are persisted in Neon PostgreSQL:

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

---

## Common Issues & Solutions

### Issue 1: Form Not Pre-populating

**Symptom**: Edit form shows empty fields

**Solution**: Check that `initialData` is being passed correctly and `defaultValues` is set in `useForm`

```typescript
// Verify initialData is not undefined
console.log('Initial data:', initialData);

// Ensure defaultValues is set
defaultValues: mode === 'edit' && initialData ? { ... } : { ... }
```

### Issue 2: 403 Forbidden on Edit

**Symptom**: Getting 403 error when trying to edit own task

**Solution**: Verify JWT token contains correct user_id and matches URL user_id

```typescript
// Check session
console.log('Session user ID:', session.userId);

// Check task owner
console.log('Task owner ID:', task.owner_id);

// Verify they match
if (parseInt(session.userId) !== task.owner_id) {
  console.error('User ID mismatch!');
}
```

### Issue 3: Create Mode Broken After Changes

**Symptom**: Create task no longer works

**Solution**: Ensure default props are set correctly

```typescript
// Add default values
export default function TaskForm({
  mode = 'create',  // Default to create
  initialData,
  onSuccess,
  onCancel
}: TaskFormProps) {
```

### Issue 4: Updated Task Not Showing in List

**Symptom**: Task updates but list doesn't refresh

**Solution**: Ensure dashboard refetches tasks after navigation

```typescript
// In dashboard, use useEffect to refetch on mount
useEffect(() => {
  fetchTasks();
}, []); // Refetch when component mounts
```

---

## Performance Optimization

### Lazy Loading

If the edit page becomes slow, consider lazy loading the form:

```typescript
import dynamic from 'next/dynamic';

const TaskForm = dynamic(() => import('@/components/forms/task-form'), {
  loading: () => <p>Loading form...</p>
});
```

### Caching

For frequently edited tasks, consider caching:

```typescript
// Use SWR or React Query for caching
import useSWR from 'swr';

const { data: task, error } = useSWR(
  `/api/${userId}/tasks/${taskId}`,
  fetcher
);
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All manual tests passed
- [ ] No console errors in browser
- [ ] Backend logs show no errors
- [ ] Database queries optimized
- [ ] Authorization working correctly
- [ ] Mobile responsive
- [ ] Accessibility tested (keyboard navigation, screen readers)
- [ ] Error messages user-friendly
- [ ] Loading states implemented
- [ ] Success messages clear

---

## Next Steps

After completing implementation:

1. Run `/sp.tasks` to generate detailed task breakdown
2. Create pull request with changes
3. Request code review
4. Deploy to staging environment
5. Perform QA testing
6. Deploy to production

---

## Support & Resources

- **Specification**: `specs/001-edit-task/spec.md`
- **Implementation Plan**: `specs/001-edit-task/plan.md`
- **API Contract**: `specs/001-edit-task/contracts/task-api.yaml`
- **Data Model**: `specs/001-edit-task/data-model.md`

For questions or issues, refer to the specification and plan documents first.
