import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'
import { siteUrl } from './api/client'

const organization = document.createElement('script')
organization.type = 'application/ld+json'
organization.dataset.globalJsonld = 'true'
organization.textContent = JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: '华丽电器制造有限公司',
  url: siteUrl,
  logo: `${siteUrl}/images/logo.jpg`,
})
document.head.appendChild(organization)

const app = createApp(App)
app.use(router)
app.mount('#app')
