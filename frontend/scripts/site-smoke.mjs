import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { chromium } from 'playwright'

const baseUrl = (process.env.SMOKE_BASE_URL || 'http://127.0.0.1:5173').replace(/\/$/, '')
const outputDir = path.resolve(import.meta.dirname, '..', '..', 'tmp', 'browser-smoke')
await mkdir(outputDir, { recursive: true })

const cases = [
  ['home', '/'],
  ['products', '/products/'],
  ['product-detail', '/products/rotary-hammers/HL-RH501/'],
  ['news', '/news/'],
  ['news-detail', '/news/company-news/5g-factory-2025/'],
  ['inquiry', '/inquiry/'],
  ['contact', '/contact/'],
  ['not-found', '/missing-page/'],
]
const viewports = [
  ['desktop', { width: 1440, height: 1000 }],
  ['mobile', { width: 390, height: 844 }],
]

const browser = await chromium.launch({ headless: true })
const failures = []
try {
  for (const [viewportName, viewport] of viewports) {
    const page = await browser.newPage({ viewport })
    const errors = []
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()) })
    page.on('pageerror', error => errors.push(error.message))
    page.on('requestfailed', request => errors.push(`${request.url()} ${request.failure()?.errorText}`))
    for (const [name, route] of cases) {
      errors.length = 0
      await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle', timeout: 45000 })
      await page.waitForTimeout(500)
      const state = await page.evaluate(() => ({
        body: document.querySelector('main')?.innerText.trim() || '',
        overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
        brokenImages: [...document.images].filter(image => image.complete && image.naturalWidth === 0).map(image => image.src),
      }))
      if (!state.body) failures.push(`${viewportName}/${name}: 正文为空`)
      if (state.overflow) failures.push(`${viewportName}/${name}: 存在横向滚动`)
      if (state.brokenImages.length) failures.push(`${viewportName}/${name}: 破图 ${state.brokenImages.join(', ')}`)
      if (errors.length) failures.push(`${viewportName}/${name}: ${errors.join(' | ')}`)
      if (['home', 'product-detail', 'inquiry', 'not-found'].includes(name)) {
        await page.screenshot({ path: path.join(outputDir, `${viewportName}-${name}.png`), fullPage: true })
      }
    }
    await page.close()
  }
} finally {
  await browser.close()
}

if (failures.length) throw new Error(failures.join('\n'))
process.stdout.write('桌面与手机浏览器冒烟测试通过。\n')
