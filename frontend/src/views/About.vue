<template>
  <div class="about-page">
    <div class="page-banner">
      <h1>关于华丽电器</h1>
      <p>始于 2003 · 匠心传承 · 智造未来</p>
    </div>

    <!-- 公司简介 -->
    <section class="section">
      <div class="container">
        <div class="intro-grid">
          <div class="intro-text">
            <span class="section-label">COMPANY PROFILE</span>
            <h2 class="section-title">引领电动工具行业 20 年</h2>
            <p>华丽电器制造有限公司（原武义华丽电器制造有限公司）成立于 2003 年 3 月，坐落于浙江省金华市武义县泉溪镇王元工业区，注册资本 6000 万元。公司总占地面积 8 万平方米，是一家集研发、生产、销售于一体的国家高新技术企业。</p>
            <p>2019 年，公司由"武义华丽电器制造有限公司"正式更名为"华丽电器制造有限公司"，标志着企业从区域品牌向全球化品牌的战略升级。</p>
            <p>公司主营电锤、电镐、电钻、型材切割机等专业电动工具及配件，同时涵盖风动工具、金属工具、园林工具的制造与销售。年产能达 500 万台以上，拥有自营进出口权和技术进出口资质，产品远销欧洲、北美、东南亚、中东、非洲等 80 多个国家和地区。</p>
            <img src="/images/company/factory-exterior.webp" alt="华丽电器生产基地" class="intro-image" />
          </div>
          <div class="intro-stats">
            <div class="intro-stat" v-for="s in introStats" :key="s.label">
              <span class="intro-stat-num">{{ s.num }}</span>
              <span class="intro-stat-label">{{ s.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 制造能力 -->
    <section class="section capability-gallery">
      <div class="container text-center">
        <span class="section-label">MANUFACTURING</span>
        <h2 class="section-title">研发与制造能力</h2>
        <p class="section-subtitle mx-auto">以工程研发、智能生产和严格验证支撑全球交付</p>
        <div class="gallery-grid">
          <figure v-for="item in capabilityGallery" :key="item.title">
            <img :src="item.image" :alt="item.title" loading="lazy" />
            <figcaption><h3>{{ item.title }}</h3><p>{{ item.desc }}</p></figcaption>
          </figure>
        </div>
      </div>
    </section>

    <!-- 发展历程 -->
    <section class="section section-gray">
      <div class="container text-center">
        <span class="section-label">MILESTONES</span>
        <h2 class="section-title">发展历程</h2>
        <p class="section-subtitle mx-auto">从创立到行业标杆，每一步都是实力积淀</p>
        <div class="timeline-wrap">
          <aside class="timeline-visual">
            <img src="/images/editorial/company-milestones.webp" alt="华丽电器产品与技术发展历程" loading="lazy" />
            <p>从产品研发到智能制造，持续推进制造能力升级。</p>
          </aside>
          <div class="timeline">
          <div class="tl-item" v-for="(m,i) in milestones" :key="m.year">
            <div class="tl-dot"></div>
            <div class="tl-year">{{ m.year }}</div>
            <div class="tl-content">
              <h4>{{ m.title }}</h4>
              <p>{{ m.desc }}</p>
            </div>
          </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 荣誉墙 -->
    <section class="section">
      <div class="container text-center">
        <span class="section-label">CERTIFICATIONS</span>
        <h2 class="section-title">荣誉资质</h2>
        <div class="honors-layout">
          <div class="honors-visual">
            <img src="/images/editorial/honors-certifications.webp" alt="华丽电器荣誉证书与产品展示" loading="lazy" />
            <div><span>QUALITY & RECOGNITION</span><p>以制造能力与品质体系，获得长期市场认可。</p></div>
          </div>
          <div class="certs-grid">
          <div class="cert-card" v-for="c in certs" :key="c">
            <div class="cert-icon">
              <svg viewBox="0 0 60 60" width="40" height="40"><rect width="60" height="60" rx="6" fill="var(--brand)" opacity=".08"/><path d="M30 10 L34 24 L48 24 L36 32 L40 48 L30 38 L20 48 L24 32 L12 24 L26 24Z" fill="none" stroke="var(--brand)" stroke-width="1.8"/></svg>
            </div>
            <span>{{ c }}</span>
          </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const introStats = [
  { num: '2003', label: '成立年份' },
  { num: '6000万', label: '注册资本' },
  { num: '80000㎡', label: '生产基地' },
  { num: '800+', label: '在职员工' },
  { num: '120+', label: '研发人员' },
  { num: '80+', label: '出口国家' },
]
const milestones = [
  { year: '2003', title: '公司成立', desc: '武义华丽电器制造有限公司正式成立，落户浙江武义' },
  { year: '2008', title: 'ISO 认证', desc: '首次通过 ISO 9001 质量管理体系认证，建立标准化生产流程' },
  { year: '2012', title: '进军国际', desc: '获得自营进出口权，首批产品出口欧洲市场' },
  { year: '2015', title: '高新技术企业', desc: '获评国家高新技术企业，研发投入持续加大' },
  { year: '2019', title: '品牌升级', desc: '更名为华丽电器制造有限公司，开启全球化品牌战略' },
  { year: '2021', title: '智能工厂', desc: '建成浙江省智能工厂，引入全自动化装配线' },
  { year: '2023', title: '专精特新', desc: '获浙江省专精特新中小企业认定' },
  { year: '2025', title: '5G 工厂', desc: '入选国家级 5G 工厂，数字化制造达到行业领先水平' },
]
const certs = ['国家高新技术企业', '浙江省专精特新中小企业', '国家级 5G 工厂', '浙江省智能工厂', '浙江省企业技术中心', '浙江省工业设计中心', 'ISO 9001 认证', 'CE 产品认证', 'UL 产品认证', 'GS 产品认证']
const capabilityGallery = [
  { title: '自动化装配', desc: '关键工序数字化管理，支持多型号柔性生产。', image: '/images/company/assembly-line.webp' },
  { title: '研发实验室', desc: '开展动力系统、结构设计和人机工程验证。', image: '/images/company/rd-lab.webp' },
  { title: '可靠性检测', desc: '覆盖性能、安全、温升、跌落与寿命测试。', image: '/images/company/quality-lab.webp' },
]
</script>

<style scoped>
.intro-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 60px; align-items: center; }
.intro-text .section-label { display: block; font-size: 12px; font-weight: 700; color: var(--brand); letter-spacing: 3px; margin-bottom: 12px; }
.intro-text p { font-size: 15px; color: var(--text-light); line-height: 2; margin-bottom: 14px; }
.intro-image { width: 100%; aspect-ratio: 16 / 8; object-fit: cover; margin-top: 24px; }
.intro-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.intro-stat {
  text-align: center; padding: 24px 12px; background: var(--gray-100);
  border-radius: var(--radius-lg); border-left: 3px solid var(--brand);
}
.intro-stat-num { display: block; font-size: 28px; font-weight: 800; color: var(--brand); }
.intro-stat-label { font-size: 13px; color: var(--gray-600); }

/* Timeline */
.timeline-wrap { display: grid; grid-template-columns: minmax(230px, .55fr) minmax(0, 1fr); gap: 54px; max-width: 1040px; margin: 48px auto 0; align-items: stretch; text-align: left; }
.timeline-visual { min-height: 100%; position: relative; overflow: hidden; color: var(--white); }
.timeline-visual img { width: 100%; height: 100%; min-height: 450px; object-fit: cover; }
.timeline-visual::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,.88), rgba(0,0,0,.04) 70%); }
.timeline-visual p { position: absolute; z-index: 1; bottom: 22px; left: 22px; right: 22px; color: rgba(255,255,255,.82); font-size: 13px; line-height: 1.8; }
.timeline { position: relative; padding-left: 40px; }
.timeline::before {
  content: ''; position: absolute; left: 15px; top: 0; bottom: 0;
  width: 2px; background: linear-gradient(to bottom, var(--brand), var(--brand-hover));
}
.tl-item { position: relative; padding-bottom: 36px; text-align: left; }
.tl-item:last-child { padding-bottom: 0; }
.tl-dot {
  position: absolute; left: -33px; top: 6px; width: 12px; height: 12px;
  background: var(--brand); border-radius: 50%; border: 3px solid var(--white);
  box-shadow: 0 0 0 2px var(--brand);
}
.tl-year { font-size: 14px; font-weight: 700; color: var(--brand); margin-bottom: 4px; }
.tl-content h4 { font-size: 16px; color: var(--text); margin-bottom: 4px; }
.tl-content p { font-size: 13px; color: var(--gray-600); line-height: 1.6; }

