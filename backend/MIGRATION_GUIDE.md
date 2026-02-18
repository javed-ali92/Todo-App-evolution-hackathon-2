"""
Migration guide: OpenAI Chat Completions → OpenAI Agents SDK

This document outlines the migration from manual OpenAI chat completions
to the official OpenAI Agents SDK.
"""

# MIGRATION GUIDE: OpenAI Agents SDK

## Overview

This migration moves from manual OpenAI chat completions API to the official
OpenAI Agents SDK, providing:

- **Agent/Runner/Session primitives**: Structured agent architecture
- **Native tool integration**: Automatic schema generation from Python functions
- **Persistent sessions**: Conversation memory managed by SDK
- **Improved error handling**: Built-in retry and error management
- **Better observability**: Structured logging and tracing

## Architecture Changes

### Before (Manual Implementation)
```
User Request → ChatService → TaskAgent → OpenAI Chat Completions API
                                       ↓
                                  Tool Execution (MCP Server)
                                       ↓
                                  Response Generation
```

### After (SDK Implementation)
```
User Request → ChatServiceSDK → SDKTaskAgent → Agent/Runner/Session
                                              ↓
                                         Tool Execution (Wrapped)
                                              ↓
                                         Session State Update
                                              ↓
                                         Response Generation
```

## Key Components

### 1. SDKTaskAgent (backend/src/agents/sdk_agent.py)

**Purpose**: Wraps OpenAI Agents SDK with multi-tenant security

**Key Features**:
- `UserContextManager`: Thread-local storage for user_id injection
- `inject_user_context`: Decorator for automatic user_id injection
- `Agent`: SDK agent with instructions and tools
- `Session`: Persistent conversation memory
- `Runner`: Executes agent with session context

**User Context Injection Pattern**:
```python
# Before tool execution
UserContextManager.set_user_id(user_id)

# Tool wrapper automatically injects user_id
@inject_user_context
def add_task(title: str, user_id: int = None, ...):
    # user_id is automatically injected
    pass

# After execution
UserContextManager.clear()
```

### 2. ChatServiceSDK (backend/src/services/chat_service_sdk.py)

**Purpose**: Orchestrates SDK agent execution with PostgreSQL persistence

**Key Features**:
- Session state persistence in `conversation.meta["sdk_session"]`
- PostgreSQL remains source of truth for message history
- Dual-layer memory: SDK Session (ephemeral) + PostgreSQL (durable)

**Session Persistence Flow**:
```python
# 1. Load session state from conversation.meta
session_state = conversation.meta.get("sdk_session")

# 2. Restore SDK session
session = restore_session(session_state)

# 3. Execute agent
result = Runner.run_sync(agent, session, message)

# 4. Serialize updated session
updated_state = serialize_session(session)

# 5. Persist to conversation.meta
conversation.meta["sdk_session"] = updated_state
```

## Migration Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements_sdk.txt
```

### Step 2: Update Environment Variables

No new environment variables required. Existing variables work:
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: Model name (default: gpt-4-turbo-preview)
- `CONVERSATION_ENCRYPTION_KEY`: Message encryption key

### Step 3: Update API Routes (Optional - Gradual Migration)

**Option A: Gradual Migration (Recommended)**

Create new endpoint for SDK-based chat:
```python
# backend/src/api/chat.py

from ..services.chat_service_sdk import ChatServiceSDK

