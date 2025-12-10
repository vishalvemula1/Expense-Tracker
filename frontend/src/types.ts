// Types matching backend models

export interface User {
    user_id: number;
    username: string;
    email: string;
    salary: number | null;
}

// Category
export type Color = 'Blue' | 'Red' | 'Black' | 'White';

export interface Category {
    category_id: number;
    name: string;
    description: string | null;
    tag: Color | null;
    date_of_entry: string;
    is_default: boolean;
}

export interface CategoryCreate {
    name: string;
    description?: string | null;
    tag?: Color | null;
}

export interface CategoryUpdate {
    name?: string;
    description?: string | null;
    tag?: Color | null;
}

// Expense
export interface Expense {
    expense_id: number;
    name: string;
    amount: number;
    category_id: number;
    description: string | null;
    date_of_entry: string;
    date_of_update: string | null;
}

export interface ExpenseCreate {
    name: string;
    amount: number;
    category_id?: number | null;
    description?: string | null;
}

export interface ExpenseUpdate {
    name?: string;
    amount?: number;
    category_id?: number | null;
    description?: string | null;
}

// API Response types
export interface Token {
    access_token: string;
    token_type: string;
}
