# Implementation Plan: AI Chatbot for Task Management

**Branch**: `002-ai-chatbot` | **Date**: 2026-02-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ai-chatbot/spec.md`

## Summary

Add an AI-powered chatbot that enables users to manage their tasks through natural language conversations. The chatbot interprets user intent, executes task operations via MCP (Model Context Protocol) tools, and maintains conversation history for contextual interactions. This feature integrates with the existing FastAPI backend and Neon PostgreSQL database without modifying existing task management APIs.

**Primary Requirement**: Natural language interface for task CRUD operations (create, read, update, delete, complete) with conversation context.

**Technical Approach**:
- OpenAI Agents SDK for natural language understanding and intent recognition
- MCP server exposing task management tools to the AI agent
- New chat API endpoint (POST /api/{user_id}/chat) with JWT authentication
- Database models for Conversation and Message entities
- Stateless server design with conversation history stored in PostgreSQL

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP Python SDK, PyJWT
- Frontend: Next.js 16+, React, ChatKit UI library (or custom chat component)

**Storage**: Neon Serverless PostgreSQL (existing + new tables: conversations, messages)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web (frontend + backend in monorepo)

**Performance Goals**:
- Chat response time: <3 seconds for 95% of requests
- Support 100 concurrent chat sessions
- Database queries: <500ms for conversation history

**Constraints**:
- MUST NOT modify existing task API endpoints
- MUST maintain stateless server (conversation state in DB only)
- MUST enforce JWT authentication and user ownership
- AI service timeout: 10 seconds max

**Scale/Scope**:
- Support 1000+ users with conversation history
- Handle 100 messages/day per user (rate limit)
- Retain conversation history for 30 days

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement
- [x] No direct implementation without approved specs, plans, and tasks

### Architecture Compliance
- [x] Maintains monorepo structure: frontend/ (Next.js), backend/ (FastAPI), specs/, docker-compose.yml
- [x] Clear separation between frontend and backend components

### Technology Stack Compliance
- [x] Frontend uses Next.js 16+ (App Router), TypeScript, Better Auth
- [x] Backend uses Python FastAPI, SQLModel ORM
- [x] Database uses Neon Serverless PostgreSQL
- [x] Authentication uses Better Auth with JWT

### Security Compliance
- [x] All API routes require JWT token authentication
- [x] Backend verifies JWT token and extracts user ID
- [x] Backend compares token_user_id == url_user_id to prevent unauthorized access
- [x] Users can only access their own tasks and conversations

### API Contract Compliance
- [x] Existing task API routes remain unchanged:
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{id}
  - PUT /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH /api/{user_id}/tasks/{id}/complete
- [x] New chat endpoint follows same pattern: POST /api/{user_id}/chat

**Constitution Compliance**: ✅ PASS - All principles satisfied. New chat endpoint follows existing patterns without modifying current APIs.

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Database schema for conversations/messages
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API contracts
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool definitions
└── tasks.md             # Phase 2: Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py      # NEW: Conversation model
│   │   ├── message.py           # NEW: Message model
│   │   ├── task.py              # EXISTING: No changes
│   │   └── user.py              # EXISTING: No changes
│   ├── services/
│   │   ├── chat_service.py      # NEW: Chat orchestration logic
│   │   ├── conversation_service.py  # NEW: Conversation CRUD
│   │   ├── message_service.py   # NEW: Message CRUD
│   │   ├── task_service.py      # EXISTING: No changes
│   │   └── auth_service.py      # EXISTING: No changes
│   ├── api/
│   │   ├── chat.py              # NEW: Chat endpoint
│   │   ├── tasks.py             # EXISTING: No changes
│   │   └── auth.py              # EXISTING: No changes
│   ├── mcp/
│   │   ├── server.py            # NEW: MCP server setup
│   │   ├── tools/
│   │   │   ├── add_task.py      # NEW: MCP tool for task creation
│   │   │   ├── list_tasks.py    # NEW: MCP tool for listing tasks
│   │   │   ├── complete_task.py # NEW: MCP tool for completing tasks
│   │   │   ├── update_task.py   # NEW: MCP tool for updating tasks
│   │   │   └── delete_task.py   # NEW: MCP tool for deleting tasks
│   │   └── __init__.py
│   ├── agents/
│   │   ├── task_agent.py        # NEW: OpenAI agent configuration
│   │   └── __init__.py
│   └── database/
│       └── database.py          # EXISTING: Add new table creation
└── tests/
    ├── test_chat_api.py         # NEW: Chat endpoint tests
    ├── test_conversation_service.py  # NEW: Conversation service tests
    ├── test_mcp_tools.py        # NEW: MCP tool tests
    └── test_agent.py            # NEW: Agent integration tests

frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── chat-interface.tsx    # NEW: Main chat UI
│   │   │   ├── message-list.tsx      # NEW: Message display
│   │   │   ├── message-input.tsx     # NEW: Input field
│   │   │   └── chat-bubble.tsx       # NEW: Individual message
│   │   └── [existing components]
│   ├── lib/
│   │   ├── api/
│   │   │   ├── chat-client.ts        # NEW: Chat API client
│   │   │   └── task-client.ts        # EXISTING: No changes
│   │   └── hooks/
│   │       └── use-chat.ts           # NEW: Chat state management hook
│   └── app/
│       ├── chat/
│       │   └── page.tsx              # NEW: Chat page
│       └── [existing pages]
└── tests/
    └── chat-interface.test.tsx       # NEW: Chat UI tests
```

