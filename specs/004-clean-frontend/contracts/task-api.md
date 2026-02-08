# API Contracts: Task Management Endpoints

**Feature**: 004-clean-frontend
**Date**: 2026-02-07
**Base URL**: `/api`

## Overview

This document describes the task management API endpoints that the frontend will consume. These endpoints are already implemented in the backend and require authentication.

---

## 1. Get All User Tasks

**Endpoint**: `GET /api/{user_id}/tasks`

**Description**: Retrieve all tasks for a specific user

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id`: number - ID of the user whose tasks to retrieve

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the API",
    "due_date": "2026-02-15T00:00:00Z",
    "priority": "High",
    "tags": "documentation,urgent",
    "recursion_pattern": null,
    "completed": false,
    "owner_id": 1,
    "created_at": "2026-02-07T10:30:00Z",
    "updated_at": "2026-02-07T10:30:00Z"
  },
  {
    "id": 2,
    "title": "Review pull requests",
    "description": null,
    "due_date": null,
    "priority": "Medium",
    "tags": "code-review",
    "recursion_pattern": "daily",
    "completed": false,
    "owner_id": 1,
    "created_at": "2026-02-07T11:00:00Z",
    "updated_at": "2026-02-07T11:00:00Z"
  }
]
```

**Error Responses**:

401 Unauthorized - Invalid or missing token:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden - User trying to access another user's tasks:
```json
{
  "detail": "Not authorized to access this resource"
}
```

---

## 2. Create New Task

**Endpoint**: `POST /api/{user_id}/tasks`

**Description**: Create a new task for a specific user

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id`: number - ID of the user creating the task

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "due_date": "string (optional, ISO 8601 format)",
  "priority": "High | Medium | Low (optional, defaults to Medium)",
  "tags": "string (optional, comma-separated)",
  "recursion_pattern": "string (optional)",
  "completed": "boolean (optional, defaults to false)"
}
```

**Example Request**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "due_date": "2026-02-15T00:00:00Z",
  "priority": "High",
  "tags": "documentation,urgent",
  "recursion_pattern": null
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "due_date": "2026-02-15T00:00:00Z",
  "priority": "High",
  "tags": "documentation,urgent",
  "recursion_pattern": null,
  "completed": false,
  "owner_id": 1,
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "detail": "Title is required"
}
```

401 Unauthorized:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to create tasks for this user"
}
```

422 Unprocessable Entity - Validation error:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 3. Get Single Task

**Endpoint**: `GET /api/{user_id}/tasks/{task_id}`

**Description**: Retrieve a specific task by ID

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id`: number - ID of the user who owns the task
- `task_id`: number - ID of the task to retrieve

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "due_date": "2026-02-15T00:00:00Z",
  "priority": "High",
  "tags": "documentation,urgent",
  "recursion_pattern": null,
  "completed": false,
  "owner_id": 1,
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to access this resource"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

---

## 4. Update Task

**Endpoint**: `PUT /api/{user_id}/tasks/{task_id}`

**Description**: Update an existing task

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id`: number - ID of the user who owns the task
- `task_id`: number - ID of the task to update

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)"
}
```

**Example Request**:
```json
{
  "title": "Updated task title",
  "description": "Updated description"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated task title",
  "description": "Updated description",
  "due_date": "2026-02-15T00:00:00Z",
  "priority": "High",
  "tags": "documentation,urgent",
  "recursion_pattern": null,
  "completed": false,
  "owner_id": 1,
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T12:00:00Z"
}
```

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to update this task"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

---

## 5. Delete Task

**Endpoint**: `DELETE /api/{user_id}/tasks/{task_id}`

**Description**: Delete a specific task

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id`: number - ID of the user who owns the task
- `task_id`: number - ID of the task to delete

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response** (204 No Content):
```
(empty response body)
```

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to delete this task"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

---

## 6. Toggle Task Completion

**Endpoint**: `PATCH /api/{user_id}/tasks/{task_id}/complete`

**Description**: Toggle the completion status of a task

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `user_id`: number - ID of the user who owns the task
- `task_id`: number - ID of the task to toggle

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "due_date": "2026-02-15T00:00:00Z",
  "priority": "High",
  "tags": "documentation,urgent",
  "recursion_pattern": null,
  "completed": true,
  "owner_id": 1,
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T12:30:00Z"
}
```

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Could not validate credentials"
}
```

403 Forbidden:
```json
{
  "detail": "Not authorized to update this task"
}
```

404 Not Found:
```json
{
  "detail": "Task not found"
}
```

---

## Frontend Implementation Notes

### Authorization
- All endpoints require valid JWT token in Authorization header
- Backend validates that `token_user_id == url_user_id` for security
- Users can only access their own tasks

### Error Handling
- Handle 401 by redirecting to login
- Handle 403 by showing "Access Denied" message
- Handle 404 by showing "Task not found" message
- Display validation errors from 422 responses

### Request Example (TypeScript)
```typescript
// Create a new task
const response = await fetch(`/api/${userId}/tasks`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'New task',
    description: 'Task description',
    priority: 'High'
  }),
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail);
}

const task = await response.json();
console.log('Created task:', task);
```