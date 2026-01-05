'use client'

import { useEffect } from 'react'

/**
 * کامپوننت برای سرکوب خطاهای افزونه‌های مرورگر
 * این خطاها معمولاً از افزونه‌های SEO، AdBlock و غیره می‌آیند
 */
export function ErrorSuppressor() {
  useEffect(() => {
    // سرکوب خطاهای افزونه‌های مرورگر
    const handleError = (event: ErrorEvent) => {
      const errorMessage = event.message || ''
      
      // خطاهای مربوط به افزونه‌های مرورگر
      if (
        errorMessage.includes('Could not establish connection') ||
        errorMessage.includes('Receiving end does not exist') ||
        errorMessage.includes('content-all.js') ||
        errorMessage.includes('Extension context invalidated') ||
        errorMessage.includes('chrome.runtime') ||
        errorMessage.includes('browser.runtime') ||
        errorMessage.includes('message channel closed') ||
        errorMessage.includes('listener indicated an asynchronous response') ||
        errorMessage.includes('hot-reloader-client.js') ||
        errorMessage.includes('Fast Refresh')
      ) {
        // جلوگیری از نمایش خطا در کنسول
        event.preventDefault()
        return false
      }
    }

    // سرکوب Promise rejection های مربوط به افزونه‌ها
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const reason = event.reason?.message || event.reason?.toString() || ''
      
      if (
        reason.includes('Could not establish connection') ||
        reason.includes('Receiving end does not exist') ||
        reason.includes('Extension context invalidated') ||
        reason.includes('message channel closed') ||
        reason.includes('listener indicated an asynchronous response') ||
        reason.includes('content-all.js') ||
        reason.includes('chrome.runtime') ||
        reason.includes('browser.runtime')
      ) {
        event.preventDefault()
        return false
      }
    }

    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)

    return () => {
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [])

  return null
}

