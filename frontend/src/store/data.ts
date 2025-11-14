import { create } from 'zustand';
import { apiClient } from '@/lib/api';
import type {
  Category,
  Expense,
  CreateCategoryRequest,
  UpdateCategoryRequest,
  CreateExpenseRequest,
  UpdateExpenseRequest,
} from '@/types';

interface DataState {
  categories: Category[];
  expenses: Expense[];
  isLoading: boolean;
  error: string | null;

  // Category actions
  fetchCategories: () => Promise<void>;
  createCategory: (data: CreateCategoryRequest) => Promise<Category>;
  updateCategory: (id: number, data: UpdateCategoryRequest) => Promise<Category>;
  deleteCategory: (id: number) => Promise<void>;

  // Expense actions
  fetchExpenses: (limit?: number, offset?: number) => Promise<void>;
  createExpense: (data: CreateExpenseRequest) => Promise<Expense>;
  updateExpense: (id: number, data: UpdateExpenseRequest) => Promise<Expense>;
  deleteExpense: (id: number) => Promise<void>;

  clearError: () => void;
}

export const useDataStore = create<DataState>((set) => ({
  categories: [],
  expenses: [],
  isLoading: false,
  error: null,

  fetchCategories: async () => {
    set({ isLoading: true, error: null });
    try {
      const categories = await apiClient.getCategories();
      set({ categories, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch categories';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  createCategory: async (data: CreateCategoryRequest) => {
    set({ isLoading: true, error: null });
    try {
      const category = await apiClient.createCategory(data);
      set((state) => ({
        categories: [...state.categories, category],
        isLoading: false,
      }));
      return category;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create category';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateCategory: async (id: number, data: UpdateCategoryRequest) => {
    set({ isLoading: true, error: null });
    try {
      const category = await apiClient.updateCategory(id, data);
      set((state) => ({
        categories: state.categories.map((c) => (c.id === id ? category : c)),
        isLoading: false,
      }));
      return category;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update category';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteCategory: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteCategory(id);
      set((state) => ({
        categories: state.categories.filter((c) => c.id !== id),
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete category';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchExpenses: async (limit?: number, offset?: number) => {
    set({ isLoading: true, error: null });
    try {
      const expenses = await apiClient.getExpenses(limit, offset);
      set({ expenses, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch expenses';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  createExpense: async (data: CreateExpenseRequest) => {
    set({ isLoading: true, error: null });
    try {
      const expense = await apiClient.createExpense(data);
      set((state) => ({
        expenses: [expense, ...state.expenses],
        isLoading: false,
      }));
      return expense;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create expense';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateExpense: async (id: number, data: UpdateExpenseRequest) => {
    set({ isLoading: true, error: null });
    try {
      const expense = await apiClient.updateExpense(id, data);
      set((state) => ({
        expenses: state.expenses.map((e) => (e.id === id ? expense : e)),
        isLoading: false,
      }));
      return expense;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update expense';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteExpense: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteExpense(id);
      set((state) => ({
        expenses: state.expenses.filter((e) => e.id !== id),
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete expense';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
