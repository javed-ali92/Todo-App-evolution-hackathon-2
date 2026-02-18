/**
 * Custom hook for managing chat state and interactions.
 * Handles message sending, conversation history, and loading states.
 */

import { useState, useCallback } from "react";
import { sendMessage, ChatResponse } from "@/lib/api/chat-client";
import { useAuth } from "@/app/providers/auth-provider";

export interface Message {
  id: string;
  sender: "user" | "bot";
  content: string;
  timestamp: Date;
  taskOperation?: any;
}

export interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendUserMessage: (message: string) => Promise<void>;
  clearError: () => void;
  clearMessages: () => void;
}

/**
 * Hook for managing chat state and API interactions.
 *
 * @returns Chat state and methods
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { session } = useAuth();

  /**
   * Send a user message to the chatbot.
   */
  const sendUserMessage = useCallback(
    async (messageText: string) => {
      if (!messageText.trim()) {
        return;
      }

      // Get authentication details from AuthContext
      const token = session.accessToken;
      const userId = session.userId;

      if (!token || !userId || !session.isLoggedIn) {
        setError("Not authenticated. Please log in again.");
        return;
      }

      const userIdNum = parseInt(userId, 10);

      // Add user message to UI immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        sender: "user",
        content: messageText,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        // Send message to API
        const response: ChatResponse = await sendMessage(
          userIdNum,
          messageText,
          conversationId,
          token
        );

        // Update conversation ID if this is a new conversation
        if (!conversationId && response.conversation_id) {
          setConversationId(response.conversation_id);
        }

        // Add bot response to UI
        const botMessage: Message = {
          id: `bot-${Date.now()}`,
          sender: "bot",
          content: response.message,
          timestamp: new Date(),
          taskOperation: response.task_operation,
        };

        setMessages((prev) => [...prev, botMessage]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);

        // Add error message to chat
        const errorBotMessage: Message = {
          id: `error-${Date.now()}`,
          sender: "bot",
          content: `Sorry, I encountered an error: ${errorMessage}`,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorBotMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, session]
  );

  /**
   * Clear error state.
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Clear all messages and start a new conversation.
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendUserMessage,
    clearError,
    clearMessages,
  };
}
