'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface ContentItem {
  id?: string
  title?: string
  content?: string
  type?: string
  word_count?: number
  keywords?: string[]
  status?: string
  created_at?: string
  seo_score?: number
  file_path?: string
  file_type?: string
  duration?: string
  description?: string
}

export default function ContentPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null)
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
        
        // استخراج محتوای تولید شده
        const generatedContent = dashboardData.data?.generated_content
        if (generatedContent) {
          if (generatedContent.content_items && Array.isArray(generatedContent.content_items)) {
            setContentItems(generatedContent.content_items)
          } else if (generatedContent.items && Array.isArray(generatedContent.items)) {
            setContentItems(generatedContent.items)
          } else {
            // اگر ساختار متفاوت است، سعی می‌کنیم آن را تبدیل کنیم
            setContentItems([])
          }
        } else {
          setContentItems([])
        }
        
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

  const generatedContent = data?.data?.generated_content || {}
  const totalItems = contentItems.length
  const totalWords = generatedContent.total_words || 0
  const contentTypes = generatedContent.content_types || []

  const getContentTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'text':
      case 'article':
        return 'bg-blue-100 text-blue-800'
      case 'image':
        return 'bg-purple-100 text-purple-800'
      case 'video':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getContentTypeIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'text':
      case 'article':
        return '📝'
      case 'image':
        return '🖼️'
      case 'video':
        return '🎥'
      default:
        return '📄'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">در حال بارگذاری محتوای تولید شده...</p>
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
        <h1 className="text-3xl font-bold mb-8">محتوای تولید شده</h1>
        
        {data?.status === 'processing' && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800">
              ⏳ تحلیل در حال انجام است. محتوا به محض تولید نمایش داده می‌شود...
            </p>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm mb-2">تعداد محتوا</h3>
            <p className="text-3xl font-bold text-blue-600">
              {totalItems}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm mb-2">تعداد کلمات</h3>
            <p className="text-3xl font-bold text-green-600">
              {totalWords.toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm mb-2">انواع محتوا</h3>
            <p className="text-3xl font-bold text-purple-600">
              {contentTypes.length || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-600 text-sm mb-2">وضعیت</h3>
            <p className={`text-lg font-bold ${
              data?.status === 'completed' ? 'text-green-600' :
              data?.status === 'processing' ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {data?.status === 'completed' ? 'تکمیل شده' :
               data?.status === 'processing' ? 'در حال تولید' :
               'نامشخص'}
            </p>
          </div>
        </div>

        {/* Content Types Summary */}
        {contentTypes.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">انواع محتوا</h2>
            <div className="flex flex-wrap gap-3">
              {contentTypes.map((type: string, index: number) => (
                <span
                  key={index}
                  className={`px-4 py-2 rounded-lg font-medium ${getContentTypeColor(type)}`}
                >
                  {getContentTypeIcon(type)} {type}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Content List */}
        {contentItems.length > 0 ? (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">لیست محتوا ({contentItems.length})</h2>
            <div className="space-y-4">
              {contentItems.map((item: ContentItem, index: number) => (
                <div
                  key={item.id || index}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => setSelectedContent(item)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {item.type && (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getContentTypeColor(item.type)}`}>
                            {getContentTypeIcon(item.type)} {item.type}
                          </span>
                        )}
                        {item.status && (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            item.status === 'published' ? 'bg-green-100 text-green-800' :
                            item.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {item.status}
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {item.title || `محتوا ${index + 1}`}
                      </h3>
                      {item.content && (
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {item.content.substring(0, 150)}...
                        </p>
                      )}
                      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                        {item.word_count && (
                          <span>📊 {item.word_count.toLocaleString()} کلمه</span>
                        )}
                        {item.seo_score !== undefined && (
                          <span>⭐ امتیاز سئو: {item.seo_score}/100</span>
                        )}
                        {item.keywords && item.keywords.length > 0 && (
                          <span>🔑 {item.keywords.length} کلمه کلیدی</span>
                        )}
                        {item.created_at && (
                          <span>📅 {new Date(item.created_at).toLocaleDateString('fa-IR')}</span>
                        )}
                      </div>
                      {item.keywords && item.keywords.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {item.keywords.slice(0, 5).map((keyword: string, keyIndex: number) => (
                            <span
                              key={keyIndex}
                              className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                            >
                              {keyword}
                            </span>
                          ))}
                          {item.keywords.length > 5 && (
                            <span className="px-2 py-1 text-gray-500 text-xs">
                              +{item.keywords.length - 5} بیشتر
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedContent(item)
                      }}
                      className="mr-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                    >
                      مشاهده کامل
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="mb-4">
              <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">محتوایی تولید نشده است</h2>
            <p className="text-gray-600 mb-6">
              {data?.status === 'processing' 
                ? 'محتوای تولید شده به محض آماده شدن در اینجا نمایش داده می‌شود.'
                : 'هنوز محتوایی برای این تحلیل تولید نشده است.'}
            </p>
            {data?.status === 'processing' && (
              <div className="inline-flex items-center gap-2 text-blue-600 mb-4">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>در حال تولید...</span>
              </div>
            )}
            {data?.status !== 'processing' && (
              <button
                onClick={async () => {
                  try {
                    setLoading(true)
                    const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/generate-content`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        content_types: ['text', 'image', 'video']
                      })
                    })
                    
                    if (response.ok) {
                      const result = await response.json()
                      alert('محتوای تولید شده با موفقیت! صفحه را رفرش کنید.')
                      // Refresh data
                      window.location.reload()
                    } else {
                      const error = await response.json()
                      alert('خطا در تولید محتوا: ' + (error.detail || 'خطای نامشخص'))
                    }
                  } catch (err) {
                    alert('خطا در تولید محتوا: ' + err)
                  } finally {
                    setLoading(false)
                  }
                }}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                    در حال تولید...
                  </>
                ) : (
                  '✨ تولید محتوا'
                )}
              </button>
            )}
          </div>
        )}

        {/* Content Detail Modal */}
        {selectedContent && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedContent(null)}
          >
            <div
              className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
                <h2 className="text-2xl font-bold">
                  {selectedContent.title || 'جزئیات محتوا'}
                </h2>
                <button
                  onClick={() => setSelectedContent(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              <div className="p-6">
                <div className="mb-6 flex flex-wrap gap-3">
                  {selectedContent.type && (
                    <span className={`px-3 py-1 rounded-lg font-medium ${getContentTypeColor(selectedContent.type)}`}>
                      {getContentTypeIcon(selectedContent.type)} {selectedContent.type}
                    </span>
                  )}
                  {selectedContent.status && (
                    <span className={`px-3 py-1 rounded-lg font-medium ${
                      selectedContent.status === 'published' ? 'bg-green-100 text-green-800' :
                      selectedContent.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {selectedContent.status}
                    </span>
                  )}
                  {selectedContent.seo_score !== undefined && (
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-lg font-medium">
                      امتیاز سئو: {selectedContent.seo_score}/100
                    </span>
                  )}
                </div>

                {/* نمایش ویدیو */}
                {selectedContent.type === 'video' && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">ویدیو</h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      {selectedContent.file_path ? (
                        <video
                          controls
                          className="w-full rounded-lg bg-black"
                          style={{ maxHeight: '500px' }}
                          onError={(e) => {
                            // اگر ویدیو لود نشد، placeholder نمایش بده
                            const videoElement = e.currentTarget
                            videoElement.style.display = 'none'
                            const placeholder = videoElement.parentElement?.querySelector('.video-placeholder')
                            if (placeholder) {
                              (placeholder as HTMLElement).style.display = 'block'
                            }
                          }}
                        >
                          <source
                            src={`http://localhost:8002/dashboard/${analysisId}/content/${selectedContent.id}/download`}
                            type="video/mp4"
                          />
                          مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
                        </video>
                      ) : null}
                      <div className="video-placeholder bg-gray-200 rounded-lg p-8 text-center" style={{ display: selectedContent.file_path ? 'none' : 'block' }}>
                        <div className="mb-4">
                          <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <p className="text-gray-600 font-medium mb-2">ویدیو آموزشی</p>
                        <p className="text-gray-500 text-sm">
                          {selectedContent.description || 'ویدیو در حال تولید است. فایل ویدیو به زودی آماده خواهد شد.'}
                        </p>
                        {selectedContent.duration && (
                          <p className="text-gray-500 mt-2 text-xs">
                            مدت زمان: {selectedContent.duration}
                          </p>
                        )}
                      </div>
                      {selectedContent.description && selectedContent.file_path && (
                        <p className="text-gray-600 mt-4 text-sm">
                          {selectedContent.description}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* نمایش تصویر */}
                {selectedContent.type === 'image' && selectedContent.file_path && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">تصویر</h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <img
                        src={`http://localhost:8002/dashboard/${analysisId}/content/${selectedContent.id}/download`}
                        alt={selectedContent.title || 'تصویر'}
                        className="w-full rounded-lg"
                        style={{ maxHeight: '500px', objectFit: 'contain' }}
                      />
                      {selectedContent.description && (
                        <p className="text-gray-600 mt-4 text-sm">
                          {selectedContent.description}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* نمایش محتوای متنی */}
                {selectedContent.content && selectedContent.type === 'text' && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">محتوا</h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {selectedContent.content}
                      </p>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {selectedContent.word_count && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <span className="text-sm text-gray-600">تعداد کلمات</span>
                      <p className="text-xl font-bold">{selectedContent.word_count.toLocaleString()}</p>
                    </div>
                  )}
                  {selectedContent.created_at && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <span className="text-sm text-gray-600">تاریخ تولید</span>
                      <p className="text-xl font-bold">
                        {new Date(selectedContent.created_at).toLocaleString('fa-IR')}
                      </p>
                    </div>
                  )}
                </div>

                {selectedContent.keywords && selectedContent.keywords.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">کلمات کلیدی</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedContent.keywords.map((keyword: string, index: number) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-lg text-sm"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-4">
                  <button
                    onClick={() => {
                      if (selectedContent.content) {
                        navigator.clipboard.writeText(selectedContent.content)
                        alert('محتوا کپی شد!')
                      }
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    📋 کپی محتوا
                  </button>
                  {selectedContent.file_path ? (
                    <a
                      href={`http://localhost:8002/dashboard/${analysisId}/content/${selectedContent.id}/download`}
                      download
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 inline-block text-center"
                    >
                      💾 دانلود فایل ({selectedContent.file_type?.toUpperCase() || 'FILE'})
                    </a>
                  ) : (
                    <button
                      onClick={() => {
                        const blob = new Blob([selectedContent.content || ''], { type: 'text/plain' })
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.href = url
                        const extension = selectedContent.type === 'text' ? 'txt' : 
                                        selectedContent.type === 'image' ? 'jpg' : 'mp4'
                        a.download = `${selectedContent.title || 'content'}.${extension}`
                        a.click()
                        URL.revokeObjectURL(url)
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      💾 دانلود
                    </button>
                  )}
                </div>
              </div>
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

