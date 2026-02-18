"""
Unit tests for OpenAI Agents SDK integration.
Tests user context injection, session persistence, and tool execution.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import components to test
from backend.src.agents.sdk_agent import (
    SDKTaskAgent,
    UserContextManager,
    inject_user_context
)
from backend.src.services.chat_service_sdk import ChatServiceSDK


class TestUserContextManager:
    """Test suite for UserContextManager."""

    def test_set_and_get_user_id(self):
        """Test setting and getting user context."""
        UserContextManager.set_user_id(123)
        assert UserContextManager.get_user_id() == 123
        UserContextManager.clear()

    def test_get_user_id_without_setting(self):
        """Test that getting user_id without setting raises error."""
        UserContextManager.clear()
        with pytest.raises(RuntimeError, match="User context not set"):
            UserContextManager.get_user_id()

    def test_clear_user_context(self):
        """Test clearing user context."""
        UserContextManager.set_user_id(456)
        UserContextManager.clear()
        with pytest.raises(RuntimeError):
            UserContextManager.get_user_id()


class TestInjectUserContext:
    """Test suite for inject_user_context decorator."""

    def test_inject_user_context_decorator(self):
        """Test that decorator injects user_id correctly."""
        @inject_user_context
        def test_function(title: str, user_id: int = None):
            return {"title": title, "user_id": user_id}

        UserContextManager.set_user_id(789)
        result = test_function(title="Test Task")

        assert result["title"] == "Test Task"
        assert result["user_id"] == 789

        UserContextManager.clear()

    def test_inject_user_context_with_multiple_args(self):
        """Test decorator with multiple arguments."""
        @inject_user_context
        def test_function(title: str, priority: str, user_id: int = None):
            return {"title": title, "priority": priority, "user_id": user_id}

        UserContextManager.set_user_id(100)
        result = test_function(title="Task", priority="High")

        assert result["user_id"] == 100
        UserContextManager.clear()

    def test_inject_user_context_without_setting(self):
        """Test that decorator raises error if context not set."""
        @inject_user_context
        def test_function(user_id: int = None):
            return {"user_id": user_id}

        UserContextManager.clear()
        with pytest.raises(RuntimeError, match="User context not set"):
            test_function()


class TestSDKTaskAgent:
    """Test suite for SDKTaskAgent."""

    @patch('backend.src.agents.sdk_agent.OpenAI')
    @patch('backend.src.agents.sdk_agent.Agent')
    def test_agent_initialization(self, mock_agent, mock_openai):
        """Test that agent initializes correctly."""
        mock_mcp_server = Mock()
        mock_mcp_server.get_tool_schemas.return_value = {}

        agent = SDKTaskAgent(mock_mcp_server)

        assert agent.mcp_server == mock_mcp_server
        assert agent.model == "gpt-4-turbo-preview"
        mock_agent.assert_called_once()

    @patch('backend.src.agents.sdk_agent.Runner')
    @patch('backend.src.agents.sdk_agent.Session')
    def test_process_message_new_session(self, mock_session, mock_runner):
        """Test processing message with new session."""
        # Setup mocks
        mock_mcp_server = Mock()
        mock_runner.run_sync.return_value = {
            "message": "Task created successfully",
            "tool_calls": [{"success": True, "task_id": 1}]
        }

        with patch('backend.src.agents.sdk_agent.OpenAI'):
            with patch('backend.src.agents.sdk_agent.Agent'):
                agent = SDKTaskAgent(mock_mcp_server)

                # Process message
                result = agent.process_message(
                    user_id=1,
                    message="Add task: Buy milk",
                    session_state=None
                )

                assert result["success"] is True
                assert "message" in result
                assert "session_state" in result

    @patch('backend.src.agents.sdk_agent.Runner')
    def test_process_message_with_existing_session(self, mock_runner):
        """Test processing message with existing session state."""
        mock_mcp_server = Mock()
        mock_runner.run_sync.return_value = {
            "message": "Here are your tasks",
            "tool_calls": []
        }

        session_state = {
            "messages": [{"role": "user", "content": "Previous message"}],
            "context": {},
            "metadata": {}
        }

        with patch('backend.src.agents.sdk_agent.OpenAI'):
            with patch('backend.src.agents.sdk_agent.Agent'):
                agent = SDKTaskAgent(mock_mcp_server)

                result = agent.process_message(
                    user_id=1,
                    message="List my tasks",
                    session_state=session_state
                )

                assert result["success"] is True
                assert "session_state" in result

    def test_serialize_and_restore_session(self):
        """Test session serialization and restoration."""
        mock_mcp_server = Mock()

        with patch('backend.src.agents.sdk_agent.OpenAI'):
            with patch('backend.src.agents.sdk_agent.Agent'):
                with patch('backend.src.agents.sdk_agent.Session') as mock_session:
                    agent = SDKTaskAgent(mock_mcp_server)

                    # Create mock session
                    session = Mock()
                    session.messages = [{"role": "user", "content": "Test"}]
                    session.context = {"key": "value"}
                    session.metadata = {"version": "1.0"}

                    # Serialize
                    serialized = agent._serialize_session(session)

                    assert "messages" in serialized
                    assert "context" in serialized
                    assert "metadata" in serialized
                    assert serialized["version"] == "1.0"

                    # Restore
                    restored = agent._restore_session(serialized)
                    assert restored is not None


class TestChatServiceSDK:
    """Test suite for ChatServiceSDK."""

    @patch('backend.src.services.chat_service_sdk.SDKTaskAgent')
    def test_process_message_new_conversation(self, mock_agent_class):
        """Test processing message in new conversation."""
        # Setup mocks
        mock_session = Mock()
        mock_agent = Mock()
        mock_agent.process_message.return_value = {
            "message": "Task created",
            "session_state": {"messages": []},
            "tool_operations": [{"success": True}],
            "success": True
        }
        mock_agent_class.return_value = mock_agent

        # Create service
        service = ChatServiceSDK(mock_session)
        service.conversation_service = Mock()
        service.message_service = Mock()

        # Mock conversation creation
        mock_conversation = Mock()
        mock_conversation.id = uuid.uuid4()
        mock_conversation.meta = None
        service.conversation_service.create_conversation.return_value = mock_conversation

        # Process message
        result = service.process_message(
            user_id=1,
            message="Add task: Test",
            conversation_id=None
        )

        assert "conversation_id" in result
        assert "message" in result
        service.conversation_service.create_conversation.assert_called_once_with(1)

    @patch('backend.src.services.chat_service_sdk.SDKTaskAgent')
    def test_process_message_existing_conversation(self, mock_agent_class):
        """Test processing message in existing conversation."""
        mock_session = Mock()
        mock_agent = Mock()
        mock_agent.process_message.return_value = {
            "message": "Here are your tasks",
            "session_state": {"messages": [{"role": "user", "content": "Test"}]},
            "tool_operations": None,
            "success": True
        }
        mock_agent_class.return_value = mock_agent

        service = ChatServiceSDK(mock_session)
        service.conversation_service = Mock()
        service.message_service = Mock()

        # Mock existing conversation with session state
        conv_id = uuid.uuid4()
        mock_conversation = Mock()
        mock_conversation.id = conv_id
        mock_conversation.meta = {
            "sdk_session": {"messages": [], "context": {}}
        }
        service.conversation_service.get_conversation.return_value = mock_conversation

        # Process message
        result = service.process_message(
            user_id=1,
            message="List tasks",
            conversation_id=conv_id
        )

        assert result["conversation_id"] == str(conv_id)
        service.conversation_service.get_conversation.assert_called_once()

    def test_update_conversation_session(self):
        """Test updating conversation with session state."""
        mock_session = Mock()
        service = ChatServiceSDK(mock_session)
        service.conversation_service = Mock()

        conv_id = uuid.uuid4()
        mock_conversation = Mock()
        mock_conversation.id = conv_id
        mock_conversation.meta = {}
        service.conversation_service.get_conversation.return_value = mock_conversation

        session_state = {"messages": [], "context": {}, "version": "1.0"}

        service._update_conversation_session(conv_id, 1, session_state)

        assert mock_conversation.meta["sdk_session"] == session_state
        assert "sdk_session_updated_at" in mock_conversation.meta

    def test_extract_primary_operation(self):
        """Test extracting primary operation from tool operations."""
        mock_session = Mock()
        service = ChatServiceSDK(mock_session)

        # Test with list of operations
        operations = [
            {"success": True, "task_id": 1},
            {"success": True, "task_id": 2}
        ]
        result = service._extract_primary_operation(operations)
        assert result == operations[0]

        # Test with None
        result = service._extract_primary_operation(None)
        assert result is None

        # Test with empty list
        result = service._extract_primary_operation([])
        assert result is None


class TestMultiTenantSecurity:
    """Test suite for multi-tenant security."""

    def test_user_isolation(self):
        """Test that users can only access their own data."""
        @inject_user_context
        def get_tasks(user_id: int = None):
            # Simulate database query with user_id filter
            return {"user_id": user_id, "tasks": []}

        # User 1
        UserContextManager.set_user_id(1)
        result1 = get_tasks()
        assert result1["user_id"] == 1

        # User 2
        UserContextManager.set_user_id(2)
        result2 = get_tasks()
        assert result2["user_id"] == 2

        # Verify isolation
        assert result1["user_id"] != result2["user_id"]

        UserContextManager.clear()

    def test_context_cleared_after_request(self):
        """Test that context is properly cleared after request."""
        UserContextManager.set_user_id(100)
        assert UserContextManager.get_user_id() == 100

        # Simulate request completion
        UserContextManager.clear()

        # Next request should not have context
        with pytest.raises(RuntimeError):
            UserContextManager.get_user_id()


# Integration test fixtures
@pytest.fixture
def mock_database_session():
    """Fixture for mock database session."""
    return Mock()


@pytest.fixture
def mock_mcp_server():
    """Fixture for mock MCP server."""
    server = Mock()
    server.get_tool_schemas.return_value = {
        "add_task": {"name": "add_task", "description": "Add a task"},
        "list_tasks": {"name": "list_tasks", "description": "List tasks"}
    }
    return server


@pytest.fixture
def sdk_agent(mock_mcp_server):
    """Fixture for SDK agent."""
    with patch('backend.src.agents.sdk_agent.OpenAI'):
        with patch('backend.src.agents.sdk_agent.Agent'):
            return SDKTaskAgent(mock_mcp_server)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
