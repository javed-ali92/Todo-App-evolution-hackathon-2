# Implementation Plan: Clean Next.js Frontend with App Router

**Branch**: `004-clean-frontend` | **Date**: 2026-02-07 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/004-clean-frontend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a clean, minimal Next.js frontend using the App Router exclusively to replace the current mixed Pages/App Router structure. This involves removing all Pages Router files, consolidating authentication logic, implementing proper task management forms, and establishing a clean folder structure that follows Next.js best practices.

## Technical Context

**Language/Version**: TypeScript, Next.js 14+
**Primary Dependencies**: Next.js App Router, React 18+, Tailwind CSS, react-hook-form
**Storage**: Neon PostgreSQL database accessed via existing backend API
**Testing**: Not specified in requirements (to be added later)
**Target Platform**: Web browser with responsive design
**Project Type**: Web application with separate frontend/backend
**Performance Goals**: Fast initial load, responsive UI interactions
**Constraints**: Must integrate with existing backend API without changes
**Scale/Scope**: Individual user task management system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement
- [x] No direct implementation without approved specs, plans, and tasks

### Architecture Compliance
- [x] Maintains existing structure: frontend/ (Next.js), backend/ (FastAPI), specs/, docker-compose.yml
- [x] Clear separation between frontend and backend components

### Technology Stack Compliance
- [x] Frontend uses Next.js 14+ (App Router), TypeScript, Tailwind CSS
- [x] Backend uses Python FastAPI, SQLModel ORM (remains unchanged)
- [x] Database uses Neon Serverless PostgreSQL (remains unchanged)
- [x] Authentication uses existing token-based auth (to be consolidated)

### Security Compliance
- [x] All API routes require JWT token authentication (existing backend implementation)
- [x] Backend verifies JWT token and extracts user ID (existing backend implementation)
- [x] Backend compares token_user_id == url_user_id to prevent unauthorized access (existing backend implementation)
- [x] Users can only access their own tasks (existing backend implementation)

### API Contract Compliance
- [x] All API routes follow the specified contract (existing backend implementation):
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{id}
  - PUT /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH /api/{user_id}/tasks/{id}/complete

## Project Structure

### Documentation (this feature)

```text
specs/004-clean-frontend/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature requirements
└── tasks.md             # Task breakdown (/sp.tasks command output)
```

### Source Code (existing structure to be cleaned up)

```text
frontend/
├── src/
│   ├── app/                 # Next.js App Router structure
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── tasks/
│   │   │   └── new/
│   │   │       └── page.tsx
│   │   └── providers/
│   │       └── auth-provider.tsx
│   ├── components/          # Reusable UI components
│   │   ├── forms/
│   │   │   ├── login-form.tsx
│   │   │   ├── signup-form.tsx
│   │   │   └── task-form.tsx
│   │   ├── lists/
│   │   │   └── task-list.tsx
│   │   ├── layouts/
│   │   │   └── container.tsx
│   │   ├── hoc/
│   │   │   └── with-auth.tsx
│   │   └── ui/
│   │       └── header.tsx
│   ├── lib/
│   │   └── api/
│   │       ├── auth-client.ts
│   │       └── task-client.ts
│   ├── styles/
│   │   └── globals.css
│   └── context/
│       └── AuthContext.jsx  # Will be removed as we consolidate to Next.js auth provider
├── package.json
├── next.config.js
├── tsconfig.json
└── tailwind.config.js
```

**Structure Decision**: Consolidate existing frontend to use Next.js App Router exclusively. Remove all Pages Router components (src/pages/*, src/App.jsx, src/context/AuthContext.jsx) and legacy auth provider in favor of a unified Next.js App Router approach with a single Auth Provider.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| | | |