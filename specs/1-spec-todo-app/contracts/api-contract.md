# API Contract: Todo Full-Stack Web Application

## Base URL
All API endpoints follow the pattern: `{base_url}/api/{user_id}/...`

## Authentication
- All endpoints require JWT token in Authorization header
- Format: `Authorization: Bearer <jwt_token>`
- Invalid/missing tokens result in 401 Unauthorized response

## API Endpoints

### 1. Create Task
- **Endpoint**: `POST /api/{user_id}/tasks`
- **Description**: Creates a new task for the specified user
- **Path Parameter**: `user_id` (Integer) - ID of the user creating the task
- **Request Body**:
  ```json
  {
    "title": "String (Required)",
    "description": "String (Optional)",
    "completed": "Boolean (Optional, default: false)"
  }
  ```
- **Response Codes**:
  - 201 Created: Task successfully created
  - 400 Bad Request: Invalid input data
  - 401 Unauthorized: Missing or invalid JWT token
  - 403 Forbidden: user_id in token doesn't match URL user_id
  - 404 Not Found: User with specified user_id doesn't exist
- **Response Body** (201):
  ```json
  {
    "id": "Integer",
    "title": "String",
    "description": "String",
    "completed": "Boolean",
    "owner_id": "Integer",
    "created_at": "DateTime",
    "updated_at": "DateTime"
  }
  ```

### 2. List Tasks
- **Endpoint**: `GET /api/{user_id}/tasks`
- **Description**: Retrieves all tasks for the specified user
- **Path Parameter**: `user_id` (Integer) - ID of the user whose tasks to retrieve
- **Query Parameters**: None
- **Response Codes**:
  - 200 OK: Successfully retrieved tasks
  - 401 Unauthorized: Missing or invalid JWT token
  - 403 Forbidden: user_id in token doesn't match URL user_id
- **Response Body** (200):
  ```json
  [
    {
      "id": "Integer",
      "title": "String",
      "description": "String",
      "completed": "Boolean",
      "owner_id": "Integer",
      "created_at": "DateTime",
      "updated_at": "DateTime"
    }
  ]
  ```

### 3. Get Single Task
- **Endpoint**: `GET /api/{user_id}/tasks/{id}`
- **Description**: Retrieves a specific task for the specified user
- **Path Parameters**:
  - `user_id` (Integer) - ID of the user who owns the task
  - `id` (Integer) - ID of the task to retrieve
- **Response Codes**:
  - 200 OK: Task successfully retrieved
  - 401 Unauthorized: Missing or invalid JWT token
  - 403 Forbidden: user_id in token doesn't match URL user_id
  - 404 Not Found: Task with specified id doesn't exist for the user
- **Response Body** (200):
  ```json
  {
    "id": "Integer",
    "title": "String",
    "description": "String",
    "completed": "Boolean",
    "owner_id": "Integer",
    "created_at": "DateTime",
    "updated_at": "DateTime"
  }
  ```

### 4. Update Task
- **Endpoint**: `PUT /api/{user_id}/tasks/{id}`
- **Description**: Updates a specific task for the specified user
- **Path Parameters**:
  - `user_id` (Integer) - ID of the user who owns the task
  - `id` (Integer) - ID of the task to update
- **Request Body**:
  ```json
  {
    "title": "String (Required)",
    "description": "String (Optional)",
    "completed": "Boolean (Optional)"
  }
  ```
- **Response Codes**:
  - 200 OK: Task successfully updated
  - 400 Bad Request: Invalid input data
  - 401 Unauthorized: Missing or invalid JWT token
  - 403 Forbidden: user_id in token doesn't match URL user_id
  - 404 Not Found: Task with specified id doesn't exist for the user
- **Response Body** (200):
  ```json
  {
    "id": "Integer",
    "title": "String",
    "description": "String",
    "completed": "Boolean",
    "owner_id": "Integer",
    "created_at": "DateTime",
    "updated_at": "DateTime"
  }
  ```

### 5. Delete Task
- **Endpoint**: `DELETE /api/{user_id}/tasks/{id}`
- **Description**: Deletes a specific task for the specified user
- **Path Parameters**:
  - `user_id` (Integer) - ID of the user who owns the task
  - `id` (Integer) - ID of the task to delete
- **Response Codes**:
  - 204 No Content: Task successfully deleted
  - 401 Unauthorized: Missing or invalid JWT token
  - 403 Forbidden: user_id in token doesn't match URL user_id
  - 404 Not Found: Task with specified id doesn't exist for the user
- **Response Body**: Empty

### 6. Toggle Task Completion
- **Endpoint**: `PATCH /api/{user_id}/tasks/{id}/complete`
- **Description**: Toggles the completion status of a specific task for the specified user
- **Path Parameters**:
  - `user_id` (Integer) - ID of the user who owns the task
  - `id` (Integer) - ID of the task to toggle
- **Request Body**: None
- **Response Codes**:
  - 200 OK: Task completion status successfully toggled
  - 401 Unauthorized: Missing or invalid JWT token
  - 403 Forbidden: user_id in token doesn't match URL user_id
  - 404 Not Found: Task with specified id doesn't exist for the user
- **Response Body** (200):
  ```json
  {
    "id": "Integer",
    "title": "String",
    "description": "String",
    "completed": "Boolean",
    "owner_id": "Integer",
    "created_at": "DateTime",
    "updated_at": "DateTime"
  }
  ```

## Authorization Rules
- All endpoints require JWT authentication
- Backend must verify that the user_id in the JWT token matches the user_id in the URL
- Users can only access/modify their own tasks
- If token_user_id != url_user_id, return 403 Forbidden

## Error Response Format
All error responses (4xx, 5xx) follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

## Rate Limiting
- TBD: Implementation details for rate limiting to prevent abuse