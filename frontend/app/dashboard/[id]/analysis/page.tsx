'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface StrengthWeakness {
  title: string
  description: string
  category: string
  priority?: 'low' | 'medium' | 'high'
}

export default function AnalysisPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [strengths, setStrengths] = useState<StrengthWeakness[]>([])
  const [weaknesses, setWeaknesses] = useState<StrengthWeakness[]>([])
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const shouldPollRef = useRef<boolean>(true)

  useEffect(() => {
    const fetchData = async () => {
      // Don't fetch if we shouldn't poll anymore
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
            // Stop polling if dashboard doesn't exist
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
        setError(null) // Clear any previous errors
        
        // استخراج نقاط قوت و ضعف
        if (dashboardData.strengths) {
          setStrengths(dashboardData.strengths)
        }
        if (dashboardData.weaknesses) {
          setWeaknesses(dashboardData.weaknesses)
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
        // Stop polling on error
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
      
      // Poll for updates every 5 seconds
      intervalRef.current = setInterval(() => {
        if (shouldPollRef.current) {
          fetchData()
        } else {
          // Stop polling if we shouldn't poll anymore
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

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-600 bg-red-50'
      case 'medium':
        return 'border-orange-500 bg-orange-50'
      case 'low':
        return 'border-yellow-400 bg-yellow-50'
      default:
        return 'border-red-500 bg-red-50'
    }
  }

  const getPriorityText = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'اولویت بالا'
      case 'medium':
        return 'اولویت متوسط'
      case 'low':
        return 'اولویت پایین'
      default:
        return ''
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">در حال بارگذاری تحلیل...</p>
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
              <svg className="mx-auto h-12 w-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard یافت نشد</h2>
            <p className="text-gray-600 mb-6">{error}</p>
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
        <h1 className="text-3xl font-bold mb-8">تحلیل نقاط قوت و ضعف</h1>
        
        {data?.status === 'processing' && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800">
              ⏳ تحلیل در حال انجام است. لطفاً چند لحظه صبر کنید...
            </p>
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="ml-2">نقاط قوت</span>
            <span className="bg-green-100 text-green-800 text-sm font-medium px-2.5 py-0.5 rounded mr-auto">
              {strengths.length}
            </span>
          </h2>
          {strengths.length > 0 ? (
            <div className="space-y-3">
              {strengths.map((strength, index) => (
                <div
                  key={index}
                  className="p-4 bg-green-50 border-r-4 border-green-500 rounded hover:bg-green-100 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-green-900 font-semibold mb-1">{strength.title}</h3>
                      <p className="text-green-700 text-sm">{strength.description}</p>
                    </div>
                    <span className="bg-green-200 text-green-800 text-xs font-medium px-2 py-1 rounded mr-3">
                      {strength.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 bg-gray-50 border-r-4 border-gray-300 rounded">
              <p className="text-gray-600">در حال تحلیل...</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <span className="ml-2">نقاط ضعف</span>
            <span className="bg-red-100 text-red-800 text-sm font-medium px-2.5 py-0.5 rounded mr-auto">
              {weaknesses.length}
            </span>
          </h2>
          {weaknesses.length > 0 ? (
            <div className="space-y-3">
              {weaknesses.map((weakness, index) => (
                <div
                  key={index}
                  className={`p-4 border-r-4 rounded hover:opacity-90 transition-opacity ${getPriorityColor(weakness.priority)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{weakness.title}</h3>
                        {weakness.priority && (
                          <span className="text-xs font-medium text-gray-700">
                            ({getPriorityText(weakness.priority)})
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700 text-sm">{weakness.description}</p>
                    </div>
                    <span className="bg-gray-200 text-gray-800 text-xs font-medium px-2 py-1 rounded mr-3">
                      {weakness.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 bg-gray-50 border-r-4 border-gray-300 rounded">
              <p className="text-gray-600">در حال تحلیل...</p>
            </div>
          )}
        </div>

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

