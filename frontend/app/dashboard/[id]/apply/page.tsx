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
  id?: string
}

interface AppliedFix {
  recommendation_id: string
  title: string
  status: 'pending' | 'applying' | 'applied' | 'failed'
  message?: string
}

export default function ApplyPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([])
  const [applying, setApplying] = useState(false)
  const [appliedFixes, setAppliedFixes] = useState<AppliedFix[]>([])
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
            setError('Dashboard یافت نشد. احتمالاً بک‌اند restart شده و داده‌ها از بین رفته است. لطفاً یک تحلیل جدید ایجاد کنید.')
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
        
        // استخراج پیشنهادات
        const recs = dashboardData.recommendations || []
        setRecommendations(recs)
        
        // استخراج fixes اعمال شده
        const appliedFixesData = dashboardData.applied_fixes || []
        if (appliedFixesData.length > 0) {
          const fixesList: AppliedFix[] = appliedFixesData.map((fix: any) => ({
            recommendation_id: fix.recommendation_id || fix.id || '',
            title: fix.title || '',
            status: fix.status === 'success' ? 'applied' : 
                   fix.status === 'pending' ? 'pending' : 'failed',
            message: fix.message
          }))
          setAppliedFixes(fixesList)
        }
        
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

  const handleSelectRecommendation = (recId: string) => {
    setSelectedRecommendations(prev => 
      prev.includes(recId) 
        ? prev.filter(id => id !== recId)
        : [...prev, recId]
    )
  }

  const handleSelectAll = () => {
    if (selectedRecommendations.length === recommendations.length) {
      setSelectedRecommendations([])
    } else {
      setSelectedRecommendations(recommendations.map((r, i) => r.id || `rec_${i}`))
    }
  }

  const handleApplyRecommendations = async () => {
    if (selectedRecommendations.length === 0) {
      alert('لطفاً حداقل یک پیشنهاد را انتخاب کنید')
      return
    }

    setApplying(true)
    setAppliedFixes([])

    try {
      // ایجاد لیست fixes برای ارسال
      const fixes = selectedRecommendations.map(id => {
        const rec = recommendations.find((r, i) => (r.id || `rec_${i}`) === id)
        return rec?.title || id
      })

      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/apply-fixes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fixes: fixes,
          recommendation_ids: selectedRecommendations
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'خطا در اعمال پیشنهادات')
      }

      const result = await response.json()
      
      // ایجاد لیست fixes اعمال شده
      const fixesList: AppliedFix[] = selectedRecommendations.map((id, index) => {
        const rec = recommendations.find((r, i) => (r.id || `rec_${i}`) === id)
        return {
          recommendation_id: id,
          title: rec?.title || `پیشنهاد ${index + 1}`,
          status: result.results?.[index]?.status === 'success' ? 'applied' : 'failed',
          message: result.results?.[index]?.message
        }
      })

      setAppliedFixes(fixesList)
      
      // Clear selected recommendations
      setSelectedRecommendations([])
      
      // Refresh data after a short delay
      setTimeout(async () => {
        try {
          const refreshResponse = await fetch(`http://localhost:8002/dashboard/${analysisId}`)
          if (refreshResponse.ok) {
            const refreshData = await refreshResponse.json()
            const recs = refreshData.recommendations || []
            setRecommendations(recs)
            
            // Update applied fixes from dashboard
            const appliedFixesData = refreshData.applied_fixes || []
            if (appliedFixesData.length > 0) {
              const fixesList: AppliedFix[] = appliedFixesData.map((fix: any) => ({
                recommendation_id: fix.recommendation_id || fix.id || '',
                title: fix.title || '',
                status: fix.status === 'success' ? 'applied' : 
                       fix.status === 'pending' ? 'pending' : 'failed',
                message: fix.message
              }))
              setAppliedFixes(fixesList)
            }
          }
        } catch (err) {
          console.error('Error refreshing data:', err)
        }
      }, 1000)

    } catch (err) {
      alert('خطا در اعمال پیشنهادات: ' + (err instanceof Error ? err.message : 'خطای نامشخص'))
    } finally {
      setApplying(false)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'applied':
        return 'bg-green-100 text-green-800'
      case 'applying':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">در حال بارگذاری...</p>
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
            <div className="mb-4">
              <svg className="mx-auto h-16 w-16 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard یافت نشد</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <p className="text-sm text-gray-500 mb-6">
              این داشبورد احتمالاً بعد از restart شدن بک‌اند از بین رفته است. 
              داده‌ها در حال حاضر در حافظه ذخیره می‌شوند و با restart از بین می‌روند.
            </p>
            <div className="space-x-4">
              <Link
                href="/"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                ایجاد تحلیل جدید
              </Link>
              <Link
                href={`/dashboard/${analysisId}`}
                className="inline-flex items-center px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                بازگشت به داشبورد
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">اجرای پیشنهادات</h1>
          <p className="text-gray-600">انتخاب و اعمال پیشنهادات سئو بر روی سایت</p>
        </div>

        {/* Selection Summary */}
        {selectedRecommendations.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-blue-900">
                  {selectedRecommendations.length} پیشنهاد انتخاب شده
                </p>
                <p className="text-sm text-blue-700">
                  آماده اعمال بر روی سایت
                </p>
              </div>
              <button
                onClick={handleApplyRecommendations}
                disabled={applying}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
              >
                {applying ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                    در حال اعمال...
                  </>
                ) : (
                  '✅ اعمال پیشنهادات انتخاب شده'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Applied Fixes Status */}
        {appliedFixes.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">وضعیت اعمال پیشنهادات</h2>
            <div className="space-y-3">
              {appliedFixes.map((fix, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${getStatusColor(fix.status)}`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{fix.title}</p>
                      {fix.message && (
                        <p className="text-sm mt-1">{fix.message}</p>
                      )}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(fix.status)}`}>
                      {fix.status === 'applied' ? '✓ اعمال شد' :
                       fix.status === 'applying' ? '⏳ در حال اعمال' :
                       fix.status === 'failed' ? '✗ خطا' :
                       '⏳ در انتظار'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations List */}
        {recommendations.length > 0 ? (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">لیست پیشنهادات ({recommendations.length})</h2>
              <button
                onClick={handleSelectAll}
                className="px-4 py-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                {selectedRecommendations.length === recommendations.length ? 'لغو انتخاب همه' : 'انتخاب همه'}
              </button>
            </div>

            <div className="space-y-4">
              {recommendations.map((rec, index) => {
                const recId = rec.id || `rec_${index}`
                const isSelected = selectedRecommendations.includes(recId)
                const isApplied = appliedFixes.some(f => f.recommendation_id === recId)

                return (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      isSelected 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    } ${isApplied ? 'opacity-60' : ''}`}
                    onClick={() => !isApplied && handleSelectRecommendation(recId)}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => !isApplied && handleSelectRecommendation(recId)}
                        disabled={isApplied}
                        className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{rec.title}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                            {rec.priority === 'high' ? 'اولویت بالا' :
                             rec.priority === 'medium' ? 'اولویت متوسط' :
                             'اولویت پایین'}
                          </span>
                          {rec.automated && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                              🤖 خودکار
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 mb-3">{rec.description}</p>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          <span>📁 {rec.category}</span>
                          {rec.estimatedTime && (
                            <span>⏱️ {rec.estimatedTime}</span>
                          )}
                          <span>💡 {rec.impact}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="mb-4">
              <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">پیشنهادی یافت نشد</h2>
            <p className="text-gray-600 mb-6">
              هنوز پیشنهادی برای این تحلیل تولید نشده است.
            </p>
            <Link
              href={`/dashboard/${analysisId}/recommendations`}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              مشاهده پیشنهادات
            </Link>
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

