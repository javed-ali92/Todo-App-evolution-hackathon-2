# Data Model: Todo Full-Stack Web Application

## Entity Definitions

### User Entity
- **id**: Integer (Primary Key, Auto-generated)
- **email**: String (Unique, Required, Validated as email format)
- **hashed_password**: String (Required, Stored securely using hashing algorithm)
- **created_at**: DateTime (Auto-generated on creation)
- **updated_at**: DateTime (Auto-generated on update)

**Relationships**:
- One User → Many Tasks (via owner_id foreign key)

### Task Entity
- **id**: Integer (Primary Key, Auto-generated)
- **title**: String (Required, Max length 255 characters)
- **description**: Text (Optional, Unlimited length)
- **completed**: Boolean (Default False)
- **owner_id**: Integer (Foreign Key to User.id, Required)
- **created_at**: DateTime (Auto-generated on creation)
- **updated_at**: DateTime (Auto-generated on update)

**Validation Rules**:
- Title must be 1-255 characters
- Owner_id must reference an existing User
- Completed must be boolean value

## State Transitions

### Task State Transitions
- **Pending** → **Completed**: When user toggles completion via PATCH /api/{user_id}/tasks/{id}/complete
- **Completed** → **Pending**: When user toggles completion via PATCH /api/{user_id}/tasks/{id}/complete

## Data Relationships

### User-Task Relationship
- **Type**: One-to-Many
- **Constraint**: Cascade delete (when user is deleted, all their tasks are deleted)
- **Access Control**: Users can only access tasks where owner_id matches their user ID

## Indexes

### Required Indexes
- User.email (unique index for authentication)
- Task.owner_id (index for efficient user task retrieval)
- Task.created_at (index for chronological sorting)

## Data Integrity

### Constraints
- Foreign key constraint on Task.owner_id → User.id
- Not null constraints on required fields
- Unique constraint on User.email
- Check constraint on Task.completed (must be boolean)

### Audit Trail
- created_at and updated_at fields on both entities for tracking changes