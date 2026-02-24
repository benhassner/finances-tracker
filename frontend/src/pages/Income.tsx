import { useEffect, useMemo, useState } from 'react'
import { jobsAPI } from '../services/api'
import ConfirmationModal from '../components/ConfirmationModal'

interface Job {
  id: number
  name: string
  hourly_wage: number
  expected_shifts: number
  hours_per_shift: number
  ot1_5_hours: number
  ot2_hours: number
  created_at: string
}

const Income = () => {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, jobId: 0 })
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editRow, setEditRow] = useState<Partial<Job>>({})

  const [formData, setFormData] = useState({
    name: '',
    hourly_wage: '',
    expected_shifts: '',
    hours_per_shift: '',
    ot1_5_hours: '',
    ot2_hours: '',
  })
  const [submitLoading, setSubmitLoading] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const res = await jobsAPI.getAll()
      setJobs(res.data)
    } catch (e) {
      console.error('Failed to fetch jobs', e)
    } finally {
      setLoading(false)
    }
  }

  const computeTotal = (j: Partial<Job>): number => {
    const w = Number(j.hourly_wage || 0)
    const s = Number(j.expected_shifts || 0)
    const h = Number(j.hours_per_shift || 0)
    const ot1 = Number(j.ot1_5_hours || 0)
    const ot2 = Number(j.ot2_hours || 0)
    return w * s * h + w * ot1 * 1.5 + w * ot2 * 2
  }

  const totalAll = useMemo(() => jobs.reduce((sum, j) => sum + computeTotal(j), 0), [jobs])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitError(null)
    setSubmitLoading(true)
    try {
      const num = (v: string, def = 0) => {
        const n = Number(v)
        return Number.isFinite(n) ? n : def
      }
      const payload = {
        name: formData.name.trim(),
        hourly_wage: Math.max(0, num(formData.hourly_wage, 0)),
        expected_shifts: Math.max(0, Math.trunc(num(formData.expected_shifts, 0))),
        hours_per_shift: Math.max(0, num(formData.hours_per_shift, 0)),
        ot1_5_hours: Math.max(0, num(formData.ot1_5_hours, 0)),
        ot2_hours: Math.max(0, num(formData.ot2_hours, 0)),
      }
      if (!payload.name || payload.hourly_wage <= 0 || payload.expected_shifts < 0 || payload.hours_per_shift <= 0) {
        setSubmitError('Please fill out Job Name, Hourly Wage (> 0), and Hours per Shift (> 0).')
        setSubmitLoading(false)
        return
      }
      await jobsAPI.create(payload)
      setFormData({ name: '', hourly_wage: '', expected_shifts: '', hours_per_shift: '', ot1_5_hours: '', ot2_hours: '' })
      setShowForm(false)
      fetchJobs()
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Failed to create job.'
      setSubmitError(typeof msg === 'string' ? msg : 'Failed to create job.')
      console.error('Failed to create job', e?.response?.data || e)
    } finally {
      setSubmitLoading(false)
    }
  }

  const startEdit = (job: Job) => {
    setEditingId(job.id)
    setEditRow({ ...job })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditRow({})
  }

  const saveEdit = async () => {
    if (editingId == null) return
    try {
      const payload = {
        name: (editRow.name || '').toString(),
        hourly_wage: Number(editRow.hourly_wage || 0),
        expected_shifts: Number(editRow.expected_shifts || 0),
        hours_per_shift: Number(editRow.hours_per_shift || 0),
        ot1_5_hours: Number(editRow.ot1_5_hours || 0),
        ot2_hours: Number(editRow.ot2_hours || 0),
      }
      await jobsAPI.update(editingId, payload)
      setEditingId(null)
      setEditRow({})
      fetchJobs()
    } catch (e) {
      console.error('Failed to update job', e)
    }
  }

  const confirmDelete = async () => {
    try {
      await jobsAPI.delete(deleteModal.jobId)
      setDeleteModal({ isOpen: false, jobId: 0 })
      fetchJobs()
    } catch (e) {
      console.error('Failed to delete job', e)
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Income</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-finance-accent hover:bg-finance-highlight text-white px-4 py-2 rounded-md"
        >
          {showForm ? 'Cancel' : 'Add Job'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white dark:bg-finance-card shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">Add Job</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              {submitError && (
                <div className="text-red-600 dark:text-red-400 text-sm">{submitError}</div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Job Name</label>
                  <input type="text" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Hourly Wage</label>
                  <input type="number" min="0" step="0.01" value={formData.hourly_wage} onChange={e => setFormData({ ...formData, hourly_wage: e.target.value })} required className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Expected Shifts (per month)</label>
                  <input type="number" min="0" step="1" value={formData.expected_shifts} onChange={e => setFormData({ ...formData, expected_shifts: e.target.value })} required className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Hours per Shift</label>
                  <input type="number" min="0" step="0.25" value={formData.hours_per_shift} onChange={e => setFormData({ ...formData, hours_per_shift: e.target.value })} required className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">OT1.5 (hours)</label>
                  <input type="number" min="0" step="0.25" value={formData.ot1_5_hours} onChange={e => setFormData({ ...formData, ot1_5_hours: e.target.value })} className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">OT2 (hours)</label>
                  <input type="number" min="0" step="0.25" value={formData.ot2_hours} onChange={e => setFormData({ ...formData, ot2_hours: e.target.value })} className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white" />
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <button type="button" onClick={() => setShowForm(false)} className="bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-md">Cancel</button>
                <button type="submit" disabled={submitLoading} className={`px-4 py-2 rounded-md text-white ${submitLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-finance-accent hover:bg-finance-highlight'}`}>
                  {submitLoading ? 'Adding…' : 'Add Job'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-finance-card shadow overflow-hidden sm:rounded-md">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Job</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Hourly Wage</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Exp. Shifts</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Hours/Shift</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">OT1.5 (hrs)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">OT2 (hrs)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total Monthly Income</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-finance-card divide-y divide-gray-200 dark:divide-gray-700">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  {/* Job Name */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      <input type="text" value={editRow.name as string || ''} onChange={e => setEditRow({ ...editRow, name: e.target.value })} className="w-40 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" />
                    ) : (
                      job.name
                    )}
                  </td>
                  {/* Hourly Wage */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      <input type="number" min="0" step="0.01" value={Number(editRow.hourly_wage ?? job.hourly_wage)} onChange={e => setEditRow({ ...editRow, hourly_wage: parseFloat(e.target.value) })} className="w-28 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" />
                    ) : (
                      `$${job.hourly_wage.toFixed(2)}`
                    )}
                  </td>
                  {/* Expected Shifts */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      <input type="number" min="0" step="1" value={Number(editRow.expected_shifts ?? job.expected_shifts)} onChange={e => setEditRow({ ...editRow, expected_shifts: parseInt(e.target.value) })} className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" />
                    ) : (
                      job.expected_shifts
                    )}
                  </td>
                  {/* Hours/Shift */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      <input type="number" min="0" step="0.25" value={Number(editRow.hours_per_shift ?? job.hours_per_shift)} onChange={e => setEditRow({ ...editRow, hours_per_shift: parseFloat(e.target.value) })} className="w-24 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" />
                    ) : (
                      job.hours_per_shift
                    )}
                  </td>
                  {/* OT1.5 */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      <input type="number" min="0" step="0.25" value={Number(editRow.ot1_5_hours ?? job.ot1_5_hours)} onChange={e => setEditRow({ ...editRow, ot1_5_hours: parseFloat(e.target.value) })} className="w-24 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" />
                    ) : (
                      job.ot1_5_hours
                    )}
                  </td>
                  {/* OT2 */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      <input type="number" min="0" step="0.25" value={Number(editRow.ot2_hours ?? job.ot2_hours)} onChange={e => setEditRow({ ...editRow, ot2_hours: parseFloat(e.target.value) })} className="w-24 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white" />
                    ) : (
                      job.ot2_hours
                    )}
                  </td>
                  {/* Total Monthly Income */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {editingId === job.id ? (
                      `$${computeTotal(editRow).toFixed(2)}`
                    ) : (
                      `$${computeTotal(job).toFixed(2)}`
                    )}
                  </td>
                  {/* Actions */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                    {editingId === job.id ? (
                      <>
                        <button onClick={saveEdit} className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300">Save</button>
                        <button onClick={cancelEdit} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">Cancel</button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => startEdit(job)} className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">Edit</button>
                        <button onClick={() => setDeleteModal({ isOpen: true, jobId: job.id })} className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <td colSpan={6} className="px-6 py-3 text-right text-sm font-semibold text-gray-700 dark:text-gray-200">Total</td>
                <td className="px-6 py-3 text-sm font-bold text-gray-900 dark:text-white">${totalAll.toFixed(2)}</td>
                <td className="px-6 py-3"></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {jobs.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No jobs added yet.</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">Use "Add Job" to enter your income sources.</p>
        </div>
      )}

      <ConfirmationModal
        isOpen={deleteModal.isOpen}
        title="Delete Job"
        message="Are you sure you want to delete this job? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        isDangerous={true}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteModal({ isOpen: false, jobId: 0 })}
      />
    </div>
  )
}

export default Income
