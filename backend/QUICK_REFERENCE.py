"""
Quick Reference: OpenAI Agents SDK Integration
Essential patterns and code snippets for daily development.
"""

# ============================================================================
# QUICK REFERENCE: OpenAI Agents SDK Integration
# ============================================================================

# ----------------------------------------------------------------------------
# 1. BASIC AGENT SETUP
# ----------------------------------------------------------------------------

from openai_agents import Agent, Runner, Session
from openai import OpenAI

# Create agent with instructions and tools
agent = Agent(
    name="TaskManagementAgent",
    instructions="You are a helpful task management assistant...",
    model="gpt-4-turbo-preview",
    tools=[add_task, list_tasks, complete_task, update_task, delete_task]
)

# ----------------------------------------------------------------------------
# 2. TOOL DEFINITION (SDK Auto-generates Schema)
# ----------------------------------------------------------------------------

def add_task(
    title: str,
    description: str = None,
    due_date: str = None,
    priority: str = "Medium",
    user_id: int = None  # Injected by decorator
) -> dict:
    """
    Create a new task for the user.

    Args:
        title: Task title (required)
        description: Optional task description
        due_date: Optional due date in YYYY-MM-DD format
        priority: Task priority (Low, Medium, High)
        user_id: User ID (automatically injected)

    Returns:
        Dictionary with success status and task data
    """
    # Implementation...
    return {"success": True, "task": {...}}

# SDK automatically generates schema from:
# - Function signature (parameters)
# - Type hints (parameter types)
# - Docstring (descriptions)

# ----------------------------------------------------------------------------
# 3. USER CONTEXT INJECTION (Multi-tenant Security)
# ----------------------------------------------------------------------------

from backend.src.agents.sdk_agent import UserContextManager, inject_user_context

# Wrap tools with user context injection
@inject_user_context
def add_task(title: str, user_id: int = None, ...):
    # user_id is automatically injected from UserContextManager
    pass

# In your service/API layer:
def process_message(user_id: int, message: str):
    # Set user context before agent execution
    UserContextManager.set_user_id(user_id)

    try:
        result = Runner.run_sync(agent, session, message)
    finally:
        # Always clear context after execution
        UserContextManager.clear()

# ----------------------------------------------------------------------------
# 4. SESSION MANAGEMENT (Conversation Memory)
# ----------------------------------------------------------------------------

# Create new session
session = Session()

# Execute agent with session
result = Runner.run_sync(
    agent=agent,
    session=session,
    message="Add task to buy groceries"
)

# Serialize session for persistence
session_state = {
    "messages": session.messages,
    "context": session.context,
    "metadata": session.metadata,
    "version": "1.0"
}

# Store in database
conversation.meta["sdk_session"] = session_state

# Restore session from database
session = Session()
session.messages = session_state["messages"]
session.context = session_state["context"]
session.metadata = session_state["metadata"]

# ----------------------------------------------------------------------------
# 5. COMPLETE REQUEST FLOW
# ----------------------------------------------------------------------------

def process_chat_message(user_id: int, message: str, conversation_id: UUID):
    """Complete flow for processing a chat message with SDK."""

    # 1. Load conversation from database
    conversation = get_conversation(conversation_id, user_id)

    # 2. Restore session state
    session_state = conversation.meta.get("sdk_session")
    if session_state:
        session = restore_session(session_state)
    else:
        session = Session()

    # 3. Set user context for security
    UserContextManager.set_user_id(user_id)

    try:
        # 4. Execute agent
        result = Runner.run_sync(
            agent=agent,
            session=session,
            message=message
        )

        # 5. Extract response
        bot_message = result.get("message")
        tool_operations = result.get("tool_calls")

        # 6. Save messages to database
        save_message(conversation_id, "user", message)
        save_message(conversation_id, "bot", bot_message)

        # 7. Update session state
        updated_state = serialize_session(session)
        conversation.meta["sdk_session"] = updated_state
        save_conversation(conversation)

        return {
            "message": bot_message,
            "tool_operations": tool_operations
        }

    finally:
        # 8. Always clear user context
        UserContextManager.clear()

# ----------------------------------------------------------------------------
# 6. ERROR HANDLING
# ----------------------------------------------------------------------------

try:
    result = Runner.run_sync(agent, session, message)
except Exception as e:
    logger.error(f"Agent execution failed: {e}")
    return {
        "message": "I'm having trouble processing your request.",
        "error": str(e),
        "success": False
    }

# ----------------------------------------------------------------------------
# 7. TESTING PATTERNS
# ----------------------------------------------------------------------------

# Test user context injection
def test_user_context():
    UserContextManager.set_user_id(123)

    @inject_user_context
    def test_tool(user_id: int = None):
        return user_id

    assert test_tool() == 123
    UserContextManager.clear()

