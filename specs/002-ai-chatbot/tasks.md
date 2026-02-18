# Tasks: AI Chatbot for Task Management

**Input**: Design documents from `/specs/002-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Minimal testing tasks included. Full TDD approach not specified in requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Specs**: `specs/002-ai-chatbot/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install backend Python dependencies: openai>=1.0.0, mcp>=0.1.0, dateparser>=1.1.0, slowapi>=0.1.9, tenacity>=8.0.0, cryptography>=41.0.0 in backend/requirements.txt
- [x] T002 [P] Install frontend npm dependencies: @chatscope/chat-ui-kit-react@^1.10.0, @chatscope/chat-ui-kit-styles@^1.4.0 in frontend/package.json
- [x] T003 [P] Add environment variables to backend/.env: OPENAI_API_KEY, OPENAI_MODEL, MCP_SERVER_PORT, CHAT_RATE_LIMIT, CONVERSATION_RETENTION_DAYS, CONVERSATION_ENCRYPTION_KEY
- [x] T004 [P] Generate Fernet encryption key and add to backend/.env as CONVERSATION_ENCRYPTION_KEY

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models & Migrations

- [x] T005 [P] Create Conversation model in backend/src/models/conversation.py with fields: id (UUID), user_id (FK), created_at, updated_at, last_message_at, meta (JSON)
- [x] T006 [P] Create Message model in backend/src/models/message.py with fields: id (UUID), conversation_id (FK), sender (Enum: user/bot), content (Text), created_at, meta (JSON), parent_message_id (nullable UUID)
- [x] T007 [P] Create RateLimit model in backend/src/models/rate_limit.py with fields: user_id (FK), endpoint (String), count (Integer), reset_at (DateTime), updated_at (DateTime)
- [x] T008 Create Alembic migration for conversations table in backend/alembic/versions/xxx_create_conversations_table.py with indexes on user_id, last_message_at, and composite (user_id, last_message_at)
- [x] T009 Create Alembic migration for messages table in backend/alembic/versions/xxx_create_messages_table.py with message_sender enum type and indexes on conversation_id, created_at, and composite (conversation_id, created_at)
- [x] T010 Create Alembic migration for rate_limits table in backend/alembic/versions/xxx_create_rate_limits_table.py with composite primary key (user_id, endpoint) and index on reset_at
- [x] T011 Run Alembic migrations: alembic upgrade head to create new database tables (Note: Tables will be created automatically via SQLModel.metadata.create_all at app startup)

### MCP Server & Tools

- [x] T012 [P] Create MCP server setup in backend/src/mcp/server.py with tool registration and context injection for user_id
- [x] T013 [P] Implement add_task MCP tool in backend/src/mcp/tools/add_task.py with parameters: title (required), description, due_date, priority, tags
- [x] T014 [P] Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py with filters: completed, due_date, due_before, priority, tags, limit
- [x] T015 [P] Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py with parameters: task_id (required), completed (default: true)
- [x] T016 [P] Implement update_task MCP tool in backend/src/mcp/tools/update_task.py with parameters: task_id (required), title, description, due_date, priority, tags
- [x] T017 [P] Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py with parameter: task_id (required)
- [x] T018 Configure MCP tool error handling and validation in backend/src/mcp/server.py to return structured error responses

### Agent Configuration

- [x] T019 Create OpenAI agent configuration in backend/src/agents/task_agent.py with system prompt for task management intent recognition
- [x] T020 Implement agent initialization with MCP tools registration in backend/src/agents/task_agent.py
- [x] T021 [P] Add natural language date parsing utility using dateparser in backend/src/agents/date_parser.py to convert "tomorrow", "next Friday" to YYYY-MM-DD format
- [x] T022 Configure agent timeout (10 seconds) and error handling with circuit breaker pattern using tenacity in backend/src/agents/task_agent.py

### Services

- [x] T023 [P] Create ConversationService in backend/src/services/conversation_service.py with methods: create_conversation, get_conversation, list_conversations, update_last_message_at
- [x] T024 [P] Create MessageService in backend/src/services/message_service.py with methods: create_message, get_messages, encrypt_content, decrypt_content using Fernet
- [x] T025 Create ChatService in backend/src/services/chat_service.py with methods: process_message, load_conversation_history (last 10 messages), save_conversation, execute_agent
- [x] T026 [P] Implement rate limiting service in backend/src/services/rate_limit_service.py using slowapi with PostgreSQL backend, limit: 100 messages/day/user

### API Infrastructure

- [x] T027 Create chat API router in backend/src/api/chat.py with POST /api/{user_id}/chat endpoint
- [x] T028 Add JWT authentication middleware to chat endpoint in backend/src/api/chat.py to verify token and validate user_id match
- [x] T029 Add rate limiting middleware to chat endpoint in backend/src/api/chat.py using rate_limit_service
- [x] T030 Register chat router in backend/src/main.py


**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing natural language commands to the chatbot instead of filling out forms.

**Independent Test**: Send chat message "remind me to buy groceries tomorrow" and verify a task is created with correct title and due date.

### Implementation for User Story 1

