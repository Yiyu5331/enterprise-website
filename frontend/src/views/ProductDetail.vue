<template>
  <div v-if="loading" class="detail-page">
    <section class="section not-found"><div class="container text-center"><h1>产品加载中...</h1></div></section>
  </div>

  <div v-else-if="product" class="detail-page">
    <div class="detail-crumb">
      <div class="container">
        <router-link to="/products">产品中心</router-link>
        <span>/</span><span>{{ product.category }}</span><span>/</span><strong>{{ product.name }}</strong>
      </div>
    </div>

    <section class="product-hero section">
      <div class="container product-hero-grid">
        <div class="product-main-image">
          <a :href="activeImage.image" :data-pswp-width="1600" :data-pswp-height="1066" target="_blank" rel="noreferrer" @click.prevent="openGallery(activeIndex)">
            <img :src="activeImage.image" :alt="activeImage.alt || `${product.name}产品图`" />
          </a>
          <div v-if="product.gallery?.length > 1" class="thumb-row">
            <button v-for="(image, index) in product.gallery" :key="image.image" type="button" :class="{ active: index === activeIndex }" @click="activeIndex = index">
              <img :src="image.thumb" :alt="image.alt">
            </button>
          </div>
        </div>
        <div class="product-summary">
          <span class="detail-label">{{ product.category }}</span>
          <h1>{{ product.name }}</h1>
          <div class="model-line">
            <span>{{ product.model }}</span>
            <span :class="['tag', product.level === '工业级' ? 'tag-red' : 'tag-gray']">{{ product.level }}</span>
          </div>
          <p>{{ product.summary }}</p>
          <div class="hero-specs">
            <div v-for="spec in product.specifications" :key="spec.name + spec.value" class="hero-spec">
              <span>{{ spec.name }}</span><strong>{{ spec.value }}</strong>
            </div>
          </div>
          <div class="detail-actions">
            <router-link :to="`/inquiry?product=${product.model}`" class="btn btn-primary btn-lg">获取产品报价</router-link>
            <router-link to="/contact" class="btn detail-outline btn-lg">联系销售团队</router-link>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-gray">
      <div class="container detail-content-grid">
        <div>
          <span class="detail-label">PRODUCT ADVANTAGES</span>
          <h2>产品特点</h2>
          <div class="rich-content" v-html="product.description"></div>
          <div class="highlights-grid">
            <div v-for="(item, index) in product.highlights" :key="item.title" class="highlight-item">
              <span>0{{ index + 1 }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
        <aside class="application-panel">
          <span class="detail-label">APPLICATIONS</span>
          <h2>应用场景</h2>
          <div class="application-list">
            <span v-for="application in product.applications" :key="application.name">{{ application.name }}</span>
          </div>
          <p>支持 OEM / ODM、包装定制、参数配置及批量采购方案。</p>
        </aside>
      </div>
    </section>

    <section v-if="relatedProducts.length" class="section">
      <div class="container">
        <div class="detail-section-head">
          <div><span class="detail-label">RELATED PRODUCTS</span><h2>同系列产品</h2></div>
          <router-link to="/products" class="text-link">返回产品中心 →</router-link>
        </div>
        <div class="related-grid">
          <router-link v-for="item in relatedProducts" :key="item.model" :to="`/products/${item.category_slug}/${item.model}/`" class="related-card">
            <img :src="item.image" :alt="item.name" loading="lazy" />
            <div><span>{{ item.model }}</span><h3>{{ item.name }}</h3></div>
          </router-link>
        </div>
      </div>
    </section>
  </div>

  <section v-else class="section not-found">
    <div class="container text-center">
      <h1>{{ errorTitle }}</h1>
      <p>{{ error || '产品型号可能已更新，请返回产品中心重新选择。' }}</p>
      <router-link to="/products" class="btn btn-primary">返回产品中心</router-link>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PhotoSwipeLightbox from 'photoswipe/lightbox'
import 'photoswipe/style.css'
import { fetchProductDetail } from '@/api/content'
import { readableError, setPageMeta, siteUrl } from '@/api/client'

const route = useRoute()
const product = ref(null)
const loading = ref(false)
const error = ref('')
const activeIndex = ref(0)
let controller = null
let lightbox = null

const relatedProducts = computed(() => product.value?.related_products || [])
const activeImage = computed(() => product.value?.gallery?.[activeIndex.value] || { image: product.value?.image_web || product.value?.image, thumb: product.value?.image, alt: product.value?.name })
const errorTitle = computed(() => error.value ? '产品加载失败' : '未找到该产品')

function initLightbox() {
  if (lightbox) lightbox.destroy()
  lightbox = new PhotoSwipeLightbox({
    dataSource: (product.value?.gallery || []).map(item => ({
      src: item.image,
      msrc: item.thumb,
      width: 1600,
      height: 1066,
      alt: item.alt,
    })),
    pswpModule: () => import('photoswipe'),
  })
  lightbox.init()
}

function openGallery(index) {
  if (!product.value?.gallery?.length) return
  if (!lightbox) initLightbox()
  lightbox.loadAndOpen(index)
}

async function loadDetail() {
  if (controller) controller.abort()
  controller = new AbortController()
  loading.value = true
  error.value = ''
  product.value = null
  activeIndex.value = 0
  try {
    product.value = await fetchProductDetail(route.params.model, controller.signal)
    const canonical = `${siteUrl}/products/${product.value.category_slug}/${product.value.model}/`
    const absoluteImages = product.value.gallery.map(item => item.image.startsWith('http') ? item.image : `${siteUrl}${item.image}`)
    setPageMeta({
      title: product.value.seo?.title,
      description: product.value.seo?.description,
      image: product.value.image,
      canonical,
      structuredData: [
        { '@context': 'https://schema.org', '@type': 'Product', name: product.value.name, model: product.value.model, description: product.value.summary, image: absoluteImages, manufacturer: { '@type': 'Organization', name: '华丽电器制造有限公司' } },
        { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: '产品中心', item: `${siteUrl}/products/` }, { '@type': 'ListItem', position: 2, name: product.value.category, item: `${siteUrl}/products/category/${product.value.category_slug}/` }, { '@type': 'ListItem', position: 3, name: product.value.name, item: canonical }] },
      ],
    })
    initLightbox()
  } catch (err) {
    if (err.response?.status !== 404 && err.name !== 'CanceledError' && err.code !== 'ERR_CANCELED') {
      error.value = readableError(err, '产品详情加载失败。')
    }
  } finally {
    loading.value = false
  }
}

