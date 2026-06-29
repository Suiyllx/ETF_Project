<template>
  <BaseCard class="px-5 py-4">
    <div class="text-xs text-label-2">{{ label }}</div>
    <div class="mt-2 flex items-baseline gap-2">
      <span class="text-[26px] font-bold leading-none tracking-tight" :class="valueColorClass">{{ value }}</span>
      <span v-if="delta" class="text-xs font-semibold" :class="trendColorClass">{{ delta }}</span>
    </div>
    <svg v-if="points" class="mt-3 block h-8 w-full" viewBox="0 0 100 28" preserveAspectRatio="none">
      <polyline :points="points" fill="none" :stroke="sparkColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard from './BaseCard.vue'

const props = defineProps({
  label:     { type: String, required: true },
  value:     { type: [String, Number], required: true },
  delta:     { type: String, default: '' },      // 如 '+2.3%'，留空则不显示
  trend:     { type: String, default: '' },       // 'up'|'down'|'neutral'，留空按 delta 首字符推断
  sparkline: { type: Array, default: null },      // number[]，长度 >=2 才渲染
  accent:    { type: String, default: '' },       // 'blue'|'green'|'red'|'orange'，留空则数值用默认文字色
})

const resolvedTrend = computed(() => {
  if (props.trend) return props.trend
  if (!props.delta) return 'neutral'
  return props.delta.trim().startsWith('-') ? 'down' : 'up'
})

const TREND_TEXT_CLASS = { up: 'text-sys-green', down: 'text-sys-red', neutral: 'text-label-2' }
const trendColorClass = computed(() => TREND_TEXT_CLASS[resolvedTrend.value] || TREND_TEXT_CLASS.neutral)

const ACCENT_TEXT_CLASS = { blue: 'text-sys-blue', green: 'text-sys-green', red: 'text-sys-red', orange: 'text-sys-orange' }
const valueColorClass = computed(() => ACCENT_TEXT_CLASS[props.accent] || 'text-label-1')

const points = computed(() => {
  const data = props.sparkline
  if (!data || data.length < 2) return null
  const min  = Math.min(...data)
  const max  = Math.max(...data)
  const span = max - min || 1
  const step = 100 / (data.length - 1)
  return data
    .map((v, i) => `${(i * step).toFixed(1)},${(28 - ((v - min) / span) * 26 - 1).toFixed(1)}`)
    .join(' ')
})

const SPARK_STROKE = { up: 'var(--sys-green)', down: 'var(--sys-red)', neutral: 'var(--label-2)' }
const sparkColor = computed(() => SPARK_STROKE[resolvedTrend.value] || SPARK_STROKE.neutral)
</script>
