<template>
  <span class="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold"
    :class="toneClasses">
    {{ label || defaultLabel }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 信号/交易场景的语义类型，自动映射文案与色调：
  // 'OPEN'|'ADD'|'HOLD'|'REDUCE'|'SKIP'（买入建议）
  // 'STOP_LOSS'|'TAKE_PROFIT'|'MODEL_SELL'（卖出触发）
  type:  { type: String, default: '' },
  tone:  { type: String, default: '' },   // 显式覆盖色调：'blue'|'green'|'red'|'orange'|'gray'
  label: { type: String, default: '' },   // 显式覆盖文案
})

const LABELS = {
  OPEN: '开仓', ADD: '加仓', HOLD: '持有', REDUCE: '减仓', SKIP: '观望',
  STOP_LOSS: '止损', TAKE_PROFIT: '止盈', MODEL_SELL: '模型看空',
}
const TONES = {
  OPEN: 'green', ADD: 'blue', HOLD: 'orange', REDUCE: 'red', SKIP: 'gray',
  STOP_LOSS: 'red', TAKE_PROFIT: 'orange', MODEL_SELL: 'blue',
}
const TONE_CLASSES = {
  green:  'bg-sys-greenDim text-sys-green',
  red:    'bg-sys-redDim text-sys-red',
  blue:   'bg-sys-blueDim text-sys-blue',
  orange: 'bg-sys-orangeDim text-sys-orange',
  gray:   'bg-surface-3 text-label-2',
}

const resolvedTone = computed(() => props.tone || TONES[props.type] || 'gray')
const toneClasses   = computed(() => TONE_CLASSES[resolvedTone.value] || TONE_CLASSES.gray)
const defaultLabel  = computed(() => LABELS[props.type] || props.type)
</script>