**Structure Decision**: Web application structure with clear backend/frontend separation. New chat functionality is isolated in dedicated modules (mcp/, agents/, chat service) to avoid coupling with existing task management code. Frontend chat components are self-contained in components/chat/ directory.

## Complexity Tracking

> No constitution violations - this section is not needed.

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **OpenAI Agents SDK Integration**
   - Research: Best practices for integrating OpenAI Agents SDK with FastAPI
   - Decision needed: Agent configuration, prompt engineering, error handling
   - Output: Agent setup patterns and configuration approach

2. **MCP (Model Context Protocol) Implementation**
   - Research: MCP Python SDK usage and tool definition patterns
   - Decision needed: Tool registration, parameter validation, error propagation
   - Output: MCP server architecture and tool implementation patterns

3. **Natural Language Date Parsing**
   - Research: Libraries for parsing relative dates ("tomorrow", "next Friday", "in 2 days")
   - Decision needed: Use dateparser, python-dateutil, or custom solution
   - Output: Date parsing strategy and library choice

4. **Conversation State Management**
   - Research: Patterns for maintaining conversation context in stateless servers
   - Decision needed: How much history to load, context window size, memory optimization
   - Output: Conversation loading and context management strategy

5. **Rate Limiting Implementation**
   - Research: FastAPI rate limiting libraries (slowapi, fastapi-limiter)
   - Decision needed: Per-user limits, storage backend (Redis vs PostgreSQL)
   - Output: Rate limiting approach and configuration

6. **Frontend Chat UI Library**
   - Research: React chat component libraries (react-chat-elements, ChatKit, custom)
   - Decision needed: Use library vs build custom, accessibility considerations
   - Output: Chat UI implementation approach

7. **AI Service Error Handling**
   - Research: Patterns for handling AI service timeouts, rate limits, and failures
   - Decision needed: Retry logic, fallback responses, user feedback
   - Output: Error handling strategy and user experience patterns

8. **Conversation History Encryption**
   - Research: SQLModel field-level encryption options
   - Decision needed: Encryption library, key management, performance impact
   - Output: Data encryption approach for sensitive conversation data

### Research Output Format

For each research task, document in `research.md`:

```markdown
## [Research Topic]

**Decision**: [What was chosen]

**Rationale**: [Why this approach was selected]

**Alternatives Considered**:
- Option A: [Description] - Rejected because [reason]
- Option B: [Description] - Rejected because [reason]

**Implementation Notes**: [Key considerations for implementation]

**Dependencies**: [New packages or services required]
```

---

## Phase 1: Design & Contracts

### 1.1 Data Model Design

**Output**: `data-model.md`

#### Conversation Entity

