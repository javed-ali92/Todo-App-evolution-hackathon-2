---
id: 1
title: neon-db-migration-plan
stage: plan
date: 2026-01-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: neon-db-migration
branch: 1-neon-db-migration
user: default_user
command: sp.plan
labels: [database,migration,neon,postgresql,plan]
links:
  spec: specs/1-neon-db-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-neon-db-migration/plan.md
 - specs/1-neon-db-migration/research.md
 - specs/1-neon-db-migration/data-model.md
 - specs/1-neon-db-migration/contracts/openapi.yaml
 - specs/1-neon-db-migration/quickstart.md
tests:
 - specs/1-neon-db-migration/plan.md validation
 - specs/1-neon-db-migration/data-model.md validation
---

## Prompt

Using the approved specifications:

- @specs/overview.md
- @specs/features/authentication.md
- @specs/features/task-crud.md
- @specs/database/neon-migration.md

Update and produce a complete system-wide implementation plan that includes Neon Serverless PostgreSQL migration and backend database integration.

The plan must be structured into clear phases and include:

========================
1) Repository & Monorepo Setup
========================
- Folder structure
- Spec-Kit configuration
- CLAUDE.md placement
- Environment variable strategy

========================
2) Database & Migration Plan (NEW)
========================
- Deprecating local database
- Neon PostgreSQL provisioning
- Connection string management
- Environment variable setup
- SQLModel engine configuration
- Migration strategy
- Schema initialization
- Verification steps

========================
3) Backend Architecture Plan (FastAPI)
========================
- Project structure
- SQLModel integration
- Session management
- JWT verification middleware
- API routing
- Error handling

========================
4) Frontend Architecture Plan (Next.js)
========================
- App Router structure
- Better Auth integration
- Session handling
- API client design

========================
5) Authentication Flow Plan
========================
- Signup
- Login
- Token issuance
- Token storage
- Token forwarding
- Backend verification

========================
6) Task Management Plan
========================
- Create
- Read
- Update
- Delete
- Toggle completion
- Ownership enforcement

========================
7) Security Plan
========================
- Secrets handling
- Password hashing
- Token expiry
- Authorization checks

========================
8) Testing Plan
========================
- Database tests
- Backend tests
- Auth tests
- Frontend tests

========================
9) Deployment & Local Dev Plan
========================
- Docker usage
- Local dev startup order
- Environment files

========================
RULES
========================
- No code
- No task breakdown yet
- High-level but actionable
- Follow constitution
- Follow all specs

Produce a clean, numbered, and logically ordered plan.

## Response snapshot

# Todo Full-Stack Web Application Implementation Plan

**Feature**: Neon Serverless PostgreSQL Migration and Backend Integration
**Plan Version**: 1.0.0
**Created**: 2026-01-31
**Author**: Claude Code
**Status**: Draft
**Spec Reference**: @specs/database/neon-migration.md

## Technical Context

This implementation plan covers the migration from local database to Neon Serverless PostgreSQL and backend integration. The system is a full-stack todo application with Next.js frontend, FastAPI backend, and PostgreSQL database via Neon. The application implements user authentication with Better Auth/JWT and task management with per-user data isolation.

### Technology Stack
- **Frontend**: Next.js 16+ (App Router), TypeScript, Better Auth
- **Backend**: Python FastAPI, SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (Frontend), JWT verification (Backend)
- **Architecture**: Monorepo with separate frontend/backend directories

### Known Constraints
- API contract is fixed: GET/POST/PUT/DELETE/PATCH /api/{user_id}/tasks*
- Authentication must follow JWT token verification pattern
- Per-user data isolation required
- All development must follow spec-driven workflow

### Dependencies
- Neon Serverless PostgreSQL account and connection string
- Python FastAPI ecosystem (SQLModel, Pydantic, etc.)
- Node.js/NPM for frontend dependencies
- Better Auth for frontend authentication

## Constitution Check

### Compliance Verification
- ✅ Spec-Driven Development: Following approved specifications from @specs/overview.md, @specs/features/authentication.md, @specs/features/task-crud.md, and @specs/database/neon-migration.md
- ✅ Monorepo Architecture: Maintaining separate frontend and backend in single repository
- ✅ Full-Stack Feature Completeness: Implementing all required todo features per-user
- ✅ Technology Stack Adherence: Using prescribed technologies (Next.js, FastAPI, SQLModel, Neon)
- ✅ Authentication Security: Following JWT token verification pattern
- ✅ API Contract Compliance: Using fixed API endpoints as specified
- ✅ Database Rules: Using PostgreSQL via Neon with SQLModel
- ✅ Implementation Rules: Using environment variables, proper error handling, etc.

