<template>
  <div class="inquiry-page">
    <div class="page-banner">
      <h1>在线询盘</h1>
      <p>提交您的产品需求，专业技术团队 24 小时内为您提供定制方案</p>
    </div>
    <section class="section">
      <div class="container">
        <div class="inquiry-layout">
          <div class="inquiry-form-wrap">
            <h3 class="form-title">询盘表单</h3>
            <p class="form-desc">请填写以下信息，带 * 为必填项</p>
            <form class="inquiry-form" @submit.prevent="handleSubmit">
              <div class="form-grid">
                <div class="form-group"><label>您的姓名 *</label><input v-model="form.name" placeholder="请输入您的姓名" required></div>
                <div class="form-group"><label>公司名称</label><input v-model="form.company" placeholder="请输入公司名称"></div>
                <div class="form-group"><label>邮箱 *</label><input v-model="form.email" type="email" placeholder="your@email.com" required></div>
                <div class="form-group"><label>电话</label><input v-model="form.phone" type="tel" placeholder="+86 1234567890"></div>
                <div class="form-group"><label>国家/地区</label><input v-model="form.country" placeholder="如：China"></div>
                <div class="form-group"><label>感兴趣的产品</label>
                  <select v-model="form.product" @change="updateSelectedProduct">
                    <option value="">请选择产品</option>
                    <option v-for="p in productOptions" :key="p.model" :value="p.model">{{ p.label }}</option>
                  </select>
                  <small v-if="optionsError" class="field-hint">{{ optionsError }}</small>
                </div>
              </div>
              <div v-if="selectedProduct" class="selected-product">
                <img :src="selectedProduct.image" :alt="selectedProduct.name">
                <div><strong>{{ selectedProduct.name }}</strong><span>{{ selectedProduct.model }}</span></div>
              </div>
              <div class="form-group"><label>预计数量</label><input v-model="form.quantity" placeholder="如：1000 台"></div>
              <div class="form-group"><label>详细需求 *</label><textarea v-model="form.message" rows="5" placeholder="请详细描述您的产品需求：型号、规格、数量、交期要求等" required></textarea></div>
              <div class="form-group"><label>附件上传（可选，最大 10 MB）</label><input ref="fileInput" type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png" @change="handleFile"></div>
              <input v-model="honeypot" class="form-honeypot" tabindex="-1" autocomplete="off" aria-hidden="true">
              <div v-if="captcha.required" class="captcha-row">
                <img :src="captcha.image" alt="图形验证码" @click="loadCaptcha">
                <input v-model="captcha.answer" inputmode="numeric" maxlength="4" placeholder="请输入 4 位验证码" required>
                <button type="button" class="captcha-refresh" @click="loadCaptcha">换一张</button>
              </div>
              <label class="privacy-consent">
                <input v-model="consent" type="checkbox" required>
                <span>我已阅读并同意 <RouterLink to="/privacy/" target="_blank">{{ bootstrap.privacyTitle || '隐私政策' }}</RouterLink></span>
              </label>
              <p v-if="bootstrap.message" class="form-notice">{{ bootstrap.message }}</p>
              <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="submitting || !bootstrap.formEnabled">
                {{ submitting ? '提交中...' : '提交询盘' }}
              </button>
              <p v-if="submitError" class="error-msg" role="alert">{{ submitError }}</p>
            </form>
          </div>
          <div class="inquiry-sidebar">
            <div class="is-card">
              <h4>询盘流程</h4>
              <ol><li>提交询盘表单</li><li>客服 24 小时内回复</li><li>技术方案沟通</li><li>报价与样品</li><li>订单确认</li></ol>
            </div>
            <div class="is-card">
              <h4>联系方式</h4>
              <p>📞 8770****</p>
              <p>✉️ k****@cnkainuo</p>
            </div>
            <div class="is-card">
              <h4>为什么选择华丽</h4>
              <ul><li>20 年专业制造经验</li><li>国家级高新技术企业</li><li>CE/UL/GS 国际认证</li><li>500 万台年产能</li><li>OEM/ODM 定制服务</li></ul>
            </div>
          </div>
        </div>
        <div v-if="submitted" class="success-msg">✅ 询盘已成功提交！我们将在 24 小时内与您联系。</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { fetchProductOptions, submitInquiry } from '@/api/content'