```text
Conversation
├── id: UUID (primary key)
├── user_id: Integer (foreign key to users table)
├── created_at: DateTime
├── updated_at: DateTime
├── last_message_at: DateTime
└── metadata: JSON (optional: conversation title, tags, etc.)

Relationships:
- Belongs to User (one-to-many)
- Has many Messages (one-to-many)

Validation Rules:
- user_id must reference existing user
- created_at cannot be in the future
- last_message_at must be >= created_at

State Transitions:
- Created → Active (on first message)
- Active → Archived (after 30 days of inactivity)
```

#### Message Entity

```text
Message
├── id: UUID (primary key)
├── conversation_id: UUID (foreign key to conversations table)
├── sender: Enum('user', 'bot')
├── content: Text (encrypted)
├── created_at: DateTime
├── metadata: JSON (optional: task_operation, intent, confidence)
└── parent_message_id: UUID (nullable, for threading)

Relationships:
- Belongs to Conversation (many-to-one)
- Optional parent Message (self-referential for threading)

Validation Rules:
- conversation_id must reference existing conversation
- sender must be 'user' or 'bot'
- content cannot be empty
- content max length: 10,000 characters

Indexes:
- conversation_id (for efficient history queries)
- created_at (for chronological ordering)
- composite (conversation_id, created_at) for pagination
```

### 1.2 API Contract Design

**Output**: `contracts/chat-api.yaml`

```yaml
openapi: 3.0.0
info:
  title: Chat API
  version: 1.0.0

paths:
  /api/{user_id}/chat:
    post:
      summary: Send a chat message and get AI response
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  maxLength: 1000
                  example: "add task: finish project report by Friday"
                conversation_id:
                  type: string
                  format: uuid
                  description: "Optional: continue existing conversation"
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  conversation_id:
                    type: string
                    format: uuid
                  message:
                    type: string
                    example: "I've created a task 'finish project report' with due date Friday, Feb 16."
                  task_operation:
                    type: object
                    nullable: true
                    properties:
                      action:
                        type: string
                        enum: [create, read, update, delete, complete]
                      task_id:
                        type: integer
                        nullable: true
                      success:
                        type: boolean
        '401':
          description: Unauthorized - invalid or missing JWT token
        '403':
          description: Forbidden - user_id mismatch with token
        '429':
          description: Too many requests - rate limit exceeded
        '500':
          description: Internal server error
        '503':
          description: AI service unavailable

  /api/{user_id}/conversations:
    get:
      summary: List user's conversations
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: List of conversations
          content:
            application/json:
              schema:
                type: object
                properties:
                  conversations:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                        created_at:
                          type: string
                          format: date-time
                        last_message_at:
                          type: string
                          format: date-time
                        message_count:
                          type: integer

  /api/{user_id}/conversations/{conversation_id}/messages:
    get:
      summary: Get conversation history
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
        - name: conversation_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
            maximum: 200
      responses:
        '200':
          description: Conversation messages
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                        sender:
                          type: string
                          enum: [user, bot]
                        content:
                          type: string
                        created_at:
                          type: string
                          format: date-time

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

**Output**: `contracts/mcp-tools.json`

```json
{
  "tools": [
    {
      "name": "add_task",
      "description": "Create a new task for the user",
      "parameters": {
        "type": "object",
        "required": ["title"],
        "properties": {
          "title": {
            "type": "string",
            "description": "Task title"
          },
          "description": {
            "type": "string",
            "description": "Optional task description"
          },
          "due_date": {
            "type": "string",
            "format": "date",
            "description": "Optional due date (YYYY-MM-DD)"
          },
          "priority": {
            "type": "string",
            "enum": ["Low", "Medium", "High"],
            "description": "Task priority"
          }
        }
      }
    },
    {
      "name": "list_tasks",
      "description": "List user's tasks with optional filters",
      "parameters": {
        "type": "object",
        "properties": {
          "completed": {
            "type": "boolean",
            "description": "Filter by completion status"
          },
          "due_date": {
            "type": "string",
            "format": "date",
            "description": "Filter by due date"
          },
          "priority": {
            "type": "string",
            "enum": ["Low", "Medium", "High"],
            "description": "Filter by priority"
          }
        }
      }
    },
    {
      "name": "complete_task",
      "description": "Mark a task as complete or incomplete",
      "parameters": {
        "type": "object",
        "required": ["task_id"],
        "properties": {
          "task_id": {
            "type": "integer",
            "description": "ID of the task to complete"
          },
          "completed": {
            "type": "boolean",
            "description": "Completion status (default: true)"
          }
        }
      }
    },
    {
      "name": "update_task",
      "description": "Update task details",
      "parameters": {
        "type": "object",
        "required": ["task_id"],
        "properties": {
          "task_id": {
            "type": "integer",
            "description": "ID of the task to update"
          },
          "title": {
            "type": "string",
            "description": "New task title"
          },
          "description": {
            "type": "string",
            "description": "New task description"
          },
          "due_date": {
            "type": "string",
            "format": "date",
            "description": "New due date"
          },
          "priority": {
            "type": "string",
            "enum": ["Low", "Medium", "High"],
            "description": "New priority"
          }
        }
      }
    },
    {
      "name": "delete_task",
      "description": "Delete a task permanently",
      "parameters": {
        "type": "object",
        "required": ["task_id"],
        "properties": {
          "task_id": {
            "type": "integer",
            "description": "ID of the task to delete"
          }
        }
      }
    }
  ]
}
```

### 1.3 Architecture Diagrams

**Chat Request Flow**:

```text
1. User sends message via frontend
   ↓
