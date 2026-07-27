<template>
  <div :class="['section-heading', { light, centered }]">
    <div class="heading-kicker"><span class="heading-icon" v-html="headingIcon"></span><span>{{ eyebrow }}</span></div>
    <h2>{{ title }}</h2>
    <p v-if="subtitle">{{ subtitle }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { icons } from '@/utils/icons'

const props = defineProps({
  icon: { type: String, default: 'gear' },
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  light: Boolean,
  centered: Boolean,
})

const headingIcon = computed(() => icons[props.icon] || icons.gear)
</script>

<style scoped>
.section-heading { max-width: 680px; }
.section-heading.centered { margin-inline: auto; text-align: center; }
.heading-kicker { display: flex; align-items: center; gap: 9px; color: var(--brand); font-size: 11px; font-weight: 700; letter-spacing: 1.7px; margin-bottom: 10px; }
.centered .heading-kicker { justify-content: center; }
.heading-icon { display: inline-flex; width: 19px; height: 19px; color: currentColor; }
.heading-icon :deep(svg) { width: 100%; height: 100%; }
h2 { color: var(--text); font-size: 31px; line-height: 1.3; }
p { color: var(--gray-600); margin-top: 11px; line-height: 1.8; }
.light h2 { color: var(--white); }
.light p { color: var(--gray-400); }
@media (max-width: 768px) { h2 { font-size: 24px; } }
</style>
