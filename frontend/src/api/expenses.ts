import api from './client';
import type { Expense, ExpenseCreate, ExpenseUpdate } from '../types';

export const expensesApi = {
    list: async (limit = 100, offset = 0): Promise<Expense[]> => {
        const response = await api.get('/me/expenses', { params: { limit, offset } });
        return response.data;
    },

    get: async (expenseId: number): Promise<Expense> => {
        const response = await api.get(`/me/expenses/${expenseId}`);
        return response.data;
    },

    create: async (data: ExpenseCreate): Promise<Expense> => {
        const response = await api.post('/me/expenses/', data);
        return response.data;
    },

    update: async (expenseId: number, data: ExpenseUpdate): Promise<Expense> => {
        const response = await api.put(`/me/expenses/${expenseId}`, data);
        return response.data;
    },

    delete: async (expenseId: number): Promise<void> => {
        await api.delete(`/me/expenses/${expenseId}`);
    },
};
