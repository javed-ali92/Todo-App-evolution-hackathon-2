---
id: 1
title: neon-db-migration-spec
stage: spec
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: neon-db-migration
branch: 005-neon-db-migration
user: user
command: /sp.specify
labels: ["database", "migration", "neon", "postgresql", "specification"]
links:
  spec: specs/005-neon-db-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/005-neon-db-migration/spec.md
 - specs/005-neon-db-migration/checklists/requirements.md
tests:
 - none (specification phase)
---

## Prompt

ROLE:
You are acting as a Senior Backend Engineer and Database Architect.

PROJECT:
Todo Application (FastAPI + SQLModel)

GOAL:
Migrate the application database from a local database to **Neon Serverless PostgreSQL** and ensure that **all user and task data is persisted in Neon**, not locally.

====================================
CURRENT STATE
====================================
- Backend: FastAPI
- ORM: SQLModel
- Local database was previously used
- Neon PostgreSQL DATABASE_URL is already set in `.env`
- Authentication is working
- Tasks creation exists but data is NOT being saved in Neon DB

====================================
PROBLEM STATEMENT
====================================
1. User data is not being saved in Neon PostgreSQL
2. Task data is not being saved in Neon PostgreSQL
3. Backend may still be using a local database engine/session
4. Database connection must be verified and enforced system-wide

====================================
OBJECTIVES
====================================

1. DATABASE CONNECTION (MANDATORY)
- Read `DATABASE_URL` from `.env`
- Connect FastAPI + SQLModel ONLY to Neon PostgreSQL
- Completely disable / remove local database usage
- Ensure async/sync engine choice matches Neon best practices

2. DATABASE MIGRATION
- Ensure tables are created in Neon PostgreSQL:

  USERS TABLE
  - id (primary key)
  - username (unique)
  - email (unique)
  - password (hashed)
  - created_at

  TASKS TABLE
  - id (primary key)
  - user_id (foreign key → users.id)
  - title
  - description
  - due_date
  - priority (ENUM: High, Medium, Low)
  - tags (array / list)
  - recursion_pattern
  - completed (boolean)
  - created_at
  - updated_at

3. SESSION / ENGINE FIX
- Ensure SQLModel `engine` uses Neon DATABASE_URL
- Ensure all `Session` dependencies use the Neon engine
- Remove any hardcoded SQLite or local Postgres references

4. DATA PERSISTENCE VALIDATION
- On signup → user must be saved in Neon DB
- On login → user must be read from Neon DB
- On task creation → task must be saved in Neon DB

## Response snapshot

Created comprehensive specification for Neon Serverless PostgreSQL database migration with:

**Feature Structure:**
- Branch: 005-neon-db-migration
- Spec file: specs/005-neon-db-migration/spec.md
- Quality checklist: specs/005-neon-db-migration/checklists/requirements.md

**User Stories (5 total, prioritized):**
1. Database Connection Establishment (P1) - Foundation for all persistence
2. User Data Persistence (P1) - Account registration and login
3. Task Data Persistence (P1) - Core CRUD operations
4. Data Isolation and Security (P2) - Multi-tenant data privacy
5. Database Schema Integrity (P2) - Constraints and relationships

**Requirements:**
- 15 functional requirements covering connection, schema, CRUD operations, and data isolation
- 2 key entities: User and Task with detailed attribute descriptions
- 10 success criteria with measurable metrics (100% persistence, <5s connection, zero local writes)

**Quality Validation:**
- All checklist items passed
- No [NEEDS CLARIFICATION] markers
- Technology-agnostic success criteria
- Clear scope boundaries with 14 out-of-scope items
- 7 edge cases identified
- 6 dependencies and 10 assumptions documented

**Readiness:** Specification is complete and ready for `/sp.plan` phase.

## Outcome

- ✅ Impact: Complete specification created for database migration from local to Neon PostgreSQL with clear acceptance criteria and measurable success metrics
- 🧪 Tests: No tests at specification phase; acceptance scenarios defined for implementation validation
- 📁 Files: Created spec.md (190 lines) and requirements.md checklist (validation passed)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, or `/sp.clarify` if additional requirements emerge
- 🧠 Reflection: Specification successfully balances technical precision (schema requirements, constraints) with business value (user data persistence, multi-device access). Prioritization enables MVP delivery with P1 stories only.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed without clarifications needed
- Graders run and results (PASS/FAIL): Quality checklist validation - ALL PASS (14/14 items)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed to planning phase to translate requirements into technical architecture
