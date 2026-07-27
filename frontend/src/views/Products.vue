<template>
  <div class="products-page">
    <div class="page-banner">
      <h1>产品中心</h1>
      <p>全品类电动工具 · 6 大系列 50+ 型号 · 家用/专业/工业级全场景覆盖</p>
    </div>

    <section class="section">
      <div class="container">
        <div class="category-strip">
          <button
            :class="['category-card', { active: !activeCategory }]"
            type="button"
            @click="selectCategory('')">
            <span>全部系列</span>
            <strong>全部产品</strong>
          </button>
          <button
            v-for="cat in categories"
            :key="cat.slug"
            :class="['category-card', { active: activeCategory === cat.slug }]"
            type="button"
            @click="selectCategory(cat.slug)">
            <img :src="cat.image" :alt="cat.name" loading="lazy">
            <span>{{ cat.item_count }} 款产品</span>
            <strong>{{ cat.name }}</strong>
          </button>
        </div>

        <form class="search-bar" @submit.prevent="applySearch">
          <input v-model="draftQ" maxlength="100" placeholder="搜索产品名称、型号、参数或应用场景">
          <button type="submit" class="btn btn-primary">搜索</button>
          <button v-if="q" type="button" class="btn clear-btn" @click="clearSearch">清除</button>
        </form>

        <div v-if="loading" class="content-state">产品加载中...</div>
        <div v-else-if="error" class="content-state error">
          {{ error }} <button type="button" @click="loadProducts">重试</button>
        </div>
        <div v-else-if="!products.length" class="content-state">
          暂无匹配产品，请调整分类或搜索词。
        </div>

        <transition-group v-else name="list" tag="div" class="product-grid">
          <article class="product-card" v-for="product in products" :key="product.model">
            <router-link :to="`/products/${product.category_slug}/${product.model}/`" class="product-detail-link">
              <div class="pc-visual">
                <img :src="product.image" :alt="`${product.name}产品图`" class="pc-img" loading="lazy" />
                <span :class="['pc-level', product.level === '工业级' ? 'tag-red' : product.level === '专业级' ? 'tag-gray' : '']">{{ product.level }}</span>
              </div>
              <div class="pc-body">
                <span class="pc-cat">{{ product.category }}</span>
                <h2 class="pc-name">{{ product.name }}</h2>
                <span class="pc-model">{{ product.model }}</span>
                <div class="pc-specs">
                  <div class="pc-spec" v-for="spec in product.specs" :key="spec.name">
                    <span class="pc-spec-key">{{ spec.name }}</span>
                    <span class="pc-spec-val">{{ spec.value }}</span>
                  </div>
                </div>
                <span class="view-detail">查看产品详情 →</span>
              </div>
            </router-link>
            <div class="pc-action">
              <router-link :to="`/inquiry?product=${product.model}`" class="btn btn-primary btn-block">获取报价</router-link>
            </div>
          </article>
        </transition-group>

        <div v-if="pagination.total_pages > 1" class="pagination">
          <button type="button" :disabled="pagination.page <= 1" @click="goPage(pagination.page - 1)">上一页</button>
          <button
            v-for="pageNo in pageNumbers"
            :key="pageNo"
            type="button"
            :class="{ active: pageNo === pagination.page }"
            @click="goPage(pageNo)">
            {{ pageNo }}
          </button>
          <span class="mobile-page">{{ pagination.page }} / {{ pagination.total_pages }}</span>
          <button type="button" :disabled="pagination.page >= pagination.total_pages" @click="goPage(pagination.page + 1)">下一页</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchProductCategories, fetchProducts } from '@/api/content'
import { readableError, setPageMeta } from '@/api/client'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const products = ref([])
const loading = ref(false)
const error = ref('')
const q = ref((route.query.q || '').toString())
const draftQ = ref(q.value)
const activeCategory = ref((route.params.categorySlug || route.query.category || '').toString())
const pagination = ref({ count: 0, page: Number(route.query.page || 1), page_size: 12, total_pages: 1 })
let controller = null

const pageNumbers = computed(() => {
  const total = pagination.value.total_pages
  const current = pagination.value.page
  const start = Math.max(1, current - 2)
  const end = Math.min(total, current + 2)
  return Array.from({ length: end - start + 1 }, (_, index) => start + index)
})

function syncQuery(page = 1) {
  router.push({
    path: activeCategory.value && !q.value ? `/products/category/${activeCategory.value}/` : '/products/',
    query: {
      ...(activeCategory.value ? { category: activeCategory.value } : {}),
      ...(q.value ? { q: q.value } : {}),
      ...(page > 1 ? { page } : {}),
    },
  })
}

function selectCategory(slug) {
  activeCategory.value = slug
  syncQuery(1)
}

function applySearch() {
  q.value = draftQ.value.trim()
  syncQuery(1)
}

function clearSearch() {
  q.value = ''
  draftQ.value = ''
  syncQuery(1)
}

function goPage(page) {
  syncQuery(page)
}

