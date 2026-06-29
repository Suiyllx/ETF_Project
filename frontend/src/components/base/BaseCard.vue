<template>
  <component :is="tag"
    class="rounded-2xl border border-glass-border bg-glass-bg backdrop-blur-2xl backdrop-saturate-150 shadow-glass">
    <slot />
  </component>
</template>

<script setup>
defineProps({
  tag: { type: String, default: 'div' },   // 需要 <ul>/<section> 等场景可覆盖
})
</script>
