'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await fetch('http://localhost:8002/analyze-site', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          auto_implement: true,
          content_types: ['text', 'image', 'video'],
          schedule_monitoring: true
        }),
      })
      
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Error:', error)
      setResult({ error: 'خطا در ارتباط با سرور' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">
          AI Content Factory Pro
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">
            تحلیل و بهینه‌سازی سایت
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="url" className="block mb-2 font-medium">
                آدرس سایت:
              </label>
              <input
                type="text"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading || !url}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'در حال پردازش...' : 'شروع تحلیل'}
            </button>
          </form>
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4">نتایج:</h3>
            <pre className="bg-gray-100 p-4 rounded-lg overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
            
            {result.analysis_id && (
              <Link
                href={`/dashboard/${result.analysis_id}`}
                className="mt-4 inline-block bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors"
              >
                مشاهده Dashboard
              </Link>
            )}
          </div>
        )}
      </div>
    </main>
  )
}