### Potential Violations
- None identified - all planned implementations comply with constitution

## Gates

### Gate 1: Architecture Alignment
**Status**: PASSED
- All architectural decisions align with constitution
- Technology stack matches requirements
- API contracts are compliant

### Gate 2: Security Compliance
**Status**: PASSED
- JWT token verification pattern followed
- Per-user data isolation enforced
- Authentication model compliant

### Gate 3: Specification Adherence
**Status**: PASSED
- All functional requirements from specifications will be implemented
- Success criteria will be met

## Phase 0: Research & Discovery

### Research Tasks
1. **Neon PostgreSQL Connection Patterns**: Investigate best practices for connecting to Neon Serverless PostgreSQL from FastAPI applications
2. **SQLModel Engine Configuration**: Research optimal SQLModel engine setup for Neon's serverless characteristics
3. **Connection Pooling Strategy**: Determine appropriate connection pooling for Neon's serverless sleep/wake cycle
4. **Migration Strategy**: Identify best approach for migrating from local SQLite/PostgreSQL to Neon
5. **Environment Variable Management**: Establish secure handling of database credentials

### Research Outcomes
- Neon requires connection string with SSL mode settings for secure connections
- SQLModel engines should use connection pooling optimized for serverless
- Migration should be atomic with rollback capability
- Environment variables must be properly secured and validated

## Phase 1: System Design

### 1) Repository & Monorepo Setup

#### Folder Structure
```
hackathon-todo/
├── .specify/                 # Spec-Kit configuration
│   ├── memory/              # Project constitution and guidelines
│   ├── templates/           # Template files for specs, plans, tasks
│   └── scripts/             # Automation scripts
├── specs/                   # All feature specifications
│   ├── overview.md          # Main project overview
│   ├── features/            # Individual feature specs
│   │   ├── authentication.md
│   │   └── task-crud.md
│   ├── database/            # Database-related specs
│   │   └── neon-migration.md
│   └── api/                 # API contract specifications
├── frontend/                # Next.js frontend application
│   ├── src/                 # Source code
│   ├── public/              # Static assets
│   ├── styles/              # CSS and styling
│   ├── components/          # Reusable components
│   ├── lib/                 # Utility libraries
│   │   └── api/            # API client implementations
│   ├── app/                 # App Router pages
│   │   ├── login/          # Authentication pages
│   │   ├── signup/         # Registration pages
│   │   └── dashboard/      # Task management pages
│   ├── .env.local          # Frontend environment variables
│   └── package.json        # Dependencies and scripts
├── backend/                 # FastAPI backend application
│   ├── src/                 # Source code
│   │   ├── main.py         # Application entry point
│   │   ├── database/       # Database connection and setup
│   │   ├── models/         # SQLModel definitions
│   │   ├── api/            # API route definitions
│   │   ├── services/       # Business logic implementations
│   │   └── auth/           # Authentication middleware
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
├── docker-compose.yml      # Container orchestration
├── .env.example           # Example environment variables
└── README.md              # Project documentation
```

#### Spec-Kit Configuration
- Initialize `.specify/` directory with templates and scripts
- Configure automation for spec-driven workflow
- Set up documentation templates and standards

#### CLAUDE.md Placement
- Place CLAUDE.md in project root with project-specific instructions
- Include guidelines for Claude Code usage and project-specific rules
- Document workflow expectations and architecture patterns

#### Environment Variable Strategy
- Centralize environment variable definitions across frontend and backend
- Use `.env.example` for documentation of required variables
- Separate sensitive variables into `.env` files not committed to repo
- Frontend: Use `NEXT_PUBLIC_*` prefixed variables for client-side access
- Backend: Use standard environment variables for server-side configuration

### 2) Database & Migration Plan (NEW)

#### Deprecating Local Database
- Identify current local database implementation (SQLite or local PostgreSQL)
- Create backup/export of existing data if present
- Document current schema structure and relationships
- Plan transition timeline with minimal downtime

#### Neon PostgreSQL Provisioning
- Create Neon Serverless PostgreSQL project
- Set up database with appropriate region and scaling settings
- Configure database user and permissions
- Obtain connection string with SSL settings

#### Connection String Management
- Store Neon connection string in environment variables
- Implement secure connection handling with SSL mode
- Create connection validation utility
- Document connection string format and requirements