async function loadProducts() {
  if (controller) controller.abort()
  controller = new AbortController()
  loading.value = true
  error.value = ''
  try {
    const [categoryData, productData] = await Promise.all([
      categories.value.length ? Promise.resolve(categories.value) : fetchProductCategories(controller.signal),
      fetchProducts({
        category: activeCategory.value || undefined,
        q: q.value || undefined,
        page: pagination.value.page,
      }, controller.signal),
    ])
    categories.value = categoryData
    products.value = productData.results
    pagination.value = {
      count: productData.count,
      page: productData.page,
      page_size: productData.page_size,
      total_pages: productData.total_pages,
    }
  } catch (err) {
    if (err.name !== 'CanceledError' && err.code !== 'ERR_CANCELED') {
      products.value = []
      error.value = readableError(err, '产品加载失败。')
    }
  } finally {
    loading.value = false
  }
}

watch(() => route.query, () => {
  activeCategory.value = (route.params.categorySlug || route.query.category || '').toString()
  q.value = (route.query.q || '').toString()
  draftQ.value = q.value
  pagination.value.page = Number(route.query.page || 1)
  loadProducts()
})

onMounted(() => {
  setPageMeta({ title: '产品中心 - 华丽电器', description: '浏览华丽电器电钻、电锤、角磨机、型材切割机等电动工具产品。' })
  loadProducts()
})

onBeforeUnmount(() => {
  if (controller) controller.abort()
})
</script>

<style scoped>
.category-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 28px; }
.category-card { position: relative; min-height: 118px; overflow: hidden; border: 1px solid var(--gray-200); background: var(--dark); color: var(--white); cursor: pointer; text-align: left; padding: 18px; }
.category-card img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .34; transition: transform .35s; }
.category-card span, .category-card strong { position: relative; z-index: 1; display: block; }
.category-card span { font-size: 12px; color: var(--gray-300); margin-bottom: 28px; }
.category-card strong { font-size: 18px; }
.category-card:hover img { transform: scale(1.04); }
.category-card.active { border-color: var(--brand); box-shadow: inset 0 -4px 0 var(--brand); }
.search-bar { display: flex; gap: 10px; margin-bottom: 32px; }
.search-bar input { flex: 1; min-width: 0; border: 1px solid var(--gray-300); border-radius: var(--radius); padding: 12px 14px; font-size: 14px; }
.clear-btn { border-color: var(--gray-300); color: var(--text); background: var(--white); }
.product-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.product-card { overflow: hidden; box-shadow: var(--shadow); background: var(--white); transition: all .3s; }
.product-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-lg); }
.product-detail-link { display: block; }
.pc-visual { position: relative; aspect-ratio: 3 / 2; overflow: hidden; background: #f2f2f2; }
.pc-img { width: 100%; height: 100%; object-fit: cover; transition: transform .45s ease; }
.product-card:hover .pc-img { transform: scale(1.035); }
.pc-level {
  position: absolute; top: 12px; right: 12px; padding: 3px 10px; font-size: 11px;
  font-weight: 600; border-radius: 2px; box-shadow: 0 2px 8px rgba(0,0,0,.12);
}
.pc-body { padding: 16px 20px 10px; }
.pc-cat { font-size: 11px; color: var(--gray-500); letter-spacing: 1px; }
.pc-name { font-size: 17px; margin: 4px 0 2px; }
.pc-model { font-size: 12px; color: var(--gray-500); font-family: monospace; display: block; margin-bottom: 12px; }
.pc-specs { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; margin-bottom: 14px; }
.pc-spec { display: flex; justify-content: space-between; font-size: 12px; padding: 3px 0; border-bottom: 1px dashed var(--gray-200); }
.pc-spec-key { color: var(--gray-500); }
.pc-spec-val { font-weight: 600; }
.view-detail { color: var(--brand); font-size: 13px; font-weight: 600; }
.pc-action { padding: 10px 20px 20px; }
.content-state { padding: 36px; text-align: center; background: var(--gray-100); color: var(--gray-600); border: 1px solid var(--gray-200); }
.content-state.error { color: #B42318; background: #FFF5F5; }
.content-state button { margin-left: 10px; border: 0; color: var(--brand); background: transparent; font-weight: 700; cursor: pointer; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 34px; }
.pagination button { min-width: 38px; height: 38px; border: 1px solid var(--gray-300); background: var(--white); cursor: pointer; }
.pagination button.active { background: var(--brand); border-color: var(--brand); color: var(--white); }
.pagination button:disabled { opacity: .45; cursor: not-allowed; }
.mobile-page { display: none; color: var(--gray-600); font-size: 13px; }
.list-enter-active, .list-leave-active { transition: all .4s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateY(20px); }
@media (max-width: 1024px) {
  .category-strip { grid-template-columns: repeat(3, minmax(220px, 1fr)); overflow-x: auto; padding-bottom: 8px; }
  .product-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .category-strip { display: flex; overflow-x: auto; }
  .category-card { min-width: 220px; }
  .search-bar { flex-wrap: wrap; }
  .search-bar input { flex-basis: 100%; }
  .product-grid { grid-template-columns: 1fr; }
  .pagination button:not(:first-child):not(:last-child) { display: none; }
  .mobile-page { display: inline-block; min-width: 64px; text-align: center; }
}
@media (prefers-reduced-motion: reduce) {
  .pc-img, .product-card { transition: none; }
  .product-card:hover .pc-img { transform: none; }
}
</style>