- [x] T031 [US1] Implement chat endpoint request handling in backend/src/api/chat.py to accept message and optional conversation_id
- [x] T032 [US1] Integrate ChatService.process_message in backend/src/api/chat.py to handle user message with agent execution
- [x] T033 [US1] Configure agent to recognize task creation intents ("add task", "remind me", "create task") in backend/src/agents/task_agent.py
- [x] T034 [US1] Connect agent to add_task MCP tool for task creation in backend/src/agents/task_agent.py
- [x] T035 [US1] Implement conversation and message persistence in backend/src/services/chat_service.py after agent response
- [x] T036 [US1] Return chat response with conversation_id, bot message, and task_operation details in backend/src/api/chat.py
- [x] T037 [P] [US1] Create chat page component in frontend/src/app/chat/page.tsx with authentication check
- [x] T038 [P] [US1] Create ChatInterface component in frontend/src/components/chat/chat-interface.tsx using @chatscope/chat-ui-kit-react
- [x] T039 [P] [US1] Create MessageInput component in frontend/src/components/chat/message-input.tsx for user input
- [x] T040 [P] [US1] Create MessageList component in frontend/src/components/chat/message-list.tsx to display conversation history
- [x] T041 [US1] Create chat API client in frontend/src/lib/api/chat-client.ts with sendMessage method calling POST /api/{user_id}/chat
- [x] T042 [US1] Create useChat hook in frontend/src/lib/hooks/use-chat.ts for chat state management (messages, loading, error)
- [x] T043 [US1] Integrate chat API client with ChatInterface component in frontend/src/components/chat/chat-interface.tsx
- [x] T044 [US1] Add task creation confirmation display in chat UI in frontend/src/components/chat/message-list.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language chat

---

## Phase 4: User Story 2 - View and Query Tasks (Priority: P1)

**Goal**: Users can ask the chatbot to show their tasks using natural language queries.

**Independent Test**: Ask "show me my tasks" or "what do I need to do today" and verify the chatbot returns the user's task list.

### Implementation for User Story 2

- [x] T045 [US2] Configure agent to recognize task query intents ("show tasks", "what's due", "list tasks") in backend/src/agents/task_agent.py
- [x] T046 [US2] Connect agent to list_tasks MCP tool for task retrieval in backend/src/agents/task_agent.py
- [x] T047 [US2] Implement natural language filter parsing (e.g., "due today" → due_date filter) in backend/src/agents/task_agent.py
- [x] T048 [US2] Format task list response in natural language in backend/src/agents/task_agent.py
- [x] T049 [US2] Add task list rendering in chat UI in frontend/src/components/chat/message-list.tsx with task details (title, due date, priority)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and view tasks via chat

---

## Phase 5: User Story 6 - Conversation Context (Priority: P2)

**Goal**: The chatbot maintains conversation history so users can have natural back-and-forth interactions.

**Independent Test**: Have multi-turn conversation like "show my tasks" followed by "mark the first one as done" and verify the chatbot understands context.

### Implementation for User Story 6

- [x] T050 [US6] Implement conversation history loading in backend/src/services/chat_service.py to load last 10 messages ordered by created_at
- [x] T051 [US6] Format conversation history for agent context in backend/src/services/chat_service.py with sender labels and timestamps
- [x] T052 [US6] Pass conversation history to agent initialization in backend/src/agents/task_agent.py
- [x] T053 [US6] Configure agent to use conversation context for resolving references ("the first one", "that task") in backend/src/agents/task_agent.py
- [x] T054 [US6] Implement conversation_id persistence in frontend chat state in frontend/src/lib/hooks/use-chat.ts
- [x] T055 [US6] Pass conversation_id in subsequent chat API calls in frontend/src/lib/api/chat-client.ts
- [x] T056 [US6] Add GET /api/{user_id}/conversations endpoint in backend/src/api/chat.py to list user's conversations
- [x] T057 [US6] Add GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in backend/src/api/chat.py to retrieve conversation history

**Checkpoint**: At this point, conversation context should work - users can have multi-turn conversations with context awareness

---

## Phase 6: User Story 3 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can mark tasks as complete through natural language commands.

**Independent Test**: Say "mark 'buy groceries' as done" and verify the task status changes to completed.

### Implementation for User Story 3

- [x] T058 [US3] Configure agent to recognize task completion intents ("mark done", "complete task", "finish") in backend/src/agents/task_agent.py
- [x] T059 [US3] Connect agent to complete_task MCP tool in backend/src/agents/task_agent.py
- [x] T060 [US3] Implement task identification from natural language (by title or position in list) in backend/src/agents/task_agent.py
- [x] T061 [US3] Add completion confirmation message in agent response in backend/src/agents/task_agent.py

**Checkpoint**: At this point, User Stories 1, 2, 3, and 6 should all work - users can create, view, complete tasks with context

---

## Phase 7: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Users can modify existing tasks through natural language commands.

**Independent Test**: Say "change the due date of 'project report' to next Monday" and verify the task is updated.

### Implementation for User Story 4

