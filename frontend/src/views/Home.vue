<template>
  <div class="home">
    <!-- ===== HERO 区域 ===== -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="container hero-body">
        <div class="hero-text">
          <span class="hero-tag">国家高新技术企业 · 国家级 5G 工厂</span>
          <h1 class="hero-title">华丽电器<br><span class="hero-sub">驱动全球工业</span></h1>
          <p class="hero-desc">
            20 年专注电动工具研发制造 | 6 大产品系列 50+ 型号<br>
            年产能 500 万台 · 出口 80+ 国家和地区
          </p>
          <div class="hero-actions">
            <router-link to="/products" class="btn btn-primary btn-lg">探索产品系列</router-link>
            <router-link to="/contact" class="btn btn-outline btn-lg">联系我们</router-link>
          </div>
          <div class="hero-badges">
            <span>CE 认证</span><span>UL 认证</span><span>GS 认证</span>
            <span>ISO 9001</span><span>RoHS</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 核心数据 ===== -->
    <section class="stats-bar">
      <div class="container">
        <div class="stats-grid">
          <div class="stat" v-for="s in stats" :key="s.label">
            <span class="stat-num">{{ s.num }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 产品速览 ===== -->
    <section class="section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">产品中心</h2>
          <p class="section-subtitle">全品类电动工具 — 从家用、专业到工业级全覆盖</p>
        </div>
        <div v-if="homeState.loading" class="module-state">产品数据加载中...</div>
        <div v-else-if="homeState.error" class="module-state error">
          {{ homeState.error }} <button type="button" @click="loadHome">重试</button>
        </div>
        <div v-else class="product-showcase">
          <router-link :to="`/products/${p.category_slug}/${p.model}/`" class="product-showcase-card" v-for="(p,i) in featuredProducts" :key="p.model" :style="{ animationDelay: i*0.1+'s' }">
            <div class="psc-visual">
              <img :src="p.image" :alt="p.name" loading="lazy" />
            </div>
            <div class="psc-info">
              <span class="psc-tag">{{ p.homepage_badge || p.level }}</span>
              <h3>{{ p.name }}</h3>
              <p>{{ p.summary }}</p>
              <span class="psc-link">查看产品详情 →</span>
            </div>
          </router-link>
        </div>
        <div class="section-footer">
          <router-link to="/products" class="btn btn-primary">查看全部产品及规格</router-link>
        </div>
      </div>
    </section>

    <!-- ===== 关于我们 ===== -->
    <section class="section section-gray">
      <div class="container">
        <div class="about-teaser">
          <div class="about-teaser-text">
            <span class="section-label">ABOUT US</span>
            <h2 class="section-title">关于华丽电器</h2>
            <p class="about-teaser-desc">
              华丽电器制造有限公司成立于 2003 年，坐落于浙江省武义县，占地 8 万平方米。公司于 2019 年由 "武义华丽电器制造有限公司" 更名。
              主营电锤、电镐、电钻、型材切割机等专业电动工具及配件，拥有自营进出口权，产品远销欧洲、北美、东南亚等 80 多个国家和地区。
            </p>
            <div class="about-teaser-features">
              <div v-for="f in features" :key="f" class="atf-item">{{ f }}</div>
            </div>
            <router-link to="/about" class="btn btn-primary">了解更多 →</router-link>
          </div>
          <div class="about-teaser-image">
            <img src="/images/company/factory-exterior.webp" alt="华丽电器现代化生产基地" loading="lazy" />
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 智造现场 ===== -->
    <section class="section manufacturing-section">
      <div class="container">
        <div class="section-header">
          <span class="section-label">SMART MANUFACTURING</span>
          <h2 class="section-title">走进华丽智造</h2>
          <p class="section-subtitle mx-auto">从研发验证到自动化装配，每个环节都服务于稳定品质</p>
        </div>
        <div class="manufacturing-grid">
          <router-link v-for="scene in manufacturingScenes" :key="scene.title" :to="scene.to" class="manufacturing-item">
            <img :src="scene.image" :alt="scene.title" loading="lazy" />
            <div><span>{{ scene.label }}</span><h3>{{ scene.title }}</h3><p>{{ scene.desc }}</p></div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ===== 新闻动态 ===== -->
    <section class="section section-gray">
      <div class="container">
        <div class="news-heading">
          <div><span class="section-label">LATEST NEWS</span><h2 class="section-title">新闻动态</h2></div>
          <router-link to="/news" class="home-text-link">查看全部新闻 →</router-link>
        </div>
        <div v-if="homeState.loading" class="module-state">新闻数据加载中...</div>
        <div v-else-if="homeState.error" class="module-state error">
          {{ homeState.error }} <button type="button" @click="loadHome">重试</button>
        </div>
        <div v-else class="home-news-grid">
          <router-link v-for="article in latestNews" :key="article.slug" :to="`/news/${article.category_slug}/${article.slug}/`" class="home-news-card">
            <img :src="article.image" :alt="article.title" loading="lazy" />
            <div><span>{{ article.category }} · {{ article.date }}</span><h3>{{ article.title }}</h3><p>{{ article.summary }}</p></div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ===== 荣誉资质 ===== -->
    <section class="section honors-section">
      <div class="container text-center">
        <span class="section-label">CERTIFICATIONS</span>
        <h2 class="section-title">荣誉资质</h2>
        <p class="section-subtitle mx-auto">品质认证，匠心传承</p>
        <div class="honors-grid">
          <div class="honor-card" v-for="h in honors" :key="h">
            <div class="honor-icon">
              <svg viewBox="0 0 48 48" width="36" height="36"><path d="M24 4L28 18H42L30 26L34 42L24 32L14 42L18 26L6 18H20Z" fill="var(--brand)" opacity=".15"/><path d="M24 4L28 18H42L30 26L34 42L24 32L14 42L18 26L6 18H20Z" fill="none" stroke="var(--brand)" stroke-width="1.5"/></svg>
            </div>
            <span>{{ h }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 实力数据 ===== -->
    <section class="section-dark capabilities">
      <div class="container text-center">
        <h2 class="section-title">制造实力</h2>
        <p class="section-subtitle mx-auto">智能化、数字化、全球化的生产体系</p>
        <div class="caps-grid">
          <div class="cap-item" v-for="c in caps" :key="c.title">
            <div class="cap-icon" v-html="getCapIcon(c.icon)"></div>
            <h4>{{ c.title }}</h4>
            <p>{{ c.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== CTA ===== -->
    <section class="cta-section">
      <div class="container text-center">
        <h2>立即获取产品报价</h2>
        <p>提交您的需求，专业工程师 24 小时内为您提供定制方案</p>
        <router-link to="/inquiry" class="btn btn-primary btn-lg">提交询盘</router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { fetchHomepage } from '@/api/content'
import { setPageMeta } from '@/api/client'
import { useAsyncState } from '@/composables/useAsyncState'
import { icons } from '@/utils/icons'

const stats = [
  { num: '2003', label: '成立年份' },
  { num: '6000万', label: '注册资本' },
  { num: '500万+', label: '年产能(台)' },
  { num: '80+', label: '出口国家' },
  { num: '200+', label: '专利技术' },
  { num: '500+', label: '注册商标' },
]
const { state: homeState, run: loadHome } = useAsyncState((signal) => fetchHomepage(signal), '首页内容加载失败。')
const featuredProducts = computed(() => homeState.data?.products || [])
const latestNews = computed(() => homeState.data?.news || [])
const manufacturingScenes = [
  { label: 'PRODUCTION', title: '自动化装配线', desc: '关键工序数字化协同，提升生产效率与一致性。', image: '/images/company/assembly-line.webp', to: '/about' },
  { label: 'INNOVATION', title: '研发与工程验证', desc: '围绕动力、结构、人机工程持续开展产品开发。', image: '/images/company/rd-lab.webp', to: '/about' },
  { label: 'QUALITY', title: '可靠性实验室', desc: '覆盖性能、安全、温升与耐久等多项测试。', image: '/images/company/quality-lab.webp', to: '/supply-chain' },
]
const features = ['国家高新技术企业', '浙江省专精特新', '国家级 5G 工厂', '自营进出口权', 'ISO 9001 认证', 'CE/UL/GS 认证']
const honors = ['国家高新技术企业', '浙江省专精特新', '国家级 5G 工厂', '浙江省智能工厂', '企业技术中心', '工业设计中心', '纳税千万元以上企业', '税务信用等级 A 级']
const caps = [
  { icon: '🏭', title: '智能工厂', desc: '国家级 5G 工厂，全流程数字化生产管理' },
  { icon: '🔬', title: '研发中心', desc: '省级企业技术中心，120+ 研发技术人员' },
  { icon: '⚙️', title: '精密制造', desc: 'CNC 加工中心、自动化装配线、智能检测' },
  { icon: '📊', title: '质量体系', desc: 'ISO 9001，全流程来料检测、过程控制、成品检验' },
]
function getCapIcon(icon) {
  const map = { '🏭': 'factory', '🔬': 'lab', '⚙️': 'gear', '📊': 'chart' }
  return icons[map[icon]] || icon
}

onMounted(() => {
  setPageMeta({
    title: '华丽电器制造有限公司 - 专业电动工具制造商',
    description: '华丽电器制造有限公司提供电钻、电锤、角磨机、型材切割机等电动工具制造与全球贸易服务。',
  })
  loadHome()
})

</script>

<style scoped>
/* --- Hero --- */
.hero {
  position: relative; min-height: 90vh; display: flex; align-items: center;
  margin-top: calc(var(--header-h) + 32px); overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0;
  background: linear-gradient(90deg, rgba(14,14,14,.94) 0%, rgba(18,18,18,.82) 42%, rgba(18,18,18,.22) 100%), url('/images/company/home-hero.webp') center / cover no-repeat;
}
.hero-bg::before {
  content: ''; position: absolute; inset: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(196,30,36,.12) 0%, transparent 50%),
    radial-gradient(circle at 80% 30%, rgba(196,30,36,.08) 0%, transparent 40%),
    repeating-linear-gradient(45deg, transparent, transparent 40px, rgba(255,255,255,.015) 40px, rgba(255,255,255,.015) 41px);
}
.hero-body { position: relative; z-index: 1; padding: 80px 0; }
.hero-tag {
  display: inline-block; padding: 5px 16px;
  background: rgba(196,30,36,.2); color: var(--brand-hover);
  border: 1px solid rgba(196,30,36,.3); border-radius: 2px;
  font-size: 12px; letter-spacing: 1px; margin-bottom: 24px;
}
.hero-title {
  font-size: 56px; font-weight: 900; color: var(--white);
  line-height: 1.1; margin-bottom: 8px; letter-spacing: -1.5px;
}
.hero-sub {
  display: block; font-size: 48px; font-weight: 300; color: var(--brand);
  letter-spacing: 4px;
}
.hero-desc { font-size: 16px; color: var(--gray-400); margin: 20px 0 32px; line-height: 1.8; }
.hero-actions { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }
.hero-badges { display: flex; gap: 12px; flex-wrap: wrap; }
.hero-badges span {
  padding: 3px 12px; font-size: 11px; font-weight: 600;
  background: rgba(255,255,255,.06); color: var(--gray-400);
  border: 1px solid rgba(255,255,255,.1); border-radius: 2px;
}

/* --- Stats --- */
.stats-bar {
  background: var(--white); border-bottom: 1px solid var(--gray-200);
  position: relative; z-index: 2;
}
.stats-grid { display: grid; grid-template-columns: repeat(6,1fr); }
.stat { text-align: center; padding: 28px 8px; border-right: 1px solid var(--gray-200); }
.stat:last-child { border-right: none; }
.stat-num { display: block; font-size: 30px; font-weight: 800; color: var(--brand); margin-bottom: 4px; }
.stat-label { font-size: 13px; color: var(--gray-600); }

/* --- Products --- */
.section-header { text-align: center; margin-bottom: 48px; }
.product-showcase { display: grid; grid-template-columns: repeat(3,1fr); gap: 24px; }
.product-showcase-card {
  background: var(--white); border-radius: var(--radius-lg);
  box-shadow: var(--shadow); overflow: hidden; animation: fadeUp .5s ease-out both;
  transition: transform .3s, box-shadow .3s;
}
.product-showcase-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-lg); }
.psc-visual {
  aspect-ratio: 3 / 2; overflow: hidden; background: #eee;
}
.psc-visual img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s; }
.product-showcase-card:hover .psc-visual img { transform: scale(1.04); }
.psc-info { padding: 20px 24px 24px; }
.psc-tag {
  display: inline-block; padding: 2px 10px; font-size: 11px; font-weight: 600;
  background: var(--brand-light); color: var(--brand); border-radius: 2px; margin-bottom: 10px;
}
.psc-info h3 { font-size: 18px; margin-bottom: 6px; }
.psc-info p { font-size: 13px; color: var(--gray-600); line-height: 1.6; }
.psc-link {
  display: inline-block; margin-top: 12px; font-size: 13px; font-weight: 600;
  color: var(--brand); transition: gap .3s;
}
.psc-link:hover { gap: 6px; }
.section-footer { text-align: center; margin-top: 40px; }
.module-state {
  padding: 28px;
  text-align: center;
  background: var(--gray-100);
  color: var(--gray-600);
  border: 1px solid var(--gray-200);
}
.module-state.error { color: #B42318; background: #FFF5F5; }
.module-state button {
  margin-left: 10px;
  border: 0;
  background: transparent;
  color: var(--brand);
  font-weight: 700;
  cursor: pointer;
}

/* --- About Teaser --- */
.about-teaser { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; }
.section-label {
  display: block; font-size: 12px; font-weight: 700; color: var(--brand);
  letter-spacing: 3px; margin-bottom: 12px;
}
.about-teaser-desc { font-size: 15px; color: var(--text-light); line-height: 2; margin-bottom: 24px; }
.about-teaser-features { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 28px; }
.atf-item {
  font-size: 13px; color: var(--text); padding: 6px 0;
  display: flex; align-items: center; gap: 8px;
}
.atf-item::before { content: '✓'; color: var(--brand); font-weight: 700; }
.ati-placeholder {
  border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-lg);
}
.about-teaser-image { overflow: hidden; box-shadow: var(--shadow-lg); }
.about-teaser-image img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }

