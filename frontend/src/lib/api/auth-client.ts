/**
 * API Client for Authentication
 * Handles all authentication-related API calls including login, registration, and user info
 */

interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
}

interface UserRegistration {
  username: string;
  email: string;
  password: string;
}

interface UserLogin {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username?: string;
  email?: string;
}

class AuthAPIClient {
  private baseUrl: string;

  constructor() {
    // Use environment variable for API base URL
    // In production (Vercel), this should point to Hugging Face Space
    // In development, this can use localhost or proxy
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://sibtain92-todo-app-backend.hf.space';
  }

  // Register a new user
  async register(userData: UserRegistration): Promise<LoginResponse> {
    const url = `${this.baseUrl}/auth/signup`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: userData.username,
        email: userData.email,
        password: userData.password
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to register user: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    const result = await response.json();

    // Store the token in localStorage (registration now returns a token for immediate login)
    if (typeof window !== 'undefined' && result.access_token) {
      localStorage.setItem('auth_token', result.access_token);
    }

    return result;
  }

  // Login with email and password
  async login(credentials: UserLogin): Promise<LoginResponse> {
    const url = `${this.baseUrl}/auth/login`;  // Use the login endpoint

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to login: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    const result = await response.json();

    // Store the token in localStorage
    if (typeof window !== 'undefined' && result.access_token) {
      localStorage.setItem('auth_token', result.access_token);
    }

    return result;
  }

  // Get current user info
  async getCurrentUser(): Promise<User> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;

    if (!token) {
      throw new Error('No authentication token found');
    }

    const url = `${this.baseUrl}/auth/me`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      // If unauthorized, remove the token
      if (response.status === 401) {
        localStorage.removeItem('auth_token');
      }
      throw new Error(`Failed to get user info: ${response.status} - ${response.statusText}. Details: ${errorText}`);
    }

    return response.json();
  }

  // Logout - remove token from localStorage
  async logout(): Promise<void> {
    // Remove the token from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      return !!token;
    }
    return false;
  }

  // Get the current token
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }
}

export const authClient = new AuthAPIClient();
export type { User, UserRegistration, UserLogin, LoginResponse };