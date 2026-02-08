# API Contracts: Authentication Endpoints

**Feature**: 004-clean-frontend
**Date**: 2026-02-07
**Base URL**: `/api`

## Overview

This document describes the authentication-related API endpoints that the frontend will consume. These endpoints are already implemented in the backend.

---

## 1. User Registration

**Endpoint**: `POST /api/auth/register`

**Description**: Register a new user account

**Authentication**: None required

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "username": "string (required, 3-50 chars)",
  "email": "string (required, valid email)",
  "password": "string (required, min 6 chars)"
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "detail": "Email already registered"
}
```

422 Unprocessable Entity - Validation error:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 2. User Login

**Endpoint**: `POST /api/auth/token`

**Description**: Authenticate user and receive JWT token

**Authentication**: None required

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": "1"
}
```

**Error Responses**:

401 Unauthorized - Invalid credentials:
```json
{
  "detail": "Invalid email or password"
}
```

422 Unprocessable Entity - Validation error:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 3. Get Current User

**Endpoint**: `GET /api/auth/me`

**Description**: Get information about the currently authenticated user

**Authentication**: Required (Bearer token)

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2026-02-07T10:30:00Z",
  "updated_at": "2026-02-07T10:30:00Z"
}
```

**Error Responses**:

401 Unauthorized - Invalid or missing token:
```json
{
  "detail": "Could not validate credentials"
}
```

---

## 4. Logout

**Endpoint**: `POST /api/auth/logout`

**Description**: Logout user (client-side token removal)

**Authentication**: Optional (Bearer token)

**Request Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

**Notes**:
- Logout is primarily handled client-side by removing the token from localStorage
- Backend endpoint may be called for logging purposes but is not strictly required

---

## Frontend Implementation Notes

### Token Storage
- Store `access_token` in localStorage as 'auth_token' or 'userSession'
- Include token in all authenticated requests via Authorization header
- Remove token on logout or 401 responses

### Error Handling
- Display user-friendly error messages from `detail` field
- Handle validation errors by showing field-specific messages
- Redirect to login on 401 Unauthorized responses

### Request Example (TypeScript)
```typescript
const response = await fetch('/api/auth/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  }),
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail);
}

const data = await response.json();
localStorage.setItem('auth_token', data.access_token);
```