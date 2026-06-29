<template>
  <div class="inline-flex items-center gap-0.5 rounded-xl bg-surface-2 p-1">
    <button v-for="opt in options" :key="opt.key" type="button"
      class="px-3.5 py-1.5 rounded-lg text-sm transition-colors"
      :class="opt.key === modelValue
        ? 'bg-surface-3 text-label-1 font-medium'
        : 'text-label-2 hover:text-label-1'"
      @click="$emit('update:modelValue', opt.key)">
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], required: true },
  options:    { type: Array, required: true },   // [{ key, label }]
})
defineEmits(['update:modelValue'])
</script>
