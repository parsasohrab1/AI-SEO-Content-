'use client'

import { useState, useEffect, useRef } from 'react'
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
  data?: {
    site_analysis?: any
    seo_analysis?: any
    generated_content?: any
    implementation?: any
    placement?: any
  }
  strengths?: any[]
  weaknesses?: any[]
  recommendations?: any[]
  rank_data?: any
  created_at?: string
  updated_at?: string
}

export default function DashboardPage() {
  const params = useParams()
  const analysisId = params.id as string
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const shouldPollRef = useRef<boolean>(true)

  useEffect(() => {
    const fetchDashboard = async () => {
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
          throw new Error('Dashboard not found')
        }
        const dashboardData = await response.json()
        setData(dashboardData)
        setError(null)
        
        // Continue polling even after completion for real-time updates
        if (dashboardData.status === 'failed') {
          shouldPollRef.current = false
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        } else if (dashboardData.status === 'completed') {
          // Reduce polling frequency after completion but keep polling for updates
          const hasData = dashboardData.data?.site_analysis || dashboardData.data?.seo_analysis
          if (hasData && intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
            // Continue with slower polling (every 10 seconds instead of 5)
            intervalRef.current = setInterval(() => {
              if (shouldPollRef.current) {
                fetchDashboard()
              }
            }, 10000)
          }
        }
      } catch (err) {
        // Only set error if it's not a 404 (which we already handled)
        if (!err || (err instanceof Error && !err.message.includes('404'))) {
          setError(err instanceof Error ? err.message : 'خطا در دریافت داده‌ها')
          setLoading(false)
        }
        // Don't stop polling on network errors, only on 404
        if (err instanceof Error && err.message.includes('404')) {
          shouldPollRef.current = false
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      } finally {
        setLoading(false)
      }
    }

    if (analysisId) {
      shouldPollRef.current = true
      fetchDashboard()
      // Poll for updates every 5 seconds until data is ready
      intervalRef.current = setInterval(() => {
        if (shouldPollRef.current) {
          fetchDashboard()
        } else {
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      }, 5000)
      
      return () => {
        shouldPollRef.current = false
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
      }
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
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="mb-4">
              <svg className="mx-auto h-16 w-16 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard یافت نشد</h2>
            <p className="text-gray-600 mb-4">{error || 'Dashboard یافت نشد'}</p>
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
            </div>
          </div>
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
              <Link
                href={`/dashboard/${analysisId}/content`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                محتوای تولید شده
              </Link>
              <Link
                href={`/dashboard/${analysisId}/rank`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                رنک سایت
              </Link>
              <Link
                href={`/dashboard/${analysisId}/apply`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                اجرای پیشنهادات
              </Link>
              <Link
                href={`/dashboard/${analysisId}/competitors`}
                className="px-6 py-4 text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-600"
              >
                تحلیل رقبا
              </Link>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          {data.status === 'processing' && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                ⏳ تحلیل در حال انجام است. لطفاً چند لحظه صبر کنید...
              </p>
            </div>
          )}

          {/* No Data Message */}
          {data.status === 'completed' && !data.data?.site_analysis && !data.data?.seo_analysis && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
              <p className="text-blue-800 mb-2">
                ✓ تحلیل تکمیل شده است
              </p>
              <p className="text-sm text-blue-600">
                داده‌های تحلیل در حال آماده‌سازی است. لطفاً چند لحظه صبر کنید...
              </p>
            </div>
          )}

          {/* Site Analysis Summary */}
          {data.data?.site_analysis && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">خلاصه تحلیل سایت</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.data.site_analysis.cms_type && (
                  <div>
                    <span className="text-sm text-gray-600">نوع CMS:</span>
                    <p className="font-medium capitalize">{data.data.site_analysis.cms_type}</p>
                  </div>
                )}
                {data.data.site_analysis.structure?.headings && (
                  <div>
                    <span className="text-sm text-gray-600">ساختار:</span>
                    <p className="font-medium">
                      H1: {data.data.site_analysis.structure.headings.h1 || 0} | 
                      H2: {data.data.site_analysis.structure.headings.h2 || 0} | 
                      H3: {data.data.site_analysis.structure.headings.h3 || 0}
                    </p>
                  </div>
                )}
                {data.data.site_analysis.security?.ssl_enabled !== undefined && (
                  <div>
                    <span className="text-sm text-gray-600">HTTPS:</span>
                    <p className="font-medium">
                      {data.data.site_analysis.security.ssl_enabled ? (
                        <span className="text-green-600">✓ فعال</span>
                      ) : (
                        <span className="text-red-600">✗ غیرفعال</span>
                      )}
                    </p>
                  </div>
                )}
                {data.data.site_analysis.sitemap?.found !== undefined && (
                  <div>
                    <span className="text-sm text-gray-600">Sitemap:</span>
                    <p className="font-medium">
                      {data.data.site_analysis.sitemap.found ? (
                        <span className="text-green-600">✓ موجود</span>
                      ) : (
                        <span className="text-yellow-600">⚠ موجود نیست</span>
                      )}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Generated Content */}
          {data.data?.generated_content && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">محتوای تولید شده</h2>
              <div className="space-y-3">
                {data.data.generated_content.content_items && (
                  <div>
                    <span className="text-sm text-gray-600">تعداد محتوا:</span>
                    <p className="font-medium">{data.data.generated_content.content_items.length || 0} مورد</p>
                  </div>
                )}
                {data.data.generated_content.total_words && (
                  <div>
                    <span className="text-sm text-gray-600">تعداد کلمات:</span>
                    <p className="font-medium">{data.data.generated_content.total_words.toLocaleString()} کلمه</p>
                  </div>
                )}
                <Link
                  href={`/dashboard/${analysisId}/content`}
                  className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  مشاهده جزئیات محتوا
                </Link>
              </div>
            </div>
          )}

          {/* SEO Implementation Results */}
          {data.data?.implementation && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">نتایج پیاده‌سازی سئو</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {data.data.implementation.successful_changes !== undefined && (
                  <div className="p-4 bg-green-50 rounded-lg">
                    <span className="text-sm text-gray-600">تغییرات موفق:</span>
                    <p className="text-2xl font-bold text-green-600">
                      {data.data.implementation.successful_changes}
                    </p>
                  </div>
                )}
                {data.data.implementation.failed_changes !== undefined && (
                  <div className="p-4 bg-red-50 rounded-lg">
                    <span className="text-sm text-gray-600">تغییرات ناموفق:</span>
                    <p className="text-2xl font-bold text-red-600">
                      {data.data.implementation.failed_changes}
                    </p>
                  </div>
                )}
                {data.data.implementation.total_fixes !== undefined && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <span className="text-sm text-gray-600">کل اصلاحات:</span>
                    <p className="text-2xl font-bold text-blue-600">
                      {data.data.implementation.total_fixes}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Content Placement Results */}
          {data.data?.placement && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">نتایج جانمایی محتوا</h2>
              <div className="space-y-2">
                {data.data.placement.placed_content && (
                  <div>
                    <span className="text-sm text-gray-600">محتوای جانمایی شده:</span>
                    <p className="font-medium">{data.data.placement.placed_content.length || 0} مورد</p>
                  </div>
                )}
                {data.data.placement.published_pages && (
                  <div>
                    <span className="text-sm text-gray-600">صفحات منتشر شده:</span>
                    <p className="font-medium">{data.data.placement.published_pages.length || 0} صفحه</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">عملیات</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/seo-report`)
                    if (response.ok) {
                      const report = await response.json()
                      
                      // Create a formatted HTML report
                      const html = `
                        <!DOCTYPE html>
                        <html dir="rtl" lang="fa">
                        <head>
                          <meta charset="UTF-8">
                          <title>گزارش کامل سئو - ${report.site_url || report.analysis_id}</title>
                          <style>
                            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background: #f5f5f5; }
                            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                            h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
                            h2 { color: #1e40af; margin-top: 30px; margin-bottom: 15px; }
                            h3 { color: #3b82f6; margin-top: 20px; }
                            .score { font-size: 48px; font-weight: bold; color: #10b981; text-align: center; margin: 20px 0; }
                            .grade { font-size: 32px; text-align: center; color: #2563eb; margin-bottom: 20px; }
                            .summary { background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
                            .section { margin: 25px 0; padding: 20px; background: #f9fafb; border-radius: 8px; }
                            .issue { padding: 15px; margin: 10px 0; border-right: 4px solid #ef4444; background: #fef2f2; border-radius: 4px; }
                            .strength { padding: 15px; margin: 10px 0; border-right: 4px solid #10b981; background: #f0fdf4; border-radius: 4px; }
                            .priority-high { border-right-color: #ef4444; }
                            .priority-medium { border-right-color: #f59e0b; }
                            .priority-low { border-right-color: #3b82f6; }
                            table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                            th, td { padding: 12px; text-align: right; border: 1px solid #e5e7eb; }
                            th { background: #f3f4f6; font-weight: bold; }
                            .badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }
                            .badge-success { background: #d1fae5; color: #065f46; }
                            .badge-warning { background: #fef3c7; color: #92400e; }
                            .badge-danger { background: #fee2e2; color: #991b1b; }
                            pre { background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 6px; overflow-x: auto; }
                          </style>
                        </head>
                        <body>
                          <div class="container">
                            <h1>📊 گزارش کامل سئو</h1>
                            
                            ${report.error ? `
                              <div class="section" style="background: #fee2e2; border-right: 4px solid #ef4444;">
                                <h2>خطا</h2>
                                <p>${report.error}</p>
                              </div>
                            ` : `
                            
                            ${report.overall_score ? `
                              <div class="summary">
                                <div class="score">${report.overall_score.overall}/100</div>
                                <div class="grade">امتیاز: ${report.overall_score.grade}</div>
                                <p style="text-align: center; color: #6b7280;">${report.site_url}</p>
                              </div>
                            ` : ''}
                            
                            ${report.executive_summary ? `
                              <div class="section">
                                <h2>📋 خلاصه اجرایی</h2>
                                <p>${report.executive_summary.summary}</p>
                                <table>
                                  <tr><th>نقاط قوت</th><td>${report.executive_summary.total_strengths}</td></tr>
                                  <tr><th>نقاط ضعف</th><td>${report.executive_summary.total_weaknesses}</td></tr>
                                  <tr><th>مشکلات با اولویت بالا</th><td>${report.executive_summary.high_priority_issues}</td></tr>
                                  <tr><th>نوع CMS</th><td>${report.executive_summary.cms_type}</td></tr>
                                  <tr><th>HTTPS</th><td>${report.executive_summary.has_ssl ? '✓ فعال' : '✗ غیرفعال'}</td></tr>
                                  <tr><th>Sitemap</th><td>${report.executive_summary.has_sitemap ? '✓ موجود' : '✗ موجود نیست'}</td></tr>
                                </table>
                              </div>
                            ` : ''}
                            
                            ${report.strengths && report.strengths.length > 0 ? `
                              <div class="section">
                                <h2>✅ نقاط قوت (${report.strengths.length})</h2>
                                ${report.strengths.map((s: any) => `
                                  <div class="strength">
                                    <strong>${s.title}</strong>
                                    <p>${s.description}</p>
                                    <span class="badge badge-success">${s.category}</span>
                                  </div>
                                `).join('')}
                              </div>
                            ` : ''}
                            
                            ${report.weaknesses && report.weaknesses.length > 0 ? `
                              <div class="section">
                                <h2>⚠️ نقاط ضعف (${report.weaknesses.length})</h2>
                                ${report.weaknesses.map((w: any) => `
                                  <div class="issue priority-${w.priority || 'medium'}">
                                    <strong>${w.title}</strong>
                                    <p>${w.description}</p>
                                    <span class="badge badge-${w.priority === 'high' ? 'danger' : w.priority === 'medium' ? 'warning' : 'success'}">
                                      ${w.priority || 'medium'} - ${w.category}
                                    </span>
                                  </div>
                                `).join('')}
                              </div>
                            ` : ''}
                            
                            ${report.issues_and_solutions && report.issues_and_solutions.length > 0 ? `
                              <div class="section">
                                <h2>🔧 مشکلات و راه‌حل‌ها</h2>
                                ${report.issues_and_solutions.map((item: any, idx: number) => `
                                  <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 6px; border: 1px solid #e5e7eb;">
                                    <h3>${idx + 1}. ${item.issue}</h3>
                                    <p><strong>توضیحات:</strong> ${item.description}</p>
                                    <p><strong>اولویت:</strong> <span class="badge badge-${item.priority === 'high' ? 'danger' : 'warning'}">${item.priority}</span></p>
                                    ${item.solution && item.solution.steps ? `
                                      <div style="margin-top: 10px;">
                                        <strong>راه‌حل:</strong>
                                        <ol style="margin-right: 20px;">
                                          ${item.solution.steps.map((step: string) => `<li>${step}</li>`).join('')}
                                        </ol>
                                        <p><strong>زمان تخمینی:</strong> ${item.solution.estimated_time || 'N/A'}</p>
                                      </div>
                                    ` : ''}
                                  </div>
                                `).join('')}
                              </div>
                            ` : ''}
                            
                            ${report.priority_recommendations && report.priority_recommendations.length > 0 ? `
                              <div class="section">
                                <h2>🎯 توصیه‌های اولویت‌دار</h2>
                                ${report.priority_recommendations.map((rec: any) => `
                                  <div style="padding: 15px; margin: 10px 0; background: white; border-radius: 6px;">
                                    <strong>${rec.title}</strong>
                                    <p>${rec.impact}</p>
                                    <p><strong>اقدام:</strong> ${rec.action}</p>
                                  </div>
                                `).join('')}
                              </div>
                            ` : ''}
                            
                            ${report.implementation_timeline && report.implementation_timeline.length > 0 ? `
                              <div class="section">
                                <h2>📅 جدول زمانی پیشنهادی</h2>
                                ${report.implementation_timeline.map((phase: any) => `
                                  <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 6px;">
                                    <h3>${phase.phase}</h3>
                                    <ul style="margin-right: 20px;">
                                      ${phase.items.map((item: string) => `<li>${item}</li>`).join('')}
                                    </ul>
                                    <p><strong>زمان تخمینی:</strong> ${phase.estimated_time}</p>
                                  </div>
                                `).join('')}
                              </div>
                            ` : ''}
                            
                            <div class="section">
                              <h2>📄 اطلاعات گزارش</h2>
                              <p><strong>تاریخ تولید:</strong> ${new Date(report.generated_at).toLocaleString('fa-IR')}</p>
                              <p><strong>شناسه تحلیل:</strong> ${report.analysis_id}</p>
                              ${report.created_at ? `<p><strong>تاریخ ایجاد:</strong> ${new Date(report.created_at).toLocaleString('fa-IR')}</p>` : ''}
                            </div>
                            
                            `}
                          </div>
                        </body>
                        </html>
                      `
                      
                      // Create a new window with the formatted report
                      const newWindow = window.open('', '_blank')
                      if (newWindow) {
                        newWindow.document.write(html)
                        newWindow.document.close()
                      }
                    } else {
                      alert('خطا در دریافت گزارش')
                    }
                  } catch (err) {
                    alert('خطا در دریافت گزارش: ' + err)
                  }
                }}
                className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-right"
              >
                📊 دریافت گزارش کامل سئو
              </button>
              
              <button
                onClick={async () => {
                  const fixes = prompt('لطفاً لیست ID اصلاحات را وارد کنید (با کاما جدا کنید):')
                  if (fixes) {
                    try {
                      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/apply-fixes`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ fixes: fixes.split(',').map(f => f.trim()) })
                      })
                      const result = await response.json()
                      alert(JSON.stringify(result, null, 2))
                    } catch (err) {
                      alert('خطا در اعمال اصلاحات: ' + err)
                    }
                  }
                }}
                className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-right"
              >
                ✅ اعمال اصلاحات انتخاب شده
              </button>
              
              <button
                onClick={async () => {
                  const contentType = prompt('نوع محتوا را وارد کنید (text/image/video):', 'text')
                  if (contentType) {
                    try {
                      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/generate-content`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content_type: contentType, count: 1 })
                      })
                      const result = await response.json()
                      alert(JSON.stringify(result, null, 2))
                    } catch (err) {
                      alert('خطا در تولید محتوا: ' + err)
                    }
                  }
                }}
                className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-right"
              >
                ✨ تولید محتوای جدید
              </button>
              
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/live-monitoring`)
                    if (response.ok) {
                      const monitoring = await response.json()
                      
                      // Create a formatted HTML for live monitoring
                      const html = `
                        <!DOCTYPE html>
                        <html dir="rtl" lang="fa">
                        <head>
                          <meta charset="UTF-8">
                          <title>مانیتورینگ زنده - ${monitoring.site_url || monitoring.analysis_id}</title>
                          <style>
                            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background: #f5f5f5; }
                            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                            h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
                            h2 { color: #1e40af; margin-top: 30px; margin-bottom: 15px; }
                            .status-badge { display: inline-block; padding: 6px 12px; border-radius: 6px; font-weight: bold; margin: 5px; }
                            .status-good { background: #d1fae5; color: #065f46; }
                            .status-warning { background: #fef3c7; color: #92400e; }
                            .status-error { background: #fee2e2; color: #991b1b; }
                            .status-info { background: #dbeafe; color: #1e40af; }
                            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                            .metric-card { background: #f9fafb; padding: 15px; border-radius: 8px; border-right: 4px solid #3b82f6; }
                            .metric-value { font-size: 24px; font-weight: bold; color: #1e40af; }
                            .metric-label { font-size: 12px; color: #6b7280; margin-top: 5px; }
                            .alert { padding: 15px; margin: 10px 0; border-radius: 6px; border-right: 4px solid; }
                            .alert-error { background: #fef2f2; border-color: #ef4444; }
                            .alert-warning { background: #fffbeb; border-color: #f59e0b; }
                            .alert-info { background: #eff6ff; border-color: #3b82f6; }
                            table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                            th, td { padding: 12px; text-align: right; border: 1px solid #e5e7eb; }
                            th { background: #f3f4f6; font-weight: bold; }
                            .timestamp { color: #6b7280; font-size: 12px; }
                          </style>
                        </head>
                        <body>
                          <div class="container">
                            <h1>📈 مانیتورینگ زنده</h1>
                            
                            ${monitoring.error ? `
                              <div class="alert alert-error" style="margin-bottom: 20px;">
                                <h2 style="margin-top: 0;">⚠️ خطا در تحلیل</h2>
                                <p><strong>پیام خطا:</strong> ${monitoring.error}</p>
                                <p style="font-size: 12px; margin-top: 10px; color: #6b7280;">
                                  اگر این خطا ادامه دارد، لطفاً یک تحلیل جدید ایجاد کنید یا با پشتیبانی تماس بگیرید.
                                </p>
                              </div>
                            ` : ''}
                            
                            ${(!monitoring.has_data && monitoring.status === 'failed') ? `
                              <div class="alert alert-warning" style="margin-bottom: 20px;">
                                <h2 style="margin-top: 0;">⚠️ داده‌های تحلیل موجود نیست</h2>
                                <p>تحلیل با خطا مواجه شده و داده‌های کافی برای نمایش جمع‌آوری نشده است.</p>
                                <p style="font-size: 12px; margin-top: 10px; color: #6b7280;">
                                  لطفاً یک تحلیل جدید ایجاد کنید.
                                </p>
                              </div>
                            ` : ''}
                            
                            <div style="margin: 20px 0;">
                              <span class="status-badge status-${monitoring.status === 'completed' ? 'good' : monitoring.status === 'processing' ? 'warning' : 'error'}">
                                وضعیت: ${monitoring.status === 'completed' ? 'تکمیل شده' : monitoring.status === 'processing' ? 'در حال پردازش' : 'خطا'}
                              </span>
                              <span class="timestamp">آخرین به‌روزرسانی: ${new Date(monitoring.timestamp).toLocaleString('fa-IR')}</span>
                              ${monitoring.has_data ? '<span class="status-badge status-info" style="margin-right: 10px;">✓ داده‌ها موجود است</span>' : '<span class="status-badge status-warning" style="margin-right: 10px;">⚠ داده‌ها ناقص است</span>'}
                            </div>
                            
                            ${monitoring.current_status ? `
                              <div class="metrics-grid">
                                <div class="metric-card">
                                  <div class="metric-value">${monitoring.current_status.site_accessible ? '✓' : '✗'}</div>
                                  <div class="metric-label">دسترسی سایت</div>
                                </div>
                                <div class="metric-card">
                                  <div class="metric-value">${monitoring.current_status.ssl_status ? '✓' : '✗'}</div>
                                  <div class="metric-label">وضعیت SSL</div>
                                </div>
                                <div class="metric-card">
                                  <div class="metric-value">${monitoring.current_status.response_time ? monitoring.current_status.response_time.toFixed(2) + 's' : 'N/A'}</div>
                                  <div class="metric-label">زمان پاسخ</div>
                                </div>
                                <div class="metric-card">
                                  <div class="metric-value">${monitoring.current_status.status_code || 'N/A'}</div>
                                  <div class="metric-label">Status Code</div>
                                </div>
                              </div>
                            ` : ''}
                            
                            ${monitoring.performance_metrics ? `
                              <h2>📊 متریک‌های عملکرد</h2>
                              <table>
                                <tr><th>زمان پاسخ</th><td>${monitoring.performance_metrics.response_time ? monitoring.performance_metrics.response_time.toFixed(2) + 's' : 'N/A'}</td></tr>
                                <tr><th>وضعیت زمان پاسخ</th><td><span class="status-badge status-${monitoring.performance_metrics.response_time_status === 'excellent' || monitoring.performance_metrics.response_time_status === 'good' ? 'good' : 'warning'}">${monitoring.performance_metrics.response_time_status}</span></td></tr>
                                <tr><th>طول محتوا</th><td>${monitoring.performance_metrics.content_length ? (monitoring.performance_metrics.content_length / 1024).toFixed(2) + ' KB' : 'N/A'}</td></tr>
                                <tr><th>Status Code</th><td>${monitoring.performance_metrics.status_code || 'N/A'}</td></tr>
                              </table>
                            ` : ''}
                            
                            ${monitoring.security_metrics ? `
                              <h2>🔒 متریک‌های امنیت</h2>
                              <table>
                                <tr><th>SSL فعال</th><td>${monitoring.security_metrics.ssl_enabled ? '✓ بله' : '✗ خیر'}</td></tr>
                                <tr><th>تعداد Security Headers</th><td>${monitoring.security_metrics.security_headers_count}</td></tr>
                                <tr><th>تعداد آسیب‌پذیری‌ها</th><td>${monitoring.security_metrics.vulnerabilities_count}</td></tr>
                                <tr><th>امتیاز امنیت</th><td><strong>${monitoring.security_metrics.security_score}/100</strong></td></tr>
                              </table>
                            ` : ''}
                            
                            ${monitoring.seo_metrics ? `
                              <h2>🔍 متریک‌های سئو</h2>
                              <table>
                                <tr><th>Crawlability</th><td><span class="status-badge status-${monitoring.seo_metrics.crawlability === 'good' ? 'good' : 'warning'}">${monitoring.seo_metrics.crawlability}</span></td></tr>
                                <tr><th>Indexability</th><td><span class="status-badge status-${monitoring.seo_metrics.indexability === 'good' ? 'good' : 'warning'}">${monitoring.seo_metrics.indexability}</span></td></tr>
                                <tr><th>تعداد کلمات کلیدی</th><td>${monitoring.seo_metrics.keywords_count}</td></tr>
                                <tr><th>امتیاز خوانایی</th><td>${monitoring.seo_metrics.readability_score}/100</td></tr>
                                <tr><th>تعداد مشکلات</th><td>${monitoring.seo_metrics.issues_count}</td></tr>
                              </table>
                            ` : ''}
                            
                            ${monitoring.recent_changes ? `
                              <h2>🔄 تغییرات اخیر</h2>
                              <table>
                                <tr><th>تعداد نقاط قوت</th><td>${monitoring.recent_changes.strengths_count}</td></tr>
                                <tr><th>تعداد نقاط ضعف</th><td>${monitoring.recent_changes.weaknesses_count}</td></tr>
                                <tr><th>آخرین به‌روزرسانی</th><td>${monitoring.recent_changes.time_since_update}</td></tr>
                              </table>
                            ` : ''}
                            
                            ${monitoring.alerts && monitoring.alerts.length > 0 ? `
                              <h2>⚠️ هشدارها</h2>
                              ${monitoring.alerts.map((alert: any) => `
                                <div class="alert alert-${alert.type}">
                                  <strong>${alert.type === 'error' ? '❌' : alert.type === 'warning' ? '⚠️' : 'ℹ️'} ${alert.message}</strong>
                                  <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">
                                    اولویت: ${alert.priority} | ${new Date(alert.timestamp).toLocaleString('fa-IR')}
                                  </p>
                                </div>
                              `).join('')}
                            ` : ''}
                            
                            ${monitoring.predictions ? `
                              <h2>🔮 پیش‌بینی‌ها</h2>
                              <table>
                                <tr><th>زمان تخمینی تکمیل</th><td>${monitoring.predictions.estimated_completion}</td></tr>
                                <tr><th>زمان پیشنهادی بررسی بعدی</th><td>${new Date(monitoring.predictions.next_check_recommended).toLocaleString('fa-IR')}</td></tr>
                              </table>
                            ` : ''}
                            
                            <div style="margin-top: 30px; padding: 15px; background: #f9fafb; border-radius: 6px;">
                              <p class="timestamp">زمان تولید گزارش: ${new Date(monitoring.timestamp).toLocaleString('fa-IR')}</p>
                              <p class="timestamp">شناسه تحلیل: ${monitoring.analysis_id}</p>
                              <p class="timestamp">Uptime: ${Math.floor(monitoring.uptime_seconds / 60)} دقیقه و ${monitoring.uptime_seconds % 60} ثانیه</p>
                            </div>
                          </div>
                        </body>
                        </html>
                      `
                      
                      // Create a new window with the formatted monitoring
                      const newWindow = window.open('', '_blank')
                      if (newWindow) {
                        newWindow.document.write(html)
                        newWindow.document.close()
                      }
                    } else {
                      alert('خطا در دریافت مانیتورینگ')
                    }
                  } catch (err) {
                    alert('خطا در دریافت مانیتورینگ: ' + err)
                  }
                }}
                className="px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-right"
              >
                📈 مانیتورینگ زنده
              </button>
            </div>
          </div>

          {/* Strengths & Weaknesses Summary */}
          {((data.strengths && data.strengths.length > 0) || (data.weaknesses && data.weaknesses.length > 0)) && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">خلاصه نقاط قوت و ضعف</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-lg font-medium text-green-700 mb-2">
                    نقاط قوت ({(data.strengths && data.strengths.length) || 0})
                  </h3>
                  <ul className="space-y-2">
                    {data.strengths?.slice(0, 3).map((strength: any, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-green-500 ml-2">✓</span>
                        {strength.title}
                      </li>
                    ))}
                  </ul>
                  {data.strengths && data.strengths.length > 3 && (
                    <Link
                      href={`/dashboard/${analysisId}/analysis`}
                      className="text-sm text-blue-600 hover:underline mt-2 inline-block"
                    >
                      مشاهده همه →
                    </Link>
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-medium text-red-700 mb-2">
                    نقاط ضعف ({(data.weaknesses && data.weaknesses.length) || 0})
                  </h3>
                  <ul className="space-y-2">
                    {data.weaknesses?.slice(0, 3).map((weakness: any, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-red-500 ml-2">⚠</span>
                        {weakness.title}
                      </li>
                    ))}
                  </ul>
                  {data.weaknesses && data.weaknesses.length > 3 && (
                    <Link
                      href={`/dashboard/${analysisId}/analysis`}
                      className="text-sm text-blue-600 hover:underline mt-2 inline-block"
                    >
                      مشاهده همه →
                    </Link>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Raw Data (Collapsible) */}
          <details className="bg-white rounded-lg shadow p-6">
            <summary className="cursor-pointer text-lg font-semibold mb-4">
              نمایش داده‌های خام (برای توسعه)
            </summary>
            <div className="space-y-4 mt-4">
              {/* تمام داده‌های داشبورد */}
              <div>
                <h3 className="text-md font-semibold mb-2">تمام داده‌های داشبورد:</h3>
                <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                  <pre className="text-xs">
                    {JSON.stringify(data, null, 2)}
                  </pre>
                </div>
              </div>
              
              {/* تحلیل سایت */}
              {data.data?.site_analysis && (
                <div>
                  <h3 className="text-md font-semibold mb-2">تحلیل سایت:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.data.site_analysis, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* تحلیل سئو */}
              {data.data?.seo_analysis && (
                <div>
                  <h3 className="text-md font-semibold mb-2">تحلیل سئو:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.data.seo_analysis, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* محتوای تولید شده */}
              {data.data?.generated_content && (
                <div>
                  <h3 className="text-md font-semibold mb-2">محتوای تولید شده:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.data.generated_content, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* پیاده‌سازی سئو */}
              {data.data?.implementation && (
                <div>
                  <h3 className="text-md font-semibold mb-2">پیاده‌سازی سئو:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.data.implementation, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* جانمایی محتوا */}
              {data.data?.placement && (
                <div>
                  <h3 className="text-md font-semibold mb-2">جانمایی محتوا:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.data.placement, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* نقاط قوت */}
              {data.strengths && data.strengths.length > 0 && (
                <div>
                  <h3 className="text-md font-semibold mb-2">نقاط قوت:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.strengths, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* نقاط ضعف */}
              {data.weaknesses && data.weaknesses.length > 0 && (
                <div>
                  <h3 className="text-md font-semibold mb-2">نقاط ضعف:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.weaknesses, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* پیشنهادات */}
              {data.recommendations && data.recommendations.length > 0 && (
                <div>
                  <h3 className="text-md font-semibold mb-2">پیشنهادات:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.recommendations, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* رنک */}
              {data.rank_data && (
                <div>
                  <h3 className="text-md font-semibold mb-2">رنک سایت:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                    <pre className="text-xs">
                      {JSON.stringify(data.rank_data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* اگر هیچ داده‌ای موجود نبود */}
              {!data.data?.site_analysis && !data.data?.seo_analysis && !data.strengths && !data.weaknesses && (
                <div className="text-center py-8 text-gray-500">
                  <p>هنوز داده‌ای برای نمایش وجود ندارد.</p>
                  <p className="text-sm mt-2">داده‌ها به محض آماده شدن در اینجا نمایش داده می‌شوند.</p>
                </div>
              )}
            </div>
          </details>
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

