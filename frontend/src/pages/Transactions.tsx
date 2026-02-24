import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { transactionsAPI, categoriesAPI, alertsAPI } from '../services/api'
import ConfirmationModal from '../components/ConfirmationModal'

interface Transaction {
  id: number
  date: string
  description: string
  amount: number
  transaction_type: string
  account_name: string
  category: string | null
  category_id: number | null
  categorization_method: string
  is_subscription: boolean
  notes: string | null
  fingerprint: string
  imported_at: string
}

interface Category {
  id: number
  name: string
  color: string
}

interface Alert {
  id: number
  category: string
  monthly_limit: number
  is_active: boolean
  created_at: string
}

const Transactions = () => {
  const navigate = useNavigate()
  const [groupedTransactions, setGroupedTransactions] = useState<Record<string, Record<string, Transaction[]>>>({})
  const [categories, setCategories] = useState<Category[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, transactionId: 0 })
  const [editData, setEditData] = useState<{ category: string; notes: string }>({ category: '', notes: '' })
  const [showAddForm, setShowAddForm] = useState(false)
  const [newTransaction, setNewTransaction] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    amount: 0,
    transaction_type: 'debit',
    account_name: '',
    notes: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [transactionsRes, categoriesRes, alertsRes] = await Promise.all([
        transactionsAPI.getAll(),
        categoriesAPI.getAll(),
        alertsAPI.getAll(),
      ])
      const txns = transactionsRes.data.items
      setCategories(categoriesRes.data)
      setAlerts(alertsRes.data)

      // Group transactions by year and month
      const grouped: Record<string, Record<string, Transaction[]>> = {}
      txns.forEach((txn: Transaction) => {
        const date = new Date(txn.date)
        const year = date.getFullYear().toString()
        const month = date.toLocaleString('default', { month: 'long' })
        if (!grouped[year]) grouped[year] = {}
        if (!grouped[year][month]) grouped[year][month] = []
        grouped[year][month].push(txn)
      })
      setGroupedTransactions(grouped)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (transaction: Transaction) => {
    setEditingId(transaction.id)
    setEditData({
      category: transaction.category || '',
      notes: transaction.notes || '',
    })
  }

  const handleSave = async (id: number) => {
    try {
      await transactionsAPI.update(id, editData)
      setEditingId(null)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Failed to update transaction:', error)
    }
  }

  const handleDelete = async (id: number) => {
    setDeleteModal({ isOpen: true, transactionId: id })
  }

  const confirmDelete = async () => {
    try {
      await transactionsAPI.delete(deleteModal.transactionId)
      setDeleteModal({ isOpen: false, transactionId: 0 })
      fetchData() // Refresh data
    } catch (error) {
      console.error('Failed to delete transaction:', error)
    }
  }

  const handleEditAlert = () => {
    navigate('/alerts')
  }

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const transactionData = {
        date: new Date(newTransaction.date),
        description: newTransaction.description,
        amount: newTransaction.amount,
        transaction_type: newTransaction.transaction_type === 'income' ? 'credit' : 'debit',
        account_name: newTransaction.account_name,
        notes: newTransaction.notes,
      }
      await transactionsAPI.create(transactionData)
      setShowAddForm(false)
      setNewTransaction({
        date: new Date().toISOString().split('T')[0],
        description: '',
        amount: 0,
        transaction_type: 'debit',
        account_name: '',
        notes: '',
      })
      fetchData() // Refresh data
    } catch (error) {
      console.error('Failed to add transaction:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-display font-bold text-finance-text-primary mb-2">Transactions</h1>
          <p className="text-finance-text-secondary">View and manage all your transactions</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary"
        >
          + Add Transaction
        </button>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-finance-card/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-finance-text-secondary uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-finance-text-secondary uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-finance-text-secondary uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Account
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-finance-card divide-y divide-gray-200 dark:divide-gray-700">
              {Object.keys(groupedTransactions).sort((a, b) => parseInt(b) - parseInt(a)).map((year) => (
                <React.Fragment key={year}>
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-lg font-bold text-finance-text-primary bg-gray-100 dark:bg-gray-800">
                      {year}
                    </td>
                  </tr>
                  {Object.keys(groupedTransactions[year]).sort((a, b) => new Date(`${a} 1, ${year}`).getTime() - new Date(`${b} 1, ${year}`).getTime()).reverse().map((month) => (
                    <React.Fragment key={`${year}-${month}`}>
                      <tr>
                        <td colSpan={6} className="px-6 py-2 text-md font-semibold text-finance-text-secondary bg-gray-50 dark:bg-gray-700">
                          {month} {year}
                        </td>
                      </tr>
                      {groupedTransactions[year][month].map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {new Date(transaction.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    <div>
                      <div className="font-medium">{transaction.description}</div>
                      {transaction.is_subscription && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                          Subscription
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`font-medium ${
                      transaction.transaction_type === 'credit' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.transaction_type === 'credit' ? '+' : '-'}${transaction.amount.toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {editingId === transaction.id ? (
                      <select
                        value={editData.category}
                        onChange={(e) => setEditData({ ...editData, category: e.target.value })}
                        className="block w-full px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      >
                        <option value="">Uncategorized</option>
                        {categories.map((cat) => (
                          <option key={cat.id} value={cat.name}>
                            {cat.name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        transaction.category
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {transaction.category || 'Uncategorized'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {transaction.account_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    {editingId === transaction.id ? (
                      <>
                        <button
                          onClick={() => handleSave(transaction.id)}
                          className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300"
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => handleEdit(transaction)}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                        >
                          Edit
                        </button>
                        {transaction.category && alerts.some(a => a.category === transaction.category) && (
                          <button
                            onClick={() => handleEditAlert()}
                            className="text-purple-600 hover:text-purple-900 dark:text-purple-400 dark:hover:text-purple-300"
                            title="Edit alert for this category"
                          >
                            Alert
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(transaction.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </td>
                </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Transaction Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="card w-full max-w-md mx-4 animate-slide-in">
            <h2 className="text-2xl font-display font-bold text-finance-text-primary mb-6">Add New Transaction</h2>
            <form onSubmit={handleAddTransaction} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-finance-text-primary mb-2">
                  Date
                </label>
                <input
                  type="date"
                  value={newTransaction.date}
                  onChange={(e) => setNewTransaction({ ...newTransaction, date: e.target.value })}
                  className="w-full px-3 py-2.5 bg-finance-bg border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-finance-accent focus:border-transparent text-finance-text-primary transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-finance-text-primary mb-2">
                  Description
                </label>
                <input
                  type="text"
                  value={newTransaction.description}
                  onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
                  className="w-full px-3 py-2.5 bg-finance-bg border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-finance-accent focus:border-transparent text-finance-text-primary transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-finance-text-primary mb-2">
                  Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newTransaction.amount}
                  onChange={(e) => setNewTransaction({ ...newTransaction, amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2.5 bg-finance-bg border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-finance-accent focus:border-transparent text-finance-text-primary transition-all duration-200"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-finance-text-primary mb-2">
                  Type
                </label>
                <select
                  value={newTransaction.transaction_type === 'credit' ? 'income' : 'expense'}
                  onChange={(e) => setNewTransaction({ ...newTransaction, transaction_type: e.target.value === 'income' ? 'credit' : 'debit' })}
                  className="w-full px-3 py-2.5 bg-finance-bg border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-finance-accent focus:border-transparent text-finance-text-primary transition-all duration-200"
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-finance-text-primary mb-2">
                  Account
                </label>
                <input
                  type="text"
                  value={newTransaction.account_name}
                  onChange={(e) => setNewTransaction({ ...newTransaction, account_name: e.target.value })}
                  className="w-full px-3 py-2.5 bg-finance-bg border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-finance-accent focus:border-transparent text-finance-text-primary transition-all duration-200"
                  placeholder="e.g., Checking, Savings"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-finance-text-primary mb-2">
                  Notes
                </label>
                <textarea
                  value={newTransaction.notes}
                  onChange={(e) => setNewTransaction({ ...newTransaction, notes: e.target.value })}
                  className="w-full px-3 py-2.5 bg-finance-bg border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-finance-accent focus:border-transparent text-finance-text-primary transition-all duration-200 resize-none"
                  rows={3}
                  placeholder="Optional notes..."
                />
              </div>
              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-700">
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  Add Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmationModal
        isOpen={deleteModal.isOpen}
        title="Delete Transaction"
        message="Are you sure you want to delete this transaction? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        isDangerous={true}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteModal({ isOpen: false, transactionId: 0 })}
      />
    </div>
  )
}

export default Transactions