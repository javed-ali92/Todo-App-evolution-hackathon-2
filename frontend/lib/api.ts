import { useAuth } from '@/app/providers/auth-provider';

// Base API URL - can be configured via environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic API request function with authentication
 */
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const token = localStorage.getItem('userSession')
    ? JSON.parse(localStorage.getItem('userSession')!).AccessToken
    : null;

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

/**
 * Task API functions
 */
export const taskApi = {
  // Get all tasks for a user
  getAll: async (userId: string) => {
    return apiRequest(`/api/${userId}/tasks`);
  },

  // Get a specific task
  getById: async (userId: string, taskId: string) => {
    return apiRequest(`/api/${userId}/tasks/${taskId}`);
  },

  // Create a new task
  create: async (userId: string, taskData: any) => {
    return apiRequest(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  // Update a task
  update: async (userId: string, taskId: string, taskData: any) => {
    return apiRequest(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  },

  // Delete a task
  delete: async (userId: string, taskId: string) => {
    return apiRequest(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  },

  // Toggle task completion
  toggleCompletion: async (userId: string, taskId: string) => {
    return apiRequest(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  },
};

/**
 * Authentication API functions
 */
export const authApi = {
  // Login
  login: async (email: string, password: string) => {
    // This would typically be an API call to the backend
    // For now, we'll simulate a successful login
    return {
      user: {
        id: '1',
        username: 'testuser',
        email,
      },
      accessToken: 'fake-jwt-token',
    };
  },

  // Signup
  signup: async (username: string, email: string, password: string) => {
    // This would typically be an API call to the backend
    // For now, we'll simulate a successful signup
    return {
      user: {
        id: '1',
        username,
        email,
      },
      accessToken: 'fake-jwt-token',
    };
  },
};