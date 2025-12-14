'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'

export default function SEOPage() {
  const params = useParams()
  const analysisId = params.id as string

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">مانیتورینگ سئو</h1>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600">این صفحه در حال توسعه است.</p>
        </div>

        <div className="mt-6">
          <Link
            href={`/dashboard/${analysisId}`}
            className="text-blue-600 hover:underline"
          >
            ← بازگشت به داشبورد
          </Link>
        </div>
      </div>
    </div>
  )
}