- [x] T062 [US4] Configure agent to recognize task update intents ("change", "update", "modify", "rename") in backend/src/agents/task_agent.py
- [x] T063 [US4] Connect agent to update_task MCP tool in backend/src/agents/task_agent.py
- [x] T064 [US4] Implement field-specific update parsing (due date, priority, title) in backend/src/agents/task_agent.py
- [x] T065 [US4] Add update confirmation message with changed fields in agent response in backend/src/agents/task_agent.py

**Checkpoint**: At this point, User Stories 1-4 and 6 should all work - full task management except deletion

---

## Phase 8: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Users can delete tasks through natural language commands.

**Independent Test**: Say "delete task 'old reminder'" and verify the task is removed.

### Implementation for User Story 5

- [x] T066 [US5] Configure agent to recognize task deletion intents ("delete", "remove", "get rid of") in backend/src/agents/task_agent.py
- [x] T067 [US5] Connect agent to delete_task MCP tool in backend/src/agents/task_agent.py
- [x] T068 [US5] Implement deletion confirmation prompt before executing delete in backend/src/agents/task_agent.py
- [x] T069 [US5] Add deletion confirmation message in agent response in backend/src/agents/task_agent.py

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations via chat

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling

- [x] T070 [P] Implement AI service timeout handling (10s) with circuit breaker in backend/src/agents/task_agent.py
- [x] T071 [P] Add graceful error messages for AI service failures in backend/src/api/chat.py with fallback message
- [x] T072 [P] Implement error handling for invalid task operations in backend/src/mcp/tools/ with user-friendly error messages
- [x] T073 [P] Add frontend error display in chat UI in frontend/src/components/chat/chat-interface.tsx

### Data Management

- [x] T074 [P] Implement conversation archival background task in backend/src/services/conversation_service.py for conversations inactive >30 days
- [x] T075 [P] Implement rate limit cleanup background task in backend/src/services/rate_limit_service.py for expired rate limit records
- [x] T076 [P] Add message content encryption/decryption in MessageService in backend/src/services/message_service.py using Fernet

### Testing & Validation

- [ ] T077 [P] Create integration test for chat endpoint in backend/tests/test_chat_api.py testing task creation flow
- [ ] T078 [P] Create unit tests for MCP tools in backend/tests/test_mcp_tools.py testing all 5 tools
- [ ] T079 [P] Create unit tests for agent configuration in backend/tests/test_agent.py testing intent recognition
- [ ] T080 [P] Create frontend tests for ChatInterface in frontend/tests/chat-interface.test.tsx
- [x] T081 Validate full chat workflow per quickstart.md: login → chat → create task → list tasks → complete task

### Documentation & Performance

- [x] T082 [P] Add API documentation for chat endpoints in backend/src/api/chat.py with OpenAPI annotations
- [x] T083 [P] Add logging for chat operations in backend/src/services/chat_service.py with user_id, conversation_id, intent
- [x] T084 [P] Optimize conversation history query performance in backend/src/services/conversation_service.py with proper indexes
- [x] T085 [P] Add chat navigation link in frontend header in frontend/src/components/ui/header.tsx

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Benefits from US2 (list tasks) for context but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Benefits from US2 (list tasks) for context but independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Benefits from US2 (list tasks) for context but independently testable

### Within Each User Story

- Backend implementation before frontend integration
- Services before API endpoints
- Core implementation before UI enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T001, T002, T003, T004 can all run in parallel
- **Phase 2**:
  - T005, T006, T007 (models) can run in parallel
  - T013, T014, T015, T016, T017 (MCP tools) can run in parallel
  - T023, T024, T026 (services) can run in parallel
  - T037, T038, T039, T040 (frontend components) can run in parallel
- **Phase 3 (US1)**: T037, T038, T039, T040 (frontend components) can run in parallel
- **Phase 9**: T070, T071, T072, T073 (error handling) can run in parallel; T077, T078, T079, T080 (tests) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all database models together:
Task: "Create Conversation model in backend/src/models/conversation.py"
Task: "Create Message model in backend/src/models/message.py"
Task: "Create RateLimit model in backend/src/models/rate_limit.py"

# Launch all MCP tools together:
Task: "Implement add_task MCP tool in backend/src/mcp/tools/add_task.py"
Task: "Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py"
Task: "Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py"
Task: "Implement update_task MCP tool in backend/src/mcp/tools/update_task.py"
Task: "Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Natural Language Task Creation)
4. Complete Phase 4: User Story 2 (View and Query Tasks)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready

**MVP Delivers**: Users can create and view tasks via natural language chat - core value proposition

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 6 → Test independently → Deploy/Demo (Context awareness)
4. Add User Story 3 → Test independently → Deploy/Demo (Task completion)
5. Add User Story 4 + 5 → Test independently → Deploy/Demo (Full CRUD)
6. Add Phase 9 → Polish and optimize → Final Deploy

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Task Creation)
   - Developer B: User Story 2 (View Tasks)
   - Developer C: User Story 6 (Conversation Context)
3. Stories complete and integrate independently
4. Continue with remaining stories in priority order

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow quickstart.md for setup and testing procedures
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
