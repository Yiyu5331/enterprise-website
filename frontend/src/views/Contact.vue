<template>
  <div class="contact-page">
    <div class="page-banner">
      <h1>联系我们</h1>
      <p>期待与您的合作，为您提供优质的产品与服务</p>
    </div>
    <section class="section">
      <div class="container">
        <div class="contact-grid">
          <div class="contact-info-panel">
            <h3>公司信息</h3>
            <div class="ci-block">
              <div class="ci-icon">📍</div>
              <div><strong>公司地址</strong><p>浙江省金华市武义县泉溪镇王元工业区（一照多址）</p></div>
            </div>
            <div class="ci-block">
              <div class="ci-icon">📞</div>
              <div><strong>联系电话</strong><p>销售热线：0579-8770****<br>客服热线：0579-8770****</p></div>
            </div>
            <div class="ci-block">
              <div class="ci-icon">✉️</div>
              <div><strong>电子邮箱</strong><p>销售部：k****@cnkainuo<br>国际部：k****@cnkainuo</p></div>
            </div>
            <div class="ci-block">
              <div class="ci-icon">🕐</div>
              <div><strong>工作时间</strong><p>周一至周五：8:00 - 17:00<br>周六：8:00 - 12:00（仅处理紧急事务）</p></div>
            </div>
          </div>
          <div class="contact-form-panel">
            <h3>在线留言</h3>
            <p class="form-desc">请填写以下信息，我们会尽快回复您</p>
            <form @submit.prevent="handleContact">
              <div class="form-grid">
                <div class="form-group"><label>姓名 *</label><input v-model="cform.name" placeholder="请输入您的姓名" required></div>
                <div class="form-group"><label>邮箱 *</label><input v-model="cform.email" type="email" placeholder="your@email.com" required></div>
              </div>
              <div class="form-grid">
                <div class="form-group"><label>电话</label><input v-model="cform.phone" type="tel" placeholder="您的联系电话"></div>
                <div class="form-group"><label>主题</label>
                  <select v-model="cform.subject">
                    <option value="">请选择主题</option>
                    <option>产品咨询</option><option>合作洽谈</option><option>售后服务</option><option>供应商合作</option><option>投诉建议</option><option>其他</option>
                  </select>
                </div>
              </div>
              <div class="form-group"><label>留言内容 *</label><textarea v-model="cform.message" rows="5" placeholder="请详细描述您的需求或问题" required></textarea></div>
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
                {{ submitting ? '提交中...' : '提交留言' }}
              </button>
              <p v-if="submitError" class="error-msg" role="alert">{{ submitError }}</p>
            </form>
            <p v-if="contactSent" class="success-msg">✅ 留言已成功发送，我们将尽快与您联系！</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 地图占位 -->
    <section class="section section-gray" style="padding:0">
      <div class="map-placeholder">
        <svg viewBox="0 0 1200 300" width="100%"><rect width="1200" height="300" fill="#e0e0e0"/><text x="600" y="155" text-anchor="middle" fill="#999" font-size="16">地图加载区域 — 浙江省金华市武义县泉溪镇王元工业区</text></svg>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { submitContact } from '@/api/content'
import { readableError } from '@/api/client'
import { useSecureForm } from '@/composables/useSecureForm'
const cform = reactive({ name:'', email:'', phone:'', subject:'', message:'' })
const contactSent = ref(false)
const submitting = ref(false)
const submitError = ref('')
const { bootstrap, consent, honeypot, captcha, initialize, loadCaptcha, appendSecurityFields, handleSecurityError } = useSecureForm('contact')
async function handleContact() {
  submitting.value = true
  contactSent.value = false
  submitError.value = ''

  try {
    const payload = new FormData()
    payload.append('contact_name', cform.name)
    payload.append('email', cform.email)
    payload.append('phone', cform.phone)
    payload.append('subject', cform.subject)
    payload.append('message', cform.message)
    appendSecurityFields(payload)
    await submitContact(payload)
    contactSent.value = true
    Object.assign(cform, { name:'', email:'', phone:'', subject:'', message:'' })
    consent.value = false
    await initialize()
  } catch (error) {
    await handleSecurityError(error)
    submitError.value = readableError(error, '提交失败，请检查网络或稍后重试。')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.contact-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 40px; }
.contact-info-panel h3, .contact-form-panel h3 { font-size: 22px; margin-bottom: 24px; }
.ci-block { display: flex; gap: 16px; margin-bottom: 24px; }
.ci-icon { width: 44px; height: 44px; background: var(--brand-light); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.ci-block strong { display: block; font-size: 14px; margin-bottom: 4px; }
.ci-block p { font-size: 13px; color: var(--text-light); line-height: 1.7; }
.form-desc { font-size: 13px; color: var(--gray-500); margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px 14px; border: 1px solid var(--gray-300); border-radius: var(--radius); font-size: 14px; font-family: inherit; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px rgba(196,30,36,.1); }
.success-msg { text-align: center; padding: 16px; background: #E8F5E9; color: #2E7D32; border-radius: var(--radius-lg); margin-top: 20px; font-weight: 600; }
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
.map-placeholder { line-height: 0; }
@media (max-width: 768px) {
  .contact-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