/* --- Manufacturing / News --- */
.manufacturing-section { background: var(--white); }
.manufacturing-grid { display: grid; grid-template-columns: 1.25fr 1fr 1fr; gap: 18px; }
.manufacturing-item { position: relative; min-height: 420px; overflow: hidden; color: var(--white); }
.manufacturing-item img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .45s; }
.manufacturing-item::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,.86), rgba(0,0,0,.05) 62%); }
.manufacturing-item > div { position: absolute; z-index: 1; left: 24px; right: 24px; bottom: 24px; }
.manufacturing-item span { color: #ff6b6b; font-size: 11px; font-weight: 700; letter-spacing: 2px; }
.manufacturing-item h3 { font-size: 20px; margin: 6px 0; }
.manufacturing-item p { color: rgba(255,255,255,.72); font-size: 13px; line-height: 1.7; }
.manufacturing-item:hover img { transform: scale(1.035); }
.news-heading { display: flex; align-items: end; justify-content: space-between; margin-bottom: 30px; }
.news-heading .section-title { text-align: left; }
.news-heading .section-title::after { margin-left: 0; }
.home-text-link { color: var(--brand); font-size: 14px; font-weight: 600; }
.home-news-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.home-news-card { background: var(--white); box-shadow: var(--shadow-sm); transition: .3s; }
.home-news-card:hover { transform: translateY(-4px); box-shadow: var(--shadow); }
.home-news-card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
.home-news-card > div { padding: 20px; }
.home-news-card span { color: var(--brand); font-size: 11px; }
.home-news-card h3 { font-size: 17px; line-height: 1.55; margin: 7px 0; }
.home-news-card p { color: var(--gray-600); font-size: 13px; line-height: 1.7; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* --- Honors --- */
.honors-section { background: var(--gray-100); }
.honors-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; max-width: 800px; margin: 0 auto; }
.honor-card {
  background: var(--white); border-radius: var(--radius); padding: 24px 16px;
  text-align: center; box-shadow: var(--shadow-sm); font-size: 13px; font-weight: 600;
  transition: all .3s;
}
.honor-card:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
.honor-icon { margin-bottom: 10px; }

/* --- Capabilities --- */
.capabilities { padding: 80px 0; }
.caps-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 24px; margin-top: 48px; }
.cap-item { text-align: center; padding: 32px 16px; }
.cap-icon { font-size: 40px; margin-bottom: 16px; }
.cap-item h4 { font-size: 17px; color: var(--white); margin-bottom: 10px; }
.cap-item p { font-size: 13px; color: var(--gray-400); line-height: 1.7; }

