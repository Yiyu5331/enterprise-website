<template>
  <header class="header">
    <!-- 顶部信息栏 -->
    <div class="header-top">
      <div class="container header-top-inner">
        <span class="header-top-item">📞 销售热线：8770****</span>
        <span class="header-top-item">✉️ k****@cnkainuo</span>
        <span class="header-top-item lang-switch">中 / EN</span>
      </div>
    </div>
    <!-- 主导航 -->
    <div class="header-main" :class="{ scrolled: scrolled }">
      <div class="container header-main-inner">
        <router-link to="/" class="header-logo">
          <img src="/images/logo.jpg" alt="华丽电器" class="logo-img">
          <div class="logo-text">
            <strong>华丽电器</strong>
            <small>HUALI ELECTRIC</small>
          </div>
        </router-link>
        <button class="hamburger" :class="{ active: menuOpen }" @click="toggleMenu">
          <span></span><span></span><span></span>
        </button>
        <nav :class="['header-nav', { open: menuOpen }]">
          <router-link to="/" @click="menuOpen=false">首页</router-link>
          <router-link to="/about/" @click="menuOpen=false">关于我们</router-link>
          <router-link to="/products/" @click="menuOpen=false">产品中心</router-link>
          <router-link to="/news/" @click="menuOpen=false">新闻中心</router-link>
          <router-link to="/supply-chain/" @click="menuOpen=false">供应链</router-link>
          <router-link to="/inquiry/" @click="menuOpen=false">在线询盘</router-link>
          <router-link to="/dealer/" @click="menuOpen=false">经销商</router-link>
          <router-link to="/contact/" @click="menuOpen=false">联系我们</router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const menuOpen = ref(false)
const scrolled = ref(false)
function toggleMenu() { menuOpen.value = !menuOpen.value }
function handleScroll() { scrolled.value = window.scrollY > 40 }
onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<style scoped>
.header { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; }
.header-top {
  background: var(--dark); color: var(--gray-400); height: 32px;
  font-size: 12px; border-bottom: 2px solid var(--brand);
}
.header-top-inner {
  height: 100%; display: flex; align-items: center; gap: 24px;
}
.header-top-item { display: flex; align-items: center; gap: 4px; }
.lang-switch { margin-left: auto; cursor: pointer; color: var(--gray-300); }
.lang-switch:hover { color: var(--white); }
.header-main {
  background: var(--white); height: var(--header-h);
  transition: box-shadow .3s;
}
.header-main.scrolled { box-shadow: 0 2px 12px rgba(0,0,0,.12); }
.header-main-inner {
  height: 100%; display: flex; align-items: center; justify-content: space-between;
}
.header-logo { display: flex; align-items: center; gap: 12px; text-decoration: none; }
.logo-img { height: 36px; width: auto; }
.logo-text { line-height: 1.2; }
.logo-text strong { display: block; font-size: 18px; color: var(--brand); letter-spacing: 1px; }
.logo-text small { font-size: 10px; color: var(--gray-500); letter-spacing: 1.5px; }
.header-nav { display: flex; align-items: center; gap: 2px; }
.header-nav a {
  padding: 8px 16px; font-size: 14px; font-weight: 500; color: var(--text);
  border-radius: var(--radius); transition: all .2s;
  position: relative;
}
.header-nav a::after {
  content: ''; position: absolute; bottom: 4px; left: 16px; right: 16px;
  height: 2px; background: var(--brand); transform: scaleX(0);
  transition: transform .25s;
}
.header-nav a:hover { color: var(--brand); }
.header-nav a:hover::after,
.header-nav a.router-link-active::after { transform: scaleX(1); }
.hamburger {
  display: none; flex-direction: column; gap: 5px;
  background: none; border: none; cursor: pointer; padding: 4px;
}
.hamburger span {
  display: block; width: 24px; height: 2px; background: var(--text);
  transition: all .3s; border-radius: 2px;
}
.hamburger.active span:nth-child(1) { transform: rotate(45deg) translate(5px,5px); }
.hamburger.active span:nth-child(2) { opacity: 0; }
.hamburger.active span:nth-child(3) { transform: rotate(-45deg) translate(5px,-5px); }
@media (max-width: 768px) {
  .header-top { display: none; }
  .hamburger { display: flex; }
  .header-nav {
    display: none; position: absolute; top: var(--header-h); left: 0; right: 0;
    background: var(--white); flex-direction: column; padding: 8px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,.12);
  }
  .header-nav.open { display: flex; }
  .header-nav a { padding: 12px 24px; width: 100%; }
  .header-nav a::after { display: none; }
}
</style>
