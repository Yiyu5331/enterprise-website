import { apiClient } from './client'

export function fetchHomepage(signal) {
  return apiClient.get('/homepage/', { signal }).then(response => response.data)
}

export function fetchProductCategories(signal) {
  return apiClient.get('/product-categories/', { signal }).then(response => response.data)
}

export function fetchProducts(params = {}, signal) {
  return apiClient.get('/products/', { params, signal }).then(response => response.data)
}

export function fetchProductDetail(model, signal) {
  return apiClient.get(`/products/${encodeURIComponent(model)}/`, { signal }).then(response => response.data)
}

export function fetchProductOptions(signal) {
  return apiClient.get('/product-options/', { signal }).then(response => response.data)
}

export function fetchNewsCategories(signal) {
  return apiClient.get('/news-categories/', { signal }).then(response => response.data)
}

export function fetchNews(params = {}, signal) {
  return apiClient.get('/news/', { params, signal }).then(response => response.data)
}

export function fetchNewsDetail(slug, signal) {
  return apiClient.get(`/news/${encodeURIComponent(slug)}/`, { signal }).then(response => response.data)
}

export function submitInquiry(payload) {
  return apiClient.post('/inquiries/', payload).then(response => response.data)
}

export function submitContact(payload) {
  return apiClient.post('/contacts/', payload).then(response => response.data)
}

export function fetchFormBootstrap(kind) {
  return apiClient.get('/forms/bootstrap/', { params: { kind } }).then(response => response.data)
}

export function fetchCaptcha() {
  return apiClient.post('/captcha/').then(response => response.data)
}

export function fetchPrivacyPolicy() {
  return apiClient.get('/privacy-policy/').then(response => response.data)
}
