import api from './client';
import type { Category, CategoryCreate, CategoryUpdate, Expense } from '../types';

export const categoriesApi = {
    list: async (limit = 100, offset = 0): Promise<Category[]> => {
        const response = await api.get('/me/categories', { params: { limit, offset } });
        return response.data;
    },

    get: async (categoryId: number): Promise<Category> => {
        const response = await api.get(`/me/categories/${categoryId}`);
        return response.data;
    },

    create: async (data: CategoryCreate): Promise<Category> => {
        const response = await api.post('/me/categories/', data);
        return response.data;
    },

    update: async (categoryId: number, data: CategoryUpdate): Promise<Category> => {
        const response = await api.put(`/me/categories/${categoryId}`, data);
        return response.data;
    },

    delete: async (categoryId: number): Promise<void> => {
        await api.delete(`/me/categories/${categoryId}`);
    },

    getExpenses: async (categoryId: number): Promise<Expense[]> => {
        const response = await api.get(`/me/categories/${categoryId}/expenses`);
        return response.data;
    },
};