import { readableError } from '@/api/client'
import { useSecureForm } from '@/composables/useSecureForm'
const route = useRoute()
const productOptions = ref([])
const selectedProduct = ref(null)
const optionsError = ref('')
const form = reactive({ name:'', company:'', email:'', phone:'', country:'', product:'', productName:'', quantity:'', message:'', file:null })
const submitted = ref(false)
const submitting = ref(false)
const submitError = ref('')
const fileInput = ref(null)
const { bootstrap, consent, honeypot, captcha, initialize, loadCaptcha, appendSecurityFields, handleSecurityError } = useSecureForm('inquiry')
function handleFile(e) { form.file = e.target.files[0] }
function updateSelectedProduct() {
  selectedProduct.value = productOptions.value.find(item => item.model === form.product) || null
  form.productName = selectedProduct.value?.name || ''
}
async function loadProductOptions() {
  try {
    productOptions.value = await fetchProductOptions()
    const selected = productOptions.value.find(item => item.model === route.query.product)
    if (selected) { form.product = selected.model; updateSelectedProduct() }
  } catch (error) { optionsError.value = readableError(error, '产品选项加载失败，仍可手动填写。') }
}
async function handleSubmit() {
  submitting.value = true
  submitted.value = false
  submitError.value = ''

  const payload = new FormData()
  payload.append('contact_name', form.name)
  payload.append('phone', form.phone)
  payload.append('email', form.email)
  payload.append('company_brand', form.company)
  payload.append('project_type', form.productName || form.product || '其他')
  if (form.product) payload.append('product_model_snapshot', form.product)
  payload.append('estimated_quantity', form.quantity)
  payload.append('country_region', form.country)
  payload.append('detailed_requirements', form.message)
  if (form.file) payload.append('attachment', form.file)
  appendSecurityFields(payload)

  try {
    await submitInquiry(payload)
    submitted.value = true
    Object.assign(form, { name:'', company:'', email:'', phone:'', country:'', product:'', productName:'', quantity:'', message:'', file:null })
    selectedProduct.value = null
    consent.value = false
    if (fileInput.value) fileInput.value.value = ''
    await initialize()
  } catch (error) {
    await handleSecurityError(error)
    submitError.value = readableError(error, '提交失败，请检查网络或稍后重试。')
  } finally {
    submitting.value = false
  }
}
onMounted(loadProductOptions)
</script>

<style scoped>
.inquiry-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 40px; }
.form-title { font-size: 22px; margin-bottom: 4px; }
.form-desc { font-size: 13px; color: var(--gray-500); margin-bottom: 24px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text); }
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 10px 14px; border: 1px solid var(--gray-300); border-radius: var(--radius);
  font-size: 14px; font-family: inherit; transition: border .3s;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px rgba(196,30,36,.1); }
.selected-product { display: flex; align-items: center; gap: 14px; margin: 2px 0 18px; padding: 10px; border: 1px solid var(--gray-200); background: var(--gray-100); border-radius: var(--radius); }
.selected-product img { width: 68px; height: 48px; object-fit: cover; border-radius: 4px; }
.selected-product div { display: flex; flex-direction: column; gap: 4px; }
.selected-product span { color: var(--gray-500); font-family: monospace; font-size: 12px; }
.inquiry-sidebar { display: flex; flex-direction: column; gap: 20px; }
.is-card { background: var(--gray-100); border-radius: var(--radius-lg); padding: 24px; border-left: 3px solid var(--brand); }
.is-card h4 { font-size: 15px; margin-bottom: 12px; }
.is-card ol, .is-card ul { padding-left: 18px; }
.is-card li { font-size: 13px; color: var(--text-light); padding: 4px 0; }
.is-card p { font-size: 13px; color: var(--text-light); padding: 3px 0; }
.success-msg { text-align: center; padding: 24px; background: #E8F5E9; color: #2E7D32; border-radius: var(--radius-lg); margin-top: 24px; font-weight: 600; font-size: 16px; }
.error-msg { margin-top: 14px; color: #B42318; font-size: 14px; text-align: center; }
.form-honeypot { position: absolute !important; left: -9999px !important; width: 1px !important; height: 1px !important; }
.privacy-consent { display: flex; gap: 9px; align-items: flex-start; margin: 14px 0; font-size: 13px; color: var(--text-light); }
.privacy-consent input { width: 16px; height: 16px; margin-top: 2px; }
.privacy-consent a { color: var(--brand); }
.form-notice { margin: 12px 0; padding: 10px 12px; background: #fff3cd; color: #7a5700; font-size: 13px; }
.captcha-row { display: grid; grid-template-columns: 150px 1fr auto; gap: 10px; align-items: center; margin: 14px 0; }
.captcha-row img { width: 150px; height: 54px; border: 1px solid var(--gray-300); cursor: pointer; }
.captcha-row input { min-width: 0; padding: 10px 12px; border: 1px solid var(--gray-300); }
.captcha-refresh { border: 0; background: transparent; color: var(--brand); cursor: pointer; }
@media (max-width: 768px) {
  .inquiry-layout { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .captcha-row { grid-template-columns: 150px 1fr; }
}
</style>
