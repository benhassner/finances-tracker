import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { analyticsAPI } from '../services/api'

interface DashboardData {
  current_month_income: number
  current_month_expenses: number
  current_month_net: number
  savings_rate: number
  category_breakdown: Array<{
    category: string
    total: number
    count: number
    color: string
  }>
  monthly_trends: Array<{
    year: number
    month: number
    label: string
    income: number
    expenses: number
    net: number
  }>
  alert_statuses: Array<{
    category: string
    limit: number
    spent: number
    remaining: number
    percent: number
    exceeded: boolean
    warning: boolean
  }>
}

const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await analyticsAPI.getDashboard()
        setData(response.data)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!data) {
    return <div className="text-center text-gray-500">Failed to load dashboard data</div>
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-finance-text-primary mb-2">Dashboard</h1>
        <p className="text-finance-text-secondary">Your financial overview for this month</p>
      </div>

      {/* Current Month Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="metric-card animate-slide-in" style={{ animationDelay: '0.0s' }}>
          <h3 className="metric-label">Income</h3>
          <p className="text-3xl font-bold text-finance-accent">${data.current_month_income.toFixed(2)}</p>
        </div>
        <div className="metric-card animate-slide-in" style={{ animationDelay: '0.1s' }}>
          <h3 className="metric-label">Expenses</h3>
          <p className="text-3xl font-bold text-red-400">${Math.abs(data.current_month_expenses).toFixed(2)}</p>
        </div>
        <div className="metric-card animate-slide-in" style={{ animationDelay: '0.2s' }}>
          <h3 className="metric-label">Net</h3>
          <p className="text-3xl font-bold text-purple-400">
            ${data.current_month_net.toFixed(2)}
          </p>
        </div>
        <div className="metric-card animate-slide-in" style={{ animationDelay: '0.3s' }}>
          <h3 className="metric-label">Savings Rate</h3>
          <p className="text-3xl font-bold text-finance-highlight">{data.savings_rate.toFixed(1)}%</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending by Category */}
        <div className="card p-6 animate-slide-in">
          <h3 className="text-xl font-display font-bold text-finance-text-primary mb-6">Spending by Category</h3>
          {data.category_breakdown && data.category_breakdown.length > 0 ? (
            <>
              <div className="flex justify-center">
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={data.category_breakdown.map(cat => ({ ...cat, total: Math.abs(cat.total) }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={120}
                      fill="#10b981"
                      dataKey="total"
                      nameKey="category"
                    >
                      {data.category_breakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number, name: string) => [`$${value}`, name]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                {data.category_breakdown.map((cat, idx) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full" style={{ backgroundColor: cat.color }}></div>
                    <span className="text-finance-text-secondary">{cat.category}: ${Math.abs(cat.total).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-80 flex items-center justify-center">
              <p className="text-finance-text-secondary text-center">No spending data for this month</p>
            </div>
          )}
        </div>

        {/* Monthly Trends */}
        <div className="card p-6 animate-slide-in">
          <h3 className="text-xl font-display font-bold text-finance-text-primary mb-6">Monthly Trends</h3>
          <div className="flex justify-center">
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={data.monthly_trends.map(mt => ({ ...mt, expenses: -Math.abs(mt.expenses) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis dataKey="label" stroke="#94A3B8" />
                <YAxis stroke="#94A3B8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid rgba(148, 163, 184, 0.3)', borderRadius: '8px' }}
                  formatter={(value: number, name: string) => [`$${Math.abs(value).toFixed(2)}`, name]}
                />
                <Line type="monotone" dataKey="income" stroke="#10b981" strokeOpacity={0.6} strokeWidth={2} dot={{ fill: '#10b981', r: 3 }} />
                <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeOpacity={0.6} strokeWidth={2} dot={{ fill: '#ef4444', r: 3 }} name="Expenses" />
                <Area type="monotone" dataKey="net" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {data.alert_statuses.length > 0 && (
        <div className="card p-6 animate-slide-in">
          <h3 className="text-xl font-display font-bold text-finance-text-primary mb-6">Budget Alerts</h3>
          <div className="space-y-3">
            {data.alert_statuses.map((alert, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border transition-all duration-300 ${
                  alert.exceeded
                    ? 'border-red-500/30 bg-red-500/10'
                    : alert.warning
                    ? 'border-yellow-500/30 bg-yellow-500/10'
                    : 'border-finance-highlight/30 bg-finance-highlight/10'
                }`}
              >
                <div className="flex justify-between items-center mb-3">
                  <span className="font-semibold text-finance-text-primary">{alert.category}</span>
                  <div className="flex flex-col items-end">
                    <span className={`text-lg font-bold ${
                      alert.exceeded ? 'text-red-400' : alert.warning ? 'text-yellow-400' : 'text-finance-highlight'
                    }`}>
                      ${alert.remaining?.toFixed(2) || '0.00'} remaining
                    </span>
                    <span className="text-xs text-finance-text-secondary mt-1">
                      {alert.percent?.toFixed(1) || '0.0'}% used
                    </span>
                  </div>
                </div>
                <div className="text-xs text-finance-text-secondary mb-3">
                  ${alert.spent?.toFixed(2) || '0.00'} / ${alert.limit?.toFixed(2) || '0.00'}
                </div>
                <div className="w-full bg-gray-700/50 rounded-full h-3 overflow-hidden">
                  <div
                    className="h-3 rounded-full transition-all duration-300"
                    style={{
                      width: `${Math.max(0, 100 - (alert.percent || 0))}%`,
                      backgroundColor: Math.max(0, 100 - (alert.percent || 0)) > 50 ? '#10b981' : Math.max(0, 100 - (alert.percent || 0)) > 10 ? '#f59e0b' : '#ef4444',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard