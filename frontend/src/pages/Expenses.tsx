import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Wallet, Plus, Edit2, Trash2, Search } from 'lucide-react';
import { Card } from '@/components/Card';
import { Modal } from '@/components/Modal';
import { Badge } from '@/components/Badge';
import { Loading } from '@/components/Loading';
import { EmptyState } from '@/components/EmptyState';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { useDataStore } from '@/store/data';
import { formatCurrency, formatDateTime } from '@/lib/utils';
import type { Expense } from '@/types';

export function Expenses() {
  const {
    expenses,
    categories,
    fetchExpenses,
    fetchCategories,
    createExpense,
    updateExpense,
    deleteExpense,
    isLoading,
  } = useDataStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Expense | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    amount: '',
    description: '',
    category_id: '',
  });

  useEffect(() => {
    fetchExpenses();
    fetchCategories();
  }, [fetchExpenses, fetchCategories]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data: any = {
        name: formData.name,
        amount: parseFloat(formData.amount),
      };
      if (formData.description) data.description = formData.description;
      if (formData.category_id) data.category_id = parseInt(formData.category_id);

      await createExpense(data);
      setIsCreateModalOpen(false);
      resetForm();
    } catch (error) {
      // Error handled by store
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedExpense) return;

    try {
      // Only send changed fields
      const updates: any = {};
      if (formData.name !== selectedExpense.name) updates.name = formData.name;
      if (parseFloat(formData.amount) !== selectedExpense.amount)
        updates.amount = parseFloat(formData.amount);
      if (formData.description !== (selectedExpense.description || ''))
        updates.description = formData.description;
      if (formData.category_id && parseInt(formData.category_id) !== selectedExpense.category_id)
        updates.category_id = parseInt(formData.category_id);

      await updateExpense(selectedExpense.id, updates);
      setIsEditModalOpen(false);
      setSelectedExpense(null);
      resetForm();
    } catch (error) {
      // Error handled by store
    }
  };

  const handleDelete = async (expense: Expense) => {
    try {
      await deleteExpense(expense.id);
      setDeleteConfirm(null);
    } catch (error) {
      // Error handled by store
    }
  };

  const openEditModal = (expense: Expense) => {
    setSelectedExpense(expense);
    setFormData({
      name: expense.name,
      amount: expense.amount.toString(),
      description: expense.description || '',
      category_id: expense.category_id.toString(),
    });
    setIsEditModalOpen(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      amount: '',
      description: '',
      category_id: '',
    });
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const filteredExpenses = expenses.filter((expense) =>
    expense.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading && expenses.length === 0) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Expenses</h1>
          <p className="mt-2 text-gray-600">Track and manage all your expenses</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={18} />
          New Expense
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search expenses..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Expenses List */}
      {filteredExpenses.length === 0 ? (
        <EmptyState
          icon={<Wallet size={48} />}
          title={searchQuery ? 'No expenses found' : 'No expenses yet'}
          description={
            searchQuery
              ? 'Try adjusting your search query'
              : 'Create your first expense to start tracking'
          }
          action={
            !searchQuery ? (
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="btn btn-primary flex items-center gap-2"
              >
                <Plus size={18} />
                Create Expense
              </button>
            ) : undefined
          }
        />
      ) : (
        <div className="space-y-4">
          {filteredExpenses.map((expense, index) => {
            const category = categories.find((c) => c.id === expense.category_id);
            return (
              <motion.div
                key={expense.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <Card hover>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">{expense.name}</h3>
                        {category && <Badge color={category.tag}>{category.name}</Badge>}
                      </div>
                      {expense.description && (
                        <p className="mt-1 text-sm text-gray-600">{expense.description}</p>
                      )}
                      <p className="mt-2 text-xs text-gray-500">
                        {formatDateTime(expense.created_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-bold text-gray-900">
                        {formatCurrency(expense.amount)}
                      </span>
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEditModal(expense)}
                          className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
                          title="Edit expense"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(expense)}
                          className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-red-100 hover:text-red-600"
                          title="Delete expense"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title="Create Expense"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label htmlFor="name" className="label">
              Name *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="input"
              placeholder="e.g., Coffee at Starbucks"
            />
          </div>

          <div>
            <label htmlFor="amount" className="label">
              Amount *
            </label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              required
              step="0.01"
              min="0"
              className="input"
              placeholder="0.00"
            />
          </div>

          <div>
            <label htmlFor="category_id" className="label">
              Category
            </label>
            <select
              id="category_id"
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              className="input"
            >
              <option value="">Use default category</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Leave empty to use your default category
            </p>
          </div>

          <div>
            <label htmlFor="description" className="label">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="input"
              placeholder="Optional notes"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setIsCreateModalOpen(false);
                resetForm();
              }}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              Create Expense
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedExpense(null);
          resetForm();
        }}
        title="Edit Expense"
      >
        <form onSubmit={handleEdit} className="space-y-4">
          <div>
            <label htmlFor="edit-name" className="label">
              Name *
            </label>
            <input
              type="text"
              id="edit-name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="input"
            />
          </div>

          <div>
            <label htmlFor="edit-amount" className="label">
              Amount *
            </label>
            <input
              type="number"
              id="edit-amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              required
              step="0.01"
              min="0"
              className="input"
            />
          </div>

          <div>
            <label htmlFor="edit-category_id" className="label">
              Category
            </label>
            <select
              id="edit-category_id"
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              className="input"
            >
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="edit-description" className="label">
              Description
            </label>
            <textarea
              id="edit-description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="input"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setIsEditModalOpen(false);
                setSelectedExpense(null);
                resetForm();
              }}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              Save Changes
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      {deleteConfirm && (
        <ConfirmDialog
          isOpen={true}
          onClose={() => setDeleteConfirm(null)}
          onConfirm={() => handleDelete(deleteConfirm)}
          title="Delete Expense"
          message={`Are you sure you want to delete "${deleteConfirm.name}" (${formatCurrency(
            deleteConfirm.amount
          )})? This action cannot be undone.`}
          confirmText="Delete"
          variant="danger"
        />
      )}
    </div>
  );
}