/* Certs */
.honors-layout { display: grid; grid-template-columns: .7fr 1.3fr; gap: 28px; margin-top: 40px; text-align: left; }
.honors-visual { min-height: 100%; position: relative; overflow: hidden; color: var(--white); }
.honors-visual img { width: 100%; height: 100%; min-height: 330px; object-fit: cover; }
.honors-visual::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,.86), rgba(0,0,0,.06) 72%); }
.honors-visual div { position: absolute; z-index: 1; left: 22px; right: 22px; bottom: 22px; }
.honors-visual span { display: block; color: #ff8a8a; font-size: 11px; font-weight: 700; letter-spacing: 1.6px; }
.honors-visual p { color: rgba(255,255,255,.78); font-size: 13px; margin-top: 7px; line-height: 1.7; }
.certs-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
.cert-card {
  padding: 28px 12px; border-radius: var(--radius); background: var(--white);
  box-shadow: var(--shadow-sm); text-align: center; transition: all .3s;
}
.cert-card:hover { transform: translateY(-4px); box-shadow: var(--shadow); }
.cert-icon { margin-bottom: 12px; }
.cert-card span { font-size: 13px; font-weight: 600; }
.capability-gallery { background: var(--dark); color: var(--white); }
.capability-gallery .section-title { color: var(--white); }
.gallery-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 40px; text-align: left; }
.gallery-grid figure { position: relative; min-height: 380px; overflow: hidden; }
.gallery-grid img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.gallery-grid figure::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,.88), transparent 68%); }
.gallery-grid figcaption { position: absolute; z-index: 1; left: 22px; right: 22px; bottom: 22px; }
.gallery-grid h3 { font-size: 18px; margin-bottom: 5px; }
.gallery-grid p { color: var(--gray-400); font-size: 13px; line-height: 1.7; }
@media (max-width: 768px) {
  .intro-grid { grid-template-columns: 1fr; gap: 32px; }
  .timeline-wrap, .honors-layout { grid-template-columns: 1fr; gap: 26px; }
  .timeline-visual img, .honors-visual img { min-height: 250px; max-height: 310px; }
  .certs-grid { grid-template-columns: repeat(2,1fr); }
  .gallery-grid { grid-template-columns: 1fr; }
  .gallery-grid figure { min-height: 340px; }
}
</style>
