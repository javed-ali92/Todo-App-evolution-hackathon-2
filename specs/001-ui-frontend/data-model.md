# Data Model: Todo App Frontend UI/UX

## Overview

This document defines the data structures and state management approach for the Todo App frontend UI/UX implementation. While the frontend doesn't directly manage persistent data (that's handled by the backend), it needs to manage UI state, user session data, and temporary form states.

## UI State Entities

### 1. User Session Entity
**Definition**: Represents the authenticated user's session state in the frontend application
- **userId**: string - Unique identifier for the authenticated user
- **username**: string - Display name for the user
- **email**: string - User's email address
- **isLoggedIn**: boolean - Authentication status
- **accessToken**: string - JWT token for API authentication
- **expiryTime**: Date - When the token expires

**Relationships**: Used across all protected pages and API interactions

### 2. Task Entity (Frontend Representation)
**Definition**: UI representation of a task from the backend API
- **id**: string - Unique identifier for the task
- **userId**: string - Owner of the task (for validation)
- **title**: string - Task title (required)
- **description**: string - Detailed task description (optional)
- **dueDate**: Date | null - Deadline for the task (optional)
- **priority**: 'low' | 'medium' | 'high' - Priority level
- **tags**: string[] - Associated tags (optional)
- **completed**: boolean - Completion status
- **createdAt**: Date - Creation timestamp
- **updatedAt**: Date - Last update timestamp

**Relationships**: Belongs to a single user; displayed in user's task list

### 3. Form State Entity
**Definition**: Temporary state for form inputs and validation
- **formData**: Object - Current values in the form fields
- **errors**: Object - Validation errors for each field
- **isLoading**: boolean - Whether the form is submitting
- **successMessage**: string | null - Success feedback after submission
- **isDirty**: boolean - Whether the form has been modified

**Relationships**: Associated with specific forms (login, signup, task creation)

### 4. Filter State Entity
**Definition**: State for managing task filtering and search
- **showCompleted**: 'all' | 'completed' | 'pending' - Completion status filter
- **priorityFilter**: 'all' | 'low' | 'medium' | 'high' - Priority filter
- **searchQuery**: string - Text-based search filter
- **sortBy**: 'created' | 'dueDate' | 'priority' - Sorting preference
- **sortDirection**: 'asc' | 'desc' - Sort order

**Relationships**: Connected to the task list display component

## UI State Management

### Global State Structure
```
{
  session: {
    userId: string,
    username: string,
    email: string,
    isLoggedIn: boolean,
    accessToken: string,
    expiryTime: Date
  },
  tasks: {
    list: Task[],
    loading: boolean,
    error: string | null,
    filters: FilterState
  },
  forms: {
    login: FormState,
    signup: FormState,
    task: FormState
  }
}
```

### State Transitions

#### Session State Transitions
- **Initial** → **Loading**: When checking auth status on app start
- **Loading** → **Authenticated**: When valid token exists and is verified
- **Loading** → **Unauthenticated**: When no token or token is invalid
- **Authenticated** → **Unauthenticated**: When user logs out or token expires

#### Task List State Transitions
- **Initial** → **Loading**: When fetching tasks from API
- **Loading** → **Loaded**: When API returns successfully
- **Loading** → **Error**: When API request fails
- **Loaded** → **Loading**: When refreshing or modifying tasks

## Validation Rules

### Form Validation
- **Login Form**: Email must be valid format, password must be at least 8 characters
- **Signup Form**: Username 3-30 chars, email valid format, password 8+ chars with confirmation match
- **Task Form**: Title required (1-200 chars), description optional (max 1000 chars), due date in future if provided

### UI Validation
- Real-time validation feedback during user input
- Form submission disabled when validation errors exist
- Clear error messaging that guides user to fix issues

## API Interaction Patterns

### Request State Management
- **Loading State**: Show spinner/loader during API requests
- **Success State**: Update UI with new data and show success feedback
- **Error State**: Display user-friendly error message and maintain previous state
- **Optimistic Updates**: Update UI immediately, revert if API call fails

### Authentication Headers
- **JWT Token**: Attach to all API requests as `Authorization: Bearer ${token}`
- **Token Refresh**: Automatically refresh when token nears expiration
- **Error Handling**: Redirect to login on 401/403 responses

## Component Data Flow

### Landing Page
- No persistent data required
- Static content managed via props

### Authentication Pages
- Form state managed locally within each component
- Session state updated globally on successful authentication

### Dashboard
- Tasks fetched and cached based on user ID
- Filter state managed locally but affects task display
- Form state for task creation managed separately

### Task Components
- Individual task state managed through parent list component
- Edit/delete operations update global task list

## Performance Considerations

### Caching Strategy
- Cache user session information for quick access
- Cache task lists to reduce API calls
- Invalidate cache on mutations or after time-based expiry

### Memory Management
- Clean up event listeners on component unmount
- Debounce search/filter inputs to prevent excessive API calls
- Lazy-load components that aren't immediately visible

## Error Handling Patterns

### Network Errors
- Show user-friendly error messages instead of technical details
- Provide retry options for failed operations
- Gracefully degrade functionality when API is unavailable

### Validation Errors
- Distinguish between server-side and client-side validation
- Preserve user input when validation fails
- Show specific guidance for correcting errors

### Authentication Errors
- Redirect to login page when session expires
- Clear sensitive data from local state
- Prevent access to protected routes