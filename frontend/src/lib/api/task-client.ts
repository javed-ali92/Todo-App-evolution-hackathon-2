/**
 * API Client for Task Management
 * Handles all task-related API calls with proper authentication
 */

interface Task {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

interface TaskCreate {
  title: string;
  description?: string;
  due_date?: string;
  priority?: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed?: boolean;
}

interface TaskUpdate {
  title?: string;
  description?: string;
  due_date?: string;
  priority?: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed?: boolean;
}

class TaskAPIClient {
  private baseUrl: string;

  constructor() {
    // Use relative path to ensure requests go through Vite proxy during development
    // In production, this will use the actual API server
    this.baseUrl = '/api';
  }

  // Get current token from localStorage
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  // Set authentication token
  setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Remove authentication token
  removeToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Private method to get headers with auth token
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  // Create a new task
  async createTask(userId: number, taskData: TaskCreate): Promise<Task> {
    const url = `${this.baseUrl}/${userId}/tasks`;
    const response = await fetch(url, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create task: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    return response.json();
  }

  // Get all tasks for a user
  async getUserTasks(userId: number): Promise<Task[]> {
    const url = `${this.baseUrl}/${userId}/tasks`;
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch tasks: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    return response.json();
  }

  // Get a specific task
  async getTaskById(userId: number, taskId: number): Promise<Task> {
    const url = `${this.baseUrl}/${userId}/tasks/${taskId}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch task: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    return response.json();
  }

  // Update a task
  async updateTask(userId: number, taskId: number, taskData: TaskUpdate): Promise<Task> {
    const url = `${this.baseUrl}/${userId}/tasks/${taskId}`;
    const response = await fetch(url, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update task: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    return response.json();
  }

  // Delete a task
  async deleteTask(userId: number, taskId: number): Promise<void> {
    const url = `${this.baseUrl}/${userId}/tasks/${taskId}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete task: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }
  }

  // Toggle task completion
  async toggleTaskCompletion(userId: number, taskId: number): Promise<Task> {
    const url = `${this.baseUrl}/${userId}/tasks/${taskId}/complete`;
    const response = await fetch(url, {
      method: 'PATCH',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to toggle task completion: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    return response.json();
  }
}

export const taskClient = new TaskAPIClient();
export type { Task, TaskCreate, TaskUpdate };