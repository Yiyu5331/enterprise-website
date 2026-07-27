<template>
  <main class="privacy-page">
    <div class="page-banner"><h1>隐私政策</h1><p>了解我们如何保护您提交的联系信息</p></div>
    <section class="section"><div class="container privacy-content">
      <div v-if="loading">正在加载隐私政策...</div>
      <div v-else-if="error" class="error-msg">{{ error }}</div>
      <template v-else>
        <p class="version">版本：{{ policy.version }} · 发布时间：{{ formatDate(policy.published_at) }}</p>
        <h2>{{ policy.title_zh }}</h2><div class="policy-body">{{ policy.body_zh }}</div>
        <hr><h2>{{ policy.title_en }}</h2><div class="policy-body">{{ policy.body_en }}</div>
      </template>
    </div></section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchPrivacyPolicy } from '@/api/content'
import { readableError, setPageMeta } from '@/api/client'

const policy = ref({})
const loading = ref(true)
const error = ref('')
function formatDate(value) { return value ? new Date(value).toLocaleDateString('zh-CN') : '' }
onMounted(async () => {
  setPageMeta({ title: '隐私政策 - 华丽电器', description: '华丽电器网站隐私政策。' })
  try { policy.value = await fetchPrivacyPolicy() }
  catch (err) { error.value = readableError(err, '隐私政策暂不可用。') }
  finally { loading.value = false }
})
</script>

<style scoped>
.privacy-content { max-width: 860px; }
.version { color: var(--gray-500); margin-bottom: 24px; }
h2 { font-size: 24px; margin: 20px 0 12px; }
.policy-body { white-space: pre-wrap; line-height: 1.9; color: var(--text-light); }
hr { border: 0; border-top: 1px solid var(--gray-200); margin: 36px 0; }
.error-msg { color: #b42318; }
</style>
