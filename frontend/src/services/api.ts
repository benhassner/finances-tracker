import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Categories
export const categoriesAPI = {
  getAll: () => api.get('/categories'),
  create: (data: any) => api.post('/categories', data),
  update: (id: number, data: any) => api.put(`/categories/${id}`, data),
  delete: (id: number) => api.delete(`/categories/${id}`),
}

// Transactions
export const transactionsAPI = {
  getAll: (params?: any) => api.get('/transactions', { params }),
  getById: (id: number) => api.get(`/transactions/${id}`),
  create: (data: any) => api.post('/transactions', data),
  update: (id: number, data: any) => api.put(`/transactions/${id}`, data),
  delete: (id: number) => api.delete(`/transactions/${id}`),
}

// Rules
export const rulesAPI = {
  getAll: () => api.get('/rules'),
  create: (data: any) => api.post('/rules', data),
  update: (id: number, data: any) => api.put(`/rules/${id}`, data),
  delete: (id: number) => api.delete(`/rules/${id}`),
}

// Alerts
export const alertsAPI = {
  getAll: () => api.get('/alerts'),
  create: (data: any) => api.post('/alerts', data),
  update: (id: number, data: any) => api.put(`/alerts/${id}`, data),
  delete: (id: number) => api.delete(`/alerts/${id}`),
}

// Analytics
export const analyticsAPI = {
  getDashboard: () => api.get('/dashboard'),
  getSubscriptions: () => api.get('/subscriptions'),
  getProjection: (params: any) => api.get('/projection', { params }),
  getMonthlySummaries: (limit?: number) => api.get('/monthly-summaries', { params: { limit } }),
}

// Import
export const importAPI = {
  uploadCSV: (file: File, accountName?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (accountName) {
      formData.append('account_name', accountName)
    }
    return api.post('/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

// ML
export const mlAPI = {
  retrain: () => api.post('/retrain'),
}

// Jobs (Income entries)
export const jobsAPI = {
  getAll: () => api.get('/jobs'),
  create: (data: any) => api.post('/jobs', data),
  update: (id: number, data: any) => api.put(`/jobs/${id}`, data),
  delete: (id: number) => api.delete(`/jobs/${id}`),
}

export default api