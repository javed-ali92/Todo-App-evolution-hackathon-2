/**
 * Chat API client for communicating with the AI chatbot backend.
 * Handles sending messages and receiving responses.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860";

export interface ChatMessage {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  task_operation?: {
    success: boolean;
    task?: any;
    tasks?: any[];
    message?: string;
    error?: string;
  };
}

export interface ChatError {
  detail: string;
  status?: number;
}

/**
 * Send a chat message to the AI assistant.
 *
 * @param userId - ID of the authenticated user
 * @param message - User's message text
 * @param conversationId - Optional conversation ID to continue existing conversation
 * @param token - JWT authentication token
 * @returns Promise with chat response
 * @throws Error if request fails
 */
export async function sendMessage(
  userId: number,
  message: string,
  conversationId: string | null,
  token: string
): Promise<ChatResponse> {
  try {
    const requestBody: ChatMessage = {
      message,
    };

    if (conversationId) {
      requestBody.conversation_id = conversationId;
    }

    const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData: ChatError = await response.json().catch(() => ({
        detail: "An error occurred",
      }));

      if (response.status === 401) {
        throw new Error("Unauthorized. Please log in again.");
      } else if (response.status === 429) {
        throw new Error(
          errorData.detail || "Rate limit exceeded. Please try again later."
        );
      } else if (response.status === 403) {
        throw new Error("You don't have permission to access this conversation.");
      } else {
        throw new Error(errorData.detail || "Failed to send message");
      }
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Network error. Please check your connection.");
  }
}

/**
 * Get list of user's conversations.
 *
 * @param userId - ID of the authenticated user
 * @param token - JWT authentication token
 * @param limit - Maximum number of conversations to return
 * @param offset - Number of conversations to skip
 * @returns Promise with conversations list
 */
export async function getConversations(
  userId: number,
  token: string,
  limit: number = 20,
  offset: number = 0
): Promise<any> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/${userId}/conversations?limit=${limit}&offset=${offset}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch conversations");
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Network error. Please check your connection.");
  }
}

/**
 * Get messages from a specific conversation.
 *
 * @param userId - ID of the authenticated user
 * @param conversationId - UUID of the conversation
 * @param token - JWT authentication token
 * @param limit - Maximum number of messages to return
 * @returns Promise with messages list
 */
export async function getConversationMessages(
  userId: number,
  conversationId: string,
  token: string,
  limit: number = 50
): Promise<any> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/${userId}/conversations/${conversationId}/messages?limit=${limit}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch messages");
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Network error. Please check your connection.");
  }
}
