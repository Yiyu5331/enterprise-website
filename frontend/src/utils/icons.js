// 华丽电器 SVG 图标库 — 24x24 viewBox, stroke 风格
// 使用方式：import { icons } from '@/utils/icons'; v-html="icons.wrench"

export const icons = {
  // 产品类
  drill:   '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="12" width="16" height="8" rx="1"/><rect x="20" y="11" width="10" height="10" rx="1"/><circle cx="32" cy="16" r="3" fill="currentColor"/><rect x="6" y="8" width="4" height="4" rx="1"/></svg>',
  hammer:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="8" y="12" width="20" height="8" rx="2"/><rect x="4" y="11" width="6" height="10" rx="1"/><rect x="16" y="20" width="4" height="8" rx="1"/></svg>',
  grinder: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="16" cy="16" r="10"/><circle cx="16" cy="16" r="4" fill="currentColor"/><rect x="24" y="14" width="6" height="4" rx="1"/></svg>',
  cutter:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="16" cy="16" r="10"/><circle cx="16" cy="16" r="5" fill="currentColor" opacity=".3"/><line x1="16" y1="6" x2="16" y2="26"/><line x1="6" y1="16" x2="26" y2="16"/><rect x="26" y="14" width="5" height="4" rx="1"/></svg>',
  sander:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="10" width="18" height="12" rx="2"/><line x1="7" y1="10" x2="7" y2="6"/><circle cx="22" cy="16" r="5"/></svg>',
  wrench: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M10 6 L24 20 M6 10 L20 24" /><circle cx="10" cy="6" r="4"/><circle cx="24" cy="20" r="4"/><circle cx="20" cy="24" r="4"/><circle cx="6" cy="10" r="4"/></svg>',

  // 实力类
  factory: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="14" width="10" height="16" rx="1"/><rect x="4" y="20" width="3" height="3" rx=".5"/><rect x="7" y="20" width="3" height="3" rx=".5"/><rect x="4" y="24" width="3" height="4"/><rect x="7" y="24" width="3" height="4"/><rect x="14" y="6" width="16" height="24" rx="1"/><rect x="17" y="20" width="3" height="3" rx=".5"/><rect x="22" y="20" width="3" height="3" rx=".5"/><rect x="17" y="24" width="3" height="4"/><rect x="22" y="24" width="3" height="4"/><path d="M14 6 L16 2 L28 2 L30 6" fill="currentColor" opacity=".3"/><rect x="18" y="10" width="4" height="6"/></svg>',
  lab:     '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M10 2 L10 14 L4 26 L28 26 L22 14 L22 2"/><line x1="10" y1="6" x2="22" y2="6"/><line x1="10" y1="10" x2="22" y2="10"/><path d="M8 22 L14 18 L18 22 L24 18" fill="currentColor" opacity=".2"/></svg>',
  gear:    '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="16" cy="16" r="5"/><path d="M16 2 L18 7 L16 8 L14 7Z" fill="currentColor"/><path d="M16 24 L18 29 L16 30 L14 29Z" fill="currentColor"/><path d="M2 16 L7 14 L8 16 L7 18Z" fill="currentColor"/><path d="M24 16 L29 14 L30 16 L29 18Z" fill="currentColor"/></svg>',
  chart:   '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="22" width="6" height="8" rx="1"/><rect x="13" y="14" width="6" height="16" rx="1"/><rect x="22" y="8" width="6" height="22" rx="1"/><line x1="2" y1="28" x2="30" y2="28"/></svg>',

  // 经销商类
  trophy: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M10 4 H22 V12 C22 16 18 18 16 18 C14 18 10 16 10 12 V4Z"/><path d="M8 8 H6 C4 8 4 6 6 6 H8Z" /><path d="M24 8 H26 C28 8 28 6 26 6 H24Z"/><line x1="12" y1="22" x2="20" y2="22"/><line x1="14" y1="26" x2="18" y2="26"/><line x1="16" y1="18" x2="16" y2="22"/></svg>',
  coin:   '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="16" cy="16" r="10"/><text x="16" y="20" text-anchor="middle" font-size="12" fill="currentColor">$</text></svg>',
  book:   '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="4" width="24" height="24" rx="2"/><line x1="16" y1="6" x2="16" y2="26"/><line x1="6" y1="10" x2="14" y2="10"/><line x1="6" y1="14" x2="14" y2="14"/><line x1="6" y1="18" x2="14" y2="18"/></svg>',
  speaker: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 8 L12 22 L18 26 L18 4 Z"/><path d="M18 10 C22 12 22 18 18 20"/><path d="M22 8 C28 12 28 18 22 20"/></svg>',
  clipboard: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="6" y="4" width="20" height="26" rx="2"/><path d="M10 2 L10 6 L22 6 L22 2" fill="currentColor" opacity=".3"/><line x1="10" y1="14" x2="22" y2="14"/><line x1="10" y1="18" x2="18" y2="18"/><line x1="10" y1="22" x2="20" y2="22"/></svg>',
  handshake: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 20 C4 20 2 18 2 16 C2 14 4 12 6 12 L8 14"/><path d="M26 20 C28 20 30 18 30 16 C30 14 28 12 26 12 L24 14"/><path d="M8 14 L12 10 L18 12 L22 10 L24 14 L20 18 L16 16 L12 20Z"/></svg>',

  // 流程类
  search: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="14" cy="14" r="9"/><line x1="20" y1="20" x2="28" y2="28"/></svg>',
  pencil: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 24 L10 22 L24 8 L22 6 Z"/><path d="M20 10 L22 12" stroke-width="1"/><line x1="4" y1="28" x2="14" y2="28"/></svg>',
  flask:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2 L14 14 L4 26 L28 26 L18 14 L18 2"/><path d="M8 22 L16 16 L24 22" fill="currentColor" opacity=".2"/></svg>',

  // 联系类
  pin:    '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 4 C10 4 6 9 6 14 C6 22 16 28 16 28 C16 28 26 22 26 14 C26 9 22 4 16 4Z"/><circle cx="16" cy="14" r="4" fill="currentColor"/></svg>',
  phone:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M24 20 C22 22 18 22 14 18 C10 14 10 10 12 8 L10 4 L4 4 C4 16 16 28 28 28 L28 22 L24 20Z"/></svg>',
  mail:   '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="6" width="28" height="20" rx="2"/><path d="M2 8 L16 18 L30 8" fill="none"/></svg>',
  clock:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="16" cy="16" r="12"/><line x1="16" y1="8" x2="16" y2="16"/><line x1="16" y1="16" x2="22" y2="18"/></svg>',

  // 供应链类
  bolt:   '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 4 L8 18 L15 18 L13 28 L24 14 L17 14Z"/></svg>',
  package:'<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="8" width="28" height="22" rx="2"/><line x1="2" y1="16" x2="30" y2="16"/><line x1="16" y1="8" x2="16" y2="30"/></svg>',
  shield: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M16 2 C8 6 6 10 6 16 C6 24 16 30 16 30 C16 30 26 24 26 16 C26 10 24 6 16 2Z"/><path d="M12 16 L15 19 L20 13" fill="none" stroke-width="2"/></svg>',
  route:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="7" cy="8" r="3"/><circle cx="25" cy="24" r="3"/><path d="M10 8 H16 C21 8 22 12 22 16 V21"/><path d="M18 18 L22 22 L26 18"/></svg>',
  layers: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 10 L16 4 L28 10 L16 16 Z"/><path d="M4 16 L16 22 L28 16"/><path d="M4 22 L16 28 L28 22"/></svg>',

  // 其他
  check:  '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 16 L14 24 L26 8"/></svg>',
  arrowR: '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="4" y1="16" x2="28" y2="16"/><line x1="20" y1="8" x2="28" y2="16"/><line x1="20" y1="24" x2="28" y2="16"/></svg>',
}

// 渲染函数：在模板中使用 v-html="iconSvg('wrench', 24, 'var(--brand)')"
export function iconSvg(name, size = 32, color = 'currentColor') {
  const svg = icons[name]
  if (!svg) return ''
  return svg.replace('currentColor', color)
}
