# Research: NeonDB Authentication & Task Persistence

## Executive Summary

This research document outlines the technical approach for implementing NeonDB persistence for authentication and task data in the Todo application. The focus is on ensuring all user data (signup/login) and task data are properly stored in Neon PostgreSQL with frontend forms aligned to the database schema.

## Database Schema Analysis

### Current NeonDB Schema Requirements

Based on the specifications, the following database schema is required:

#### Users Table
- **id**: Integer (Primary Key, Auto-increment) - Unique identifier for each user
- **email**: String (Unique, Not Null) - User's email address for login
- **password_hash**: String (Not Null) - BCrypt hashed password
- **created_at**: DateTime (Not Null) - Account creation timestamp
- **updated_at**: DateTime (Not Null) - Last update timestamp

#### Tasks Table
- **id**: Integer (Primary Key, Auto-increment) - Unique identifier for each task
- **user_id**: Integer (Foreign Key, Not Null) - References user who owns the task
- **title**: String (Not Null) - Task title (max 255 characters)
- **description**: Text (Nullable) - Task description
- **completed**: Boolean (Not Null, Default: false) - Completion status
- **created_at**: DateTime (Not Null) - Task creation timestamp
- **updated_at**: DateTime (Not Null) - Last update timestamp

#### Sessions Table
- **id**: Integer (Primary Key, Auto-increment) - Unique identifier for each session
- **user_id**: Integer (Foreign Key, Not Null) - References user associated with session
- **token**: String (Unique, Not Null) - JWT token identifier
- **expires_at**: DateTime (Not Null) - Session expiration timestamp
- **created_at**: DateTime (Not Null) - Session creation timestamp
- **last_used_at**: DateTime (Not Null) - Last activity timestamp

## Frontend-Backend Alignment

### Signup Form Fields vs Database Schema
- **Email field** → Maps to `users.email` column (required, unique validation)
- **Password field** → Used to generate `users.password_hash` (encrypted with bcrypt)

### Login Form Fields vs Database Schema
- **Email field** → Matches against `users.email` column
- **Password field** → Verified against `users.password_hash` (decrypted and compared)

### Task Form Fields vs Database Schema
- **Title field** → Maps to `tasks.title` column (required, max 255 chars)
- **Description field** → Maps to `tasks.description` column (optional)
- **Completed checkbox** → Maps to `tasks.completed` column (boolean)

## Technical Implementation Approach

### Backend Changes Required

1. **Authentication Service Enhancement**:
   - Ensure signup data is saved to NeonDB users table
   - Implement proper password hashing with bcrypt
   - Ensure login validates credentials against NeonDB users table

2. **Task Service Enhancement**:
   - Ensure task CRUD operations persist to NeonDB tasks table
   - Maintain user isolation by associating tasks with user_id
   - Implement proper validation before database operations

3. **Database Layer Configuration**:
   - Configure SQLModel models to match schema requirements
   - Ensure proper foreign key relationships
   - Implement connection pooling for Neon Serverless

### Frontend Changes Required

1. **Form Validation Alignment**:
   - Match required fields with database constraints
   - Implement client-side validation that mirrors server-side
   - Ensure data types match between frontend and backend

2. **API Integration**:
   - Update API calls to properly send data to backend
   - Handle responses from NeonDB operations
   - Implement proper error handling for database failures

## NeonDB-Specific Considerations

### Connection Management
- Neon Serverless PostgreSQL has sleep/wake cycles
- Need proper connection pooling with appropriate timeout settings
- Handle reconnection logic for idle connections

### Security Implementation
- SSL connections required for Neon
- Proper password hashing (bcrypt) before storage
- JWT token validation with proper expiration handling

## Potential Challenges & Solutions

### Challenge: Database Connection Reliability
**Solution**: Implement connection pooling with proper timeout and retry logic

### Challenge: Form Schema Alignment
**Solution**: Create validation layers that ensure frontend forms match database schema exactly

### Challenge: User Data Isolation
**Solution**: Strict enforcement of user_id matching between JWT token and URL parameters

## Technology Stack Compliance

All implementation will comply with the established technology stack:
- Backend: Python FastAPI with SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Frontend: Next.js 16+ with TypeScript
- Authentication: JWT-based with proper token validation