/* --- CTA --- */
.cta-section {
  background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
  color: var(--white); padding: 80px 0;
}
.cta-section h2 { font-size: 36px; font-weight: 800; margin-bottom: 12px; }
.cta-section p { font-size: 16px; opacity: .85; margin-bottom: 32px; }

/* --- Responsive --- */
@media (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(3,1fr); }
  .product-showcase { grid-template-columns: repeat(2,1fr); }
  .manufacturing-grid { grid-template-columns: repeat(2, 1fr); }
  .manufacturing-item:first-child { grid-column: 1 / -1; }
  .home-news-grid { grid-template-columns: repeat(2, 1fr); }
  .caps-grid { grid-template-columns: repeat(2,1fr); }
  .honors-grid { grid-template-columns: repeat(2,1fr); }
}
@media (max-width: 768px) {
  .hero { min-height: 70vh; margin-top: var(--header-h); }
  .hero-title { font-size: 36px; }
  .hero-sub { font-size: 30px; }
  .stats-grid { grid-template-columns: repeat(3,1fr); }
  .stat { padding: 20px 8px; }
  .stat:nth-child(3) { border-right: none; }
  .stat:nth-child(4), .stat:nth-child(5), .stat:nth-child(6) { border-top: 1px solid var(--gray-200); }
  .product-showcase { grid-template-columns: 1fr; }
  .about-teaser { grid-template-columns: 1fr; gap: 32px; }
  .manufacturing-grid, .home-news-grid { grid-template-columns: 1fr; }
  .manufacturing-item:first-child { grid-column: auto; }
  .manufacturing-item { min-height: 360px; }
  .news-heading { align-items: start; flex-direction: column; gap: 12px; }
  .caps-grid { grid-template-columns: 1fr; }
  .cta-section h2 { font-size: 26px; }
  .honors-grid { grid-template-columns: repeat(2,1fr); }
}
</style>
