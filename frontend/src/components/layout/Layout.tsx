import type { ReactNode } from 'react';
import { Navbar } from './Navbar';

export function Layout({ children }: { children: ReactNode }) {
    return (
        <div className="min-h-screen bg-black text-white font-sans selection:bg-white/20">
            <Navbar />
            <main className="relative pt-20 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto pb-16">
                {children}
            </main>
        </div>
    );
}
