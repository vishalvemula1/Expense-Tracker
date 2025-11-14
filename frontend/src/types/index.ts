export interface User {
  id: number;
  username: string;
  email: string;
  salary: number;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  tag: string;
  is_default: boolean;
  created_at: string;
}

export interface Expense {
  id: number;
  name: string;
  amount: number;
  description: string | null;
  category_id: number;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface SignupRequest {
  username: string;
  email: string;
  salary: number;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface CreateCategoryRequest {
  name: string;
  description?: string;
  tag: string;
}

export interface UpdateCategoryRequest {
  name?: string;
  description?: string;
  tag?: string;
}

export interface CreateExpenseRequest {
  name: string;
  amount: number;
  description?: string;
  category_id?: number;
}

export interface UpdateExpenseRequest {
  name?: string;
  amount?: number;
  description?: string;
  category_id?: number;
}

export interface UpdateUserRequest {
  username?: string;
  email?: string;
  salary?: number;
  password?: string;
}

export interface APIError {
  detail: string;
}

export interface PaginatedExpenses {
  expenses: Expense[];
  total: number;
  offset: number;
  limit: number;
}