2. Frontend: POST /api/{user_id}/chat with JWT token
   ↓
3. Backend: Verify JWT, extract user_id, validate user_id match
   ↓
4. Backend: Load conversation history (last N messages)
   ↓
5. Backend: Initialize OpenAI Agent with conversation context
   ↓
6. Backend: Agent processes message, determines intent
   ↓
7. Backend: Agent calls MCP tool (e.g., add_task)
   ↓
8. MCP Tool: Execute task operation via existing task service
   ↓
9. MCP Tool: Return result to agent
   ↓
10. Agent: Generate natural language response
   ↓
11. Backend: Save user message and bot response to database
   ↓
12. Backend: Return response to frontend
   ↓
13. Frontend: Display bot response in chat UI
```

**MCP Tool Execution Flow**:

```text
Agent decides to call tool
   ↓
MCP Server receives tool call request
   ↓
Validate tool parameters
   ↓
Extract user_id from context
   ↓
Call appropriate task service method
   ↓
Task service executes operation (uses existing code)
   ↓
Return result (success/failure + data)
   ↓
MCP Server formats result for agent
   ↓
Agent incorporates result into response
```

### 1.4 Quickstart Guide

**Output**: `quickstart.md`

```markdown
# AI Chatbot Quickstart Guide

## Prerequisites

- Existing Todo App backend running (FastAPI + Neon PostgreSQL)
- OpenAI API key (for Agents SDK)
- Python 3.11+
- Node.js 18+ (for frontend)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install openai-agents-sdk mcp-python-sdk dateparser slowapi
```

### 2. Environment Variables

Add to `backend/.env`:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
MCP_SERVER_PORT=8001
CHAT_RATE_LIMIT=100  # messages per day per user
CONVERSATION_RETENTION_DAYS=30
```

### 3. Database Migration

```bash
# Create new tables for conversations and messages
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

### 4. Run Backend

```bash
uvicorn src.main:app --reload
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install @chatscope/chat-ui-kit-react
```

### 2. Add Chat Route

Navigate to `http://localhost:3000/chat` to access the chat interface.

## Testing

### Backend Tests

```bash
cd backend
pytest tests/test_chat_api.py -v
pytest tests/test_mcp_tools.py -v
```

### Frontend Tests

```bash
cd frontend
npm test -- chat-interface.test.tsx
```

## Usage

1. Login to the application
2. Navigate to Chat page
3. Type natural language commands:
   - "add task: buy groceries tomorrow"
   - "show me my tasks"
   - "mark 'buy groceries' as done"
   - "what's due today?"

## Troubleshooting

**Issue**: Chat responses are slow
- Check OpenAI API latency
- Verify database query performance
- Review conversation history size

**Issue**: Agent misunderstands intent
- Review agent prompts in `agents/task_agent.py`
- Check MCP tool descriptions
- Verify conversation context is loading correctly

