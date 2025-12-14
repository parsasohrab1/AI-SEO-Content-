/**
 * Load Testing با K6
 * تست عملکرد با K6 برای مقایسه با Locust
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom Metrics
const errorRate = new Rate('errors');
const analysisDuration = new Trend('analysis_duration');

// Configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.01'],   // Error rate should be less than 1%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  // Test 1: Analyze Site
  const analyzePayload = JSON.stringify({
    url: 'https://example.com',
    auto_implement: true,
    content_types: ['text', 'image'],
    schedule_monitoring: true,
  });

  const analyzeRes = http.post(
    `${BASE_URL}/analyze-site`,
    analyzePayload,
    { headers: { 'Content-Type': 'application/json' } }
  );

  const analyzeSuccess = check(analyzeRes, {
    'analyze site status is 200': (r) => r.status === 200,
    'analyze site has analysis_id': (r) => {
      const body = JSON.parse(r.body);
      return body.analysis_id !== undefined;
    },
  });

  errorRate.add(!analyzeSuccess);
  analysisDuration.add(analyzeRes.timings.duration);

  if (analyzeSuccess) {
    const body = JSON.parse(analyzeRes.body);
    const analysisId = body.analysis_id;

    // Test 2: Get Dashboard
    const dashboardRes = http.get(`${BASE_URL}/dashboard/${analysisId}`);
    check(dashboardRes, {
      'dashboard status is 200': (r) => r.status === 200,
    });

    // Test 3: Get SEO Report
    const seoReportRes = http.get(`${BASE_URL}/dashboard/${analysisId}/seo-report`);
    check(seoReportRes, {
      'seo report status is 200': (r) => r.status === 200,
    });

    // Test 4: Live Monitoring
    const monitoringRes = http.get(
      `${BASE_URL}/dashboard/${analysisId}/live-monitoring`
    );
    check(monitoringRes, {
      'monitoring status is 200': (r) => r.status === 200,
    });
  }

  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data),
    'summary.json': JSON.stringify(data),
  };
}

function textSummary(data) {
  return `
    ========================
    Load Test Summary
    ========================
    Total Requests: ${data.metrics.http_reqs.values.count}
    Failed Requests: ${data.metrics.http_req_failed.values.rate * 100}%
    Average Response Time: ${data.metrics.http_req_duration.values.avg}ms
    P95 Response Time: ${data.metrics.http_req_duration.values['p(95)']}ms
    P99 Response Time: ${data.metrics.http_req_duration.values['p(99)']}ms
    ========================
  `;
}

