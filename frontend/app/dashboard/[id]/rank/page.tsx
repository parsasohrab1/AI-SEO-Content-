'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface RankData {
  domain: string
  url: string
  timestamp: string
  global: {
    global_rank?: number
    country_rank?: number
    country?: string
    traffic_rank?: number
    sources?: Array<{
      name: string
      rank: number
      method: string
    }>
  }
  iran: {
    iran_rank?: number
    iran_traffic_rank?: number
    local_rank?: number
    sources?: Array<{
      name: string
      rank: number
      method: string
    }>
  }
  score: {
    overall: number
    global_score: number
    iran_score: number
    level: string
    level_fa: string
    grade: string
  }
  trend: string
  last_updated: string
}

export default function RankPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [rankData, setRankData] = useState<RankData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const shouldPollRef = useRef<boolean>(true)

  useEffect(() => {
    const fetchRankData = async () => {
      if (!shouldPollRef.current) {
        return
      }
      
      try {
        const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/rank`)
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
          throw new Error(`Failed to fetch rank data: ${response.status}`)
        }
        const data = await response.json()
        setRankData(data)
        setError(null)
        setLastUpdate(new Date())
        setIsRefreshing(false)
        
        // Continue polling with slower frequency after first load
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
        // Poll every 10 seconds for real-time updates
        intervalRef.current = setInterval(() => {
          if (shouldPollRef.current) {
            fetchRankData()
          }
        }, 10000)
        
      } catch (err) {
        console.error('Error:', err)
        setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌های رنک')
        setLoading(false)
        setIsRefreshing(false)
      } finally {
        setLoading(false)
      }
    }

    if (analysisId) {
      shouldPollRef.current = true
      fetchRankData()
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
        shouldPollRef.current = false
      }
    }
  }, [analysisId])

  const handleManualRefresh = async () => {
    setIsRefreshing(true)
    shouldPollRef.current = true
    try {
      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/rank`)
      if (response.ok) {
        const data = await response.json()
        setRankData(data)
        setLastUpdate(new Date())
      }
    } catch (err) {
      console.error('Error refreshing:', err)
    } finally {
      setIsRefreshing(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-blue-600'
    if (score >= 40) return 'text-yellow-600'
    if (score >= 20) return 'text-orange-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 border-green-500'
    if (score >= 60) return 'bg-blue-100 border-blue-500'
    if (score >= 40) return 'bg-yellow-100 border-yellow-500'
    if (score >= 20) return 'bg-orange-100 border-orange-500'
    return 'bg-red-100 border-red-500'
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-600 bg-green-100'
    if (grade.startsWith('B')) return 'text-blue-600 bg-blue-100'
    if (grade.startsWith('C')) return 'text-yellow-600 bg-yellow-100'
    if (grade.startsWith('D')) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const formatRank = (rank: number | null | undefined): string => {
    if (!rank) return 'N/A'
    return rank.toLocaleString('fa-IR')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">در حال بارگذاری رنک سایت...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error && !rankData) {
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
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">رنک سایت</h1>
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

        {rankData && (
          <>
            {/* Overall Score Card */}
            <div className={`bg-white rounded-lg shadow-lg p-8 mb-6 border-r-4 ${getScoreBgColor(rankData.score.overall)}`}>
              <div className="text-center">
                <h2 className="text-2xl font-semibold mb-4">امتیاز کلی رنک</h2>
                <div className="flex items-center justify-center gap-6">
                  <div>
                    <div className={`text-6xl font-bold ${getScoreColor(rankData.score.overall)}`}>
                      {rankData.score.overall.toFixed(1)}
                    </div>
                    <div className="text-gray-600 mt-2">از 100</div>
                  </div>
                  <div className="text-center">
                    <div className={`inline-block px-6 py-3 rounded-lg text-3xl font-bold ${getGradeColor(rankData.score.grade)}`}>
                      {rankData.score.grade}
                    </div>
                    <div className="text-gray-600 mt-2">{rankData.score.level_fa}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Rank Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Global Rank */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold flex items-center gap-2">
                    🌍 رنک جهانی
                  </h3>
                  <span className="text-sm text-gray-500">
                    امتیاز: {rankData.score.global_score.toFixed(1)}
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">رنک جهانی</div>
                    <div className="text-3xl font-bold text-blue-600">
                      {formatRank(rankData.global.global_rank)}
                    </div>
                    {rankData.global.global_rank && (
                      <div className="text-xs text-gray-500 mt-1">
                        از {formatRank(1000000)} سایت برتر
                      </div>
                    )}
                  </div>
                  {rankData.global.traffic_rank && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">رنک ترافیک</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {formatRank(rankData.global.traffic_rank)}
                      </div>
                    </div>
                  )}
                  {rankData.global.country_rank && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">رنک کشوری</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {formatRank(rankData.global.country_rank)}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        کشور: {rankData.global.country || 'N/A'}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Iran Rank */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold flex items-center gap-2">
                    🇮🇷 رنک ایران
                  </h3>
                  <span className="text-sm text-gray-500">
                    امتیاز: {rankData.score.iran_score.toFixed(1)}
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">رنک ایران</div>
                    <div className="text-3xl font-bold text-green-600">
                      {formatRank(rankData.iran.iran_rank)}
                    </div>
                    {rankData.iran.iran_rank && (
                      <div className="text-xs text-gray-500 mt-1">
                        از {formatRank(100000)} سایت برتر ایران
                      </div>
                    )}
                  </div>
                  {rankData.iran.iran_traffic_rank && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">رنک ترافیک ایران</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {formatRank(rankData.iran.iran_traffic_rank)}
                      </div>
                    </div>
                  )}
                  {rankData.iran.local_rank && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600 mb-1">رنک محلی</div>
                      <div className="text-2xl font-bold text-gray-700">
                        {formatRank(rankData.iran.local_rank)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-xl font-semibold mb-4">جزئیات امتیاز</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">امتیاز جهانی</span>
                    <span className={`font-bold ${getScoreColor(rankData.score.global_score)}`}>
                      {rankData.score.global_score.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        rankData.score.global_score >= 80 ? 'bg-green-600' :
                        rankData.score.global_score >= 60 ? 'bg-blue-600' :
                        rankData.score.global_score >= 40 ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}
                      style={{ width: `${Math.min(rankData.score.global_score, 100)}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">امتیاز ایران</span>
                    <span className={`font-bold ${getScoreColor(rankData.score.iran_score)}`}>
                      {rankData.score.iran_score.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        rankData.score.iran_score >= 80 ? 'bg-green-600' :
                        rankData.score.iran_score >= 60 ? 'bg-blue-600' :
                        rankData.score.iran_score >= 40 ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}
                      style={{ width: `${Math.min(rankData.score.iran_score, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sources */}
            {(rankData.global.sources && rankData.global.sources.length > 0) || 
             (rankData.iran.sources && rankData.iran.sources.length > 0) ? (
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-xl font-semibold mb-4">منابع داده</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {rankData.global.sources && rankData.global.sources.map((source, index) => (
                    <div key={`global-${index}`} className="p-3 bg-gray-50 rounded-lg">
                      <div className="font-medium text-gray-700">{source.name}</div>
                      <div className="text-sm text-gray-500">رنک: {formatRank(source.rank)}</div>
                      <div className="text-xs text-gray-400 mt-1">روش: {source.method}</div>
                    </div>
                  ))}
                  {rankData.iran.sources && rankData.iran.sources.map((source, index) => (
                    <div key={`iran-${index}`} className="p-3 bg-gray-50 rounded-lg">
                      <div className="font-medium text-gray-700">{source.name}</div>
                      <div className="text-sm text-gray-500">رنک: {formatRank(source.rank)}</div>
                      <div className="text-xs text-gray-400 mt-1">روش: {source.method}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            {/* Domain Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">اطلاعات دامنه</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">دامنه:</span>
                  <span className="font-medium">{rankData.domain}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">URL:</span>
                  <span className="font-medium text-sm">{rankData.url}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">وضعیت:</span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    rankData.trend === 'up' ? 'bg-green-100 text-green-800' :
                    rankData.trend === 'down' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {rankData.trend === 'up' ? '📈 در حال بهبود' :
                     rankData.trend === 'down' ? '📉 در حال کاهش' :
                     '➡️ ثابت'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">آخرین به‌روزرسانی:</span>
                  <span className="text-sm text-gray-500">
                    {new Date(rankData.last_updated).toLocaleString('fa-IR')}
                  </span>
                </div>
              </div>
            </div>
          </>
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

