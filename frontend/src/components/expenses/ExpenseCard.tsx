import type { Expense, Category } from '../../types';
import { CategoryBadge } from '../categories/CategoryBadge';
import { Pencil, Trash2 } from 'lucide-react';

interface ExpenseCardProps {
    expense: Expense;
    category?: Category;
    onEdit: () => void;
    onDelete: () => void;
}

export function ExpenseCard({ expense, category, onEdit, onDelete }: ExpenseCardProps) {
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    const formatAmount = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    return (
        <div className="glass-panel rounded-lg p-4 card-hover group">
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-white font-medium truncate">{expense.name}</h3>
                        {category && (
                            <CategoryBadge
                                name={category.name}
                                tag={category.tag}
                                isDefault={category.is_default}
                            />
                        )}
                    </div>
                    {expense.description && (
                        <p className="text-sm text-zinc-500 line-clamp-1 mb-2">{expense.description}</p>
                    )}
                    <p className="text-xs text-zinc-600">{formatDate(expense.date_of_entry)}</p>
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-lg font-semibold text-white whitespace-nowrap">
                        {formatAmount(expense.amount)}
                    </span>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                            onClick={onEdit}
                            className="p-2 rounded-lg text-zinc-500 hover:text-white hover:bg-zinc-800 transition-colors"
                            title="Edit"
                        >
                            <Pencil size={16} />
                        </button>
                        <button
                            onClick={onDelete}
                            className="p-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                            title="Delete"
                        >
                            <Trash2 size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
