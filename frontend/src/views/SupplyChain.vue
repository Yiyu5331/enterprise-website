<template>
  <div class="supply-page">
    <div class="page-banner supply-banner">
      <h1>供应链管理</h1>
      <p>从材料、部件到全球交付，建立稳定、透明、可追溯的供应网络</p>
    </div>

    <section class="section visual-edge-section edge-right" style="--edge-image: url('/images/editorial/supplier-procurement.webp')">
      <div class="container supply-overview">
        <div class="overview-copy">
          <SectionHeading icon="shield" eyebrow="SUPPLY CHAIN" title="品质从源头开始" />
          <p>华丽电器建立供应商准入、样品验证、批次检验和持续评价机制。采购团队围绕材料一致性、关键尺寸、环境合规和供货能力，对供应商开展全过程管理。</p>
          <p>合作网络覆盖电机、传动、金属结构、工程塑料、电子元件和包装材料等核心环节，并通过 ERP 记录物料、批次和订单流转信息。</p>
          <div class="overview-index">
            <span><strong>300+</strong>合作供应商</span>
            <span><strong>98.5%</strong>来料合格率</span>
            <span><strong>ERP</strong>批次追溯</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-gray process-section">
      <div class="container">
        <SectionHeading icon="route" eyebrow="SUPPLIER PROCESS" title="供应商采购流程" subtitle="明确每一步输入、评估标准和合作结果" />
        <div class="process-board">
          <div class="process-image"><img src="/images/editorial/supplier-procurement.webp" alt="供应商零部件审核" loading="lazy" /></div>
          <ol class="process-list">
            <li v-for="(item, index) in process" :key="item.title">
              <span class="process-no">0{{ index + 1 }}</span>
              <div><h3>{{ item.title }}</h3><p>{{ item.desc }}</p></div>
            </li>
          </ol>
        </div>
      </div>
    </section>

    <section class="section categories-section visual-edge-section edge-left" style="--edge-image: url('/images/editorial/procurement-categories.webp')">
      <div class="container">
        <SectionHeading icon="layers" eyebrow="PROCUREMENT CATEGORIES" title="核心采购品类" subtitle="展示采购对象本身：原料、零部件和对应生产环节" />
        <div class="category-ledger">
          <article v-for="item in categories" :key="item.name" class="category-row">
            <div class="category-thumb"><img :src="item.image" :alt="item.name" loading="lazy" /></div>
            <div class="category-name"><span>{{ item.code }}</span><h3>{{ item.name }}</h3></div>
            <p>{{ item.desc }}</p>
            <div class="category-tags"><span v-for="tag in item.tags" :key="tag">{{ tag }}</span></div>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-dark visual-edge-section edge-right dark-edge" style="--edge-image: url('/images/company/quality-lab.webp')">
      <div class="container quality-content">
        <SectionHeading icon="check" eyebrow="QUALITY CONTROL" title="质量保障体系" subtitle="从来料到出货形成闭环质量控制" light />
        <div class="quality-list">
          <article v-for="item in quality" :key="item.title"><span>{{ item.code }}</span><h3>{{ item.title }}</h3><p>{{ item.desc }}</p></article>
        </div>
      </div>
    </section>

    <section class="supply-cta">
      <div class="container"><div><span>SUPPLIER PARTNERSHIP</span><h2>成为华丽电器的供应商</h2><p>欢迎具备稳定品质、持续交付能力和合规体系的企业提交合作信息。</p></div><router-link to="/contact" class="btn btn-primary btn-lg">提交合作申请</router-link></div>
    </section>
  </div>
</template>

<script setup>
import SectionHeading from '@/components/SectionHeading.vue'

const process = [
  { title: '提交合作资料', desc: '提供企业资质、生产设备、质量体系、产品范围和主要客户信息。' },
  { title: '能力与合规审核', desc: '评估产能、关键工序、质量控制、环保与社会责任合规。' },
  { title: '样品与小批验证', desc: '完成尺寸、性能、可靠性测试，并验证小批量交付稳定性。' },
  { title: '批量供货与评价', desc: '纳入合格名录，按质量、交期、服务和改善能力持续评价。' },
]

const categories = [
  { code: '01', name: '电机与电子', image: '/images/editorial/motors-electronics.webp', desc: '动力与控制系统核心物料，重点关注效率、温升、绝缘与批次一致性。', tags: ['串激电机', '无刷电机', 'PCB', '开关'] },
  { code: '02', name: '传动部件', image: '/images/editorial/procurement-categories.webp', desc: '影响扭矩传递、噪声与寿命的精密机械部件。', tags: ['齿轮箱', '轴承', '传动轴', '离合器'] },
  { code: '03', name: '金属材料', image: '/images/editorial/procurement-categories.webp', desc: '覆盖压铸、冲压和机加工结构件，控制材料牌号与关键尺寸。', tags: ['铝压铸', '锌合金', '冲压件', '紧固件'] },
  { code: '04', name: '塑料与橡胶', image: '/images/editorial/procurement-categories.webp', desc: '用于机身、握持与缓冲结构，关注阻燃、强度和耐老化性能。', tags: ['工程塑料', '注塑件', '橡胶握把', '密封件'] },
  { code: '05', name: '包装材料', image: '/images/company/warehouse-logistics.webp', desc: '保护产品在仓储和国际运输中的完整性，并适配客户包装规范。', tags: ['彩盒', '纸箱', '内衬', '说明书'] },
  { code: '06', name: '辅助材料', image: '/images/company/quality-lab.webp', desc: '用于装配、散热、润滑和电气连接的工艺材料。', tags: ['润滑脂', '导热材料', '胶粘剂', '漆包线'] },
]

