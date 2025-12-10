import { useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Lock, User, Loader } from 'lucide-react';

export function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            await login(response.data.access_token);
            navigate('/dashboard');
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 animate-fadeIn">
            <div className="glass-panel-solid p-8 rounded-xl w-full max-w-sm space-y-6">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-white">Welcome back</h2>
                    <p className="text-zinc-500 mt-1 text-sm">Sign in to your account</p>
                </div>

                {error && (
                    <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="label-text">Username</label>
                        <div className="relative">
                            <User className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter username"
                                required
                                className="input-field input-with-icon"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="label-text">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter password"
                                required
                                className="input-field input-with-icon"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${loading
                                ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed'
                                : 'btn-primary'
                            }`}
                    >
                        {loading ? <Loader className="w-4 h-4 animate-spin" /> : 'Sign In'}
                    </button>
                </form>

                <div className="text-center text-sm text-zinc-500">
                    Don't have an account?{' '}
                    <Link to="/register" className="text-white hover:underline">
                        Create one
                    </Link>
                </div>
            </div>
        </div>
    );
}
