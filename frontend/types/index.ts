export interface User {
  id: string;
  username: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  dueDate?: string;
  priority: 'low' | 'medium' | 'high';
  tags?: string[];
  recursionPattern?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface UserSession {
  userId: string | null;
  username: string | null;
  email: string | null;
  isLoggedIn: boolean;
  accessToken: string | null;
  expiryTime: Date | null;
}

export interface FilterState {
  showCompleted: 'all' | 'completed' | 'pending';
  priorityFilter: 'all' | 'low' | 'medium' | 'high';
  searchQuery: string;
  sortBy: 'created' | 'dueDate' | 'priority';
  sortDirection: 'asc' | 'desc';
}

export interface FormState {
  formData: Record<string, any>;
  errors: Record<string, string>;
  isLoading: boolean;
  successMessage: string | null;
  isDirty: boolean;
}