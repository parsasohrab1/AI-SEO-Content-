'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface DashboardData {
  analysis_id: string
  site_url: string
  status: string
  summary?: {
    total_pages?: number
    seo_score?: number
    content_count?: number
    issues_fixed?: number
  }
  site_analysis?: any
  seo_analysis?: any
  created_at?: string
  updated_at?: string
}

export default function DashboardPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await fetch(`http://localhost:8002/dashboard/${analysisId}`)
        if (!response.ok) {
          throw new Error('Dashboard not found')
        }
        const dashboardData = await response.json()
        setData(dashboardData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها')
      } finally {
        setLoading(false)
      }
    }

    if (analysisId) {
      fetchDashboard()
      // Poll for updates every 5 seconds if status is processing
      const interval = setInterval(() => {
        fetchDashboard()
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [analysisId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال بارگذاری...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Dashboard یافت نشد'}</p>
          <Link href="/" className="text-blue-600 hover:underline">
            بازگشت به صفحه اصلی
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">داشبورد مدیریتی</h1>
          <p className="text-gray-600">{data.site_url}</p>
          <div className="mt-2">
            <span className={`px-3 py-1 rounded-full text-sm ${
              data.status === 'completed' ? 'bg-green-100 text-green-800' :
              data.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {data.status === 'completed' ? 'تکمیل شده' :
               data.status === 'processing' ? 'در حال پردازش' :
               'خطا'}
            </span>
          </div>
        </div>

        {/* Summary Cards */}
        {data.summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">امتیاز سئو</h3>
              <p className="text-3xl font-bold text-blue-600">
                {data.summary.seo_score || 'N/A'}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">تعداد صفحات</h3>
              <p className="text-3xl font-bold text-green-600">
                {data.summary.total_pages || 'N/A'}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">محتوا تولید شده</h3>
              <p className="text-3xl font-bold text-purple-600">
                {data.summary.content_count || 'N/A'}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">مشکلات رفع شده</h3>
              <p className="text-3xl font-bold text-orange-600">
                {data.summary.issues_fixed || 'N/A'}
              </p>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <Link
                href={`/dashboard/${analysisId}`}
                className="px-6 py-4 border-b-2 border-blue-600 text-blue-600 font-medium"
              >
                داشبورد اصلی
              </Link>
              <Link
                href={`/dashboard/${analysisId}/analysis`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                تحلیل قوت/ضعف
              </Link>
              <Link
                href={`/dashboard/${analysisId}/recommendations`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                پیشنهادات
              </Link>
              <Link
                href={`/dashboard/${analysisId}/seo`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                مانیتورینگ سئو
              </Link>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">اطلاعات تحلیل</h2>
          
          {data.status === 'processing' && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800">
                تحلیل در حال انجام است. لطفاً چند لحظه صبر کنید...
              </p>
            </div>
          )}

          {data.site_analysis && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">تحلیل سایت</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-sm overflow-auto">
                  {JSON.stringify(data.site_analysis, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {data.seo_analysis && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">تحلیل سئو</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-sm overflow-auto">
                  {JSON.stringify(data.seo_analysis, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {!data.site_analysis && !data.seo_analysis && data.status === 'completed' && (
            <p className="text-gray-600">داده‌های تحلیل در حال آماده‌سازی است.</p>
          )}
        </div>

        {/* Back Link */}
        <div className="mt-6">
          <Link
            href="/"
            className="text-blue-600 hover:underline"
          >
            ← بازگشت به صفحه اصلی
          </Link>
        </div>
      </div>
    </div>
  )
}

