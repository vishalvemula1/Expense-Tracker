import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User as UserIcon, Mail, DollarSign, Lock, Trash2, Save, AlertCircle } from 'lucide-react';
import { Card } from '@/components/Card';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { useAuthStore } from '@/store/auth';
import { apiClient } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';

export function Profile() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    salary: user?.salary.toString() || '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password && formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    const salary = parseFloat(formData.salary);
    if (isNaN(salary) || salary < 0) {
      setError('Please enter a valid salary');
      return;
    }

    setIsLoading(true);
    try {
      // Only send changed fields
      const updates: any = {};
      if (formData.username !== user?.username) updates.username = formData.username;
      if (formData.email !== user?.email) updates.email = formData.email;
      if (salary !== user?.salary) updates.salary = salary;
      if (formData.password) updates.password = formData.password;

      await apiClient.updateMe(updates);

      setSuccess('Profile updated successfully');
      setIsEditing(false);
      setFormData((prev) => ({ ...prev, password: '', confirmPassword: '' }));

      // Refresh user data
      const updatedUser = await apiClient.getMe();
      useAuthStore.setState({ user: updatedUser });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update profile';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsLoading(true);
    try {
      await apiClient.deleteMe();
      logout();
      navigate('/login');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete account';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setError('');
    setSuccess('');
    setFormData({
      username: user?.username || '',
      email: user?.email || '',
      salary: user?.salary.toString() || '',
      password: '',
      confirmPassword: '',
    });
  };

  if (!user) {
    return null;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <p className="mt-2 text-gray-600">Manage your account settings</p>
      </div>

      {/* Messages */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 rounded-lg bg-red-50 p-4 text-sm text-red-800"
        >
          <AlertCircle size={18} />
          <span>{error}</span>
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 rounded-lg bg-green-50 p-4 text-sm text-green-800"
        >
          <AlertCircle size={18} />
          <span>{success}</span>
        </motion.div>
      )}

      {/* Profile Card */}
      <Card>
        <div className="flex items-center justify-between border-b border-gray-100 pb-4">
          <h2 className="text-xl font-semibold text-gray-900">Account Information</h2>
          {!isEditing && (
            <button onClick={() => setIsEditing(true)} className="btn btn-primary">
              Edit Profile
            </button>
          )}
        </div>

        {isEditing ? (
          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div>
              <label htmlFor="username" className="label">
                Username
              </label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="label">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label htmlFor="salary" className="label">
                Monthly Salary
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="number"
                  id="salary"
                  name="salary"
                  value={formData.salary}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                  className="input pl-10"
                />
              </div>
            </div>

            <div className="border-t border-gray-100 pt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Change Password (Optional)</h3>

              <div className="space-y-4">
                <div>
                  <label htmlFor="password" className="label">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="password"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      minLength={6}
                      className="input pl-10"
                      placeholder="Leave blank to keep current password"
                    />
                  </div>
                </div>

                {formData.password && (
                  <div>
                    <label htmlFor="confirmPassword" className="label">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        minLength={6}
                        className="input pl-10"
                        placeholder="Confirm your new password"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={handleCancel}
                className="btn btn-secondary"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary flex items-center gap-2"
                disabled={isLoading}
              >
                <Save size={18} />
                Save Changes
              </button>
            </div>
          </form>
        ) : (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-3 py-3">
              <UserIcon className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Username</p>
                <p className="font-medium text-gray-900">{user.username}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 py-3">
              <Mail className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium text-gray-900">{user.email}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 py-3">
              <DollarSign className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Monthly Salary</p>
                <p className="font-medium text-gray-900">{formatCurrency(user.salary)}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 py-3">
              <Lock className="h-5 w-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-600">Password</p>
                <p className="font-medium text-gray-900">••••••••</p>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-4">
              <p className="text-xs text-gray-500">
                Member since {formatDate(user.created_at)}
              </p>
            </div>
          </div>
        )}
      </Card>

      {/* Danger Zone */}
      {!isEditing && (
        <Card>
          <div className="border-l-4 border-red-500 pl-4">
            <h3 className="text-lg font-semibold text-gray-900">Danger Zone</h3>
            <p className="mt-2 text-sm text-gray-600">
              Once you delete your account, there is no going back. All your data will be
              permanently deleted.
            </p>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="btn btn-danger mt-4 flex items-center gap-2"
            >
              <Trash2 size={18} />
              Delete Account
            </button>
          </div>
        </Card>
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteAccount}
        title="Delete Account"
        message="Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently deleted."
        confirmText="Delete Account"
        variant="danger"
      />
    </div>
  );
}