const quality = [
  { code: 'IQC', title: '来料检验', desc: '按风险等级与 AQL 规则执行抽检，关键安全件实施强化检验。' },
  { code: 'IPQC', title: '过程控制', desc: '首件确认、巡回检验和关键参数记录共同控制生产波动。' },
  { code: 'OQC', title: '出货检验', desc: '核查性能、安全、外观、包装和订单要求后方可放行。' },
  { code: 'LAB', title: '可靠性验证', desc: '覆盖温升、寿命、振动、跌落、环境循环等验证项目。' },
]
</script>

<style scoped>
.supply-banner { background-position: center 52%; }
.supply-overview { min-height: 470px; display: flex; align-items: center; }
.overview-copy { max-width: 680px; }
.overview-copy > p { color: var(--text-light); line-height: 2; margin-top: 14px; }
.overview-index { display: flex; gap: 34px; margin-top: 34px; padding-top: 24px; border-top: 1px solid var(--gray-200); }
.overview-index span { color: var(--gray-600); font-size: 12px; }
.overview-index strong { display: block; color: var(--text); font-size: 25px; line-height: 1.2; margin-bottom: 5px; }
.process-board { display: grid; grid-template-columns: .9fr 1.1fr; min-height: 520px; margin-top: 38px; background: var(--white); border: 1px solid var(--gray-200); }
.process-image { overflow: hidden; }
.process-image img { width: 100%; height: 100%; object-fit: cover; }
.process-list { display: flex; flex-direction: column; justify-content: center; padding: 24px 44px; }
.process-list li { display: grid; grid-template-columns: 48px 1fr; gap: 18px; padding: 23px 0; border-bottom: 1px solid var(--gray-200); }
.process-list li:last-child { border-bottom: 0; }
.process-no { color: var(--brand); font: 700 13px/1.5 ui-monospace, monospace; }
.process-list h3 { font-size: 17px; margin-bottom: 5px; }
.process-list p { color: var(--gray-600); font-size: 13px; line-height: 1.75; }
.categories-section .container { max-width: 1080px; }
.category-ledger { margin-top: 38px; border-top: 1px solid var(--gray-300); }
.category-row { display: grid; grid-template-columns: 150px 150px minmax(220px, 1fr) 230px; gap: 24px; align-items: center; padding: 20px 0; border-bottom: 1px solid var(--gray-200); }
.category-thumb { width: 150px; aspect-ratio: 4 / 3; overflow: hidden; background: var(--gray-100); }
.category-thumb img { width: 100%; height: 100%; object-fit: cover; transition: transform .35s; }
.category-row:hover .category-thumb img { transform: scale(1.035); }
.category-name span { color: var(--brand); font: 700 11px ui-monospace, monospace; }
.category-name h3 { font-size: 17px; margin-top: 5px; }
.category-row > p { color: var(--gray-600); font-size: 13px; line-height: 1.75; }
.category-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.category-tags span { padding: 4px 8px; background: var(--gray-100); color: var(--gray-600); font-size: 11px; }
.quality-content { max-width: 900px; margin-left: max(24px, calc((100% - 1200px) / 2)); }
.quality-list { display: grid; grid-template-columns: repeat(2, 1fr); margin-top: 38px; border-top: 1px solid rgba(255,255,255,.18); }
.quality-list article { padding: 28px 30px 28px 0; border-bottom: 1px solid rgba(255,255,255,.12); }
.quality-list article:nth-child(odd) { border-right: 1px solid rgba(255,255,255,.12); }
.quality-list article:nth-child(even) { padding-left: 30px; }
.quality-list span { color: #ff7b7b; font: 700 11px ui-monospace, monospace; }
.quality-list h3 { font-size: 17px; margin: 8px 0; }
.quality-list p { color: var(--gray-400); font-size: 13px; line-height: 1.75; }
.supply-cta { padding: 66px 0; background: #f0f1f2; }
.supply-cta .container { display: flex; justify-content: space-between; align-items: center; gap: 40px; }
.supply-cta span { color: var(--brand); font-size: 11px; font-weight: 700; letter-spacing: 1.5px; }
.supply-cta h2 { font-size: 29px; margin: 7px 0; }
.supply-cta p { color: var(--gray-600); }
@media (max-width: 900px) {
  .process-board { grid-template-columns: 1fr; }
  .process-image { height: 330px; }
  .category-row { grid-template-columns: 120px 130px 1fr; }
  .category-thumb { width: 120px; }
  .category-tags { grid-column: 2 / -1; }
}
@media (max-width: 768px) {
  .supply-overview { min-height: auto; }
  .overview-index { gap: 18px; overflow-x: auto; }
  .overview-index span { min-width: 105px; }
  .process-list { padding: 16px 22px; }
  .category-row { grid-template-columns: 96px 1fr; gap: 16px; }
  .category-thumb { width: 96px; }
  .category-row > p, .category-tags { grid-column: 1 / -1; }
  .quality-list { grid-template-columns: 1fr; }
  .quality-list article, .quality-list article:nth-child(even) { padding: 24px 0; border-right: 0; }
  .supply-cta .container { align-items: flex-start; flex-direction: column; }
}
</style>
