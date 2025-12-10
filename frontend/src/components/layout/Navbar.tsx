import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, LogOut, Wallet, FolderOpen, User as UserIcon } from 'lucide-react';

export function Navbar() {
    const { isAuthenticated, logout, user } = useAuth();
    const location = useLocation();

    const NavItem = ({ to, icon: Icon, label }: { to: string; icon: React.ElementType; label: string }) => {
        const isActive = location.pathname === to;
        return (
            <Link
                to={to}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                        ? 'bg-white text-black'
                        : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
                    }`}
            >
                <Icon size={16} />
                <span className="hidden sm:inline">{label}</span>
            </Link>
        );
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3 border-b border-zinc-900 bg-black/95 backdrop-blur-sm">
            <div className="max-w-6xl mx-auto flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-md bg-white flex items-center justify-center">
                        <Wallet className="text-black w-4 h-4" />
                    </div>
                    <span className="text-lg font-semibold text-white hidden sm:block">
                        Tracker
                    </span>
                </Link>

                {isAuthenticated ? (
                    <div className="flex items-center gap-2">
                        <NavItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
                        <NavItem to="/expenses" icon={Wallet} label="Expenses" />
                        <NavItem to="/categories" icon={FolderOpen} label="Categories" />

                        <div className="w-px h-5 bg-zinc-800 mx-2" />

                        <div className="flex items-center gap-2">
                            <div className="flex items-center gap-2 text-sm text-zinc-400">
                                <div className="w-7 h-7 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center">
                                    <UserIcon size={14} />
                                </div>
                                <span className="hidden sm:inline">{user?.username}</span>
                            </div>
                            <button
                                onClick={logout}
                                className="p-2 rounded-lg hover:bg-zinc-900 text-zinc-500 hover:text-red-400 transition-colors"
                                title="Logout"
                            >
                                <LogOut size={16} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-3">
                        <Link to="/login" className="text-sm text-zinc-400 hover:text-white transition-colors">
                            Sign In
                        </Link>
                        <Link to="/register" className="btn-primary text-sm px-4 py-2">
                            Get Started
                        </Link>
                    </div>
                )}
            </div>
        </nav>
    );
}