watch(() => route.params.model, loadDetail)
onMounted(loadDetail)
onBeforeUnmount(() => {
  if (controller) controller.abort()
  if (lightbox) lightbox.destroy()
})
</script>

<style scoped>
.detail-page { margin-top: calc(var(--header-h) + 32px); }
.detail-crumb { padding: 18px 0; border-bottom: 1px solid var(--gray-200); color: var(--gray-500); font-size: 13px; }
.detail-crumb .container { display: flex; gap: 10px; flex-wrap: wrap; }
.detail-crumb a:hover, .text-link { color: var(--brand); }
.detail-crumb strong { color: var(--text); }
.product-hero-grid { display: grid; grid-template-columns: 1.05fr .95fr; gap: 64px; align-items: center; }
.product-main-image { background: #f1f1f1; border: 1px solid var(--gray-200); }
.product-main-image > a { display: block; aspect-ratio: 3 / 2; overflow: hidden; cursor: zoom-in; }
.product-main-image img { width: 100%; height: 100%; object-fit: cover; }
.thumb-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; padding: 10px; background: var(--white); }
.thumb-row button { aspect-ratio: 3 / 2; border: 2px solid transparent; padding: 0; cursor: pointer; background: var(--gray-100); overflow: hidden; }
.thumb-row button.active { border-color: var(--brand); }
.detail-label { display: block; color: var(--brand); font-size: 12px; font-weight: 700; letter-spacing: 2px; margin-bottom: 10px; }
.product-summary h1 { font-size: 42px; line-height: 1.2; margin-bottom: 10px; }
.model-line { display: flex; gap: 12px; align-items: center; color: var(--gray-500); font-family: monospace; margin-bottom: 24px; }
.product-summary > p { color: var(--text-light); font-size: 16px; line-height: 1.9; margin-bottom: 28px; }
.hero-specs { display: grid; grid-template-columns: repeat(2, 1fr); border-top: 1px solid var(--gray-200); border-left: 1px solid var(--gray-200); }
.hero-spec { padding: 14px 16px; border-right: 1px solid var(--gray-200); border-bottom: 1px solid var(--gray-200); }
.hero-spec span { display: block; font-size: 12px; color: var(--gray-500); }
.hero-spec strong { font-size: 16px; }
.detail-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 28px; }
.detail-outline { border-color: var(--gray-300); color: var(--text); background: var(--white); }
.detail-outline:hover { border-color: var(--brand); color: var(--brand); }
.detail-content-grid { display: grid; grid-template-columns: 1.5fr .7fr; gap: 48px; }
.detail-content-grid h2, .detail-section-head h2 { font-size: 28px; margin-bottom: 26px; }
.rich-content { margin-bottom: 26px; color: var(--text-light); line-height: 1.95; }
.rich-content :deep(table) { width: 100%; border-collapse: collapse; min-width: 560px; }
.rich-content :deep(td), .rich-content :deep(th) { border: 1px solid var(--gray-300); padding: 8px 10px; }
.highlights-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.highlight-item { background: var(--white); padding: 26px; border-top: 3px solid var(--brand); }
.highlight-item > span { color: var(--gray-400); font: 700 12px monospace; }
.highlight-item h3 { font-size: 16px; margin: 14px 0 6px; }
.highlight-item p, .application-panel p { font-size: 13px; color: var(--gray-600); line-height: 1.8; }
.application-panel { background: var(--dark); color: var(--white); padding: 32px; align-self: start; }
.application-panel h2 { color: var(--white); }
.application-list { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }
.application-list span { padding: 7px 12px; border: 1px solid rgba(255,255,255,.18); font-size: 13px; }
.application-panel p { color: var(--gray-400); }
.detail-section-head { display: flex; justify-content: space-between; align-items: end; margin-bottom: 28px; }
.detail-section-head h2 { margin-bottom: 0; }
.related-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.related-card { border: 1px solid var(--gray-200); transition: .25s; }
.related-card:hover { border-color: var(--brand); transform: translateY(-3px); }
.related-card img { aspect-ratio: 3 / 2; width: 100%; object-fit: cover; }
.related-card div { padding: 16px 18px; }
.related-card span { font: 12px monospace; color: var(--gray-500); }
.related-card h3 { font-size: 16px; margin-top: 4px; }
.not-found { margin-top: calc(var(--header-h) + 32px); padding: 140px 0; }
.not-found p { margin: 12px 0 24px; color: var(--gray-600); }
@media (max-width: 768px) {
  .detail-page { margin-top: var(--header-h); }
  .product-hero-grid, .detail-content-grid { grid-template-columns: 1fr; gap: 30px; }
  .product-summary h1 { font-size: 30px; }
  .highlights-grid, .related-grid { grid-template-columns: 1fr; }
  .detail-section-head { align-items: start; gap: 10px; flex-direction: column; }
}
</style>
