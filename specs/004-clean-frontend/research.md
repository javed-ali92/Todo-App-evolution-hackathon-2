# Research: Clean Next.js Frontend with App Router

**Feature**: 004-clean-frontend
**Date**: 2026-02-07
**Purpose**: Research and document technology decisions for implementing a clean Next.js App Router frontend

## Phase 0: Research Findings

### 1. Next.js App Router vs Pages Router

**Decision**: Use Next.js App Router exclusively

**Rationale**:
- App Router is the modern, recommended approach for Next.js 13+
- Provides better performance with React Server Components
- Cleaner routing structure with file-system based routing
- Better support for layouts and nested routes
- Improved data fetching patterns with async/await in components

**Alternatives Considered**:
- Pages Router: Legacy approach, still supported but not recommended for new projects
- Hybrid approach: Would maintain the current confusion and complexity

**Implementation Notes**:
- All routes will be defined in `src/app/` directory
- Use `page.tsx` for route pages
- Use `layout.tsx` for shared layouts
- Use `loading.tsx` for loading states (optional)
- Use `error.tsx` for error boundaries (optional)

---

### 2. Authentication State Management

**Decision**: Use React Context API with Next.js App Router patterns

**Rationale**:
- Existing auth-provider.tsx already uses Context API
- Lightweight solution without additional dependencies
- Works well with Next.js App Router client components
- Token storage in localStorage is already implemented
- Backend JWT validation is already working

**Alternatives Considered**:
- NextAuth.js: Overkill for simple token-based auth, would require backend changes
- Zustand/Redux: Unnecessary complexity for simple auth state
- Better Auth: Mentioned in requirements but backend already has JWT implementation

**Implementation Notes**:
- Keep existing `src/app/providers/auth-provider.tsx`
- Consolidate auth logic from multiple sources into single provider
- Use 'use client' directive for client-side auth operations
- Implement protected route wrapper component

---

### 3. Form State Management

**Decision**: Use React Hook Form with native HTML5 validation

**Rationale**:
- Lightweight and performant
- Built-in validation support
- Easy integration with TypeScript
- Reduces boilerplate code
- Already commonly used in Next.js projects

**Alternatives Considered**:
- Formik: More heavyweight, slower performance
- Native React state: Too much boilerplate for complex forms
- Uncontrolled forms: Less control over validation

**Implementation Notes**:
- Install react-hook-form if not already present
- Use for login, signup, and task creation forms
- Implement custom validation rules for task fields
- Handle API errors and display to users

---

### 4. API Client Architecture

**Decision**: Keep existing fetch-based API clients (auth-client.ts, task-client.ts)

**Rationale**:
- Already implemented and working
- Native fetch API is sufficient for this use case
- No need for additional dependencies
- TypeScript interfaces already defined

**Alternatives Considered**:
- Axios: Already partially used but creates inconsistency
- React Query/SWR: Overkill for simple CRUD operations
- tRPC: Would require backend changes

**Implementation Notes**:
- Consolidate to use only the TypeScript clients in `lib/api/`
- Remove axios.js and related dependencies
- Ensure consistent error handling across all API calls
- Use relative paths (/api) to work with Vite proxy

---

### 5. Styling Approach

**Decision**: Continue using Tailwind CSS

**Rationale**:
- Already configured in the project
- Provides utility-first CSS for rapid development
- Good integration with Next.js
- Responsive design utilities built-in

**Alternatives Considered**:
- CSS Modules: More verbose, less flexible
- Styled Components: Requires additional setup, runtime overhead
- Plain CSS: Too much manual work

**Implementation Notes**:
- Keep existing Tailwind configuration
- Use consistent spacing and color utilities
- Create reusable component classes where needed
- Ensure responsive design for mobile devices

---

### 6. Component Organization

**Decision**: Organize by feature and type

**Rationale**:
- Clear separation of concerns
- Easy to locate components
- Scalable structure
- Follows Next.js best practices

**Structure**:
```
components/
├── forms/          # Form components (login, signup, task)
├── lists/          # List components (task list)
├── layouts/        # Layout components (container)
├── hoc/            # Higher-order components (with-auth)
└── ui/             # Reusable UI components (header, footer)
```

**Alternatives Considered**:
- Flat structure: Becomes unwieldy as project grows
- Feature-based only: Harder to find reusable components
- Atomic design: Too complex for this project size

---

### 7. Protected Routes Implementation

**Decision**: Use Higher-Order Component (HOC) pattern

**Rationale**:
- Clean and reusable
- Easy to wrap any page that needs authentication
- Centralized auth checking logic
- Works well with Next.js App Router

**Implementation**:
```typescript
// components/hoc/with-auth.tsx
export function WithAuth({ children }) {
  const { session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!session.isLoggedIn) {
      router.push('/login');
    }
  }, [session, router]);

  if (!session.isLoggedIn) return null;
  return children;
}
```

**Alternatives Considered**:
- Middleware: More complex setup, overkill for client-side auth
- Route guards: Not native to Next.js App Router
- Server-side checks: Would require backend changes

---

### 8. Error Handling Strategy

**Decision**: Implement consistent error handling with user-friendly messages

**Rationale**:
- Improves user experience
- Helps with debugging
- Provides clear feedback

**Implementation Notes**:
- Display error messages in forms
- Use toast notifications for success/error (optional)
- Log errors to console for debugging
- Handle network failures gracefully

---

## Technology Stack Summary

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| Framework | Next.js | 14+ | Modern App Router support |
| Language | TypeScript | Latest | Type safety |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Forms | React Hook Form | 7.x | Performance and validation |
| State | React Context | Built-in | Simple auth state |
| API Client | Fetch API | Native | No extra dependencies |
| Auth | JWT Tokens | N/A | Backend already implements |

---

## Dependencies to Add

```json
{
  "react-hook-form": "^7.49.0"
}
```

## Dependencies to Remove

- axios (consolidate to fetch)
- react-router-dom (not needed with App Router)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing auth flow | Medium | High | Thorough testing of login/signup |
| Data loss during cleanup | Low | High | Backup before deletion |
| API integration issues | Low | Medium | Use existing working clients |
| User confusion with new UI | Low | Low | Keep UI similar to existing |

---

## Next Steps

1. Proceed to Phase 1: Design & Contracts
2. Generate data-model.md with entity definitions
3. Generate API contracts documentation
4. Create quickstart.md for setup instructions