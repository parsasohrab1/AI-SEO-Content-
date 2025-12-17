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
  const [showCredentialsForm, setShowCredentialsForm] = useState(false)
  const [savingCredentials, setSavingCredentials] = useState(false)
  const [credentials, setCredentials] = useState({
    cms_type: 'wordpress',
    admin_url: '',
    username: '',
    password: '',
    api_key: ''
  })
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const shouldPollRef = useRef<boolean>(true)

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
            id: `rec_${recs.length}`,
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
            id: `rec_${recs.length}`,
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
            id: `rec_${recs.length}`,
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
            id: `rec_${recs.length}`,
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
            id: `rec_${recs.length}`,
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
            id: `rec_${recs.length}`,
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
        id: `rec_${recs.length}`,
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
        id: `rec_${recs.length}`,
        title: 'ایجاد و ارسال Sitemap به Google Search Console',
        description: 'پس از ایجاد sitemap.xml، آن را در Google Search Console ثبت کنید.',
        category: 'سئو فنی',
        priority: 'high',
        impact: 'بهبود ایندکس شدن',
        estimatedTime: '15 دقیقه',
        automated: false
      })
    }

    // پیشنهادات عمومی
    recs.push({
      id: `rec_${recs.length}`,
      title: 'بهینه‌سازی Meta Tags',
      description: 'مطمئن شوید که تمام صفحات دارای Meta Title و Meta Description مناسب هستند.',
      category: 'سئو محتوایی',
      priority: 'medium',
      impact: 'بهبود کلیک‌ها در نتایج جستجو',
      estimatedTime: '2-3 ساعت',
      automated: true
    })

    recs.push({
      id: `rec_${recs.length}`,
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
        
        // استخراج و به‌روزرسانی اطلاعات لاگین CMS
        const cmsCreds = dashboardData.cms_credentials
        if (cmsCreds) {
          setCredentials({
            cms_type: cmsCreds.cms_type || 'wordpress',
            admin_url: cmsCreds.admin_url || '',
            username: cmsCreds.username || '',
            password: '', // برای امنیت، پسورد را نمایش نمی‌دهیم
            api_key: cmsCreds.api_key || ''
          })
        }
        
        // استخراج پیشنهادات - استفاده از همان منطق صفحه recommendations
        const recs = generateRecommendations(dashboardData)
        setRecommendations(recs)
        
        // استخراج fixes اعمال شده (همیشه به‌روزرسانی می‌کنیم، حتی اگر خالی باشد)
        const appliedFixesData = dashboardData.applied_fixes || []
        const fixesList: AppliedFix[] = appliedFixesData.map((fix: any) => ({
          recommendation_id: fix.recommendation_id || fix.id || '',
          title: fix.title || '',
          status: fix.status === 'success' ? 'applied' : 
                 fix.status === 'pending' ? 'pending' : 'failed',
          message: fix.message
        }))
        setAppliedFixes(fixesList)
        
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

  const handleSaveCredentials = async () => {
    if (!credentials.username || !credentials.password) {
      alert('لطفاً نام کاربری و رمز عبور را وارد کنید')
      return
    }

    setSavingCredentials(true)
    try {
      const response = await fetch(`http://localhost:8002/dashboard/${analysisId}/save-credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'خطا در ذخیره اطلاعات لاگین')
      }

      const result = await response.json()
      alert('اطلاعات لاگین با موفقیت ذخیره شد! حالا می‌توانید پیشنهادات را اعمال کنید.')
      setShowCredentialsForm(false)
      
      // Refresh data
      const refreshResponse = await fetch(`http://localhost:8002/dashboard/${analysisId}`)
      if (refreshResponse.ok) {
        const refreshData = await refreshResponse.json()
        const cmsCreds = refreshData.cms_credentials
        if (cmsCreds) {
          setCredentials({
            cms_type: cmsCreds.cms_type || 'wordpress',
            admin_url: cmsCreds.admin_url || '',
            username: cmsCreds.username || '',
            password: '', // برای امنیت، پسورد را نمایش نمی‌دهیم
            api_key: cmsCreds.api_key || ''
          })
        }
      }
    } catch (err) {
      alert('خطا در ذخیره اطلاعات لاگین: ' + (err instanceof Error ? err.message : 'خطای نامشخص'))
    } finally {
      setSavingCredentials(false)
    }
  }

  const handleApplyRecommendations = async () => {
    if (selectedRecommendations.length === 0) {
      alert('لطفاً حداقل یک پیشنهاد را انتخاب کنید')
      return
    }

    // بررسی اینکه آیا پیشنهادات نیاز به لاگین دارند
    const needsCredentials = selectedRecommendations.some(id => {
      const rec = recommendations.find((r, i) => (r.id || `rec_${i}`) === id)
      return !rec?.automated
    })

    // اگر نیاز به لاگین دارد و لاگین موجود نیست، فرم را نمایش بده
    if (needsCredentials && (!credentials.username || !credentials.password)) {
      const shouldContinue = confirm('برای اعمال این پیشنهادات نیاز به اطلاعات لاگین CMS دارید. آیا می‌خواهید اطلاعات لاگین را وارد کنید؟')
      if (shouldContinue) {
        setShowCredentialsForm(true)
        return
      }
    }

    setApplying(true)
    setAppliedFixes([])

    try {
      // ایجاد لیست fixes برای ارسال
      const fixes = selectedRecommendations.map(id => {
        // بررسی اینکه آیا این یک مشکل سئو است یا پیشنهاد عادی
        if (id.startsWith('seo_issue_')) {
          const issueIndex = parseInt(id.replace('seo_issue_', ''))
          const seoIssues = data?.data?.seo_analysis?.issues || []
          if (seoIssues[issueIndex]) {
            return seoIssues[issueIndex].title || id
          }
        }
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
        const resultItem = result.results?.find((r: any) => r.recommendation_id === id) || result.results?.[index]
        return {
          recommendation_id: id,
          title: rec?.title || `پیشنهاد ${index + 1}`,
          status: resultItem?.status === 'success' ? 'applied' : 
                 resultItem?.status === 'pending' ? 'pending' : 'failed',
          message: resultItem?.message
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
            const recs = generateRecommendations(refreshData)
            setRecommendations(recs)
            
            // Update applied fixes from dashboard (همیشه به‌روزرسانی می‌کنیم، حتی اگر خالی باشد)
            const appliedFixesData = refreshData.applied_fixes || []
            const fixesList: AppliedFix[] = appliedFixesData.map((fix: any) => ({
              recommendation_id: fix.recommendation_id || fix.id || '',
              title: fix.title || '',
              status: fix.status === 'success' ? 'applied' : 
                     fix.status === 'pending' ? 'pending' : 'failed',
              message: fix.message
            }))
            setAppliedFixes(fixesList)
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

        {/* CMS Credentials Info */}
        {credentials.username && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-green-900">
                  ✓ اطلاعات لاگین CMS ذخیره شده است
                </p>
                <p className="text-sm text-green-700">
                  نوع CMS: {credentials.cms_type === 'wordpress' ? 'وردپرس' : 
                           credentials.cms_type === 'joomla' ? 'جوملا' : 
                           credentials.cms_type === 'drupal' ? 'دروپال' : credentials.cms_type}
                  {credentials.admin_url && ` | آدرس ادمین: ${credentials.admin_url}`}
                </p>
              </div>
              <button
                onClick={() => setShowCredentialsForm(true)}
                className="px-4 py-2 text-green-700 hover:text-green-900 text-sm font-medium"
              >
                تغییر اطلاعات
              </button>
            </div>
          </div>
        )}

        {/* Credentials Form Modal */}
        {showCredentialsForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
                <h2 className="text-2xl font-bold">اطلاعات لاگین CMS</h2>
                <button
                  onClick={() => setShowCredentialsForm(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              <div className="p-6">
                <p className="text-gray-600 mb-6">
                  برای اعمال خودکار پیشنهادات، لطفاً اطلاعات لاگین CMS خود را وارد کنید.
                  این اطلاعات به صورت امن ذخیره می‌شود و فقط برای اعمال تغییرات استفاده می‌شود.
                </p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      نوع CMS
                    </label>
                    <select
                      value={credentials.cms_type}
                      onChange={(e) => setCredentials({...credentials, cms_type: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="wordpress">وردپرس (WordPress)</option>
                      <option value="joomla">جوملا (Joomla)</option>
                      <option value="drupal">دروپال (Drupal)</option>
                      <option value="custom">سایر</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      آدرس پنل ادمین
                    </label>
                    <input
                      type="text"
                      value={credentials.admin_url}
                      onChange={(e) => setCredentials({...credentials, admin_url: e.target.value})}
                      placeholder={credentials.cms_type === 'wordpress' ? 'https://example.com/wp-admin' : 'https://example.com/administrator'}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      نام کاربری
                    </label>
                    <input
                      type="text"
                      value={credentials.username}
                      onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                      placeholder="نام کاربری ادمین"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      رمز عبور
                    </label>
                    <input
                      type="password"
                      value={credentials.password}
                      onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                      placeholder="رمز عبور ادمین"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API Key (اختیاری)
                    </label>
                    <input
                      type="text"
                      value={credentials.api_key}
                      onChange={(e) => setCredentials({...credentials, api_key: e.target.value})}
                      placeholder="کلید API (در صورت نیاز)"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={handleSaveCredentials}
                    disabled={savingCredentials}
                    className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                  >
                    {savingCredentials ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                        در حال ذخیره...
                      </>
                    ) : (
                      '💾 ذخیره اطلاعات'
                    )}
                  </button>
                  <button
                    onClick={() => setShowCredentialsForm(false)}
                    className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium"
                  >
                    انصراف
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

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
              <div className="flex gap-3">
                {!credentials.username && (
                  <button
                    onClick={() => setShowCredentialsForm(true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    🔐 وارد کردن اطلاعات لاگین
                  </button>
                )}
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

        {/* SEO Issues Section */}
        {data?.data?.seo_analysis?.issues && data.data.seo_analysis.issues.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">مشکلات سئو شناسایی شده</h2>
              <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                {data.data.seo_analysis.issues.length} مشکل
              </span>
            </div>
            
            <div className="space-y-3 mb-4">
              {data.data.seo_analysis.issues.map((issue: any, index: number) => {
                const issueId = `seo_issue_${index}`
                const isSelected = selectedRecommendations.includes(issueId)
                const appliedFix = appliedFixes.find(f => f.recommendation_id === issueId)
                const isApplied = appliedFix && appliedFix.status === 'applied'
                const isPending = appliedFix && appliedFix.status === 'pending'
                
                return (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 transition-all ${
                      isSelected 
                        ? 'border-blue-500 bg-blue-50' 
                        : isApplied
                        ? 'border-green-300 bg-green-50'
                        : isPending
                        ? 'border-yellow-300 bg-yellow-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isApplied && !isPending ? 'cursor-pointer' : ''}`}
                    onClick={() => !isApplied && !isPending && handleSelectRecommendation(issueId)}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => !isApplied && !isPending && handleSelectRecommendation(issueId)}
                        disabled={isApplied || isPending}
                        className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <h3 className="text-lg font-semibold text-gray-900">{issue.title || 'مشکل سئو'}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium border ${
                            issue.severity === 'high' 
                              ? 'bg-red-100 text-red-800 border-red-300'
                              : issue.severity === 'medium'
                              ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
                              : 'bg-blue-100 text-blue-800 border-blue-300'
                          }`}>
                            {issue.severity === 'high' ? 'اولویت بالا' :
                             issue.severity === 'medium' ? 'اولویت متوسط' :
                             'اولویت پایین'}
                          </span>
                          {isApplied && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                              ✓ اعمال شد
                            </span>
                          )}
                          {isPending && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                              ⏳ در انتظار
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 mb-2">{issue.description || ''}</p>
                        {issue.recommendation && (
                          <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
                            <strong>راهکار:</strong> {issue.recommendation}
                          </div>
                        )}
                        {appliedFix && appliedFix.message && (
                          <div className={`mt-2 p-2 rounded text-sm ${
                            isApplied ? 'bg-green-100 text-green-800' :
                            isPending ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {appliedFix.message}
                          </div>
                        )}
                        {!appliedFix && !credentials.username && (
                          <div className="mt-2 p-2 rounded text-sm bg-yellow-100 text-yellow-800">
                            برای اعمال این مشکل، لطفاً اطلاعات لاگین CMS را وارد کنید.
                          </div>
                        )}
                        {!appliedFix && credentials.username && (
                          <div className="mt-2 p-2 rounded text-sm bg-blue-100 text-blue-800">
                            ✓ اطلاعات لاگین موجود است. این مشکل به صورت خودکار اعمال می‌شود.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
            
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">
                <strong>نکته:</strong> مشکلات سئو شناسایی شده از تحلیل عمیق سایت استخراج شده‌اند. 
                با انتخاب و اعمال این مشکلات، می‌توانید سئو سایت را بهبود دهید.
              </p>
              <p className="text-sm text-gray-500">
                این مشکلات می‌توانند شامل: مشکلات سرفصل‌ها، تصاویر بدون alt text، مشکلات crawlability و indexability باشند.
              </p>
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
                const appliedFix = appliedFixes.find(f => f.recommendation_id === recId)
                const isApplied = appliedFix && appliedFix.status === 'applied'
                const isPending = appliedFix && appliedFix.status === 'pending'
                const isFailed = appliedFix && appliedFix.status === 'failed'

                return (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 transition-all ${
                      isSelected 
                        ? 'border-blue-500 bg-blue-50' 
                        : isApplied
                        ? 'border-green-300 bg-green-50'
                        : isFailed
                        ? 'border-red-300 bg-red-50'
                        : isPending
                        ? 'border-yellow-300 bg-yellow-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!isApplied && !isPending && !isFailed ? 'cursor-pointer' : ''}`}
                    onClick={() => !isApplied && !isPending && !isFailed && handleSelectRecommendation(recId)}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => !isApplied && !isPending && !isFailed && handleSelectRecommendation(recId)}
                        disabled={isApplied || isPending || isFailed}
                        className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
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
                          {isApplied && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                              ✓ اعمال شد
                            </span>
                          )}
                          {isPending && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                              ⏳ در انتظار
                            </span>
                          )}
                          {isFailed && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                              ✗ خطا
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 mb-3">{rec.description}</p>
                        {appliedFix && appliedFix.message && (
                          <div className={`mb-3 p-2 rounded text-sm ${
                            isApplied ? 'bg-green-100 text-green-800' :
                            isPending ? 'bg-yellow-100 text-yellow-800' :
                            isFailed ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {appliedFix.message}
                          </div>
                        )}
                        {/* نمایش پیام مناسب بر اساس وضعیت */}
                        {!appliedFix && !rec.automated && !credentials.username && (
                          <div className="mb-3 p-2 rounded text-sm bg-yellow-100 text-yellow-800">
                            این پیشنهاد نیاز به اعمال دستی دارد. لطفاً اطلاعات لاگین CMS را وارد کنید.
                          </div>
                        )}
                        {!appliedFix && !rec.automated && credentials.username && (
                          <div className="mb-3 p-2 rounded text-sm bg-blue-100 text-blue-800">
                            ✓ اطلاعات لاگین موجود است. این پیشنهاد به صورت خودکار اعمال می‌شود.
                          </div>
                        )}
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

