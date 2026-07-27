import axios from 'axios'

export const siteUrl = (import.meta.env.VITE_SITE_URL || window.location.origin).replace(/\/$/, '')

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 12000,
  xsrfCookieName: 'huali_csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withCredentials: true,
})

let activeRequests = 0
function updatePrerenderReady() {
  window.__API_ACTIVE_REQUESTS__ = activeRequests
  window.clearTimeout(window.__PRERENDER_TIMER__)
  if (activeRequests === 0) window.__PRERENDER_TIMER__ = window.setTimeout(() => { window.__PRERENDER_READY__ = true }, 250)
}

apiClient.interceptors.request.use(config => {
  activeRequests += 1
  window.__API_ACTIVE_REQUESTS__ = activeRequests
  window.__PRERENDER_READY__ = false
  return config
})

apiClient.interceptors.response.use(
  response => { activeRequests = Math.max(0, activeRequests - 1); updatePrerenderReady(); return response },
  async error => {
    const config = error.config || {}
    const status = error.response?.status
    const canRetry = !config.__retried && (!status || status >= 500)
    if (canRetry) {
      activeRequests = Math.max(0, activeRequests - 1)
      window.__API_ACTIVE_REQUESTS__ = activeRequests
      config.__retried = true
      return apiClient(config)
    }
    activeRequests = Math.max(0, activeRequests - 1)
    updatePrerenderReady()
    return Promise.reject(error)
  }
)

export function readableError(error, fallback = '加载失败，请稍后重试。') {
  const data = error.response?.data
  if (data?.message) return data.message
  if (data?.errors) return Object.values(data.errors).flat().join(' ')
  return fallback
}

export function setPageMeta({ title, description, image, canonical, robots, structuredData }) {
  if (title) document.title = title
  const desc = description || '华丽电器制造有限公司，专业电动工具研发制造与全球贸易服务。'
  setMeta('description', desc)
  setMeta('og:title', title || document.title, 'property')
  setMeta('og:description', desc, 'property')
  if (image) setMeta('og:image', image, 'property')
  setMeta('og:url', canonical || `${siteUrl}${window.location.pathname}`, 'property')
  if (robots) setMeta('robots', robots)
  let canonicalTag = document.head.querySelector('link[rel="canonical"]')
  if (!canonicalTag) { canonicalTag = document.createElement('link'); canonicalTag.rel = 'canonical'; document.head.appendChild(canonicalTag) }
  canonicalTag.href = canonical || `${siteUrl}${window.location.pathname}`
  document.head.querySelectorAll('script[data-seo-jsonld]').forEach(node => node.remove())
  for (const item of structuredData || []) {
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.dataset.seoJsonld = 'true'
    script.textContent = JSON.stringify(item)
    document.head.appendChild(script)
  }
}

function setMeta(name, content, attr = 'name') {
  let tag = document.head.querySelector(`meta[${attr}="${name}"]`)
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute(attr, name)
    document.head.appendChild(tag)
  }
  tag.setAttribute('content', content)
}
