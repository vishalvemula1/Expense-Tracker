import { useState, useEffect } from 'react';
import { expensesApi } from '../api/expenses';
import { categoriesApi } from '../api/categories';
import type { Expense, Category } from '../types';
import { ExpenseCard } from '../components/expenses/ExpenseCard';
import { ExpenseForm, type ExpenseFormData } from '../components/expenses/ExpenseForm';
import { Modal } from '../components/ui/Modal';
import { Plus, Search, Filter } from 'lucide-react';

export function Expenses() {
    const [expenses, setExpenses] = useState<Expense[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
    const [deleteTarget, setDeleteTarget] = useState<Expense | null>(null);
    const [filterCategory, setFilterCategory] = useState<number | null>(null);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [expensesData, categoriesData] = await Promise.all([
                expensesApi.list(100, 0),
                categoriesApi.list()
            ]);
            setExpenses(expensesData);
            setCategories(categoriesData);
        } catch (error) {
            console.error('Failed to load expenses:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (data: ExpenseFormData) => {
        await expensesApi.create(data);
        setShowAddModal(false);
        loadData();
    };

    const handleUpdate = async (data: ExpenseFormData) => {
        if (!editingExpense) return;
        await expensesApi.update(editingExpense.expense_id, data);
        setEditingExpense(null);
        loadData();
    };

    const handleDelete = async () => {
        if (!deleteTarget) return;
        await expensesApi.delete(deleteTarget.expense_id);
        setDeleteTarget(null);
        loadData();
    };

    const getCategoryById = (id: number) => categories.find(c => c.category_id === id);

    // Filter expenses
    const filteredExpenses = expenses.filter(exp => {
        const matchesCategory = filterCategory === null || exp.category_id === filterCategory;
        const matchesSearch = searchQuery === '' ||
            exp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (exp.description?.toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesCategory && matchesSearch;
    });

    const totalFiltered = filteredExpenses.reduce((sum, exp) => sum + exp.amount, 0);
    const formatAmount = (amount: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">Expenses</h1>
                    <p className="text-zinc-500 mt-1">
                        {filteredExpenses.length} expense{filteredExpenses.length !== 1 ? 's' : ''} · {formatAmount(totalFiltered)} total
                    </p>
                </div>
                <button onClick={() => setShowAddModal(true)} className="btn-primary flex items-center gap-2">
                    <Plus size={18} />
                    Add Expense
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                    <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Search expenses..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input-field input-with-icon"
                    />
                </div>
                <div className="relative sm:w-48">
                    <Filter className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                    <select
                        value={filterCategory ?? ''}
                        onChange={(e) => setFilterCategory(e.target.value ? Number(e.target.value) : null)}
                        className="input-field input-with-icon appearance-none cursor-pointer"
                    >
                        <option value="">All categories</option>
                        {categories.map((cat) => (
                            <option key={cat.category_id} value={cat.category_id}>{cat.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Expenses List */}
            {filteredExpenses.length === 0 ? (
                <div className="glass-panel rounded-xl p-12 text-center">
                    <p className="text-zinc-500">
                        {expenses.length === 0 ? 'No expenses yet. Add your first one!' : 'No expenses match your filters.'}
                    </p>
                </div>
            ) : (
                <div className="space-y-3 stagger-children">
                    {filteredExpenses.map((expense) => (
                        <ExpenseCard
                            key={expense.expense_id}
                            expense={expense}
                            category={getCategoryById(expense.category_id)}
                            onEdit={() => setEditingExpense(expense)}
                            onDelete={() => setDeleteTarget(expense)}
                        />
                    ))}
                </div>
            )}

            {/* Add Modal */}
            <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add Expense">
                <ExpenseForm onSubmit={handleCreate} onCancel={() => setShowAddModal(false)} />
            </Modal>

            {/* Edit Modal */}
            <Modal isOpen={!!editingExpense} onClose={() => setEditingExpense(null)} title="Edit Expense">
                {editingExpense && (
                    <ExpenseForm
                        initialData={{
                            name: editingExpense.name,
                            amount: editingExpense.amount,
                            category_id: editingExpense.category_id,
                            description: editingExpense.description,
                        }}
                        onSubmit={handleUpdate}
                        onCancel={() => setEditingExpense(null)}
                        isEdit
                    />
                )}
            </Modal>

            {/* Delete Confirmation */}
            <Modal isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} title="Delete Expense" size="sm">
                <div className="space-y-5">
                    <p className="text-zinc-400">
                        Are you sure you want to delete <span className="text-white font-medium">"{deleteTarget?.name}"</span>? This action cannot be undone.
                    </p>
                    <div className="flex gap-3">
                        <button onClick={() => setDeleteTarget(null)} className="btn-secondary flex-1">Cancel</button>
                        <button onClick={handleDelete} className="btn-danger flex-1">Delete</button>
                    </div>
                </div>
            </Modal>
        </div>
    );
}
