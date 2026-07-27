import { chromium } from 'playwright'

const baseUrl = (process.env.PRERENDER_BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '')
const browser = await chromium.launch({ headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle' })
  await page.waitForFunction(() => window.__PRERENDER_READY__ === true, null, { timeout: 20000 })
  if (!(await page.locator('main').innerText()).trim()) throw new Error('首页正文为空。')
  if (await page.locator('body').evaluate(node => node.scrollWidth > node.clientWidth + 2)) throw new Error('手机页面存在横向滚动。')
  if ((await page.locator('link[rel="canonical"]').count()) !== 1) throw new Error('缺少 canonical。')
  process.stdout.write('预渲染冒烟测试通过。\n')
} finally {
  await browser.close()
}