#### Environment Variable Setup
- Define `DATABASE_URL` for Neon PostgreSQL connection
- Set up `NEON_DATABASE_URL` specifically for Neon connection string
- Implement validation for required database configuration
- Create fallback configuration for development environments

#### SQLModel Engine Configuration
- Configure SQLModel engine with Neon-optimized settings
- Implement connection pooling with appropriate timeout values
- Handle Neon's serverless sleep/wake cycle efficiently
- Set up automatic reconnection mechanisms

#### Migration Strategy
- Create atomic migration process with rollback capability
- Implement data validation before and after migration
- Develop migration verification procedures
- Plan for zero-downtime migration if possible

#### Schema Initialization
- Define SQLModel models matching required schema
- Implement automatic schema creation/migration
- Set up indexes for optimal query performance
- Configure foreign key relationships and constraints

#### Verification Steps
- Create database connectivity tests
- Implement schema validation checks
- Verify data integrity post-migration
- Test connection pooling and performance

### 3) Backend Architecture Plan (FastAPI)

#### Project Structure
- Organize code in modular, maintainable modules
- Separate concerns into models, services, API routes, and database layers
- Implement proper error handling and logging
- Create reusable utility functions

#### SQLModel Integration
- Define User, Task, and Session models using SQLModel
- Implement proper relationships and constraints
- Create model validation and serialization
- Set up automatic table creation and migrations

#### Session Management
- Implement database session management with proper lifecycle
- Create session dependency for API routes
- Handle session cleanup and error recovery
- Optimize for Neon's connection characteristics

#### JWT Verification Middleware
- Create middleware for JWT token validation
- Extract user ID from token payload
- Compare token user ID with request user ID
- Handle token expiration and invalidation

#### API Routing
- Implement fixed API contract routes as specified
- Create proper route organization and grouping
- Add input validation and error handling
- Implement response formatting and serialization

#### Error Handling
- Create comprehensive error response formats
- Handle database, authentication, and validation errors
- Implement proper HTTP status codes
- Add logging for debugging and monitoring

### 4) Frontend Architecture Plan (Next.js)

#### App Router Structure
- Organize pages using Next.js App Router
- Create authentication flow pages (login, signup)
- Implement dashboard with task management
- Ensure proper navigation and routing

#### Better Auth Integration
- Configure Better Auth with JWT plugin
- Set up authentication state management
- Implement login, signup, and logout flows
- Handle authentication state persistence

#### Session Handling
- Store JWT tokens securely in browser storage
- Implement token refresh mechanisms
- Handle session expiration gracefully
- Create authentication context for components

#### API Client Design
- Create centralized API client for backend communication
- Implement proper error handling and retry logic
- Add authentication token attachment to requests
- Create type-safe interfaces for API operations

### 5) Authentication Flow Plan

#### Signup
- Collect user credentials (email, password)
- Validate input on frontend and backend
- Create user record in database with hashed password
- Return JWT token upon successful registration

#### Login
- Accept user credentials (email, password)
- Verify credentials against stored hash
- Generate JWT token with user identity
- Return token and user information

#### Token Issuance
- Create JWT with appropriate claims and expiration
- Include user ID in token payload
- Use secure signing algorithm and secret
- Set appropriate token lifetime

#### Token Storage
- Store JWT in secure browser storage
- Implement token refresh mechanisms
- Handle token expiration and renewal
- Clear tokens on logout

#### Token Forwarding
- Attach JWT to all API requests as Authorization header
- Implement automatic token attachment
- Handle token refresh when needed
- Retry failed requests with fresh tokens

#### Backend Verification
- Validate JWT signature and expiration
- Extract user ID from token payload
- Compare token user ID with request user ID
- Reject requests with invalid tokens

### 6) Task Management Plan

#### Create
- Accept task data from authenticated user
- Validate task properties and user permissions
- Create task record linked to user ID
- Return created task with all properties

#### Read
- Retrieve tasks for authenticated user only
- Validate user has permission to access tasks
- Apply proper filtering and pagination
- Return tasks with all required properties

#### Update
- Locate task and verify user ownership
- Apply requested changes to task
- Validate updated data integrity
- Return updated task with all properties

#### Delete
- Locate task and verify user ownership
- Remove task from database
- Return success confirmation
- Handle cascading relationships if needed

#### Toggle Completion
- Locate task and verify user ownership
- Switch completion status of task
- Update timestamp and save changes
- Return updated task with new status

