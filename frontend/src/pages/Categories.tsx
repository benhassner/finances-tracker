import { useEffect, useState } from 'react'
import { categoriesAPI, alertsAPI } from '../services/api'
import CategoryIcon from '../components/CategoryIcon'
import ConfirmationModal from '../components/ConfirmationModal'

interface Category {
  id: number
  name: string
  color: string
  icon: string
  budget_limit: number | null
  created_at: string
}

interface Alert {
  id: number
  category: string
  monthly_limit: number
  is_active: boolean
  created_at: string
}

const Categories = () => {
  const [categories, setCategories] = useState<Category[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, categoryId: 0 })
  const [formData, setFormData] = useState({
    name: '',
    color: '#6366f1',
    icon: 'tag',
    budget_limit: '',
  })

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const [categoriesRes, alertsRes] = await Promise.all([
        categoriesAPI.getAll(),
        alertsAPI.getAll(),
      ])
      setCategories(categoriesRes.data)
      setAlerts(alertsRes.data)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const data = {
        ...formData,
        budget_limit: formData.budget_limit ? parseFloat(formData.budget_limit) : null,
      }
      await categoriesAPI.create(data)
      setFormData({ name: '', color: '#6366f1', icon: 'tag', budget_limit: '' })
      setShowForm(false)
      fetchCategories()
    } catch (error) {
      console.error('Failed to create category:', error)
    }
  }

  const handleDelete = async (id: number) => {
    setDeleteModal({ isOpen: true, categoryId: id })
  }

  const confirmDelete = async () => {
    try {
      await categoriesAPI.delete(deleteModal.categoryId)
      setDeleteModal({ isOpen: false, categoryId: 0 })
      fetchCategories()
    } catch (error) {
      console.error('Failed to delete category:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Build a quick lookup for alerts by category name
  const alertsByCategory: Record<string, Alert> = alerts.reduce((acc, a) => {
    // If multiple alerts exist for a category, keep the first encountered
    if (!acc[a.category]) acc[a.category] = a
    return acc
  }, {} as Record<string, Alert>)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Categories</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-finance-accent hover:bg-finance-highlight text-white px-4 py-2 rounded-md"
        >
          {showForm ? 'Cancel' : 'Add Category'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white dark:bg-finance-card shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
              Add New Category
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Groceries"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="color" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Color
                  </label>
                  <input
                    type="color"
                    id="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    className="mt-1 block w-full h-10 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label htmlFor="icon" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Icon
                  </label>
                  <select
                    id="icon"
                    value={formData.icon}
                    onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="tag">Tag</option>
                    <option value="shopping-cart">Shopping Cart</option>
                    <option value="utensils">Utensils</option>
                    <option value="car">Car</option>
                    <option value="home">Home</option>
                    <option value="dollar-sign">Dollar Sign</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="budget_limit" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Monthly Budget Limit (Optional)
                  </label>
                  <input
                    type="number"
                    id="budget_limit"
                    value={formData.budget_limit}
                    onChange={(e) => setFormData({ ...formData, budget_limit: e.target.value })}
                    placeholder="e.g., 500"
                    min="0"
                    step="0.01"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-finance-accent hover:bg-finance-highlight text-white px-4 py-2 rounded-md"
                >
                  Add Category
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map((category) => (
          <div key={category.id} className="bg-white dark:bg-finance-card shadow sm:rounded-lg">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center text-white"
                    style={{ backgroundColor: category.color }}
                  >
                    <CategoryIcon category={category.name} className="w-7 h-7" />
                  </div>
                  <h3 className="ml-3 text-lg font-medium text-gray-900 dark:text-white">
                    {category.name}
                  </h3>
                </div>
                <button
                  onClick={() => handleDelete(category.id)}
                  className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              {alertsByCategory[category.name] && (
                <div className="mt-4">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Budget: ${alertsByCategory[category.name].monthly_limit.toFixed(2)}/month
                  </p>
                </div>
              )}
              <div className="mt-4">
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  Created {new Date(category.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <ConfirmationModal
        isOpen={deleteModal.isOpen}
        title="Delete Category"
        message="Are you sure you want to delete this category? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        isDangerous={true}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteModal({ isOpen: false, categoryId: 0 })}
      />
    </div>
  )
}

export default Categories