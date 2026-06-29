<template>
  <button :type="type" :disabled="disabled"
    class="inline-flex items-center justify-center gap-1.5 rounded-full font-semibold transition active:scale-[0.97] disabled:opacity-40 disabled:pointer-events-none"
    :class="[sizeClasses, variantClasses]">
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant:  { type: String, default: 'primary' },  // 'primary' | 'green' | 'red' | 'danger' | 'ghost'
  size:     { type: String, default: 'md' },       // 'sm' | 'md'
  type:     { type: String, default: 'button' },
  disabled: { type: Boolean, default: false },
})

const VARIANT_CLASSES = {
  primary: 'bg-sys-blue text-white hover:opacity-90',
  green:   'bg-sys-green text-white hover:opacity-90',
  red:     'bg-sys-red text-white hover:opacity-90',
  danger:  'bg-sys-red text-white hover:opacity-90',
  ghost:   'bg-surface-2 text-label-1 hover:bg-surface-3',
}
const variantClasses = computed(() => VARIANT_CLASSES[props.variant] || VARIANT_CLASSES.primary)

const SIZE_CLASSES = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-5 py-2.5 text-sm',
}
const sizeClasses = computed(() => SIZE_CLASSES[props.size] || SIZE_CLASSES.md)
</script>
