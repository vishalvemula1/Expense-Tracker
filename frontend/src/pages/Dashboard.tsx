import { useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  CreditCard,
  Calendar,
  ArrowRight,
} from 'lucide-react';
import { Card } from '@/components/Card';
import { Loading } from '@/components/Loading';
import { Badge } from '@/components/Badge';
import { useAuthStore } from '@/store/auth';
import { useDataStore } from '@/store/data';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { startOfMonth, endOfMonth, isWithinInterval, parseISO } from 'date-fns';

const CHART_COLORS = [
  '#0ea5e9',
  '#8b5cf6',
  '#ec4899',
  '#f59e0b',
  '#10b981',
  '#ef4444',
  '#6366f1',
  '#14b8a6',
];

export function Dashboard() {
  const { user } = useAuthStore();
  const { categories, expenses, fetchCategories, fetchExpenses, isLoading } = useDataStore();

  useEffect(() => {
    fetchCategories();
    fetchExpenses(10); // Fetch 10 most recent expenses
  }, [fetchCategories, fetchExpenses]);

  // Calculate current month expenses
  const currentMonthExpenses = useMemo(() => {
    const now = new Date();
    const start = startOfMonth(now);
    const end = endOfMonth(now);

    return expenses.filter((expense) => {
      try {
        const expenseDate = parseISO(expense.created_at);
        return isWithinInterval(expenseDate, { start, end });
      } catch {
        return false;
      }
    });
  }, [expenses]);

  const totalSpent = useMemo(() => {
    return currentMonthExpenses.reduce((sum, expense) => sum + expense.amount, 0);
  }, [currentMonthExpenses]);

  const remainingBudget = (user?.salary || 0) - totalSpent;
  const spentPercentage = user?.salary ? (totalSpent / user.salary) * 100 : 0;

  // Category-wise spending
  const categorySpending = useMemo(() => {
    const spending = new Map<number, { name: string; amount: number; tag: string }>();

    currentMonthExpenses.forEach((expense) => {
      const category = categories.find((c) => c.id === expense.category_id);
      if (category) {
        const current = spending.get(category.id) || {
          name: category.name,
          amount: 0,
          tag: category.tag,
        };
        spending.set(category.id, {
          ...current,
          amount: current.amount + expense.amount,
        });
      }
    });

    return Array.from(spending.values()).sort((a, b) => b.amount - a.amount);
  }, [currentMonthExpenses, categories]);

  const pieChartData = categorySpending.map((item) => ({
    name: item.name,
    value: item.amount,
  }));

  if (isLoading && categories.length === 0) {
    return <Loading />;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.username}! Here's your expense overview.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Monthly Salary</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {formatCurrency(user?.salary || 0)}
                </p>
              </div>
              <div className="rounded-full bg-primary-100 p-3">
                <Wallet className="h-8 w-8 text-primary-600" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Spent</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {formatCurrency(totalSpent)}
                </p>
                <div className="mt-2 flex items-center gap-1 text-sm">
                  {spentPercentage > 80 ? (
                    <>
                      <TrendingUp className="h-4 w-4 text-red-600" />
                      <span className="text-red-600">{spentPercentage.toFixed(1)}% of salary</span>
                    </>
                  ) : (
                    <>
                      <TrendingDown className="h-4 w-4 text-green-600" />
                      <span className="text-green-600">{spentPercentage.toFixed(1)}% of salary</span>
                    </>
                  )}
                </div>
              </div>
              <div className="rounded-full bg-red-100 p-3">
                <CreditCard className="h-8 w-8 text-red-600" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Remaining Budget</p>
                <p
                  className={`mt-2 text-3xl font-bold ${
                    remainingBudget < 0 ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {formatCurrency(remainingBudget)}
                </p>
              </div>
              <div
                className={`rounded-full p-3 ${
                  remainingBudget < 0 ? 'bg-red-100' : 'bg-green-100'
                }`}
              >
                <Calendar
                  className={`h-8 w-8 ${remainingBudget < 0 ? 'text-red-600' : 'text-green-600'}`}
                />
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Charts and Recent Expenses */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Category Pie Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <h2 className="text-lg font-semibold text-gray-900">Spending by Category</h2>
            {pieChartData.length > 0 ? (
              <div className="mt-6">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieChartData.map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={CHART_COLORS[index % CHART_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(value as number)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-6 space-y-3">
                  {categorySpending.slice(0, 5).map((cat, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className="h-3 w-3 rounded-full"
                          style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                        />
                        <span className="text-sm text-gray-700">{cat.name}</span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {formatCurrency(cat.amount)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-gray-500">
                No expenses this month
              </div>
            )}
          </Card>
        </motion.div>

        {/* Recent Expenses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Recent Expenses</h2>
              <Link
                to="/expenses"
                className="flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                View all
                <ArrowRight size={16} />
              </Link>
            </div>
            {expenses.length > 0 ? (
              <div className="mt-6 space-y-4">
                {expenses.slice(0, 5).map((expense) => {
                  const category = categories.find((c) => c.id === expense.category_id);
                  return (
                    <div
                      key={expense.id}
                      className="flex items-center justify-between border-b border-gray-100 pb-3 last:border-0 last:pb-0"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{expense.name}</p>
                        <div className="mt-1 flex items-center gap-2">
                          {category && <Badge color={category.tag}>{category.name}</Badge>}
                          <span className="text-xs text-gray-500">
                            {formatDate(expense.created_at)}
                          </span>
                        </div>
                      </div>
                      <span className="text-lg font-semibold text-gray-900">
                        {formatCurrency(expense.amount)}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="py-12 text-center text-gray-500">No expenses yet</div>
            )}
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
