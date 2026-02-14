# AI Chatbot Quickstart Guide

**Feature**: AI Chatbot for Task Management
**Branch**: 002-ai-chatbot
**Date**: 2026-02-13

This guide helps developers set up and test the AI chatbot feature locally.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Existing Todo App backend running (FastAPI + Neon PostgreSQL)
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed (for frontend)
- ✅ OpenAI API key (sign up at https://platform.openai.com)
- ✅ Git repository cloned and on branch `002-ai-chatbot`

---

## Backend Setup

### Step 1: Install Python Dependencies

```bash
cd Todo_App_Backend

# Install new dependencies for chatbot
pip install openai>=1.0.0
pip install mcp>=0.1.0
pip install dateparser>=1.1.0
pip install slowapi>=0.1.9
pip install tenacity>=8.0.0
pip install cryptography>=41.0.0

# Or install all at once
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Add these variables to `Todo_App_Backend/.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4-turbo-preview  # Or gpt-4, gpt-3.5-turbo

# MCP Server Configuration
MCP_SERVER_PORT=8001

# Rate Limiting
CHAT_RATE_LIMIT=100  # Messages per day per user

# Data Retention
CONVERSATION_RETENTION_DAYS=30

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
CONVERSATION_ENCRYPTION_KEY=<your-32-byte-base64-key>
```

**Generate Encryption Key:**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and set it as `CONVERSATION_ENCRYPTION_KEY`.

### Step 3: Create Database Tables

Run Alembic migrations to create new tables:

```bash
cd Todo_App_Backend

# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables for chatbot"

# Review the generated migration file in alembic/versions/
# Make sure it creates: conversations, messages, rate_limits tables

# Apply migration
alembic upgrade head
```

**Verify Tables Created:**

```bash
# Connect to your Neon database and verify tables exist
psql $DATABASE_URL -c "\dt"

# Should show:
# - conversations
# - messages
# - rate_limits
```

### Step 4: Verify Backend Imports

Test that all new modules can be imported:

```bash
cd Todo_App_Backend

python -c "
from src.models.conversation import Conversation
from src.models.message import Message
from src.services.chat_service import ChatService
from src.mcp.server import MCPServer
from src.agents.task_agent import TaskAgent
print('✓ All imports successful')
"
```

If you see import errors, the implementation phase hasn't started yet. This is expected during planning.

### Step 5: Start Backend Server

```bash
cd Todo_App_Backend

# Development mode with auto-reload
uvicorn src.main:app --reload --port 7860

# Or use the run script
python run_server.py
```

**Verify Backend Running:**

```bash
# Health check
curl http://localhost:7860/health

# Should return: {"status":"ok","database":"connected"}
```

---

## Frontend Setup

### Step 1: Install npm Dependencies

```bash
cd frontend

# Install chat UI library
npm install @chatscope/chat-ui-kit-react@^1.10.0
npm install @chatscope/chat-ui-kit-styles@^1.4.0
```

### Step 2: Verify Frontend Environment

Check that `frontend/.env.local` points to the correct backend:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:7860
```

### Step 3: Start Frontend Development Server

```bash
cd frontend

npm run dev
```

Frontend will be available at: http://localhost:3000

### Step 4: Access Chat Interface

Navigate to: http://localhost:3000/chat

You should see the chat interface (once implemented).

---

## Testing the Chatbot

### Manual Testing

1. **Login to the application**
   - Go to http://localhost:3000/login
   - Login with existing credentials or create new account

2. **Navigate to Chat**
   - Go to http://localhost:3000/chat
   - You should see a chat interface

3. **Test Natural Language Commands**

   **Create Tasks:**
   ```
   User: "add task: buy groceries tomorrow"
   Bot: "I've created a task 'buy groceries' with due date Feb 14."

   User: "remind me to call mom"
   Bot: "I've created a task 'call mom'."

   User: "create high priority task: finish report by Friday"
   Bot: "I've created a high priority task 'finish report' due Friday, Feb 16."
   ```

   **List Tasks:**
   ```
   User: "show me my tasks"
   Bot: "You have 3 tasks: 1) Buy groceries (due tomorrow), 2) Call mom, 3) Finish report (due Friday)"

   User: "what's due today?"
   Bot: "You have no tasks due today."
   ```

   **Complete Tasks:**
   ```
   User: "mark 'buy groceries' as done"
   Bot: "I've marked 'buy groceries' as complete."

   User: "complete task #1"
   Bot: "I've marked task #1 as complete."
   ```

   **Update Tasks:**
   ```
   User: "change the due date of 'finish report' to next Monday"
   Bot: "I've updated the due date to Feb 19."

   User: "make 'call mom' high priority"
   Bot: "I've updated the priority to High."
   ```

   **Delete Tasks:**
   ```
   User: "delete task 'old reminder'"
   Bot: "I've deleted the task 'old reminder'."
   ```

### Automated Testing

#### Backend API Tests

```bash
cd Todo_App_Backend

# Test chat endpoint
pytest tests/test_chat_api.py -v

# Test MCP tools
pytest tests/test_mcp_tools.py -v

# Test conversation service
pytest tests/test_conversation_service.py -v

# Test agent integration
pytest tests/test_agent.py -v

# Run all chatbot tests
pytest tests/test_chat*.py tests/test_mcp*.py tests/test_agent*.py -v
```

#### Frontend Tests

```bash
cd frontend

# Test chat components
npm test -- chat-interface.test.tsx

# Test chat API client
npm test -- chat-client.test.ts

# Run all chat tests
npm test -- chat
```

### Load Testing

Test concurrent chat sessions:

```bash
cd Todo_App_Backend

# Install load testing tool
pip install locust

# Run load test
locust -f tests/load_test_chat.py --host=http://localhost:7860
```

Open http://localhost:8089 and configure:
- Number of users: 50
- Spawn rate: 10 users/second

Monitor:
- Response times (should be <3s for p95)
- Error rate (should be <1%)
- Database connection pool

---

## Troubleshooting

### Issue: "OpenAI API key not found"

**Symptoms:** Chat endpoint returns 500 error, logs show "OPENAI_API_KEY not set"

**Solution:**
1. Verify `.env` file exists in `Todo_App_Backend/`
2. Check `OPENAI_API_KEY` is set correctly
3. Restart backend server to reload environment variables

```bash
# Verify environment variable is loaded
cd Todo_App_Backend
python -c "import os; print('Key set:', bool(os.getenv('OPENAI_API_KEY')))"
```

---

### Issue: Chat responses are very slow (>10 seconds)

**Symptoms:** Chat takes a long time to respond, sometimes times out

**Possible Causes:**
1. OpenAI API latency
2. Large conversation history being loaded
3. Database query performance

**Solutions:**

**Check OpenAI API latency:**
```bash
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4-turbo-preview","messages":[{"role":"user","content":"test"}]}'
```

**Check database query performance:**
```sql
-- Enable query timing
\timing on

-- Test conversation history query
SELECT * FROM messages
WHERE conversation_id = '<some-uuid>'
ORDER BY created_at DESC
LIMIT 10;

-- Should complete in <100ms
```

**Optimize:**
- Reduce conversation history size (currently 10 messages)
- Add database indexes (should already exist from migration)
- Use faster OpenAI model (gpt-3.5-turbo instead of gpt-4)

---

### Issue: Agent misunderstands user intent

**Symptoms:** Bot creates wrong task, doesn't recognize commands, asks for clarification too often

**Possible Causes:**
1. Agent prompt needs improvement
2. Conversation context not loading correctly
3. MCP tool descriptions unclear

**Solutions:**

**Review agent prompt:**
```bash
# Check agent configuration
cat Todo_App_Backend/src/agents/task_agent.py
```

**Test with explicit commands:**
```
Instead of: "do something tomorrow"
Try: "create task: do something, due date: tomorrow"
```

**Check conversation context:**
```python
# In chat_service.py, add logging
logger.info(f"Loading {len(messages)} messages for context")
```

---

### Issue: Rate limit errors (429)

**Symptoms:** User gets "Rate limit exceeded" error

**Solutions:**

**Check current rate limit:**
```sql
SELECT * FROM rate_limits WHERE user_id = <user-id>;
```

**Adjust rate limit:**
```env
# In .env, increase limit
CHAT_RATE_LIMIT=200  # Instead of 100
```

**Reset user's rate limit:**
```sql
DELETE FROM rate_limits WHERE user_id = <user-id>;
```

---

### Issue: Database migration fails

**Symptoms:** `alembic upgrade head` fails with errors

**Solutions:**

**Check current migration status:**
```bash
alembic current
alembic history
```

**Rollback and retry:**
```bash
# Rollback one version
alembic downgrade -1

# Try upgrade again
alembic upgrade head
```

**Manual table creation (last resort):**
```sql
-- Run the SQL from data-model.md manually
-- See: specs/002-ai-chatbot/data-model.md
```

---

### Issue: Encryption errors

**Symptoms:** "Invalid token" or "Fernet" errors when loading messages

**Possible Causes:**
1. Encryption key changed
2. Encryption key not set
3. Messages encrypted with different key

**Solutions:**

**Verify encryption key is set:**
```bash
python -c "import os; print('Key length:', len(os.getenv('CONVERSATION_ENCRYPTION_KEY', '')))"
# Should print: Key length: 44
```

**Re-encrypt messages (if key changed):**
```python
# This is a data migration - be careful!
# See: specs/002-ai-chatbot/data-model.md section on key rotation
```

---

## Development Workflow

### Adding a New MCP Tool

1. Create tool file: `Todo_App_Backend/src/mcp/tools/new_tool.py`
2. Implement tool function with proper parameters and return type
3. Register tool in `Todo_App_Backend/src/mcp/server.py`
4. Add tool definition to `specs/002-ai-chatbot/contracts/mcp-tools.json`
5. Write tests: `Todo_App_Backend/tests/test_new_tool.py`
6. Update agent prompt if needed

### Improving Agent Prompts

1. Edit: `Todo_App_Backend/src/agents/task_agent.py`
2. Modify system prompt to improve intent recognition
3. Test with various user inputs
4. Monitor agent decisions in logs
5. Iterate based on user feedback

### Debugging Agent Decisions

Enable verbose logging:

```python
# In chat_service.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs will show:
# - User message
# - Agent's tool selection
# - Tool parameters
# - Tool response
# - Agent's final response
```

---

## Performance Benchmarks

Expected performance on development machine:

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Chat response time (p95) | <2s | <3s | >5s |
| Database query time | <100ms | <500ms | >1s |
| OpenAI API latency | <1s | <2s | >3s |
| Concurrent users | 100+ | 50+ | <20 |
| Messages per second | 10+ | 5+ | <2 |

---

## Next Steps

After completing setup:

1. ✅ Backend and frontend running locally
2. ✅ Database tables created
3. ✅ Environment variables configured
4. ⏳ Implement chatbot features (see tasks.md)
5. ⏳ Write tests
6. ⏳ Deploy to production

**Ready to implement?** Run `/sp.tasks` to generate the detailed task breakdown.

---

## Useful Commands

```bash
# Backend
cd Todo_App_Backend
uvicorn src.main:app --reload --port 7860  # Start server
pytest tests/test_chat*.py -v              # Run tests
alembic upgrade head                       # Apply migrations
python -m pdb src/main.py                  # Debug

# Frontend
cd frontend
npm run dev                                # Start dev server
npm test -- chat                           # Run tests
npm run build                              # Production build

# Database
psql $DATABASE_URL                         # Connect to database
psql $DATABASE_URL -c "\dt"                # List tables
psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages;"  # Query

# Git
git status                                 # Check branch
git log --oneline -10                      # Recent commits
git diff main                              # Changes from main
```

---

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [Chat UI Kit React](https://chatscope.io/storybook/react/)

---

## Support

If you encounter issues not covered in this guide:

1. Check the main project README
2. Review the specification: `specs/002-ai-chatbot/spec.md`
3. Review the implementation plan: `specs/002-ai-chatbot/plan.md`
4. Check existing tests for examples
5. Ask for help in team chat

---

**Last Updated**: 2026-02-13
**Maintainer**: Development Team
**Status**: Ready for implementation
