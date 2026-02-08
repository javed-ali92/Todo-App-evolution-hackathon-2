# Data Model: Clean Next.js Frontend with App Router

**Feature**: 004-clean-frontend
**Date**: 2026-02-07
**Purpose**: Define data entities and their relationships for the frontend application

## Overview

This document defines the data structures used in the frontend application. Note that the actual database schema is managed by the backend - this document describes the TypeScript interfaces and types used in the frontend.

---

## Entities

### 1. User

Represents an authenticated user in the system.

**Fields**:
- `id`: number - Unique identifier for the user
- `username`: string - User's chosen username
- `email`: string - User's email address
- `created_at`: string (ISO 8601) - Timestamp when user was created
- `updated_at`: string (ISO 8601) - Timestamp when user was last updated

**TypeScript Interface**:
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}
```

**Validation Rules**:
- `username`: Required, 3-50 characters
- `email`: Required, valid email format
- `password`: Required for registration, minimum 6 characters

**Source**: Backend API `/api/auth/me`

---

### 2. UserSession

Represents the current user's authentication session (frontend only).

**Fields**:
- `userId`: string | null - User's ID from backend
- `username`: string | null - User's username
- `email`: string | null - User's email
- `isLoggedIn`: boolean - Whether user is authenticated
- `accessToken`: string | null - JWT token for API requests
- `expiryTime`: Date | null - When the token expires

**TypeScript Interface**:
```typescript
interface UserSession {
  userId: string | null;
  username: string | null;
  email: string | null;
  isLoggedIn: boolean;
  accessToken: string | null;
  expiryTime: Date | null;
}
```

**Storage**: localStorage as 'userSession' (JSON serialized)

**Lifecycle**:
- Created on successful login/signup
- Updated on token refresh (if implemented)
- Cleared on logout or token expiration

---

### 3. Task

Represents a user's task/todo item.

**Fields**:
- `id`: number - Unique identifier for the task
- `title`: string - Task title/name
- `description`: string | undefined - Optional detailed description
- `due_date`: string | undefined - Optional due date (ISO 8601 format)
- `priority`: 'High' | 'Medium' | 'Low' - Task priority level
- `tags`: string | undefined - Optional comma-separated tags
- `recursion_pattern`: string | undefined - Optional pattern for recurring tasks
- `completed`: boolean - Whether task is completed
- `owner_id`: number - ID of user who owns this task
- `created_at`: string (ISO 8601) - Timestamp when task was created
- `updated_at`: string (ISO 8601) - Timestamp when task was last updated

**TypeScript Interface**:
```typescript
interface Task {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
}
```

**Validation Rules**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `due_date`: Optional, must be valid date format
- `priority`: Required, must be one of: 'High', 'Medium', 'Low'
- `tags`: Optional, comma-separated string
- `recursion_pattern`: Optional, string describing recurrence (e.g., "daily", "weekly")

**Source**: Backend API `/api/{user_id}/tasks`

---

### 4. TaskCreate

Represents the data needed to create a new task (subset of Task).

**Fields**:
- `title`: string - Task title (required)
- `description`: string | undefined - Optional description
- `due_date`: string | undefined - Optional due date
- `priority`: 'High' | 'Medium' | 'Low' | undefined - Optional priority (defaults to 'Medium')
- `tags`: string | undefined - Optional tags
- `recursion_pattern`: string | undefined - Optional recursion pattern
- `completed`: boolean | undefined - Optional completion status (defaults to false)

**TypeScript Interface**:
```typescript
interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
  priority?: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed?: boolean;
}
```

**Usage**: Sent to backend when creating a new task

---

### 5. TaskUpdate

Represents the data that can be updated on an existing task.

**Fields**:
- `title`: string | undefined - Updated title
- `description`: string | undefined - Updated description
- `completed`: boolean | undefined - Updated completion status

**TypeScript Interface**:
```typescript
interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

**Usage**: Sent to backend when updating a task

---

### 6. LoginCredentials

Represents login form data.

**Fields**:
- `email`: string - User's email
- `password`: string - User's password

**TypeScript Interface**:
```typescript
interface LoginCredentials {
  email: string;
  password: string;
}
```

**Validation Rules**:
- `email`: Required, valid email format
- `password`: Required, minimum 6 characters

---

### 7. RegistrationData

Represents signup/registration form data.

**Fields**:
- `username`: string - Desired username
- `email`: string - User's email
- `password`: string - User's password

**TypeScript Interface**:
```typescript
interface RegistrationData {
  username: string;
  email: string;
  password: string;
}
```

**Validation Rules**:
- `username`: Required, 3-50 characters
- `email`: Required, valid email format
- `password`: Required, minimum 6 characters

---

### 8. LoginResponse

Represents the response from successful login.

**Fields**:
- `access_token`: string - JWT token for authentication
- `token_type`: string - Type of token (usually "Bearer")
- `user_id`: string - ID of authenticated user

**TypeScript Interface**:
```typescript
interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
}
```

**Source**: Backend API `/api/auth/token`

---

## Relationships

```
User (1) ──── (many) Task
  │
  └─ UserSession (1:1, frontend only)
```

**Description**:
- One User can have many Tasks
- Each Task belongs to exactly one User (owner_id)
- UserSession is a frontend-only representation of the authenticated User

---

## State Transitions

### Task Completion Flow

```
Task (completed: false)
  │
  ├─ User clicks "Mark Complete"
  │
  └─> Task (completed: true)
```

### Authentication Flow

```
No Session
  │
  ├─ User logs in/signs up
  │
  └─> UserSession created (isLoggedIn: true)
       │
       ├─ Token expires
       │
       └─> UserSession cleared (isLoggedIn: false)
```

---

## Data Flow

### Task Creation Flow

```
1. User fills TaskCreate form
2. Frontend validates input
3. Frontend sends POST /api/{user_id}/tasks with TaskCreate data
4. Backend creates Task in database
5. Backend returns complete Task object
6. Frontend updates UI with new Task
```

### Authentication Flow

```
1. User submits LoginCredentials
2. Frontend sends POST /api/auth/token
3. Backend validates credentials
4. Backend returns LoginResponse with access_token
5. Frontend creates UserSession and stores in localStorage
6. Frontend redirects to dashboard
```

---

## File Locations

All TypeScript interfaces are defined in:
- `frontend/src/lib/api/auth-client.ts` - Auth-related types
- `frontend/src/lib/api/task-client.ts` - Task-related types

---

## Notes

- All dates are stored as ISO 8601 strings for consistency
- Optional fields use TypeScript's `?` syntax
- Frontend does not modify the database directly - all changes go through backend API
- Token expiration is checked client-side but enforced server-side