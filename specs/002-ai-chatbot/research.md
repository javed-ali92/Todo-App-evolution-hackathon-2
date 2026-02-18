# Research & Technology Decisions: AI Chatbot

**Feature**: AI Chatbot for Task Management
**Branch**: 002-ai-chatbot
**Date**: 2026-02-13

This document captures all technology research and decisions made during the planning phase.

---

## 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK with FastAPI via async/await pattern

**Rationale**:
- OpenAI Agents SDK provides built-in tool calling and conversation management
- Native async support integrates well with FastAPI's async endpoints
- Handles retry logic and error handling automatically
- Supports streaming responses for better UX (future enhancement)

**Alternatives Considered**:
- **LangChain**: More complex, heavier dependency, overkill for our use case
- **Direct OpenAI API calls**: Would require manual tool calling implementation and conversation management
- **Anthropic Claude**: Excellent but adds vendor lock-in; OpenAI has better MCP integration

**Implementation Notes**:
- Use `openai.AsyncOpenAI` client for non-blocking operations
- Configure agent with system prompt defining task management capabilities
- Set timeout to 10 seconds to prevent hanging requests
- Use environment variables for API key and model selection

**Dependencies**:
- `openai>=1.0.0` (Python package)
- Environment variables: `OPENAI_API_KEY`, `OPENAI_MODEL`

---

## 2. MCP (Model Context Protocol) Implementation

**Decision**: Use MCP Python SDK with custom tool implementations

**Rationale**:
- MCP provides standardized interface between AI agents and tools
- Allows agent to discover and call tools dynamically
- Type-safe parameter validation
- Easy to extend with new tools in the future

**Alternatives Considered**:
- **Function calling without MCP**: Less structured, harder to maintain
- **Custom tool protocol**: Reinventing the wheel, no ecosystem benefits
- **LangChain tools**: Tied to LangChain framework

**Implementation Notes**:
- Each MCP tool wraps existing task service methods
- Tools validate parameters before calling service layer
- Tools return structured responses (success/failure + data)
- User context (user_id) passed through tool execution context

**Dependencies**:
- `mcp>=0.1.0` (Python package)
- Custom tool implementations in `backend/src/mcp/tools/`

---

## 3. Natural Language Date Parsing

**Decision**: Use `dateparser` library with custom relative date handling

**Rationale**:
- `dateparser` handles wide variety of date formats ("tomorrow", "next Friday", "in 2 days")
- Supports multiple languages (future-proofing)
- Active maintenance and good documentation
- Handles timezone awareness

**Alternatives Considered**:
- **python-dateutil**: Good but less flexible with natural language
- **Custom regex parsing**: Error-prone, hard to maintain
- **Let AI handle it**: Inconsistent, wastes tokens

**Implementation Notes**:
- Configure dateparser with settings: `{'PREFER_DATES_FROM': 'future'}`
- Default to user's timezone (from JWT or system default)
- Validate parsed dates are not in the past for due dates
- Return ISO format dates to database

**Dependencies**:
- `dateparser>=1.1.0` (Python package)

---

## 4. Conversation State Management

**Decision**: Load last 10 messages per conversation, implement pagination for history view

**Rationale**:
- 10 messages provides sufficient context for most conversations
- Keeps token usage reasonable (avg 100 tokens/message = 1000 tokens context)
- Pagination allows users to view full history without loading everything
- Stateless server design - all state in database

**Alternatives Considered**:
- **Load all messages**: Expensive, slow, high token usage
- **Load last 5 messages**: Too little context for complex conversations
- **Sliding window**: More complex, marginal benefit

