<template>
  <div class="dealer-page">
    <div class="page-banner dealer-banner">
      <h1>经销商合作</h1>
      <p>建立清晰的区域政策、产品支持和售后协同机制</p>
    </div>

    <section class="section dealer-overview visual-edge-section edge-right" style="--edge-image: url('/images/editorial/dealer-partnership.webp')">
      <div class="container">
        <div class="dealer-intro">
          <SectionHeading icon="handshake" eyebrow="DEALER PARTNERSHIP" title="与长期合作伙伴共同经营市场" />
          <p>华丽电器面向具备渠道运营、技术服务和本地客户能力的合作伙伴开放经销合作。总部提供产品资料、销售培训、市场活动和售后资源，经销商负责区域客户开发和服务落地。</p>
          <div class="dealer-facts"><span><strong>80+</strong>覆盖国家和地区</span><span><strong>6</strong>核心产品系列</span><span><strong>1 对 1</strong>业务支持</span></div>
        </div>
      </div>
    </section>

    <section class="section section-gray benefits-section">
      <div class="container">
        <SectionHeading icon="trophy" eyebrow="PARTNER BENEFITS" title="经销商权益" subtitle="权益不是装饰口号，而是可执行的经营支持" />
        <div class="benefit-ledger">
          <article v-for="(item, index) in benefits" :key="item.title">
            <span class="benefit-no">0{{ index + 1 }}</span>
            <div class="benefit-title"><span class="benefit-icon" v-html="icons[item.icon]"></span><h3>{{ item.title }}</h3></div>
            <p>{{ item.desc }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section support-section visual-edge-section edge-left" style="--edge-image: url('/images/company/global-trade.webp')">
      <div class="container support-layout">
        <div class="support-copy">
          <SectionHeading icon="chart" eyebrow="BUSINESS SUPPORT" title="从进入市场到持续经营" />
          <p>合作支持围绕产品知识、区域销售、市场传播和售后履约展开。不同市场根据渠道结构和认证要求制定对应的产品组合与推进节奏。</p>
        </div>
        <div class="support-lines">
          <div><span>01</span><strong>市场进入</strong><p>产品组合、区域规划与客户类型分析。</p></div>
          <div><span>02</span><strong>销售启动</strong><p>产品培训、样机资料与推广内容支持。</p></div>
          <div><span>03</span><strong>持续经营</strong><p>售后配件、技术反馈与新品协同。</p></div>
        </div>
      </div>
    </section>

    <section class="dealer-access visual-edge-section edge-left dark-edge" style="--edge-image: url('/images/editorial/dealer-partnership.webp')">
      <div class="container access-layout">
        <div class="access-copy"><span>DEALER PORTAL</span><h2>经销商业务入口</h2><p>已签约合作伙伴可通过经销商编号登录。申请新合作请使用右侧申请入口。</p></div>
        <form class="dealer-login" @submit.prevent="handleLogin">
          <label>用户名 / 经销商编号<input v-model="account" autocomplete="username" placeholder="请输入账号"></label>
          <label>密码<input v-model="password" type="password" autocomplete="current-password" placeholder="请输入密码"></label>
          <button type="submit" class="btn btn-primary btn-block">登录经销商系统</button>
          <p v-if="loginError" class="login-error">当前尚未接入真实登录服务，请联系业务人员获取支持。</p>
          <router-link to="/contact" class="application-link">申请成为经销商 →</router-link>
        </form>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SectionHeading from '@/components/SectionHeading.vue'
import { icons } from '@/utils/icons'

const account = ref('')
const password = ref('')
const loginError = ref(false)
function handleLogin() { loginError.value = true }

const benefits = [
  { icon: 'trophy', title: '区域政策', desc: '根据市场容量、渠道能力和服务覆盖范围明确合作区域与客户边界。' },
  { icon: 'coin', title: '价格体系', desc: '结合采购规模和合作阶段提供清晰的分级政策与商务条件。' },
  { icon: 'book', title: '产品培训', desc: '提供产品结构、应用选择、销售演示和基础维护培训。' },
  { icon: 'speaker', title: '市场推广', desc: '支持展会、样品展示、宣传资料和重点客户联合推广。' },
  { icon: 'wrench', title: '售后协同', desc: '提供配件资料、问题反馈通道和常见故障处理指导。' },
  { icon: 'clipboard', title: '技术支持', desc: '协助完成产品选型、参数确认和行业应用方案沟通。' },
]
</script>

<style scoped>
.dealer-banner { background-position: center 48%; }
.dealer-overview .container { min-height: 470px; display: flex; align-items: center; }
.dealer-intro { max-width: 660px; }
.dealer-intro > p { color: var(--text-light); line-height: 2; margin-top: 16px; }
.dealer-facts { display: flex; gap: 44px; margin-top: 34px; padding-top: 24px; border-top: 1px solid var(--gray-200); }
.dealer-facts span { color: var(--gray-600); font-size: 12px; }
.dealer-facts strong { display: block; color: var(--text); font-size: 24px; margin-bottom: 4px; }
.benefit-ledger { display: grid; grid-template-columns: repeat(2, 1fr); margin-top: 38px; border-top: 1px solid var(--gray-300); }
.benefit-ledger article { display: grid; grid-template-columns: 44px 150px 1fr; gap: 18px; align-items: center; min-height: 122px; padding: 22px 28px 22px 0; border-bottom: 1px solid var(--gray-300); }
.benefit-ledger article:nth-child(odd) { border-right: 1px solid var(--gray-300); }
.benefit-ledger article:nth-child(even) { padding-left: 28px; }
.benefit-no { color: var(--gray-500); font: 700 11px ui-monospace, monospace; }
.benefit-title { display: flex; align-items: center; gap: 10px; }
.benefit-icon { display: inline-flex; width: 20px; height: 20px; color: var(--brand); flex: 0 0 auto; }
.benefit-icon :deep(svg) { width: 100%; height: 100%; }
.benefit-title h3 { font-size: 15px; }
.benefit-ledger p { color: var(--gray-600); font-size: 13px; line-height: 1.75; }
.support-layout { min-height: 430px; display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; padding-left: clamp(100px, 13vw, 190px); }
.support-copy > p { color: var(--text-light); line-height: 2; margin-top: 16px; }
.support-lines { border-top: 1px solid var(--gray-300); }
.support-lines div { display: grid; grid-template-columns: 42px 110px 1fr; gap: 16px; padding: 22px 0; border-bottom: 1px solid var(--gray-200); align-items: start; }
.support-lines span { color: var(--brand); font: 700 11px ui-monospace, monospace; }
.support-lines strong { font-size: 14px; }
.support-lines p { color: var(--gray-600); font-size: 13px; }
.dealer-access { position: relative; background: var(--dark); color: var(--white); overflow: hidden; }
.access-layout { min-height: 500px; display: grid; grid-template-columns: 1fr 430px; gap: 90px; align-items: center; padding-left: clamp(140px, 17vw, 250px); }
.access-copy span { color: #ff7777; font-size: 11px; font-weight: 700; letter-spacing: 1.8px; }
.access-copy h2 { font-size: 31px; margin: 9px 0 12px; }
.access-copy p { color: var(--gray-400); line-height: 1.9; }
.dealer-login { padding: 34px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(8px); }
.dealer-login label { display: block; color: var(--gray-300); font-size: 12px; font-weight: 600; margin-bottom: 16px; }
.dealer-login input { display: block; width: 100%; margin-top: 7px; padding: 12px 13px; border: 1px solid rgba(255,255,255,.2); background: rgba(0,0,0,.22); color: var(--white); font: inherit; }
.dealer-login input:focus { outline: 2px solid rgba(239,68,68,.35); border-color: var(--brand-hover); }
.login-error { color: #ff9b9b; font-size: 12px; line-height: 1.6; margin-top: 12px; }
.application-link { display: inline-block; color: var(--gray-300); font-size: 12px; margin-top: 18px; }
.application-link:hover { color: var(--white); }
@media (max-width: 900px) {
  .benefit-ledger article { grid-template-columns: 35px 130px 1fr; }
  .support-layout, .access-layout { grid-template-columns: 1fr; gap: 36px; padding-left: 110px; }
  .access-layout { padding-block: 70px; }
}
@media (max-width: 768px) {
  .dealer-overview .container { min-height: auto; }
  .dealer-facts { gap: 18px; overflow-x: auto; }
  .dealer-facts span { min-width: 100px; }
  .benefit-ledger { grid-template-columns: 1fr; }
  .benefit-ledger article, .benefit-ledger article:nth-child(even) { grid-template-columns: 32px 1fr; padding: 22px 0; border-right: 0; }
  .benefit-ledger p { grid-column: 2; }
  .support-layout, .access-layout { padding-left: 24px; }
  .support-lines div { grid-template-columns: 32px 90px 1fr; }
  .dealer-login { padding: 24px; }
}
</style>
