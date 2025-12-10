import type { Color } from '../../types';

interface CategoryBadgeProps {
    name: string;
    tag: Color | null;
    isDefault?: boolean;
    size?: 'sm' | 'md';
}

const colorClasses: Record<Color, string> = {
    Blue: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    Red: 'bg-red-500/15 text-red-400 border-red-500/30',
    Black: 'bg-zinc-700/50 text-zinc-300 border-zinc-600/50',
    White: 'bg-white/10 text-white border-white/20',
};

export function CategoryBadge({ name, tag, isDefault, size = 'sm' }: CategoryBadgeProps) {
    const colorClass = tag ? colorClasses[tag] : 'bg-zinc-800 text-zinc-400 border-zinc-700';
    const sizeClass = size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-sm';

    return (
        <span className={`inline-flex items-center gap-1.5 rounded-md border font-medium ${colorClass} ${sizeClass}`}>
            {isDefault && (
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
            )}
            {name}
        </span>
    );
}