**Implementation Notes**:
- Query: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 10`
- Reverse order before sending to agent (oldest first)
- Cache conversation metadata (user_id, created_at) to avoid repeated queries
- Implement separate endpoint for full history pagination

**Dependencies**:
- SQLModel queries with proper indexing

---

## 5. Rate Limiting Implementation

**Decision**: Use `slowapi` with PostgreSQL backend for rate limit storage

**Rationale**:
- `slowapi` integrates seamlessly with FastAPI
- PostgreSQL backend avoids Redis dependency
- Per-user limits stored in database (100 messages/day)
- Supports different limits for different endpoints

**Alternatives Considered**:
- **fastapi-limiter with Redis**: Adds Redis dependency, operational complexity
- **Custom middleware**: Reinventing the wheel
- **No rate limiting**: Risk of abuse and cost overruns

**Implementation Notes**:
- Decorator: `@limiter.limit("100/day", key_func=get_user_id_from_token)`
- Store rate limit data in `rate_limits` table with user_id, endpoint, count, reset_at
- Clean up expired rate limit records daily (background task)
- Return 429 status with Retry-After header

**Dependencies**:
- `slowapi>=0.1.9` (Python package)
- New database table: `rate_limits`

---

## 6. Frontend Chat UI Library

**Decision**: Use `@chatscope/chat-ui-kit-react` for chat components

**Rationale**:
- Pre-built accessible chat components (message bubbles, input, list)
- TypeScript support
- Customizable styling
- Active maintenance
- Handles common chat UX patterns (scrolling, timestamps, sender identification)

**Alternatives Considered**:
- **react-chat-elements**: Less polished, fewer features
- **Custom components**: Time-consuming, accessibility concerns
- **stream-chat-react**: Overkill, designed for real-time streaming

**Implementation Notes**:
- Install: `npm install @chatscope/chat-ui-kit-react @chatscope/chat-ui-kit-styles`
- Components: `MainContainer`, `ChatContainer`, `MessageList`, `Message`, `MessageInput`
- Customize colors to match existing app theme
- Add loading states for AI responses
- Implement auto-scroll to latest message

**Dependencies**:
- `@chatscope/chat-ui-kit-react>=1.10.0` (npm package)
- `@chatscope/chat-ui-kit-styles>=1.4.0` (npm package)

---

## 7. AI Service Error Handling

**Decision**: Implement circuit breaker pattern with graceful degradation

**Rationale**:
- Prevents cascading failures when OpenAI API is down
- Provides clear user feedback
- Allows system to recover automatically
- Protects against rate limits and timeouts

**Alternatives Considered**:
- **Simple retry**: Can make problems worse during outages
- **No error handling**: Poor user experience
- **Queue-based**: Adds complexity, not needed for synchronous chat

**Implementation Notes**:
- Use `tenacity` library for retry logic with exponential backoff
- Circuit breaker states: Closed (normal) → Open (failing) → Half-Open (testing)
- After 3 consecutive failures, open circuit for 60 seconds
- Return user-friendly error: "AI service is temporarily unavailable. Please try again or use the task dashboard."
- Log all failures for monitoring

**Dependencies**:
- `tenacity>=8.0.0` (Python package for retry logic)

---

## 8. Conversation History Encryption

**Decision**: Use `cryptography` library with Fernet symmetric encryption for message content

**Rationale**:
- Fernet provides authenticated encryption (prevents tampering)
- Simple API, hard to misuse
- Reasonable performance impact (<10ms per message)
- Meets privacy requirements for sensitive task data

**Alternatives Considered**:
- **No encryption**: Privacy risk, not acceptable for task data
- **Database-level encryption**: Doesn't protect against SQL injection or admin access
- **Asymmetric encryption**: Overkill, key management complexity

**Implementation Notes**:
- Generate encryption key from environment variable: `CONVERSATION_ENCRYPTION_KEY`
- Encrypt message content before storing in database
- Decrypt when loading conversation history
- Store encrypted data as TEXT field in database
- Key rotation strategy: Generate new key, re-encrypt old messages (future enhancement)

**Dependencies**:
- `cryptography>=41.0.0` (Python package)
- Environment variable: `CONVERSATION_ENCRYPTION_KEY` (32-byte base64-encoded key)

---

## Summary of Technology Stack

### Backend Dependencies
```
openai>=1.0.0
mcp>=0.1.0
dateparser>=1.1.0
slowapi>=0.1.9
tenacity>=8.0.0
cryptography>=41.0.0
```

### Frontend Dependencies
```
@chatscope/chat-ui-kit-react>=1.10.0
@chatscope/chat-ui-kit-styles>=1.4.0
```

### Environment Variables
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
MCP_SERVER_PORT=8001
CHAT_RATE_LIMIT=100
CONVERSATION_RETENTION_DAYS=30
CONVERSATION_ENCRYPTION_KEY=<base64-encoded-32-byte-key>
```

### Database Tables
- `conversations` (id, user_id, created_at, updated_at, last_message_at, metadata)
- `messages` (id, conversation_id, sender, content_encrypted, created_at, metadata)
- `rate_limits` (user_id, endpoint, count, reset_at)

---

## Open Questions Resolved

1. **Which AI service?** → OpenAI (best MCP integration, proven reliability)
2. **How much conversation history?** → Last 10 messages (balance context vs cost)
3. **Rate limiting backend?** → PostgreSQL (avoid Redis dependency)
4. **Encryption approach?** → Fernet symmetric encryption (simple, secure)
5. **Frontend UI library?** → @chatscope/chat-ui-kit-react (feature-rich, accessible)

---

## Next Steps

1. Create database models (data-model.md)
2. Define API contracts (contracts/)
3. Write quickstart guide (quickstart.md)
4. Update agent context with new technologies
5. Generate task breakdown (/sp.tasks)
