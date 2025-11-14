import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FolderOpen, Plus, Edit2, Trash2, Lock } from 'lucide-react';
import { Card } from '@/components/Card';
import { Modal } from '@/components/Modal';
import { Badge } from '@/components/Badge';
import { Loading } from '@/components/Loading';
import { EmptyState } from '@/components/EmptyState';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { useDataStore } from '@/store/data';
import { formatDate, availableColors } from '@/lib/utils';
import type { Category } from '@/types';

export function Categories() {
  const { categories, fetchCategories, createCategory, updateCategory, deleteCategory, isLoading } =
    useDataStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Category | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tag: 'blue',
  });

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createCategory(formData);
      setIsCreateModalOpen(false);
      resetForm();
    } catch (error) {
      // Error handled by store
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCategory) return;

    try {
      // Only send changed fields
      const updates: any = {};
      if (formData.name !== selectedCategory.name) updates.name = formData.name;
      if (formData.description !== (selectedCategory.description || ''))
        updates.description = formData.description;
      if (formData.tag !== selectedCategory.tag) updates.tag = formData.tag;

      await updateCategory(selectedCategory.id, updates);
      setIsEditModalOpen(false);
      setSelectedCategory(null);
      resetForm();
    } catch (error) {
      // Error handled by store
    }
  };

  const handleDelete = async (category: Category) => {
    try {
      await deleteCategory(category.id);
      setDeleteConfirm(null);
    } catch (error) {
      // Error handled by store
    }
  };

  const openEditModal = (category: Category) => {
    setSelectedCategory(category);
    setFormData({
      name: category.name,
      description: category.description || '',
      tag: category.tag,
    });
    setIsEditModalOpen(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      tag: 'blue',
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

  if (isLoading && categories.length === 0) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Categories</h1>
          <p className="mt-2 text-gray-600">Organize your expenses by category</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus size={18} />
          New Category
        </button>
      </div>

      {/* Categories Grid */}
      {categories.length === 0 ? (
        <EmptyState
          icon={<FolderOpen size={48} />}
          title="No categories yet"
          description="Create your first category to start organizing your expenses"
          action={
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="btn btn-primary flex items-center gap-2"
            >
              <Plus size={18} />
              Create Category
            </button>
          }
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((category, index) => (
            <motion.div
              key={category.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card hover>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                      {category.is_default && (
                        <span title="Default category">
                          <Lock size={16} className="text-gray-400" />
                        </span>
                      )}
                    </div>
                    {category.description && (
                      <p className="mt-1 text-sm text-gray-600">{category.description}</p>
                    )}
                    <div className="mt-3 flex items-center gap-2">
                      <Badge color={category.tag}>{category.tag}</Badge>
                      <span className="text-xs text-gray-500">
                        Created {formatDate(category.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => openEditModal(category)}
                    disabled={category.is_default}
                    className={`btn btn-secondary flex-1 flex items-center justify-center gap-2 ${
                      category.is_default ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    title={category.is_default ? 'Cannot edit default category' : 'Edit category'}
                  >
                    <Edit2 size={16} />
                    Edit
                  </button>
                  <button
                    onClick={() => setDeleteConfirm(category)}
                    disabled={category.is_default}
                    className={`btn btn-danger flex-1 flex items-center justify-center gap-2 ${
                      category.is_default ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    title={
                      category.is_default ? 'Cannot delete default category' : 'Delete category'
                    }
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title="Create Category"
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
              placeholder="e.g., Groceries"
            />
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
              placeholder="Optional description"
            />
          </div>

          <div>
            <label htmlFor="tag" className="label">
              Tag Color *
            </label>
            <select
              id="tag"
              name="tag"
              value={formData.tag}
              onChange={handleChange}
              required
              className="input"
            >
              {availableColors.map((color) => (
                <option key={color} value={color}>
                  {color.charAt(0).toUpperCase() + color.slice(1)}
                </option>
              ))}
            </select>
            <div className="mt-2">
              <Badge color={formData.tag}>Preview</Badge>
            </div>
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
              Create Category
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedCategory(null);
          resetForm();
        }}
        title="Edit Category"
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

          <div>
            <label htmlFor="edit-tag" className="label">
              Tag Color *
            </label>
            <select
              id="edit-tag"
              name="tag"
              value={formData.tag}
              onChange={handleChange}
              required
              className="input"
            >
              {availableColors.map((color) => (
                <option key={color} value={color}>
                  {color.charAt(0).toUpperCase() + color.slice(1)}
                </option>
              ))}
            </select>
            <div className="mt-2">
              <Badge color={formData.tag}>Preview</Badge>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setIsEditModalOpen(false);
                setSelectedCategory(null);
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
          title="Delete Category"
          message={`Are you sure you want to delete "${deleteConfirm.name}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="danger"
        />
      )}
    </div>
  );
}
