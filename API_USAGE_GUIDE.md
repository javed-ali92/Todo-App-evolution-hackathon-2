# Todo API with Neon PostgreSQL - Usage Guide

## Server Status
✅ The server is running correctly on `http://localhost:8000`

## API Endpoints

### Public Endpoints (No Authentication Required)
- `GET /` - Root endpoint
- `GET /docs` - API Documentation
- `GET /redoc` - Alternative API Documentation

### Authentication Endpoints (Mounted at `/api/auth/`)
- `POST /api/auth/register` - Register new user (JSON data)
- `POST /api/auth/login` - Login (Form data, NOT JSON)
- `GET /api/auth/me` - Get current user info (Requires JWT token)
- `POST /api/auth/logout` - Logout (currently client-side only)

### Task Endpoints (Mounted at `/api/{user_id}/tasks`)
- `GET /api/{user_id}/tasks` - Get all tasks for user (Requires JWT token)
- `POST /api/{user_id}/tasks` - Create new task (Requires JWT token)
- `GET /api/{user_id}/tasks/{id}` - Get specific task (Requires JWT token)
- `PUT /api/{user_id}/tasks/{id}` - Update task (Requires JWT token)
- `DELETE /api/{user_id}/tasks/{id}` - Delete task (Requires JWT token)
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion (Requires JWT token)

## Important Notes

### 1. Authentication Flow
1. Register a user with JSON data:
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
        -H "Content-Type: application/json" \
        -d '{"username":"myuser","email":"my@email.com","password":"mypassword123"}'
   ```

2. Login with FORM DATA (not JSON):
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
        -d "email=my@email.com&password=mypassword123"
   ```
   This returns a JWT token.

3. Use the JWT token for protected endpoints:
   ```bash
   curl -X GET http://localhost:8000/api/auth/me \
        -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
   ```

### 2. Common Mistakes That Cause 404/401 Errors
- ❌ Using JSON data for login instead of form data
- ❌ Accessing `/api/tasks` without user_id in the URL
- ❌ Accessing protected endpoints without Authorization header
- ❌ Mismatching user_id in URL with the authenticated user ID
- ❌ Using wrong HTTP methods for endpoints

### 3. Correct Usage Examples

#### Register a new user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

#### Login to get token:
```bash
curl -X POST http://localhost:8000/api/auth/login \
     -d "email=test@example.com&password=password123"
```

#### Get user info (after login):
```bash
curl -X GET http://localhost:8000/api/auth/me \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Create a task (after login):
```bash
curl -X POST http://localhost:8000/api/USER_ID/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"title":"My Task","description":"Task description","completed":false}'
```

#### Get user's tasks (after login):
```bash
curl -X GET http://localhost:8000/api/USER_ID/tasks \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting 404 Errors

1. **Check the URL structure**: Make sure you're using `/api/` prefix
2. **Verify the endpoint name**: `/api/auth/register` not `/api/register`
3. **Include user_id**: `/api/123/tasks` not `/api/tasks`
4. **Use correct HTTP method**: POST for creating, GET for reading, etc.

## Troubleshooting 401/403 Errors

1. **Missing token**: Add Authorization header with Bearer token
2. **Invalid token**: Get a new token by logging in again
3. **User ID mismatch**: The user_id in URL must match the authenticated user

## The API is Fully Functional
All endpoints are working with Neon PostgreSQL backend. The authentication system, user isolation, and task management are all operational.