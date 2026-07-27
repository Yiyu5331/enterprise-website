import { onMounted, reactive, ref } from 'vue'
import { fetchCaptcha, fetchFormBootstrap } from '@/api/content'

export function useSecureForm(kind) {
  const bootstrap = reactive({ formEnabled: false, formToken: '', privacyVersion: '', privacyTitle: '', message: '' })
  const consent = ref(false)
  const honeypot = ref('')
  const captcha = reactive({ required: false, id: '', image: '', answer: '' })

  async function initialize() {
    const data = await fetchFormBootstrap(kind)
    Object.assign(bootstrap, {
      formEnabled: data.form_enabled,
      formToken: data.form_token,
      privacyVersion: data.privacy_version,
      privacyTitle: data.privacy_title,
      message: data.message,
    })
  }

  async function loadCaptcha() {
    const data = await fetchCaptcha()
    Object.assign(captcha, { required: true, id: data.captcha_id, image: data.image, answer: '' })
  }

  function appendSecurityFields(payload) {
    payload.append('form_token', bootstrap.formToken)
    payload.append('privacy_consent', consent.value ? 'true' : 'false')
    payload.append('privacy_version', bootstrap.privacyVersion)
    payload.append('website', honeypot.value)
    if (captcha.required) {
      payload.append('captcha_id', captcha.id)
      payload.append('captcha_answer', captcha.answer)
    }
  }

  async function handleSecurityError(error) {
    if (['captcha_required', 'captcha_invalid'].includes(error.response?.data?.code)) await loadCaptcha()
  }

  onMounted(initialize)
  return { bootstrap, consent, honeypot, captcha, initialize, loadCaptcha, appendSecurityFields, handleSecurityError }
}
