import { useState, type FormEvent } from 'react';
import type { Color } from '../../types';
import { Folder, FileText, Palette, Loader } from 'lucide-react';

export interface CategoryFormData {
    name: string;
    description: string | null;
    tag: Color | null;
}

interface CategoryFormProps {
    initialData?: Partial<CategoryFormData>;
    onSubmit: (data: CategoryFormData) => Promise<void>;
    onCancel: () => void;
    isEdit?: boolean;
}

const colors: Color[] = ['Blue', 'Red', 'Black', 'White'];

const colorDisplayClasses: Record<Color, string> = {
    Blue: 'bg-blue-500',
    Red: 'bg-red-500',
    Black: 'bg-zinc-600',
    White: 'bg-white',
};

export function CategoryForm({ initialData, onSubmit, onCancel, isEdit = false }: CategoryFormProps) {
    const [name, setName] = useState(initialData?.name || '');
    const [description, setDescription] = useState(initialData?.description || '');
    const [tag, setTag] = useState<Color | null>(initialData?.tag ?? null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await onSubmit({
                name: name.trim(),
                description: description.trim() || null,
                tag,
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to save category');
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
                    <Folder className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Category name"
                        required
                        className="input-field input-with-icon"
                    />
                </div>
            </div>

            <div>
                <label className="label-text">Description (optional)</label>
                <div className="relative">
                    <FileText className="absolute left-3.5 top-3 text-zinc-500 w-4 h-4" />
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Add a description..."
                        rows={3}
                        className="input-field input-with-icon resize-none"
                    />
                </div>
            </div>

            <div>
                <label className="label-text flex items-center gap-2">
                    <Palette className="w-4 h-4" />
                    Color Tag
                </label>
                <div className="flex gap-2 mt-2">
                    {colors.map((color) => (
                        <button
                            key={color}
                            type="button"
                            onClick={() => setTag(tag === color ? null : color)}
                            className={`w-8 h-8 rounded-lg ${colorDisplayClasses[color]} transition-all ${tag === color
                                    ? 'ring-2 ring-offset-2 ring-offset-zinc-900 ring-white scale-110'
                                    : 'opacity-50 hover:opacity-80'
                                }`}
                            title={color}
                        />
                    ))}
                </div>
                <p className="text-xs text-zinc-500 mt-2">
                    {tag ? `Selected: ${tag}` : 'No color selected'}
                </p>
            </div>

            <div className="flex gap-3 pt-2">
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                    Cancel
                </button>
                <button type="submit" disabled={loading} className="btn-primary flex-1 flex items-center justify-center gap-2">
                    {loading ? <Loader className="w-4 h-4 animate-spin" /> : (isEdit ? 'Update' : 'Add Category')}
                </button>
            </div>
        </form>
    );
}
