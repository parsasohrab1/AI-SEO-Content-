'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

export default function SEOPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const shouldPollRef = useRef<boolean>(true)

  useEffect(() => {
    const fetchData = async () => {
      if (!shouldPollRef.current) {
        return
      }
      
      try {
        const response = await fetch(`http://localhost:8002/dashboard/${analysisId}`)
        if (!response.ok) {
          if (response.status === 404) {
            setError('Dashboard یافت نشد. لطفاً یک تحلیل جدید ایجاد کنید.')
            setLoading(false)
            shouldPollRef.current = false
            if (intervalRef.current) {
              clearInterval(intervalRef.current)
              intervalRef.current = null
            }
            return
          }
          throw new Error(`Failed to fetch dashboard data: ${response.status}`)
        }
        const dashboardData = await response.json()
        setData(dashboardData)
        setError(null)
        
        // Stop polling if analysis is completed or failed
        if (dashboardData.status === 'completed' || dashboardData.status === 'failed') {
          shouldPollRef.current = false
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      } catch (err) {
        console.error('Error:', err)
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها')
        setLoading(false)
        shouldPollRef.current = false
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
      } finally {
        setLoading(false)
      }
    }

    if (analysisId) {
      shouldPollRef.current = true
      fetchData()
      
      intervalRef.current = setInterval(() => {
        if (shouldPollRef.current) {
          fetchData()
        } else {
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      }, 5000)
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
        shouldPollRef.current = false
      }
    }
  }, [analysisId])

  const seoAnalysis = data?.data?.seo_analysis || {}
  const siteAnalysis = data?.data?.site_analysis || {}
  const technical = seoAnalysis.technical || {}
  const content = seoAnalysis.content || {}
  const security = siteAnalysis.security || {}
  const performance = siteAnalysis.performance || {}
  const sitemap = siteAnalysis.sitemap || {}

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      'good': { color: 'bg-green-100 text-green-800', text: 'خوب' },
      'fair': { color: 'bg-yellow-100 text-yellow-800', text: 'متوسط' },
      'poor': { color: 'bg-red-100 text-red-800', text: 'ضعیف' },
      'excellent': { color: 'bg-blue-100 text-blue-800', text: 'عالی' }
    }
    const statusInfo = statusMap[status] || { color: 'bg-gray-100 text-gray-800', text: status }
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${statusInfo.color}`}>
        {statusInfo.text}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">در حال بارگذاری مانیتورینگ سئو...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">خطا</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <Link
              href="/"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              ایجاد تحلیل جدید
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">مانیتورینگ سئو</h1>
        
        {data?.status === 'processing' && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800">
              ⏳ تحلیل در حال انجام است. لطفاً چند لحظه صبر کنید...
            </p>
          </div>
        )}

        {/* Technical SEO */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">سئو فنی</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 mb-2">Crawlability</h3>
              {getStatusBadge(technical.crawlability || 'unknown')}
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 mb-2">Indexability</h3>
              {getStatusBadge(technical.indexability || 'unknown')}
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 mb-2">Core Web Vitals</h3>
              {technical.core_web_vitals && Object.keys(technical.core_web_vitals).length > 0 ? (
                <span className="text-xs text-gray-600">در حال بررسی...</span>
              ) : (
                <span className="text-xs text-gray-500">داده موجود نیست</span>
              )}
            </div>
          </div>
        </div>

        {/* Content Analysis */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">تحلیل محتوا</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 mb-2">Keywords</h3>
              {content.keywords && content.keywords.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {content.keywords.slice(0, 5).map((keyword: string, index: number) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                      {keyword}
                    </span>
                  ))}
                  {content.keywords.length > 5 && (
                    <span className="text-xs text-gray-500">+{content.keywords.length - 5} بیشتر</span>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500">هیچ کلمه کلیدی شناسایی نشد</p>
              )}
            </div>
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 mb-2">Readability Score</h3>
              {content.readability !== undefined && content.readability > 0 ? (
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${Math.min(content.readability, 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{content.readability}/100</span>
                </div>
              ) : (
                <p className="text-sm text-gray-500">امتیاز خوانایی محاسبه نشده</p>
              )}
            </div>
          </div>
        </div>

        {/* Security & Performance */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Security */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">امنیت</h2>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">HTTPS</span>
                {security.ssl_enabled ? (
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                    ✓ فعال
                  </span>
                ) : (
                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">
                    ✗ غیرفعال
                  </span>
                )}
              </div>
              
              {security.security_headers && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Security Headers</h3>
                  <div className="space-y-2">
                    {Object.entries(security.security_headers).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">{key.replace(/_/g, ' ')}</span>
                        {value ? (
                          <span className="text-green-600">✓</span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Performance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">عملکرد</h2>
            
            <div className="space-y-3">
              {performance.response_time !== undefined && performance.response_time !== null ? (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">زمان پاسخ سرور</span>
                    <span className="text-sm font-medium">
                      {performance.response_time.toFixed(2)}s
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        performance.response_time < 2
                          ? 'bg-green-600'
                          : performance.response_time < 3
                          ? 'bg-yellow-600'
                          : 'bg-red-600'
                      }`}
                      style={{
                        width: `${Math.min((performance.response_time / 5) * 100, 100)}%`
                      }}
                    ></div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500">داده عملکرد موجود نیست</p>
              )}
              
              {performance.status_code && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status Code</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    performance.status_code === 200
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {performance.status_code}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sitemap Status */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Sitemap</h2>
          
          {sitemap.found ? (
            <div className="p-4 bg-green-50 border-r-4 border-green-500 rounded">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-green-900">Sitemap یافت شد</p>
                  {sitemap.url && (
                    <p className="text-sm text-green-700 mt-1">{sitemap.url}</p>
                  )}
                </div>
                <span className="text-green-600 text-2xl">✓</span>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-yellow-50 border-r-4 border-yellow-500 rounded">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-yellow-900">Sitemap یافت نشد</p>
                  <p className="text-sm text-yellow-700 mt-1">
                    توصیه می‌شود یک Sitemap برای سایت ایجاد کنید
                  </p>
                </div>
                <span className="text-yellow-600 text-2xl">⚠</span>
              </div>
            </div>
          )}
        </div>

        {/* SEO Issues */}
        {seoAnalysis.issues && seoAnalysis.issues.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">مشکلات سئو</h2>
            
            <div className="space-y-3">
              {seoAnalysis.issues.map((issue: any, index: number) => (
                <div
                  key={index}
                  className="p-4 bg-red-50 border-r-4 border-red-500 rounded"
                >
                  <h3 className="font-medium text-red-900 mb-1">
                    {issue.title || 'مشکل سئو'}
                  </h3>
                  {issue.description && (
                    <p className="text-sm text-red-700">{issue.description}</p>
                  )}
                  {issue.priority && (
                    <span className="inline-block mt-2 px-2 py-1 bg-red-200 text-red-800 rounded text-xs">
                      اولویت: {issue.priority}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Site Structure */}
        {siteAnalysis.structure && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">ساختار سایت</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {siteAnalysis.structure.headings && (
                <>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 mb-1">H1</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {siteAnalysis.structure.headings.h1 || 0}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 mb-1">H2</p>
                    <p className="text-2xl font-bold text-green-600">
                      {siteAnalysis.structure.headings.h2 || 0}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-xs text-gray-600 mb-1">H3</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {siteAnalysis.structure.headings.h3 || 0}
                    </p>
                  </div>
                </>
              )}
              
              {siteAnalysis.structure.links && (
                <div className="p-3 bg-gray-50 rounded">
                  <p className="text-xs text-gray-600 mb-1">لینک‌های داخلی</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {siteAnalysis.structure.links.internal || 0}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Back Link */}
        <div className="mt-6">
          <Link
            href={`/dashboard/${analysisId}`}
            className="inline-flex items-center text-blue-600 hover:text-blue-800 hover:underline"
          >
            ← بازگشت به داشبورد
          </Link>
        </div>
      </div>
    </div>
  )
}

