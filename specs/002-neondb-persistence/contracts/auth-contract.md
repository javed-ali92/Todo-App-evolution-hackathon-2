# Authentication API Contract

## Overview
Authentication API contract for NeonDB authentication and task persistence implementation. Defines the required endpoints for user registration, login, and session management.

## Base URL
`/api/auth`

## Endpoints

### POST /api/auth/register
Register a new user account with NeonDB persistence.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Headers:**
- `Content-Type: application/json`

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T10:00:00Z"
}
```

**Response (409 Conflict):**
```json
{
  "detail": "Email already registered"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Validation error"
}
```

### POST /api/auth/login
Authenticate user credentials against NeonDB and return JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Headers:**
- `Content-Type: application/json`

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "1"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect email or password"
}
```

### GET /api/auth/me
Get current authenticated user information from NeonDB.

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
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

### POST /api/auth/logout
Logout user and invalidate session (client-side token invalidation).

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

## Security Requirements
- All endpoints except `/register` and `/login` require JWT token in Authorization header
- Token validation must verify user identity against NeonDB
- User data isolation must be enforced (users can only access their own data)