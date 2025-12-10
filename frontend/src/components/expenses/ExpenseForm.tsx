import { useState, useEffect, type FormEvent } from 'react';
import type { Category } from '../../types';
import { DollarSign, FileText, Tag, Loader } from 'lucide-react';
import { categoriesApi } from '../../api/categories';

export interface ExpenseFormData {
    name: string;
    amount: number;
    category_id: number | null;
    description: string | null;
}

interface ExpenseFormProps {
    initialData?: Partial<ExpenseFormData>;
    onSubmit: (data: ExpenseFormData) => Promise<void>;
    onCancel: () => void;
    isEdit?: boolean;
}

export function ExpenseForm({ initialData, onSubmit, onCancel, isEdit = false }: ExpenseFormProps) {
    const [name, setName] = useState(initialData?.name || '');
    const [amount, setAmount] = useState(initialData?.amount?.toString() || '');
    const [categoryId, setCategoryId] = useState<number | null>(initialData?.category_id ?? null);
    const [description, setDescription] = useState(initialData?.description || '');
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        categoriesApi.list().then(setCategories).catch(console.error);
    }, []);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await onSubmit({
                name: name.trim(),
                amount: parseFloat(amount),
                category_id: categoryId,
                description: description.trim() || null,
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save expense');
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                    {error}
                </div>
            )}

            <div>
                <label className="label-text">Name</label>
                <div className="relative">
                    <FileText className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Expense name"
                        required
                        className="input-field input-with-icon"
                    />
                </div>
            </div>

            <div>
                <label className="label-text">Amount</label>
                <div className="relative">
                    <DollarSign className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                    <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        placeholder="0.00"
                        required
                        className="input-field input-with-icon"
                    />
                </div>
            </div>

            <div>
                <label className="label-text">Category</label>
                <div className="relative">
                    <Tag className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                    <select
                        value={categoryId ?? ''}
                        onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : null)}
                        className="input-field input-with-icon appearance-none cursor-pointer"
                    >
                        <option value="">Select category...</option>
                        {categories.map((cat) => (
                            <option key={cat.category_id} value={cat.category_id}>
                                {cat.name} {cat.is_default ? '(default)' : ''}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div>
                <label className="label-text">Description (optional)</label>
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Add a note..."
                    rows={3}
                    className="input-field resize-none"
                />
            </div>

            <div className="flex gap-3 pt-2">
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                    Cancel
                </button>
                <button type="submit" disabled={loading} className="btn-primary flex-1 flex items-center justify-center gap-2">
                    {loading ? <Loader className="w-4 h-4 animate-spin" /> : (isEdit ? 'Update' : 'Add Expense')}
                </button>
            </div>
        </form>
    );
}
