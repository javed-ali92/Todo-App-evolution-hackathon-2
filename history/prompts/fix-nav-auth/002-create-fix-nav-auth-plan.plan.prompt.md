---
id: 002
title: Create Fix Nav Auth Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: fix-nav-auth
branch: 002-fix-nav-auth
user: HP
command: /sp.plan
labels: ["planning", "fix-nav-auth", "navigation", "auth-persistence", "header-ui"]
links:
  spec: specs/002-fix-nav-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fix-nav-auth/plan.md
  - specs/002-fix-nav-auth/research.md
  - specs/002-fix-nav-auth/data-model.md
  - specs/002-fix-nav-auth/quickstart.md
tests: []
---

## Prompt

Goal:
Fix redirect loop, improve header navigation, and persist login on page reload.

Plan:
1. Review auth guard and redirect logic.
2. Stop forced dashboard redirect for logged-in users.
3. Allow navigation between Home and Dashboard.
4. Update header with all page links.
5. Improve header UI and active state.
6. Persist auth state across page reloads.
7. Ensure logout clears auth correctly.

Constraints:
- No backend changes
- No new libraries
- Minimal frontend changes

Validation:
- No redirect loop
- Header links work
- User stays logged in after refresh

## Response snapshot

Created comprehensive implementation plan for fixing navigation, header UI, and auth persistence issues.

**Planning Artifacts Created**:

1. **plan.md** - Complete implementation plan with:
   - Technical context (TypeScript, Next.js, React, localStorage)
   - Constitution compliance check (all passed)
   - Project structure and file changes
   - 4 implementation phases with validation criteria
   - Risk assessment and mitigation strategies
   - Success criteria validation

2. **research.md** - Technical decisions covering:
   - Root cause of redirect loop (forced redirect in page.tsx)
   - Auth persistence verification (localStorage already implemented)
   - Header navigation structure (conditional rendering)
   - Active page indicator (usePathname hook)
   - Responsive design (stacked layout on mobile)
   - Technology stack verification (no new dependencies)

3. **data-model.md** - Data model documentation:
   - Existing UserSession entity structure
   - State transition flows (auth, navigation, header display)
   - Field modification rules
   - Validation rules (frontend)
   - TypeScript interfaces
   - localStorage schema
   - Data flow diagrams

4. **quickstart.md** - Developer implementation guide:
   - 4-phase implementation roadmap
   - Step-by-step instructions with code examples
   - Manual testing checklist
   - Common issues and solutions
   - Performance optimization tips
   - Deployment checklist

**Key Technical Decisions**:
- Remove forced dashboard redirect from home page (page.tsx lines 12-16)
- Verify existing localStorage implementation (already correct)
- Use conditional rendering for auth-aware header navigation
- Use Next.js usePathname hook for active page indicator
- No new dependencies required

**Constitution Compliance**: ✅ All checks passed
- Spec-driven development workflow followed
- Monorepo architecture maintained (frontend-only changes)
- Technology stack adherence (Next.js, TypeScript, Better Auth)
- Security compliance (no auth flow changes)
- API contract compliance (no API changes)

**Implementation Phases**:
1. Fix Infinite Redirect Loop (30 minutes)
2. Verify Auth Persistence (15 minutes)
3. Enhance Header Navigation (1 hour)
4. Testing & Validation (30 minutes)

**Files to Modify**:
- frontend/src/app/page.tsx (remove forced redirect)
- frontend/src/components/ui/header.tsx (add navigation links, auth-aware display)
- frontend/src/app/providers/auth-provider.tsx (verify only, likely no changes)

**Files to Create**:
- None (all changes are modifications to existing files)

**Backend Changes**: None required

**Root Cause Analysis**:
- Redirect loop: page.tsx forces logged-in users to dashboard (lines 12-16)
- Auth persistence: Already implemented correctly in auth-provider.tsx
- Header: Currently returns null for logged-out users, needs enhancement

**Next Steps**: Run `/sp.tasks` to generate detailed implementation tasks.

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation with 4 phases, technical decisions, and developer guide
- 🧪 Tests: Manual testing procedures documented in quickstart.md
- 📁 Files: 4 files created (plan.md, research.md, data-model.md, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate detailed implementation tasks
- 🧠 Reflection: Plan successfully addresses all 3 user-reported issues with minimal changes (frontend-only, no new dependencies)

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all Phase 0 and Phase 1 artifacts
- Graders run and results (PASS/FAIL): PASS - All constitution checks passed, technical decisions documented
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Consider adding automated tests for header navigation in future iterations