@router.post("/api/{user_id}/chat/sdk")
async def send_chat_message_sdk(
    user_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    # Use ChatServiceSDK instead of ChatService
    chat_service = ChatServiceSDK(session)
    # ... rest of implementation
```

**Option B: Full Migration**

Replace ChatService with ChatServiceSDK in existing endpoint:
```python
# backend/src/api/chat.py

# Change import
from ..services.chat_service_sdk import ChatServiceSDK

# Update endpoint
@router.post("/api/{user_id}/chat")
async def send_chat_message(...):
    chat_service = ChatServiceSDK(session)  # Changed
    # ... rest stays the same
```

### Step 4: Update Main Application

```python
# backend/src/main.py

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    # Initialize MCP tools (still needed for tool functions)
    from .mcp.server import initialize_mcp_tools
    initialize_mcp_tools()
    logger.info("MCP tools initialized")

    # Optionally: Validate SDK agent initialization
    from .agents.sdk_agent import SDKTaskAgent
    from .mcp.server import mcp_server
    try:
        test_agent = SDKTaskAgent(mcp_server)
        logger.info("SDK agent initialized successfully")
    except Exception as e:
        logger.error(f"SDK agent initialization failed: {e}")
```

### Step 5: Database Migration (No Schema Changes Required)

The `conversation.meta` field already exists as JSONB, so no schema changes needed.
Session state is stored as:
```json
{
  "sdk_session": {
    "messages": [...],
    "context": {...},
    "metadata": {...},
    "version": "1.0"
  },
  "sdk_session_updated_at": "2026-02-15T10:30:00Z"
}
```

## Testing Strategy

### Unit Tests

```python
# tests/test_sdk_agent.py

def test_user_context_injection():
    """Test that user_id is properly injected into tool calls."""
    from backend.src.agents.sdk_agent import UserContextManager, inject_user_context

    @inject_user_context
    def test_tool(title: str, user_id: int = None):
        return {"user_id": user_id, "title": title}

    UserContextManager.set_user_id(123)
    result = test_tool(title="Test")
    assert result["user_id"] == 123
    UserContextManager.clear()

def test_session_persistence():
    """Test that session state is properly serialized/deserialized."""
    agent = SDKTaskAgent(mcp_server)

    # First message
    result1 = agent.process_message(
        user_id=1,
        message="Add task: Buy groceries",
        session_state=None
    )
    session_state = result1["session_state"]

    # Second message with session
    result2 = agent.process_message(
        user_id=1,
        message="What tasks do I have?",
        session_state=session_state
    )

    # Should remember context
    assert "groceries" in result2["message"].lower()
```

### Integration Tests

```python
# tests/test_chat_service_sdk.py

def test_conversation_persistence():
    """Test that conversations persist across requests."""
    service = ChatServiceSDK(session)

    # First message
    result1 = service.process_message(
        user_id=1,
        message="Add task: Buy milk"
    )
    conv_id = uuid.UUID(result1["conversation_id"])

    # Second message in same conversation
    result2 = service.process_message(
        user_id=1,
        message="List my tasks",
        conversation_id=conv_id
    )

    # Verify session state was persisted
    conversation = service.conversation_service.get_conversation(conv_id, 1)
    assert "sdk_session" in conversation.meta
```

## Rollback Strategy

If issues arise, rollback is simple:

1. **Revert API routes** to use original `ChatService`
2. **No database changes** needed (meta field is backward compatible)
3. **Keep both implementations** during transition period

```python
# Rollback: Change one line in chat.py
from ..services.chat_service import ChatService  # Original
# from ..services.chat_service_sdk import ChatServiceSDK  # SDK version
```

## Performance Considerations

### Memory Usage
- SDK Sessions add ~5-10KB per conversation in `conversation.meta`
- PostgreSQL message history remains primary storage
- Consider archiving old session states after 30 days

### Latency
- SDK adds ~50-100ms overhead for session management
- Tool execution time unchanged
- Overall latency similar to manual implementation

### Scalability
- Session state is per-conversation, not per-user
- Stateless design: each request is independent
- Horizontal scaling supported

## Monitoring and Observability

### Key Metrics to Track

1. **Session State Size**: Monitor `conversation.meta` size
2. **Tool Execution Success Rate**: Track tool call failures
3. **Session Restoration Failures**: Alert on deserialization errors
4. **User Context Injection Failures**: Critical security metric

### Logging

```python
# Key log points
logger.info(f"Restored SDK session state for conversation {conv_id}")
logger.info(f"Updated SDK session state for conversation {conv_id}")
logger.error(f"Failed to restore session: {error}")
logger.warning(f"User context not set during tool execution")
```

## Security Considerations

### Multi-Tenant Isolation

The `UserContextManager` ensures user_id is injected into every tool call:

```python
# CRITICAL: User context must be set before tool execution
UserContextManager.set_user_id(user_id)

# Tools automatically receive user_id
@inject_user_context
def list_tasks(user_id: int, ...):
    # user_id is guaranteed to match authenticated user
    pass

# CRITICAL: Clear context after execution
UserContextManager.clear()
```

### Session State Security

- Session state stored in encrypted database (PostgreSQL)
- No sensitive data in session state (only conversation context)
- User ownership verified before session restoration

## Troubleshooting

### Issue: "User context not set"
**Cause**: UserContextManager.set_user_id() not called before tool execution
**Fix**: Ensure set_user_id() is called in process_message()

### Issue: Session restoration fails
**Cause**: Session state format changed or corrupted
**Fix**: Implement version checking in _restore_session()

### Issue: Tool calls fail with SDK
**Cause**: Tool function signatures incompatible with SDK
**Fix**: Ensure all tools have proper type hints and return Dict[str, Any]

## Next Steps

1. **Deploy to staging** with gradual rollout
2. **Monitor metrics** for 24-48 hours
3. **A/B test** SDK vs manual implementation
4. **Full migration** after validation
5. **Remove old implementation** after 30 days

## Support

For issues or questions:
- Check SDK documentation: https://openai.github.io/openai-agents-python/
- Review implementation: `backend/src/agents/sdk_agent.py`
- Contact: [Your team contact]
