<template>
  <main class="not-found-page">
    <section class="section"><div class="container not-found-content">
      <span>404</span><h1>页面不存在</h1><p>该页面可能已移动、更新或输入地址有误。</p>
      <div class="actions"><RouterLink to="/" class="btn btn-primary">返回首页</RouterLink><RouterLink to="/products/" class="btn btn-outline">浏览产品</RouterLink></div>
    </div></section>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { setPageMeta } from '@/api/client'
onMounted(() => setPageMeta({ title: '页面不存在 - 华丽电器', description: '请求的页面不存在。', robots: 'noindex,follow' }))
</script>

<style scoped>
.not-found-page { margin-top: var(--header-h); min-height: 70vh; display: grid; place-items: center; }
.not-found-content { text-align: center; max-width: 620px; }
.not-found-content > span { color: var(--brand); font-size: 72px; font-weight: 800; }
h1 { font-size: 34px; margin: 8px 0 12px; }
p { color: var(--text-light); margin-bottom: 26px; }
.actions { display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; }
</style>
