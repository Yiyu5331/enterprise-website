import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', meta: { title: '首页' }, component: () => import('@/views/Home.vue') },
  { path: '/about/', name: 'About', meta: { title: '关于我们' }, component: () => import('@/views/About.vue') },
  { path: '/products/', name: 'Products', meta: { title: '产品中心' }, component: () => import('@/views/Products.vue') },
  { path: '/products/category/:categorySlug/', name: 'ProductCategory', meta: { title: '产品分类' }, component: () => import('@/views/Products.vue') },
  { path: '/products/:categorySlug/:model/', name: 'ProductDetail', meta: { title: '产品详情' }, component: () => import('@/views/ProductDetail.vue') },
  { path: '/news/', name: 'News', meta: { title: '新闻中心' }, component: () => import('@/views/News.vue') },
  { path: '/news/category/:categorySlug/', name: 'NewsCategory', meta: { title: '新闻分类' }, component: () => import('@/views/News.vue') },
  { path: '/news/:categorySlug/:slug/', name: 'NewsDetail', meta: { title: '新闻详情' }, component: () => import('@/views/NewsDetail.vue') },
  { path: '/supply-chain/', name: 'SupplyChain', meta: { title: '供应链' }, component: () => import('@/views/SupplyChain.vue') },
  { path: '/inquiry/', name: 'Inquiry', meta: { title: '在线询盘', noindex: true }, component: () => import('@/views/Inquiry.vue') },
  { path: '/dealer/', name: 'Dealer', meta: { title: '经销商入口' }, component: () => import('@/views/Dealer.vue') },
  { path: '/contact/', name: 'Contact', meta: { title: '联系我们' }, component: () => import('@/views/Contact.vue') },
  { path: '/privacy/', name: 'Privacy', meta: { title: '隐私政策', noindex: true }, component: () => import('@/views/Privacy.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', meta: { title: '页面不存在', noindex: true }, component: () => import('@/views/NotFound.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(to => {
  window.__PRERENDER_READY__ = false
  const robots = to.meta.noindex || to.query.q ? 'noindex,follow' : 'index,follow'
  let tag = document.head.querySelector('meta[name="robots"]')
  if (!tag) { tag = document.createElement('meta'); tag.name = 'robots'; document.head.appendChild(tag) }
  tag.content = robots
  window.clearTimeout(window.__ROUTE_READY_TIMER__)
  window.__ROUTE_READY_TIMER__ = window.setTimeout(() => {
    if (!window.__API_ACTIVE_REQUESTS__) window.__PRERENDER_READY__ = true
  }, 1000)
})

export default router