**Issue**: Rate limit errors
- Check `CHAT_RATE_LIMIT` environment variable
- Verify rate limiting middleware configuration
- Review user's message count in database
```

### 1.5 Agent Context Update

Run the agent context update script to add new technologies to the project context:

```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This will add:
- OpenAI Agents SDK
- MCP Python SDK
- Chat API patterns
- Conversation management patterns

---

## Phase 2: Task Breakdown

**Note**: Task breakdown is created by the `/sp.tasks` command, not by `/sp.plan`.

The tasks.md file will be generated in the next phase and will include:
- Database migration tasks
- MCP tool implementation tasks
- Agent configuration tasks
- Chat API endpoint tasks
- Frontend chat UI tasks
- Integration testing tasks
- Documentation tasks

---

## Implementation Strategy

### Incremental Rollout

1. **Phase 1 (MVP)**: Basic chat with task creation and listing
   - Implement core chat endpoint
   - Add MCP tools for add_task and list_tasks
   - Basic frontend chat UI
   - Test with simple commands

2. **Phase 2**: Complete CRUD operations
   - Add MCP tools for update, delete, complete
   - Enhance agent prompts for better intent recognition
   - Add conversation history UI

3. **Phase 3**: Polish and optimization
   - Add rate limiting
   - Implement conversation retention policy
   - Add error handling and fallbacks
   - Performance optimization

### Testing Strategy

1. **Unit Tests**: Test each MCP tool independently
2. **Integration Tests**: Test agent + MCP tool execution
3. **API Tests**: Test chat endpoint with various inputs
4. **E2E Tests**: Test complete user flows in frontend
5. **Load Tests**: Verify performance under concurrent load

### Rollback Plan

If issues arise:
1. Chat feature is isolated - can be disabled without affecting existing functionality
2. Database migrations are reversible
3. Frontend chat page can be hidden from navigation
4. Rate limiting prevents runaway costs

---

## Risk Mitigation

### Technical Risks

1. **AI Service Dependency**
   - Mitigation: Implement circuit breaker pattern
   - Fallback: Show error message with link to traditional UI
   - Monitoring: Track AI service uptime and latency

2. **Cost Overruns**
   - Mitigation: Strict rate limiting (100 messages/day/user)
   - Monitoring: Track API usage and costs daily
   - Alert: Notify if daily costs exceed threshold

3. **Intent Misinterpretation**
   - Mitigation: Confirmation prompts for destructive operations
   - Logging: Log all agent decisions for review
   - Feedback: Allow users to report misunderstandings

### Security Risks

1. **Prompt Injection**
   - Mitigation: Sanitize user input before sending to agent
   - Validation: Strict parameter validation in MCP tools
   - Monitoring: Log suspicious patterns

2. **Data Leakage**
   - Mitigation: Encrypt conversation history at rest
   - Access Control: Strict user_id validation
   - Audit: Log all conversation access

---

## Success Metrics

Track these metrics to validate implementation:

1. **Adoption**: % of users who try chat feature
2. **Engagement**: Average messages per user per day
3. **Success Rate**: % of messages that successfully complete task operations
4. **Performance**: p95 response time for chat endpoint
5. **Accuracy**: % of correctly interpreted intents (manual review sample)
6. **Cost**: Average AI API cost per user per month

---

## Dependencies & Prerequisites

### External Services
- OpenAI API (for Agents SDK)
- Existing Neon PostgreSQL database
- Existing JWT authentication system

### Internal Dependencies
- Existing task service (for CRUD operations)
- Existing auth service (for JWT validation)
- Existing database connection management

### New Dependencies
- openai-agents-sdk (Python package)
- mcp-python-sdk (Python package)
- dateparser (Python package for date parsing)
- slowapi (Python package for rate limiting)
- @chatscope/chat-ui-kit-react (npm package for chat UI)

---

## Completion Criteria

This plan is complete when:

1. ✅ All research tasks documented in research.md
2. ✅ Data models defined in data-model.md
3. ✅ API contracts specified in contracts/
4. ✅ Quickstart guide created in quickstart.md
5. ✅ Agent context updated with new technologies
6. ✅ Constitution check passes (no violations)
7. ⏳ Ready for `/sp.tasks` command to generate task breakdown

**Next Step**: Run `/sp.tasks` to generate the detailed task breakdown for implementation.