#### Ownership Enforcement
- Verify user ID in JWT matches task owner
- Prevent cross-user data access
- Return appropriate error for unauthorized access
- Log security violations for monitoring

### 7) Security Plan

#### Secrets Handling
- Store database credentials in environment variables
- Never commit secrets to version control
- Use secure secret management for production
- Implement secret validation and rotation

#### Password Hashing
- Use bcrypt or similar secure hashing algorithm
- Implement proper salt generation
- Validate password strength requirements
- Handle password updates securely

#### Token Expiry
- Set appropriate JWT expiration times
- Implement token refresh mechanisms
- Handle token expiration gracefully
- Clean up expired sessions appropriately

#### Authorization Checks
- Validate user permissions for every request
- Compare token user ID with request user ID
- Prevent unauthorized data access
- Log security-related events and violations

### 8) Testing Plan

#### Database Tests
- Test database connectivity and configuration
- Verify schema creation and relationships
- Validate data integrity and constraints
- Test connection pooling and performance

#### Backend Tests
- Test all API endpoints with valid/invalid data
- Verify authentication and authorization flows
- Test error handling and edge cases
- Validate JWT token verification

#### Auth Tests
- Test user registration and login flows
- Verify token issuance and validation
- Test session management and logout
- Validate security against unauthorized access

#### Frontend Tests
- Test authentication UI flows
- Verify task management functionality
- Test API client integration
- Validate responsive design and UX

### 9) Deployment & Local Dev Plan

#### Docker Usage
- Create containerized environment for both frontend and backend
- Set up Docker Compose for local development
- Implement proper networking between services
- Configure volume mounting for development

#### Local Dev Startup Order
1. Start Neon PostgreSQL (or local alternative for dev)
2. Initialize database schema and migrations
3. Start backend FastAPI server
4. Start frontend Next.js development server
5. Verify connectivity and basic functionality

#### Environment Files
- Create `.env.example` with all required variables documented
- Implement proper environment file loading for each service
- Set up different configurations for dev, staging, production
- Secure sensitive environment variables appropriately

## Phase 2: Implementation Preparation

### Prerequisites Checklist
- [ ] Neon PostgreSQL instance provisioned with connection string
- [ ] Development environment with required tools installed
- [ ] Environment variable files created and secured
- [ ] Database schema design finalized and reviewed
- [ ] API contract confirmed and documented
- [ ] Authentication flow designed and validated
- [ ] Security requirements understood and planned

### Team Preparation
- [ ] Developers briefed on architecture and requirements
- [ ] Development workflow established and documented
- [ ] Code review and testing standards defined
- [ ] Deployment pipeline planned and prepared

## Success Criteria

### Technical Achievement
- Neon PostgreSQL successfully integrated as primary database
- All existing functionality preserved during migration
- Database performance meets or exceeds current levels
- Security and data isolation maintained

### Process Achievement
- All development follows spec-driven workflow
- Architecture complies with constitution requirements
- Implementation meets all functional requirements
- Testing validates all success criteria

### Quality Achievement
- Zero data loss during migration process
- Minimal downtime during transition
- Improved scalability and performance
- Enhanced security and reliability

## Additional Generated Artifacts

### Research Summary
- Neon PostgreSQL connection strategy and configuration
- SQLModel engine optimization for serverless
- Migration strategy with validation approach
- Environment variable management approach

### Data Model
- Detailed entity definitions for User, Task, and Session
- Field specifications and validation rules
- Relationship mappings and constraints
- State transition definitions

### API Contracts
- Complete OpenAPI specification for all endpoints
- Request/response schemas for all operations
- Security definitions and error responses
- Parameter and validation specifications

### Quickstart Guide
- Step-by-step setup instructions
- Environment configuration requirements
- Development and deployment commands
- Troubleshooting tips

## Outcome

- ✅ Impact: Created comprehensive implementation plan for Neon PostgreSQL migration that addresses all requirements from specifications
- 🧪 Tests: Generated complete API contracts, data models, and testing plan aligned with specifications
- 📁 Files: Created plan.md, research.md, data-model.md, contracts/openapi.yaml, and quickstart.md
- 🔁 Next prompts: Ready for task breakdown phase (/sp.tasks) to convert plan into executable tasks
- 🧠 Reflection: Plan comprehensively covers all aspects of database migration and backend integration while maintaining security and functionality

## Evaluation notes (flywheel)

- Failure modes observed: None - plan addresses all requirements and follows constitution
- Graders run and results (PASS/FAIL): PASS - all validation checks passed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task breakdown phase