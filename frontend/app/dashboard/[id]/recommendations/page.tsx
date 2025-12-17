'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface Recommendation {
  title: string
  description: string
  category: string
  priority: 'high' | 'medium' | 'low'
  impact: string
  estimatedTime?: string
  automated?: boolean
}

export default function RecommendationsPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
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
        setLastUpdate(new Date())
        setIsRefreshing(false)
        
        // استخراج پیشنهادات از داده‌ها
        const recs = generateRecommendations(dashboardData)
        setRecommendations(recs)
        
        // Continue polling even after completion for real-time updates
        if (dashboardData.status === 'failed') {
          shouldPollRef.current = false
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        } else if (dashboardData.status === 'completed') {
          // Reduce polling frequency after completion but keep polling for updates
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
          // Continue with slower polling (every 10 seconds instead of 5)
          intervalRef.current = setInterval(() => {
            if (shouldPollRef.current) {
              fetchData()
            }
          }, 10000)
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

  const generateRecommendations = (dashboardData: any): Recommendation[] => {
    const recs: Recommendation[] = []
    const siteAnalysis = dashboardData.data?.site_analysis || {}
    const seoAnalysis = dashboardData.data?.seo_analysis || {}
    const weaknesses = dashboardData.weaknesses || []

    // پیشنهادات بر اساس نقاط ضعف
    weaknesses.forEach((weakness: any) => {
      const priority = weakness.priority || 'medium'
      let recommendation: Recommendation | null = null

      switch (weakness.title) {
        case 'عدم استفاده از HTTPS':
          recommendation = {
            title: 'فعال‌سازی HTTPS',
            description: 'برای امنیت و اعتماد کاربران، SSL/TLS را فعال کنید. این کار تأثیر مثبت زیادی بر رتبه‌بندی دارد.',
            category: 'امنیت',
            priority: 'high',
            impact: 'تأثیر بالا بر امنیت و سئو',
            estimatedTime: '1-2 ساعت',
            automated: false
          }
          break

        case 'عدم وجود Sitemap':
          recommendation = {
            title: 'ایجاد Sitemap XML',
            description: 'یک فایل sitemap.xml ایجاد کنید تا موتورهای جستجو بتوانند صفحات سایت را بهتر ایندکس کنند.',
            category: 'سئو فنی',
            priority: 'high',
            impact: 'بهبود ایندکس شدن صفحات',
            estimatedTime: '30 دقیقه',
            automated: true
          }
          break

        case 'عدم وجود تگ H1':
          recommendation = {
            title: 'افزودن تگ H1 به صفحات',
            description: 'هر صفحه باید یک تگ H1 داشته باشد که موضوع اصلی صفحه را مشخص کند.',
            category: 'ساختار محتوا',
            priority: 'high',
            impact: 'بهبود ساختار و سئو محتوا',
            estimatedTime: '15 دقیقه',
            automated: true
          }
          break

        case 'چندین تگ H1':
          recommendation = {
            title: 'کاهش تعداد تگ‌های H1',
            description: 'هر صفحه باید فقط یک تگ H1 داشته باشد. تگ‌های اضافی را به H2 یا H3 تبدیل کنید.',
            category: 'ساختار محتوا',
            priority: 'medium',
            impact: 'بهبود ساختار سئو',
            estimatedTime: '30 دقیقه',
            automated: true
          }
          break

        case 'زمان بارگذاری کند':
          recommendation = {
            title: 'بهینه‌سازی سرعت بارگذاری',
            description: 'تصاویر را فشرده کنید، از CDN استفاده کنید و کدهای JavaScript و CSS را بهینه کنید.',
            category: 'عملکرد',
            priority: 'high',
            impact: 'بهبود تجربه کاربری و رتبه‌بندی',
            estimatedTime: '2-4 ساعت',
            automated: false
          }
          break

        default:
          recommendation = {
            title: weakness.title,
            description: weakness.description || 'این مشکل نیاز به بررسی و اصلاح دارد.',
            category: weakness.category || 'عمومی',
            priority: priority as 'high' | 'medium' | 'low',
            impact: 'بهبود سئو',
            automated: false
          }
      }

      if (recommendation) {
        recs.push(recommendation)
      }
    })

    // پیشنهادات اضافی بر اساس تحلیل
    const security = siteAnalysis.security || {}
    if (!security.ssl_enabled) {
      recs.push({
        title: 'فعال‌سازی گواهینامه SSL',
        description: 'برای امنیت و اعتماد کاربران، گواهینامه SSL را نصب و فعال کنید.',
        category: 'امنیت',
        priority: 'high',
        impact: 'تأثیر بسیار بالا',
        estimatedTime: '1 ساعت',
        automated: false
      })
    }

    const sitemap = siteAnalysis.sitemap || {}
    if (!sitemap.found) {
      recs.push({
        title: 'ایجاد و ارسال Sitemap به Google Search Console',
        description: 'پس از ایجاد sitemap.xml، آن را در Google Search Console ثبت کنید.',
        category: 'سئو فنی',
        priority: 'high',
        impact: 'بهبود ایندکس شدن',
        estimatedTime: '15 دقیقه',
        automated: false
      })
    }

    const structure = siteAnalysis.structure || {}
    const headings = structure.headings || {}
    if (headings.h1 === 0) {
      recs.push({
        title: 'افزودن تگ H1 به صفحه اصلی',
        description: 'صفحه اصلی باید یک تگ H1 واضح و مرتبط با موضوع سایت داشته باشد.',
        category: 'ساختار محتوا',
        priority: 'high',
        impact: 'بهبود سئو صفحه اصلی',
        estimatedTime: '10 دقیقه',
        automated: true
      })
    }

    const performance = siteAnalysis.performance || {}
    if (performance.response_time && performance.response_time > 3) {
      recs.push({
        title: 'بهینه‌سازی سرعت سایت',
        description: 'از تکنیک‌های بهینه‌سازی مانند فشرده‌سازی، کش، و بهینه‌سازی تصاویر استفاده کنید.',
        category: 'عملکرد',
        priority: 'high',
        impact: 'بهبود تجربه کاربری',
        estimatedTime: '3-5 ساعت',
        automated: false
      })
    }

    // پیشنهادات عمومی
    recs.push({
      title: 'بهینه‌سازی Meta Tags',
      description: 'مطمئن شوید که تمام صفحات دارای Meta Title و Meta Description مناسب هستند.',
      category: 'سئو محتوایی',
      priority: 'medium',
      impact: 'بهبود کلیک‌ها در نتایج جستجو',
      estimatedTime: '2-3 ساعت',
      automated: true
    })

    recs.push({
      title: 'افزودن Alt Text به تصاویر',
      description: 'تمام تصاویر باید دارای متن جایگزین (Alt Text) باشند تا برای موتورهای جستجو قابل فهم باشند.',
      category: 'سئو محتوایی',
      priority: 'medium',
      impact: 'بهبود دسترسی و سئو تصاویر',
      estimatedTime: '1-2 ساعت',
      automated: true
    })

    // حذف تکراری‌ها
    const uniqueRecs = recs.filter((rec, index, self) =>
      index === self.findIndex((r) => r.title === rec.title)
    )

    // مرتب‌سازی بر اساس اولویت
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    uniqueRecs.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])

    return uniqueRecs
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-500'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-500'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-500'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-500'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return '🔴'
      case 'medium':
        return '🟡'
      case 'low':
        return '🔵'
      default:
        return '⚪'
    }
  }

  const highPriorityRecs = recommendations.filter(r => r.priority === 'high')
  const mediumPriorityRecs = recommendations.filter(r => r.priority === 'medium')
  const lowPriorityRecs = recommendations.filter(r => r.priority === 'low')

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">در حال بارگذاری پیشنهادات...</p>
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

  const handleManualRefresh = async () => {
    setIsRefreshing(true)
    shouldPollRef.current = true
    const response = await fetch(`http://localhost:8002/dashboard/${analysisId}`)
    if (response.ok) {
      const dashboardData = await response.json()
      setData(dashboardData)
      const recs = generateRecommendations(dashboardData)
      setRecommendations(recs)
      setLastUpdate(new Date())
    }
    setIsRefreshing(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">پیشنهادات و اصلاحات</h1>
          <div className="flex items-center gap-4">
            {lastUpdate && (
              <span className="text-sm text-gray-500">
                آخرین به‌روزرسانی: {lastUpdate.toLocaleTimeString('fa-IR')}
              </span>
            )}
            <button
              onClick={handleManualRefresh}
              disabled={isRefreshing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isRefreshing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  در حال به‌روزرسانی...
                </>
              ) : (
                <>
                  🔄 به‌روزرسانی
                </>
              )}
            </button>
          </div>
        </div>
        
        {data?.status === 'processing' && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800">
              ⏳ تحلیل در حال انجام است. پیشنهادات به محض تکمیل تحلیل نمایش داده می‌شوند...
            </p>
          </div>
        )}

        {/* Summary */}
        {recommendations.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">اولویت بالا</span>
                <span className="text-2xl font-bold text-red-600">{highPriorityRecs.length}</span>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">اولویت متوسط</span>
                <span className="text-2xl font-bold text-yellow-600">{mediumPriorityRecs.length}</span>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">اولویت پایین</span>
                <span className="text-2xl font-bold text-blue-600">{lowPriorityRecs.length}</span>
              </div>
            </div>
          </div>
        )}

        {/* High Priority Recommendations */}
        {highPriorityRecs.length > 0 && (
          <div className="mb-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <span className="ml-2">اولویت بالا</span>
              <span className="bg-red-100 text-red-800 text-sm font-medium px-2.5 py-0.5 rounded mr-auto">
                {highPriorityRecs.length} مورد
              </span>
            </h2>
            <div className="space-y-4">
              {highPriorityRecs.map((rec, index) => (
                <div
                  key={index}
                  className={`bg-white rounded-lg shadow p-6 border-r-4 ${getPriorityColor(rec.priority)}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                        <span>{getPriorityIcon(rec.priority)}</span>
                        {rec.title}
                      </h3>
                      <p className="text-gray-700 mb-3">{rec.description}</p>
                      <div className="flex flex-wrap gap-2 mt-4">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {rec.category}
                        </span>
                        {rec.estimatedTime && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                            ⏱ {rec.estimatedTime}
                          </span>
                        )}
                        {rec.automated && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                            ✓ قابل اجرای خودکار
                          </span>
                        )}
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                          {rec.impact}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Medium Priority Recommendations */}
        {mediumPriorityRecs.length > 0 && (
          <div className="mb-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <span className="ml-2">اولویت متوسط</span>
              <span className="bg-yellow-100 text-yellow-800 text-sm font-medium px-2.5 py-0.5 rounded mr-auto">
                {mediumPriorityRecs.length} مورد
              </span>
            </h2>
            <div className="space-y-4">
              {mediumPriorityRecs.map((rec, index) => (
                <div
                  key={index}
                  className={`bg-white rounded-lg shadow p-6 border-r-4 ${getPriorityColor(rec.priority)}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                        <span>{getPriorityIcon(rec.priority)}</span>
                        {rec.title}
                      </h3>
                      <p className="text-gray-700 mb-3">{rec.description}</p>
                      <div className="flex flex-wrap gap-2 mt-4">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {rec.category}
                        </span>
                        {rec.estimatedTime && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                            ⏱ {rec.estimatedTime}
                          </span>
                        )}
                        {rec.automated && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                            ✓ قابل اجرای خودکار
                          </span>
                        )}
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                          {rec.impact}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Low Priority Recommendations */}
        {lowPriorityRecs.length > 0 && (
          <div className="mb-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <span className="ml-2">اولویت پایین</span>
              <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded mr-auto">
                {lowPriorityRecs.length} مورد
              </span>
            </h2>
            <div className="space-y-4">
              {lowPriorityRecs.map((rec, index) => (
                <div
                  key={index}
                  className={`bg-white rounded-lg shadow p-6 border-r-4 ${getPriorityColor(rec.priority)}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                        <span>{getPriorityIcon(rec.priority)}</span>
                        {rec.title}
                      </h3>
                      <p className="text-gray-700 mb-3">{rec.description}</p>
                      <div className="flex flex-wrap gap-2 mt-4">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {rec.category}
                        </span>
                        {rec.estimatedTime && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                            ⏱ {rec.estimatedTime}
                          </span>
                        )}
                        {rec.automated && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                            ✓ قابل اجرای خودکار
                          </span>
                        )}
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                          {rec.impact}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {recommendations.length === 0 && !loading && (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 mb-4">هنوز پیشنهادی برای نمایش وجود ندارد.</p>
            <p className="text-sm text-gray-500">
              پس از تکمیل تحلیل، پیشنهادات در اینجا نمایش داده می‌شوند.
            </p>
          </div>
        )}

        {/* Action Buttons */}
        {recommendations.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">آماده اعمال پیشنهادات؟</h3>
                <p className="text-gray-600 text-sm">
                  می‌توانید پیشنهادات را انتخاب کرده و بر روی سایت اعمال کنید
                </p>
              </div>
              <Link
                href={`/dashboard/${analysisId}/apply`}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
              >
                🚀 اجرای پیشنهادات
              </Link>
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

