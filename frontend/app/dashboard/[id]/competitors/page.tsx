'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface CompetitorKeyword {
  id: string
  keyword: string
  frequency: number
  competitors_count: number
  competitors: Array<{
    url: string
    frequency: number
  }>
  selected: boolean
  priority: 'high' | 'medium' | 'low'
  word_count?: number
  type?: 'single' | 'phrase'
}

interface Competitor {
  url: string
  keywords: Array<{
    keyword: string
    frequency: number
  }>
  meta_info: {
    title?: string
    description?: string
  }
  content_analysis: {
    total_words: number
    h1_count: number
    h2_count: number
  }
}

export default function CompetitorsPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [keywords, setKeywords] = useState<CompetitorKeyword[]>([])
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedKeywords, setSelectedKeywords] = useState<Set<string>>(new Set())
  const [competitorUrls, setCompetitorUrls] = useState<string>('')
  const [showAddCompetitors, setShowAddCompetitors] = useState(false)
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')

  useEffect(() => {
    fetchCompetitorKeywords()
  }, [analysisId])

  const fetchCompetitorKeywords = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/competitor-keywords`)
      if (!response.ok) {
        if (response.status === 404) {
          const errorData = await response.json().catch(() => ({}))
          if (errorData.detail && errorData.detail.includes('Dashboard یافت نشد')) {
            setError('Dashboard یافت نشد. احتمالاً بک‌اند restart شده است. لطفاً یک تحلیل جدید ایجاد کنید.')
          } else {
            setError('هنوز تحلیل رقبا انجام نشده است')
          }
          setLoading(false)
          return
        }
        throw new Error(`Failed to fetch: ${response.status}`)
      }
      
      const data = await response.json()
      setKeywords(data.keywords || [])
      setCompetitors(data.competitors || [])
      
      // بازیابی کلمات کلیدی انتخاب شده
      const selected = new Set<string>()
      data.keywords?.forEach((kw: CompetitorKeyword) => {
        if (kw.selected) {
          selected.add(kw.id)
        }
      })
      setSelectedKeywords(selected)
      
    } catch (err) {
      console.error('Error:', err)
      setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeCompetitors = async () => {
    if (!competitorUrls.trim()) {
      alert('لطفاً حداقل یک آدرس رقیب وارد کنید')
      return
    }

    setAnalyzing(true)
    setError(null)

    try {
      // تبدیل متن به آرایه URL
      const urls = competitorUrls
        .split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0 && (url.startsWith('http://') || url.startsWith('https://')))

      if (urls.length === 0) {
        alert('لطفاً آدرس‌های معتبر وارد کنید (با http:// یا https://)')
        setAnalyzing(false)
        return
      }

      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/analyze-competitors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          competitor_urls: urls
        })
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'خطا در ارتباط با سرور' }))
        if (response.status === 404 && error.detail && error.detail.includes('Dashboard یافت نشد')) {
          throw new Error('Dashboard یافت نشد. احتمالاً بک‌اند restart شده است. لطفاً یک تحلیل جدید ایجاد کنید.')
        }
        throw new Error(error.detail || 'خطا در تحلیل رقبا')
      }

      const result = await response.json()
      alert(`✅ ${result.message}`)
      
      setShowAddCompetitors(false)
      setCompetitorUrls('')
      
      // به‌روزرسانی لیست
      await fetchCompetitorKeywords()
      
    } catch (err) {
      alert('خطا در تحلیل رقبا: ' + (err instanceof Error ? err.message : 'خطای نامشخص'))
    } finally {
      setAnalyzing(false)
    }
  }

  const handleToggleKeyword = (keywordId: string) => {
    setSelectedKeywords(prev => {
      const newSet = new Set(prev)
      if (newSet.has(keywordId)) {
        newSet.delete(keywordId)
      } else {
        newSet.add(keywordId)
      }
      return newSet
    })
  }

  const handleSelectAll = () => {
    if (selectedKeywords.size === keywords.length) {
      setSelectedKeywords(new Set())
    } else {
      setSelectedKeywords(new Set(keywords.map(kw => kw.id)))
    }
  }

  const handleUseSelectedKeywords = () => {
    if (selectedKeywords.size === 0) {
      alert('لطفاً حداقل یک کلمه کلیدی انتخاب کنید')
      return
    }

    const selected = keywords.filter(kw => selectedKeywords.has(kw.id))
    const keywordList = selected.map(kw => kw.keyword).join(', ')
    
    alert(`✅ ${selected.length} کلمه کلیدی انتخاب شد:\n\n${keywordList}\n\nاین کلمات کلیدی برای تولید محتوا استفاده خواهند شد.`)
    
    // در اینجا می‌توانید کلمات کلیدی را به سیستم تولید محتوا ارسال کنید
    // یا در localStorage ذخیره کنید
    localStorage.setItem(`selected_keywords_${analysisId}`, JSON.stringify(selected))
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

  if (loading && keywords.length === 0) {
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

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">تحلیل رقبا و کلمات کلیدی</h1>
          <p className="text-gray-600">مطالعه سایت‌های رقیب و استخراج کلمات کلیدی برای تولید محتوا</p>
        </div>

        {/* دکمه افزودن رقبا */}
        {keywords.length === 0 && !error && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="text-center">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">هنوز رقیبی تحلیل نشده است</h2>
              <p className="text-gray-600 mb-6">
                برای شروع، آدرس سایت‌های رقیب را وارد کنید تا کلمات کلیدی آنها استخراج شود.
              </p>
              <button
                onClick={() => setShowAddCompetitors(true)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                ➕ افزودن رقبا
              </button>
            </div>
          </div>
        )}

        {/* فرم افزودن رقبا */}
        {showAddCompetitors && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">افزودن رقبا برای تحلیل</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  آدرس سایت‌های رقیب (هر آدرس در یک خط)
                </label>
                <textarea
                  value={competitorUrls}
                  onChange={(e) => setCompetitorUrls(e.target.value)}
                  placeholder="https://competitor1.com&#10;https://competitor2.com&#10;https://competitor3.com"
                  rows={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-sm text-gray-500 mt-2">
                  هر آدرس باید با http:// یا https:// شروع شود
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleAnalyzeCompetitors}
                  disabled={analyzing}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                >
                  {analyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                      در حال تحلیل...
                    </>
                  ) : (
                    '🔍 شروع تحلیل رقبا'
                  )}
                </button>
                <button
                  onClick={() => {
                    setShowAddCompetitors(false)
                    setCompetitorUrls('')
                  }}
                  className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium"
                >
                  انصراف
                </button>
              </div>
            </div>
          </div>
        )}

        {/* نمایش خطا */}
        {error && keywords.length === 0 && (
          <div className={`border rounded-lg p-6 mb-6 ${
            error.includes('Dashboard یافت نشد') || error.includes('restart')
              ? 'bg-red-50 border-red-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-start">
              <svg className={`h-6 w-6 mr-3 mt-1 ${
                error.includes('Dashboard یافت نشد') || error.includes('restart')
                  ? 'text-red-600'
                  : 'text-yellow-600'
              }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <p className={`font-semibold ${
                  error.includes('Dashboard یافت نشد') || error.includes('restart')
                    ? 'text-red-900'
                    : 'text-yellow-900'
                }`}>{error}</p>
                {error.includes('Dashboard یافت نشد') || error.includes('restart') ? (
                  <div className="mt-4 space-y-2">
                    <p className="text-sm text-red-700">
                      برای استفاده از این قابلیت، لطفاً:
                    </p>
                    <ol className="list-decimal list-inside text-sm text-red-700 space-y-1">
                      <li>یک تحلیل جدید از صفحه اصلی ایجاد کنید</li>
                      <li>منتظر بمانید تا تحلیل کامل شود</li>
                      <li>سپس به این صفحه بازگردید</li>
                    </ol>
                    <div className="mt-4 flex gap-3">
                      <Link
                        href="/"
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
                      >
                        ایجاد تحلیل جدید
                      </Link>
                      <Link
                        href={`/dashboard/${analysisId}`}
                        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 text-sm font-medium"
                      >
                        بازگشت به داشبورد
                      </Link>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowAddCompetitors(true)}
                    className="mt-2 text-yellow-700 hover:text-yellow-900 underline"
                  >
                    افزودن رقبا برای تحلیل
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* خلاصه انتخاب */}
        {selectedKeywords.size > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-blue-900">
                  {selectedKeywords.size} کلمه کلیدی انتخاب شده
                </p>
                <p className="text-sm text-blue-700">
                  آماده استفاده در تولید محتوا
                </p>
              </div>
              <button
                onClick={handleUseSelectedKeywords}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                ✅ استفاده از کلمات انتخاب شده
              </button>
            </div>
          </div>
        )}

        {/* لیست کلمات کلیدی */}
        {keywords.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">
                کلمات کلیدی استخراج شده ({keywords.length})
              </h2>
              <div className="flex gap-3">
                {/* فیلتر اولویت */}
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value as 'all' | 'high' | 'medium' | 'low')}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">همه اولویت‌ها</option>
                  <option value="high">اولویت بالا</option>
                  <option value="medium">اولویت متوسط</option>
                  <option value="low">اولویت پایین</option>
                </select>
                <button
                  onClick={handleSelectAll}
                  className="px-4 py-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  {selectedKeywords.size === keywords.length ? 'لغو انتخاب همه' : 'انتخاب همه'}
                </button>
                {!showAddCompetitors && (
                  <button
                    onClick={() => setShowAddCompetitors(true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                  >
                    ➕ افزودن رقیب جدید
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-3">
              {keywords
                .filter(kw => priorityFilter === 'all' || kw.priority === priorityFilter)
                .map((keyword) => {
                const isSelected = selectedKeywords.has(keyword.id)
                return (
                  <div
                    key={keyword.id}
                    className={`border rounded-lg p-4 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } cursor-pointer`}
                    onClick={() => handleToggleKeyword(keyword.id)}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleToggleKeyword(keyword.id)}
                        className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <h3 className="text-lg font-semibold text-gray-900">{keyword.keyword}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${getPriorityColor(keyword.priority)}`}>
                            {keyword.priority === 'high' ? '🔥 اولویت بالا' :
                             keyword.priority === 'medium' ? '⭐ اولویت متوسط' :
                             '📌 اولویت پایین'}
                          </span>
                          {keyword.word_count && keyword.word_count > 1 && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                              {keyword.word_count} کلمه‌ای
                            </span>
                          )}
                          <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                            فرکانس: {keyword.frequency}
                          </span>
                          <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                            در {keyword.competitors_count} رقیب
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          <p className="mb-2">
                            این کلمه کلیدی در {keyword.competitors_count} سایت رقیب یافت شده است.
                          </p>
                          <details className="mt-2">
                            <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                              مشاهده رقبا ({keyword.competitors.length})
                            </summary>
                            <div className="mt-2 space-y-1">
                              {keyword.competitors.map((comp, idx) => (
                                <div key={idx} className="text-xs text-gray-500 pl-4">
                                  • <a href={comp.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                    {comp.url}
                                  </a> (فرکانس: {comp.frequency})
                                </div>
                              ))}
                            </div>
                          </details>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* لیست رقبا */}
        {competitors.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">سایت‌های رقیب تحلیل شده ({competitors.length})</h2>
            <div className="space-y-4">
              {competitors.map((competitor, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-2">
                        <a href={competitor.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                          {competitor.url}
                        </a>
                      </h3>
                      {competitor.meta_info?.title && (
                        <p className="text-sm text-gray-600 mb-1">
                          <strong>عنوان:</strong> {competitor.meta_info.title}
                        </p>
                      )}
                      {competitor.meta_info?.description && (
                        <p className="text-sm text-gray-600 mb-2">
                          <strong>توضیحات:</strong> {competitor.meta_info.description}
                        </p>
                      )}
                      <div className="flex gap-4 text-xs text-gray-500 mt-2">
                        <span>کلمات: {competitor.content_analysis?.total_words || 0}</span>
                        <span>H1: {competitor.content_analysis?.h1_count || 0}</span>
                        <span>H2: {competitor.content_analysis?.h2_count || 0}</span>
                        <span>کلمات کلیدی: {competitor.keywords?.length || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* لینک بازگشت */}
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

