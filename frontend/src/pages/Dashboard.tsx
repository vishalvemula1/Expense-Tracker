import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { expensesApi } from '../api/expenses';
import { categoriesApi } from '../api/categories';
import type { Expense, Category } from '../types';
import { CategoryBadge } from '../components/categories/CategoryBadge';
import { TrendingUp, Wallet, FolderOpen, ArrowRight, Plus } from 'lucide-react';
import { Modal } from '../components/ui/Modal';
import { ExpenseForm, type ExpenseFormData } from '../components/expenses/ExpenseForm';

export function Dashboard() {
    const [expenses, setExpenses] = useState<Expense[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddExpense, setShowAddExpense] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [expensesData, categoriesData] = await Promise.all([
                expensesApi.list(10, 0),
                categoriesApi.list()
            ]);
            setExpenses(expensesData);
            setCategories(categoriesData);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddExpense = async (data: ExpenseFormData) => {
        await expensesApi.create(data);
        setShowAddExpense(false);
        loadData();
    };

    const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

    const formatAmount = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    const getCategoryById = (id: number) => categories.find(c => c.category_id === id);

    // Group expenses by category for breakdown
    const categoryTotals = expenses.reduce((acc, exp) => {
        const catId = exp.category_id;
        acc[catId] = (acc[catId] || 0) + exp.amount;
        return acc;
    }, {} as Record<number, number>);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fadeIn">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                    <p className="text-zinc-500 mt-1">Overview of your expenses</p>
                </div>
                <button onClick={() => setShowAddExpense(true)} className="btn-primary flex items-center gap-2">
                    <Plus size={18} />
                    Add Expense
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-panel rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-white/10">
                            <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-sm text-zinc-500">Total Spent</span>
                    </div>
                    <p className="text-3xl font-bold text-white">{formatAmount(totalExpenses)}</p>
                </div>

                <div className="glass-panel rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-white/10">
                            <Wallet className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-sm text-zinc-500">Expenses</span>
                    </div>
                    <p className="text-3xl font-bold text-white">{expenses.length}</p>
                </div>

                <div className="glass-panel rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-white/10">
                            <FolderOpen className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-sm text-zinc-500">Categories</span>
                    </div>
                    <p className="text-3xl font-bold text-white">{categories.length}</p>
                </div>
            </div>

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Expenses */}
                <div className="glass-panel rounded-xl p-6">
                    <div className="flex items-center justify-between mb-5">
                        <h2 className="text-lg font-semibold text-white">Recent Expenses</h2>
                        <Link to="/expenses" className="text-sm text-zinc-400 hover:text-white flex items-center gap-1 transition-colors">
                            View all <ArrowRight size={14} />
                        </Link>
                    </div>

                    {expenses.length === 0 ? (
                        <p className="text-zinc-500 text-center py-8">No expenses yet</p>
                    ) : (
                        <div className="space-y-3 stagger-children">
                            {expenses.slice(0, 5).map((expense) => {
                                const cat = getCategoryById(expense.category_id);
                                return (
                                    <div key={expense.expense_id} className="flex items-center justify-between py-3 border-b border-zinc-800 last:border-0">
                                        <div className="flex items-center gap-3">
                                            <div>
                                                <p className="text-white font-medium">{expense.name}</p>
                                                {cat && (
                                                    <CategoryBadge name={cat.name} tag={cat.tag} isDefault={cat.is_default} />
                                                )}
                                            </div>
                                        </div>
                                        <span className="text-white font-medium">{formatAmount(expense.amount)}</span>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Category Breakdown */}
                <div className="glass-panel rounded-xl p-6">
                    <div className="flex items-center justify-between mb-5">
                        <h2 className="text-lg font-semibold text-white">By Category</h2>
                        <Link to="/categories" className="text-sm text-zinc-400 hover:text-white flex items-center gap-1 transition-colors">
                            Manage <ArrowRight size={14} />
                        </Link>
                    </div>

                    {Object.keys(categoryTotals).length === 0 ? (
                        <p className="text-zinc-500 text-center py-8">No data yet</p>
                    ) : (
                        <div className="space-y-4 stagger-children">
                            {Object.entries(categoryTotals)
                                .sort(([, a], [, b]) => b - a)
                                .map(([catId, total]) => {
                                    const cat = getCategoryById(Number(catId));
                                    const percentage = totalExpenses > 0 ? (total / totalExpenses) * 100 : 0;
                                    return (
                                        <div key={catId}>
                                            <div className="flex items-center justify-between mb-2">
                                                {cat && (
                                                    <CategoryBadge name={cat.name} tag={cat.tag} isDefault={cat.is_default} size="md" />
                                                )}
                                                <span className="text-white font-medium">{formatAmount(total)}</span>
                                            </div>
                                            <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-white/60 rounded-full transition-all duration-500"
                                                    style={{ width: `${percentage}%` }}
                                                />
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    )}
                </div>
            </div>

            {/* Add Expense Modal */}
            <Modal isOpen={showAddExpense} onClose={() => setShowAddExpense(false)} title="Add Expense">
                <ExpenseForm
                    onSubmit={handleAddExpense}
                    onCancel={() => setShowAddExpense(false)}
                />
            </Modal>
        </div>
    );
}
