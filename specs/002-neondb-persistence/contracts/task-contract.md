# Task API Contract

## Overview
Task API contract for NeonDB task persistence implementation. Defines the required endpoints for task CRUD operations with user isolation.

## Base URL
`/api/{user_id}/tasks`

## Endpoints

### POST /api/{user_id}/tasks
Create a new task for the specified user in NeonDB.

**Path Parameters:**
- `user_id`: Integer - ID of the user to create task for

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description (optional)",
  "completed": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "New Task",
  "description": "Task description (optional)",
  "completed": false,
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T10:00:00Z"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to create tasks for this user"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Validation error"
}
```

### GET /api/{user_id}/tasks
Get all tasks for the specified user from NeonDB.

**Path Parameters:**
- `user_id`: Integer - ID of the user whose tasks to retrieve

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Sample Task",
    "description": "Task description",
    "completed": false,
    "created_at": "2026-02-03T10:00:00Z",
    "updated_at": "2026-02-03T10:00:00Z"
  }
]
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to access this user's tasks"
}
```

### GET /api/{user_id}/tasks/{id}
Get a specific task for the specified user from NeonDB.

**Path Parameters:**
- `user_id`: Integer - ID of the user who owns the task
- `id`: Integer - ID of the task to retrieve

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Sample Task",
  "description": "Task description",
  "completed": false,
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T10:00:00Z"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to access this user's tasks"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

### PUT /api/{user_id}/tasks/{id}
Update a specific task for the specified user in NeonDB.

**Path Parameters:**
- `user_id`: Integer - ID of the user who owns the task
- `id`: Integer - ID of the task to update

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "title": "Updated Task Title",
  "description": "Updated description",
  "completed": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated Task Title",
  "description": "Updated description",
  "completed": true,
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T11:00:00Z"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to access this user's tasks"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

### DELETE /api/{user_id}/tasks/{id}
Delete a specific task for the specified user from NeonDB.

**Path Parameters:**
- `user_id`: Integer - ID of the user who owns the task
- `id`: Integer - ID of the task to delete

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "message": "Task deleted successfully"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to access this user's tasks"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

### PATCH /api/{user_id}/tasks/{id}/complete
Toggle the completion status of a specific task for the specified user in NeonDB.

**Path Parameters:**
- `user_id`: Integer - ID of the user who owns the task
- `id`: Integer - ID of the task to toggle

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Sample Task",
  "description": "Task description",
  "completed": true,
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T11:00:00Z"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to access this user's tasks"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

## Security Requirements
- All endpoints require JWT token in Authorization header
- Backend must verify that token_user_id matches the URL user_id
- Users can only access their own tasks
- NeonDB must enforce proper data isolation