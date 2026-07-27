import { execFileSync } from 'node:child_process'
import { access, cp, mkdir, readdir, rename, rm, symlink, writeFile } from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { chromium } from 'playwright'

const frontendDir = path.resolve(import.meta.dirname, '..')
const projectDir = path.resolve(frontendDir, '..')
const releaseRoot = process.env.PRERENDER_ROOT || path.join(projectDir, 'prerender_releases')
const baseUrl = (process.env.PRERENDER_BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '')
const siteUrl = (process.env.SITE_URL || 'https://example.com').replace(/\/$/, '')
const version = new Date().toISOString().replace(/[:.]/g, '-')
const target = path.join(releaseRoot, version)

function djangoRoutes() {
  if (process.env.PRERENDER_PATHS) return JSON.parse(process.env.PRERENDER_PATHS)
  const python = process.env.PYTHON || path.join(projectDir, 'venv', 'Scripts', 'python.exe')
  const output = execFileSync(python, ['manage.py', 'list_prerender_routes'], { cwd: projectDir, encoding: 'utf8' })
  return JSON.parse(output.trim().split(/\r?\n/).at(-1))
}

function outputFile(routePath) {
  const clean = routePath.replace(/^\//, '').replace(/\/$/, '')
  return path.join(target, clean, 'index.html')
}

async function publishCurrent() {
  const current = path.join(releaseRoot, 'current')
  const next = path.join(releaseRoot, '.current-next')
  await rm(next, { recursive: true, force: true })
  await symlink(target, next, process.platform === 'win32' ? 'junction' : 'dir')
  try {
    await rename(next, current)
  } catch {
    await rm(current, { recursive: true, force: true })
    await rename(next, current)
  }
  const releases = (await readdir(releaseRoot, { withFileTypes: true }))
    .filter(item => item.isDirectory() && item.name !== 'current' && !item.name.startsWith('.'))
    .map(item => item.name).sort().reverse()
  for (const old of releases.slice(3)) await rm(path.join(releaseRoot, old), { recursive: true, force: true })
}

const routes = djangoRoutes()
const sitemapRoutes = process.env.PRERENDER_SITEMAP_PATHS ? JSON.parse(process.env.PRERENDER_SITEMAP_PATHS) : routes
await mkdir(target, { recursive: true })
try {
  await access(path.join(releaseRoot, 'current'))
  await cp(path.join(releaseRoot, 'current'), target, { recursive: true })
} catch { /* 首次发布没有可继承版本 */ }
await cp(path.join(frontendDir, 'dist'), target, { recursive: true })
const browser = await chromium.launch({ headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  const browserErrors = []
  page.on('console', message => {
    if (message.type() === 'error') browserErrors.push(`console: ${message.text()}`)
  })
  page.on('pageerror', error => browserErrors.push(`pageerror: ${error.message}`))
  page.on('requestfailed', request => browserErrors.push(`requestfailed: ${request.url()} - ${request.failure()?.errorText}`))
  for (const routePath of routes) {
    browserErrors.length = 0
    process.stdout.write(`预渲染：${routePath}\n`)
    const response = await page.goto(`${baseUrl}${routePath}`, { waitUntil: 'networkidle', timeout: 45000 })
    if (!response || response.status() >= 400) throw new Error(`${routePath} 返回 ${response?.status()}`)
    try {
      await page.waitForFunction(() => window.__PRERENDER_READY__ === true, null, { timeout: 20000 })
      await page.evaluate(async () => {
        const step = Math.max(500, Math.floor(window.innerHeight * 0.8))
        for (let top = 0; top < document.documentElement.scrollHeight; top += step) {
          window.scrollTo(0, top)
          await new Promise(resolve => setTimeout(resolve, 80))
        }
        window.scrollTo(0, 0)
      })
      await page.waitForFunction(() => [...document.images].every(image => image.complete), null, { timeout: 15000 })
    } catch (error) {
      const state = await page.evaluate(() => ({ ready: window.__PRERENDER_READY__, active: window.__API_ACTIVE_REQUESTS__, title: document.title, body: document.body.innerText.slice(0, 300) }))
      throw new Error(`${routePath} 未就绪：${JSON.stringify(state)}；${browserErrors.join('；')}`, { cause: error })
    }
    const html = `<!doctype html>\n${await page.locator('html').evaluate(node => node.outerHTML)}`
    const filename = outputFile(routePath)
    await mkdir(path.dirname(filename), { recursive: true })
    await writeFile(filename, html, 'utf8')
  }
} finally {
  await browser.close()
}

const today = new Date().toISOString().slice(0, 10)
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapRoutes.map(routePath => `  <url><loc>${siteUrl}${routePath}</loc><lastmod>${today}</lastmod></url>`).join('\n')}\n</urlset>\n`
await writeFile(path.join(target, 'sitemap.xml'), sitemap, 'utf8')
await writeFile(path.join(target, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /inquiry/\nSitemap: ${siteUrl}/sitemap.xml\n`, 'utf8')
await publishCurrent()
process.stdout.write(`预渲染完成：${routes.length} 个页面，版本 ${version}\n`)
