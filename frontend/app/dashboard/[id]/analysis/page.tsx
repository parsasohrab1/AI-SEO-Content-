'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

export default function AnalysisPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:8002/dashboard/${analysisId}`)
        const dashboardData = await response.json()
        setData(dashboardData)
      } catch (err) {
        console.error('Error:', err)
      } finally {
        setLoading(false)
      }
    }

    if (analysisId) {
      fetchData()
    }
  }, [analysisId])

  if (loading) {
    return <div className="p-8">در حال بارگذاری...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">تحلیل نقاط قوت و ضعف</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">نقاط قوت</h2>
          <div className="space-y-2">
            <div className="p-3 bg-green-50 border-r-4 border-green-500 rounded">
              <p className="text-green-800">سیستم در حال توسعه است</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">نقاط ضعف</h2>
          <div className="space-y-2">
            <div className="p-3 bg-red-50 border-r-4 border-red-500 rounded">
              <p className="text-red-800">نیاز به تکمیل ماژول‌ها</p>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <Link
            href={`/dashboard/${analysisId}`}
            className="text-blue-600 hover:underline"
          >
            ← بازگشت به داشبورد
          </Link>
        </div>
      </div>
    </div>
  )
}