# Test session persistence
def test_session_persistence():
    agent = SDKTaskAgent(mcp_server)

    # First message
    result1 = agent.process_message(1, "Add task: Buy milk", None)
    session_state = result1["session_state"]

    # Second message with session
    result2 = agent.process_message(1, "List tasks", session_state)

    # Should remember context
    assert "milk" in result2["message"].lower()

# ----------------------------------------------------------------------------
# 8. COMMON PATTERNS
# ----------------------------------------------------------------------------

# Pattern 1: New conversation
result = agent.process_message(
    user_id=1,
    message="Add task to buy groceries",
    session_state=None  # No existing session
)

# Pattern 2: Continuing conversation
result = agent.process_message(
    user_id=1,
    message="What tasks do I have?",
    session_state=previous_session_state  # Restore context
)

# Pattern 3: Multi-turn with context
session_state = None
for user_message in ["Add task: X", "Add task: Y", "List all tasks"]:
    result = agent.process_message(1, user_message, session_state)
    session_state = result["session_state"]  # Update for next turn

# ----------------------------------------------------------------------------
# 9. DATABASE SCHEMA
# ----------------------------------------------------------------------------

# conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_message_at TIMESTAMP NOT NULL,
    meta JSONB  -- Stores SDK session state
);

# Example meta field content:
{
    "sdk_session": {
        "messages": [...],
        "context": {...},
        "metadata": {...},
        "version": "1.0"
    },
    "sdk_session_updated_at": "2026-02-15T10:30:00Z"
}

# ----------------------------------------------------------------------------
# 10. ENVIRONMENT VARIABLES
# ----------------------------------------------------------------------------

# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
CONVERSATION_ENCRYPTION_KEY=...  # For message encryption

# Optional
OPENAI_MODEL=gpt-4-turbo-preview  # Default model
CONVERSATION_RETENTION_DAYS=30    # Session cleanup

# ----------------------------------------------------------------------------
# 11. DEPLOYMENT CHECKLIST
# ----------------------------------------------------------------------------

# [ ] Install dependencies: pip install openai-agents>=0.1.0
# [ ] Update main.py to include SDK router
# [ ] Set environment variables
# [ ] Run database migrations (if any)
# [ ] Run unit tests: pytest tests/test_sdk_integration.py
# [ ] Test SDK endpoint manually
# [ ] Deploy to staging
# [ ] Monitor metrics (latency, errors, session size)
# [ ] Gradual rollout to production
# [ ] Full migration after validation

# ----------------------------------------------------------------------------
# 12. MONITORING
# ----------------------------------------------------------------------------

# Key metrics to track:
# - Session state size (conversation.meta)
# - Tool execution success rate
# - Session restoration failures
# - User context injection failures
# - Average response latency
# - Memory usage per conversation

# Logging examples:
logger.info(f"Restored SDK session for conversation {conv_id}")
logger.info(f"Updated SDK session state (size: {len(str(state))} bytes)")
logger.error(f"Failed to restore session: {error}")
logger.warning(f"User context not set during tool execution")

# ----------------------------------------------------------------------------
# 13. TROUBLESHOOTING
# ----------------------------------------------------------------------------

# Issue: "User context not set"
# Fix: Ensure UserContextManager.set_user_id() called before agent execution

# Issue: Session restoration fails
# Fix: Check session_state format and version compatibility

# Issue: Tool calls fail
# Fix: Verify tool function signatures have proper type hints

# Issue: High memory usage
# Fix: Implement session state cleanup for old conversations

# ----------------------------------------------------------------------------
# 14. MIGRATION STRATEGY
# ----------------------------------------------------------------------------

# Phase 1: Parallel deployment (Week 1-2)
# - Deploy SDK endpoint: /api/{user_id}/chat/sdk
# - Keep existing endpoint: /api/{user_id}/chat
# - Route 10% traffic to SDK

# Phase 2: Validation (Week 3-4)
# - Monitor metrics and errors
# - Compare user satisfaction
# - Route 50% traffic to SDK

# Phase 3: Full migration (Week 5+)
# - Route 100% traffic to SDK
# - Deprecate old endpoint
# - Remove old implementation after 30 days

# ----------------------------------------------------------------------------
# 15. USEFUL COMMANDS
# ----------------------------------------------------------------------------

# Run tests
pytest tests/test_sdk_integration.py -v

# Run examples
python examples/sdk_usage_example.py

# Start server
uvicorn src.main:app --reload

# Test SDK endpoint
curl -X POST "http://localhost:8000/api/1/chat/sdk" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy groceries"}'

# Check SDK health
curl "http://localhost:8000/api/1/chat/sdk/health" \
  -H "Authorization: Bearer TOKEN"
