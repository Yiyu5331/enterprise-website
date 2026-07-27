<template>
  <div class="news-page">
    <div class="page-banner">
      <h1>新闻中心</h1>
      <p>掌握华丽电器最新动态、行业资讯与展会信息</p>
    </div>
    <section class="section">
      <div class="container">
        <div class="filter-bar">
          <button type="button" :class="['filter-btn', { active: !query.category }]" @click="selectCategory('')">全部</button>
          <button v-for="cat in newsCategories" :key="cat.slug" type="button" :class="['filter-btn', { active: query.category === cat.slug }]" @click="selectCategory(cat.slug)">{{ cat.name }}</button>
        </div>
        <form class="search-bar" @submit.prevent="submitSearch">
          <input v-model="searchInput" type="search" placeholder="搜索新闻标题、摘要或来源" maxlength="100" aria-label="搜索新闻">
          <button type="submit" class="btn btn-primary">搜索</button>
        </form>
        <div v-if="state.loading" class="module-state">新闻加载中...</div>
        <div v-else-if="state.error" class="module-state error">{{ state.error }} <button type="button" @click="loadNews">重新加载</button></div>
        <div v-else-if="!articles.length" class="module-state">暂时没有符合条件的新闻。</div>
        <div v-else class="news-grid">
          <router-link v-for="article in articles" :key="article.slug" :to="`/news/${article.category_slug}/${article.slug}/`" class="news-card">
            <div class="nc-img"><img :src="article.image" :alt="article.title" loading="lazy" /></div>
            <div class="nc-body">
              <div class="nc-meta"><span class="nc-cat">{{ article.category }}</span><time>{{ article.date }}</time></div>
              <h2>{{ article.title }}</h2>
              <p>{{ article.summary }}</p>
              <span class="read-more">阅读全文 →</span>
            </div>
          </router-link>
        </div>
        <nav v-if="page.total_pages > 1" class="pagination" aria-label="新闻分页">
          <button type="button" :disabled="page.page <= 1" @click="goToPage(page.page - 1)">上一页</button>
          <span>第 {{ page.page }} / {{ page.total_pages }} 页</span>
          <button type="button" :disabled="page.page >= page.total_pages" @click="goToPage(page.page + 1)">下一页</button>
        </nav>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchNews, fetchNewsCategories } from '@/api/content'
import { readableError, setPageMeta } from '@/api/client'
import { useAsyncState } from '@/composables/useAsyncState'

const route = useRoute()
const router = useRouter()
const searchInput = ref(route.query.q || '')
const query = ref({ category: route.params.categorySlug || route.query.category || '', q: route.query.q || '', page: Number(route.query.page || 1) })
const newsCategories = ref([])
const page = ref({ page: 1, total_pages: 1 })
const { state, run } = useAsyncState(signal => fetchNews(query.value, signal), '新闻加载失败。')
const articles = computed(() => state.data?.results || [])

async function loadCategories() {
  try { newsCategories.value = await fetchNewsCategories() } catch (error) { /* 分类失败时仍可显示新闻 */ }
}
async function loadNews() {
  const data = await run()
  if (data) page.value = data
}
function updateUrl() {
  router.replace({
    path: query.value.category && !query.value.q ? `/news/category/${query.value.category}/` : '/news/',
    query: { q: query.value.q || undefined, page: query.value.page > 1 ? query.value.page : undefined },
  })
}
function selectCategory(category) { query.value = { ...query.value, category, page: 1 }; updateUrl(); loadNews() }
function submitSearch() { query.value = { ...query.value, q: searchInput.value.trim(), page: 1 }; updateUrl(); loadNews() }
function goToPage(pageNumber) { query.value = { ...query.value, page: pageNumber }; updateUrl(); loadNews() }
watch(() => route.fullPath, () => {
  query.value = { category: route.params.categorySlug || route.query.category || '', q: route.query.q || '', page: Number(route.query.page || 1) }
  searchInput.value = query.value.q
  loadNews()
})
onMounted(() => { setPageMeta({ title: '新闻中心 - 华丽电器' }); loadCategories(); loadNews() })
</script>

<style scoped>
.filter-bar { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 40px; }
.filter-btn {
  padding: 8px 22px; border: 1px solid var(--gray-300); background: var(--white);
  border-radius: 20px; cursor: pointer; font-size: 14px; transition: all .25s;
}
.filter-btn:hover { border-color: var(--brand); color: var(--brand); }
.filter-btn.active { background: var(--brand); color: var(--white); border-color: var(--brand); }
.search-bar { display: flex; max-width: 680px; gap: 10px; margin: 0 auto 32px; }
.search-bar input { flex: 1; min-width: 0; padding: 10px 14px; border: 1px solid var(--gray-300); border-radius: var(--radius); font: inherit; }
.search-bar input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px rgba(196,30,36,.1); }
.module-state { padding: 32px; text-align: center; background: var(--gray-100); color: var(--gray-600); }
.module-state.error { color: #B42318; background: #FFF5F5; }
.module-state button, .pagination button { border: 0; background: transparent; color: var(--brand); cursor: pointer; font-weight: 700; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 22px; margin-top: 36px; color: var(--gray-600); font-size: 14px; }
.pagination button:disabled { color: var(--gray-400); cursor: not-allowed; }
.news-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 28px; max-width: 1000px; margin: 0 auto; }
.news-card { overflow: hidden; box-shadow: var(--shadow); background: var(--white); transition: all .3s; }
.news-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.nc-img { aspect-ratio: 16 / 9; overflow: hidden; background: var(--gray-100); }
.nc-img img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s; }
.news-card:hover .nc-img img { transform: scale(1.035); }
.nc-body { padding: 22px 24px 26px; }
.nc-meta { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }
.nc-cat { padding: 2px 10px; font-size: 11px; font-weight: 600; background: var(--brand-light); color: var(--brand); }
.nc-meta time { color: var(--gray-500); font-size: 12px; }
.nc-body h2 { font-size: 19px; line-height: 1.5; margin-bottom: 10px; }
.nc-body p { font-size: 13px; color: var(--gray-600); line-height: 1.8; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.read-more { display: inline-block; color: var(--brand); font-size: 13px; font-weight: 600; margin-top: 16px; }
@media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } }
</style>
