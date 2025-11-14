import type {
  User,
  Category,
  Expense,
  LoginRequest,
  SignupRequest,
  AuthResponse,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CreateExpenseRequest,
  UpdateExpenseRequest,
  UpdateUserRequest,
  APIError,
} from '@/types';

const API_BASE_URL = '/api';

class APIClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    // Add Authorization header if token exists
    if (this.token && !endpoint.includes('/auth/')) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    // Add Content-Type for JSON requests
    if (options.body && typeof options.body === 'string') {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle different status codes
      if (response.status === 401) {
        // Unauthorized - token expired or invalid
        this.token = null;
        throw new Error('UNAUTHORIZED');
      }

      if (response.status === 403) {
        throw new Error('FORBIDDEN');
      }

      if (response.status === 404) {
        throw new Error('NOT_FOUND');
      }

      if (!response.ok) {
        const error: APIError = await response.json().catch(() => ({
          detail: 'An error occurred',
        }));
        throw new Error(error.detail || 'An error occurred');
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // Auth endpoints
  async signup(data: SignupRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: formData,
    });

    return response;
  }

  // User endpoints
  async getMe(): Promise<User> {
    return this.request<User>('/me');
  }

  async updateMe(data: UpdateUserRequest): Promise<User> {
    return this.request<User>('/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteMe(): Promise<void> {
    await this.request<void>('/me', {
      method: 'DELETE',
    });
  }

  // Category endpoints
  async createCategory(data: CreateCategoryRequest): Promise<Category> {
    return this.request<Category>('/me/categories/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCategories(): Promise<Category[]> {
    return this.request<Category[]>('/me/categories/');
  }

  async getCategory(id: number): Promise<Category> {
    return this.request<Category>(`/me/categories/${id}`);
  }

  async updateCategory(
    id: number,
    data: UpdateCategoryRequest
  ): Promise<Category> {
    return this.request<Category>(`/me/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCategory(id: number): Promise<void> {
    await this.request<void>(`/me/categories/${id}`, {
      method: 'DELETE',
    });
  }

  async getCategoryExpenses(id: number): Promise<Expense[]> {
    return this.request<Expense[]>(`/me/categories/${id}/expenses`);
  }

  // Expense endpoints
  async createExpense(data: CreateExpenseRequest): Promise<Expense> {
    return this.request<Expense>('/me/expenses/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getExpenses(limit?: number, offset?: number): Promise<Expense[]> {
    const params = new URLSearchParams();
    if (limit !== undefined) params.append('limit', limit.toString());
    if (offset !== undefined) params.append('offset', offset.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<Expense[]>(`/me/expenses/${query}`);
  }

  async getExpense(id: number): Promise<Expense> {
    return this.request<Expense>(`/me/expenses/${id}`);
  }

  async updateExpense(id: number, data: UpdateExpenseRequest): Promise<Expense> {
    return this.request<Expense>(`/me/expenses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteExpense(id: number): Promise<void> {
    await this.request<void>(`/me/expenses/${id}`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new APIClient();
