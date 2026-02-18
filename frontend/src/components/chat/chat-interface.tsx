/**
 * ChatInterface component - main chat UI container.
 * Integrates MessageList, MessageInput, and useChat hook.
 */

"use client";

import { useChat } from "@/lib/hooks/use-chat";
import MessageList from "./message-list";
import MessageInput from "./message-input";

export default function ChatInterface() {
  const {
    messages,
    isLoading,
    error,
    conversationId,
    sendUserMessage,
    clearError,
    clearMessages,
  } = useChat();

  return (
    <div className="flex flex-col h-[600px]">
      {/* Header with conversation info */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-600">
            {conversationId ? "Conversation active" : "New conversation"}
          </span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            New Chat
          </button>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="px-4 py-3 bg-red-50 border-b border-red-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm text-red-800">{error}</span>
          </div>
          <button
            onClick={clearError}
            className="text-red-600 hover:text-red-700"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Messages area */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input area */}
      <MessageInput onSendMessage={sendUserMessage} isLoading={isLoading} />
    </div>
  );
}
