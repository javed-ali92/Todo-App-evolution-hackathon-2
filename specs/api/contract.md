# API Specification: Todo Application Endpoints

**Feature**: Todo Application API
**Created**: 2026-01-31
**Status**: Draft

## API Contract

The following endpoints must be implemented and must not change:

### Authentication Endpoints
- POST /api/auth/register - Register a new user
- POST /api/auth/login - Authenticate user and return JWT
- POST /api/auth/logout - Invalidate user session

### Task Management Endpoints
- GET /api/{user_id}/tasks - Retrieve all tasks for a user
- POST /api/{user_id}/tasks - Create a new task for a user
- GET /api/{user_id}/tasks/{id} - Retrieve a specific task for a user
- PUT /api/{user_id}/tasks/{id} - Update a specific task for a user
- DELETE /api/{user_id}/tasks/{id} - Delete a specific task for a user
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle task completion status

## Authentication Requirements

All task management endpoints require JWT token authentication:
- Header: Authorization: Bearer {jwt_token}
- Backend must verify JWT and extract user ID
- Backend must compare token_user_id with url_user_id
- Return 401 for invalid tokens, 403 for user_id mismatches

## Request/Response Formats

### User Registration Request
```json
{
  email: user@example.com,
  password: secure_password,
  username: username
}
```

### User Registration Response (Success)
```json
{
  user_id: 123,
  email: user@example.com,
  username: username,
  token: jwt_token_here
}
```

### Task Object
```json
{
  id: 123,
  user_id: 456,
  title: Task title,
  description: Task description,
  completed: false,
  due_date: 2023-12-31T23:59:59Z,
  priority: Medium,
  tags: [work, important],
  created_at: 2023-01-01T00:00:00Z,
  updated_at: 2023-01-01T00:00:00Z
}
```

### Create/Update Task Request
```json
{
  title: Task title,
  description: Task description,
  due_date: 2023-12-31T23:59:59Z,
  priority: Medium,
  tags: [work, important]
}
```

### List Tasks Response
```json
{
  tasks: [
    {
      id: 123,
      user_id: 456,
      title: Task title,
      description: Task description,
      completed: false,
      due_date: 2023-12-31T23:59:59Z,
      priority: Medium,
      tags: [work, important],
      created_at: 2023-01-01T00:00:00Z,
      updated_at: 2023-01-01T00:00:00Z
    }
  ],
  total: 1
}
```

## Error Responses

### Authentication Error
```json
{
  error: Unauthorized,
  message: Invalid or expired token,
  code: 401
}
```

### Authorization Error
```json
{
  error: Forbidden,
  message: Access denied - insufficient permissions,
  code: 403
}
```

### Validation Error
```json
{
  error: Validation Failed,
  message: Request data validation failed,
  details: {
    field: error_message
  },
  code: 400
}
```

### Not Found Error
```json
{
  error: Not Found,
  message: Requested resource not found,
  code: 404
}
```

## HTTP Status Codes

- 200: Success for GET, PUT, PATCH requests
- 201: Success for POST requests (resource created)
- 204: Success for DELETE requests (no content to return)
- 400: Bad request (validation errors)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (valid token but insufficient permissions)
- 404: Not found (requested resource doesn't exist)
- 409: Conflict (resource already exists, etc.)
- 500: Internal server error

