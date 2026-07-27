<template>
  <div id="huali-app">
    <NavBar />
    <main class="main-content">
      <router-view />
    </main>
    <FooterBar />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import FooterBar from '@/components/FooterBar.vue'
</script>

<style>
#huali-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-content {
  flex: 1;
  padding-top: 0;
}
</style>
