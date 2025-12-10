import { useState, useEffect } from 'react';
import { categoriesApi } from '../api/categories';
import type { Category } from '../types';
import { CategoryBadge } from '../components/categories/CategoryBadge';
import { CategoryForm, type CategoryFormData } from '../components/categories/CategoryForm';
import { Modal } from '../components/ui/Modal';
import { Plus, Pencil, Trash2, Lock } from 'lucide-react';

export function Categories() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [editingCategory, setEditingCategory] = useState<Category | null>(null);
    const [deleteTarget, setDeleteTarget] = useState<Category | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const data = await categoriesApi.list(100, 0);
            setCategories(data);
        } catch (error) {
            console.error('Failed to load categories:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (data: CategoryFormData) => {
        await categoriesApi.create(data);
        setShowAddModal(false);
        loadData();
    };

    const handleUpdate = async (data: CategoryFormData) => {
        if (!editingCategory) return;
        await categoriesApi.update(editingCategory.category_id, data);
        setEditingCategory(null);
        loadData();
    };

    const handleDelete = async () => {
        if (!deleteTarget) return;
        try {
            await categoriesApi.delete(deleteTarget.category_id);
            setDeleteTarget(null);
            loadData();
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Cannot delete this category');
            setDeleteTarget(null);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

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
                    <h1 className="text-2xl font-bold text-white">Categories</h1>
                    <p className="text-zinc-500 mt-1">{categories.length} categor{categories.length !== 1 ? 'ies' : 'y'}</p>
                </div>
                <button onClick={() => setShowAddModal(true)} className="btn-primary flex items-center gap-2">
                    <Plus size={18} />
                    Add Category
                </button>
            </div>

            {/* Categories Grid */}
            {categories.length === 0 ? (
                <div className="glass-panel rounded-xl p-12 text-center">
                    <p className="text-zinc-500">No categories yet. Add your first one!</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
                    {categories.map((category) => (
                        <div key={category.category_id} className="glass-panel rounded-xl p-5 card-hover group">
                            <div className="flex items-start justify-between mb-4">
                                <CategoryBadge
                                    name={category.name}
                                    tag={category.tag}
                                    isDefault={category.is_default}
                                    size="md"
                                />
                                {!category.is_default && (
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={() => setEditingCategory(category)}
                                            className="p-2 rounded-lg text-zinc-500 hover:text-white hover:bg-zinc-800 transition-colors"
                                            title="Edit"
                                        >
                                            <Pencil size={14} />
                                        </button>
                                        <button
                                            onClick={() => setDeleteTarget(category)}
                                            className="p-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                                            title="Delete"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                )}
                                {category.is_default && (
                                    <div className="flex items-center gap-1 text-zinc-600" title="Default category cannot be modified">
                                        <Lock size={14} />
                                    </div>
                                )}
                            </div>

                            {category.description ? (
                                <p className="text-sm text-zinc-500 line-clamp-2 mb-3">{category.description}</p>
                            ) : (
                                <p className="text-sm text-zinc-600 italic mb-3">No description</p>
                            )}

                            <p className="text-xs text-zinc-600">Created {formatDate(category.date_of_entry)}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Add Modal */}
            <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add Category">
                <CategoryForm onSubmit={handleCreate} onCancel={() => setShowAddModal(false)} />
            </Modal>

            {/* Edit Modal */}
            <Modal isOpen={!!editingCategory} onClose={() => setEditingCategory(null)} title="Edit Category">
                {editingCategory && (
                    <CategoryForm
                        initialData={{
                            name: editingCategory.name,
                            description: editingCategory.description,
                            tag: editingCategory.tag,
                        }}
                        onSubmit={handleUpdate}
                        onCancel={() => setEditingCategory(null)}
                        isEdit
                    />
                )}
            </Modal>

            {/* Delete Confirmation */}
            <Modal isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} title="Delete Category" size="sm">
                <div className="space-y-5">
                    <p className="text-zinc-400">
                        Are you sure you want to delete <span className="text-white font-medium">"{deleteTarget?.name}"</span>?
                        All expenses in this category will be moved to the default category.
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
