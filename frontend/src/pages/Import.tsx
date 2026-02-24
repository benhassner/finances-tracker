import { useState } from 'react'
import { importAPI } from '../services/api'

const Import = () => {
  const [file, setFile] = useState<File | null>(null)
  const [accountName, setAccountName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setUploading(true)
    setResult(null)

    try {
      const response = await importAPI.uploadCSV(file, accountName || undefined)
      setResult(response.data)
    } catch (error: any) {
      setResult({
        status: 'error',
        message: error.response?.data?.detail || 'Import failed',
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Import Transactions</h1>

      <div className="bg-white dark:bg-finance-card shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-finance-text-primary mb-4">
            Upload CSV File
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="file" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                CSV File
              </label>
              <input
                type="file"
                id="file"
                accept=".csv"
                onChange={handleFileChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                required
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Supported formats: Chase, Bank of America, Wells Fargo, or generic CSV with date, description, amount columns.
              </p>
            </div>

            <div>
              <label htmlFor="account" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Account Name (Optional)
              </label>
              <input
                type="text"
                id="account"
                value={accountName}
                onChange={(e) => setAccountName(e.target.value)}
                placeholder="e.g., Chase Checking"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={!file || uploading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-finance-accent hover:bg-finance-highlight focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-finance-accent disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : 'Import Transactions'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {result && (
        <div className={`rounded-md p-4 ${
          result.status === 'error'
            ? 'bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700'
            : 'bg-green-50 dark:bg-green-900/20 border border-green-300 dark:border-green-700'
        }`}>
          <div className="flex">
            <div className="ml-3">
              <h3 className={`text-sm font-medium ${
                result.status === 'error'
                  ? 'text-red-800 dark:text-red-200'
                  : 'text-green-800 dark:text-green-200'
              }`}>
                {result.status === 'error' ? 'Import Failed' : 'Import Successful'}
              </h3>
              <div className={`mt-2 text-sm ${
                result.status === 'error'
                  ? 'text-red-700 dark:text-red-300'
                  : 'text-green-700 dark:text-green-300'
              }`}>
                {result.status === 'error' ? (
                  <p>{result.message}</p>
                ) : (
                  <div>
                    <p>Imported: {result.imported} transactions</p>
                    <p>Duplicates skipped: {result.duplicates}</p>
                    {result.errors > 0 && <p>Errors: {result.errors}</p>}
                    {result.messages && result.messages.length > 0 && (
                      <ul className="mt-2 list-disc list-inside">
                        {result.messages.map((msg: string, idx: number) => (
                          <li key={idx}>{msg}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}

export default Import