<template>
  <div v-if="loading" class="article-missing"><div class="container text-center"><h1>新闻加载中...</h1></div></div>
  <section v-else-if="state.status === 404" class="section article-missing">
    <div class="container text-center">
      <h1>未找到该新闻</h1>
      <p>文章可能已更新或移动，请返回新闻中心查看最新内容。</p>
      <router-link to="/news" class="btn btn-primary">返回新闻中心</router-link>
    </div>
  </section>
  <section v-else-if="state.error" class="section article-missing">
    <div class="container text-center">
      <h1>新闻加载失败</h1>
      <p>{{ state.error }}</p>
      <button type="button" class="btn btn-primary" @click="loadDetail">重新加载</button>
    </div>
  </section>
  <article v-else-if="article" class="article-page">
    <header class="article-header">
      <div class="container article-header-inner">
        <router-link to="/news" class="back-link">← 返回新闻中心</router-link>
        <span class="article-cat">{{ article.category }}</span>
        <h1>{{ article.title }}</h1>
        <p>{{ article.summary }}</p>
        <time>{{ article.date }}</time>
      </div>
    </header>

    <section class="article-content section">
      <div class="container article-layout">
        <div class="article-main">
          <img :src="article.image" :alt="article.title" class="article-cover" />
          <div class="article-body rich-content" v-html="article.body"></div>
          <div class="article-actions">
            <router-link to="/contact" class="btn btn-primary">联系我们</router-link>
            <router-link to="/news" class="btn article-outline">查看更多新闻</router-link>
          </div>
        </div>
        <aside class="article-aside">
          <h2>相关新闻</h2>
          <router-link v-for="item in relatedNews" :key="item.slug" :to="`/news/${item.category_slug}/${item.slug}/`" class="aside-news">
            <img :src="item.image" :alt="item.title" loading="lazy" />
            <div><time>{{ item.date }}</time><h3>{{ item.title }}</h3></div>
          </router-link>
        </aside>
      </div>
    </section>
  </article>

  <section v-else class="section article-missing">
    <div class="container text-center">
      <h1>未找到该新闻</h1>
      <p>文章可能已更新或移动，请返回新闻中心查看最新内容。</p>
      <router-link to="/news" class="btn btn-primary">返回新闻中心</router-link>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchNewsDetail } from '@/api/content'
import { setPageMeta, siteUrl } from '@/api/client'
import { useAsyncState } from '@/composables/useAsyncState'

const route = useRoute()
const { state, run } = useAsyncState(signal => fetchNewsDetail(route.params.slug, signal), '新闻详情加载失败。')
const article = computed(() => state.data)
const relatedNews = computed(() => article.value?.related_news || [])
const loading = computed(() => state.loading)
async function loadDetail() {
  const data = await run()
  if (data) {
    const canonical = `${siteUrl}/news/${data.category_slug}/${data.slug}/`
    const cover = data.cover.startsWith('http') ? data.cover : `${siteUrl}${data.cover}`
    setPageMeta({
      title: data.seo?.title, description: data.seo?.description, image: data.cover, canonical,
      structuredData: [
        { '@context': 'https://schema.org', '@type': 'NewsArticle', headline: data.title, description: data.summary, image: [cover], datePublished: data.date, publisher: { '@type': 'Organization', name: '华丽电器制造有限公司' } },
        { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: '新闻中心', item: `${siteUrl}/news/` }, { '@type': 'ListItem', position: 2, name: data.category, item: `${siteUrl}/news/category/${data.category_slug}/` }, { '@type': 'ListItem', position: 3, name: data.title, item: canonical }] },
      ],
    })
  }
}
watch(() => route.params.slug, loadDetail)
onMounted(loadDetail)
</script>

<style scoped>
.article-page { margin-top: calc(var(--header-h) + 32px); }
.article-header { background: var(--dark); color: var(--white); padding: 72px 0 80px; }
.article-header-inner { max-width: 900px; }
.back-link { display: inline-block; color: var(--gray-400); font-size: 13px; margin-bottom: 34px; }
.back-link:hover { color: var(--white); }
.article-cat { display: block; color: var(--brand-hover); font-size: 12px; font-weight: 700; letter-spacing: 2px; margin-bottom: 14px; }
.article-header h1 { max-width: 820px; font-size: 42px; line-height: 1.3; margin-bottom: 18px; }
.article-header p { max-width: 760px; color: var(--gray-400); font-size: 16px; line-height: 1.8; margin-bottom: 18px; }
.article-header time { font-size: 13px; color: var(--gray-500); }
.article-layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 56px; align-items: start; }
.article-cover { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
.article-body { max-width: 760px; padding: 42px 0 20px; }
.article-body p { font-size: 16px; color: var(--text-light); line-height: 2.15; margin-bottom: 22px; }
.article-body :deep(h2), .article-body :deep(h3), .article-body :deep(h4) { margin: 28px 0 14px; }
.article-body :deep(table) { display: block; overflow-x: auto; width: 100%; border-collapse: collapse; }
.article-body :deep(td), .article-body :deep(th) { border: 1px solid var(--gray-300); padding: 8px 10px; min-width: 120px; }
.article-body :deep(img) { max-width: 100%; height: auto; }
.article-actions { display: flex; gap: 12px; flex-wrap: wrap; padding-top: 20px; border-top: 1px solid var(--gray-200); }
.article-outline { color: var(--text); border-color: var(--gray-300); }
.article-outline:hover { color: var(--brand); border-color: var(--brand); }
.article-aside { border-top: 3px solid var(--brand); padding-top: 20px; }
.article-aside h2 { font-size: 20px; margin-bottom: 20px; }
.aside-news { display: grid; grid-template-columns: 96px 1fr; gap: 14px; padding: 16px 0; border-bottom: 1px solid var(--gray-200); }
.aside-news img { width: 96px; height: 68px; object-fit: cover; }
.aside-news time { color: var(--gray-500); font-size: 11px; }
.aside-news h3 { font-size: 13px; line-height: 1.55; margin-top: 4px; }
.aside-news:hover h3 { color: var(--brand); }
.article-missing { margin-top: calc(var(--header-h) + 32px); padding: 140px 0; }
.article-missing p { margin: 12px 0 24px; color: var(--gray-600); }
@media (max-width: 768px) {
  .article-page { margin-top: var(--header-h); }
  .article-header { padding: 52px 0 60px; }
  .article-header h1 { font-size: 30px; }
  .article-layout { grid-template-columns: 1fr; gap: 46px; }
}
</style>
