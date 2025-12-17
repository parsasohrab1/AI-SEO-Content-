'use client'

import React from 'react'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

interface ErrorBoundaryProps {
  children: React.ReactNode
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // فقط خطاهای واقعی را لاگ می‌کنیم، نه خطاهای extension
    if (!error.message?.includes('content-script') && 
        !error.stack?.includes('chrome-extension') &&
        !error.stack?.includes('moz-extension')) {
      console.error('Application Error:', error, errorInfo)
    }
  }

  render() {
    if (this.state.hasError) {
      // فقط خطاهای واقعی را نمایش می‌دهیم
      if (this.state.error?.message?.includes('content-script') ||
          this.state.error?.stack?.includes('chrome-extension') ||
          this.state.error?.stack?.includes('moz-extension')) {
        // خطای extension را نادیده می‌گیریم
        return this.props.children
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-8">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">خطا در برنامه</h2>
            <p className="text-gray-600 mb-4">
              متأسفانه خطایی رخ داده است. لطفاً صفحه را رفرش کنید.
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: undefined })
                window.location.reload()
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              رفرش صفحه
            </button>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-4 text-right">
                <summary className="cursor-pointer text-sm text-gray-500">جزئیات خطا</summary>
                <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

