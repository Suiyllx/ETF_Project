<template>
  <BaseCard v-if="positions.length" class="p-4">
    <div class="flex items-center justify-between mb-3">
      <span class="font-semibold text-label-1 text-sm">配比建议</span>
      <span class="text-[11px] text-label-3">按当前风控参数计算</span>
    </div>

    <div v-if="!advice.length" class="flex items-center gap-2 text-sm text-sys-green py-1">
      <CheckCircle2 :size="16" class="flex-shrink-0" />
      <span>持仓配置在风控范围内，暂无需调整</span>
    </div>

    <div v-else class="space-y-2.5">
      <div v-for="(a, i) in advice" :key="i" class="flex items-start gap-2 text-xs">
        <AlertTriangle :size="14" class="flex-shrink-0 mt-0.5 text-sys-orange" />
        <span class="text-label-1 leading-relaxed">{{ a.text }}</span>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard from './base/BaseCard.vue'
import { fmtCash } from '../api.js'
import { useAllocation } from '../composables/useAllocation.js'
import { AlertTriangle, CheckCircle2 } from '@lucide/vue'

const props = defineProps({
  positions:      { type: Array,  default: () => [] },
  totalAssets:    { type: Number, default: 0 },
  marketPrices:   { type: Object, default: () => ({}) },
  categories:     { type: Object, default: () => ({}) },   // code → category
  maxPositionPct: { type: Number, default: 0.30 },
  maxSectorPct:   { type: Number, default: 0.50 },
})

const { weightRows, sectorRows } = useAllocation({
  positions:      computed(() => props.positions),
  totalAssets:    computed(() => props.totalAssets),
  marketPrices:   computed(() => props.marketPrices),
  categories:     computed(() => props.categories),
  maxPositionPct: computed(() => props.maxPositionPct),
  maxSectorPct:   computed(() => props.maxSectorPct),
})

const advice = computed(() => {
  const total = props.totalAssets || 1
  const list  = []

  for (const p of weightRows.value) {
    if (!p.overLimit) continue
    const trim = p.value - props.maxPositionPct * total
    list.push({
      text: `${p.name} 仓位占比 ${p.pct.toFixed(1)}%，超过单只上限 ${(props.maxPositionPct * 100).toFixed(0)}%，建议减仓约 ${fmtCash(trim)}`,
    })
  }

  for (const s of sectorRows.value) {
    if (!s.overLimit) continue
    const trim = s.value - props.maxSectorPct * total
    list.push({
      text: `${s.category}板块合计占比 ${s.pct.toFixed(1)}%，超过板块上限 ${(props.maxSectorPct * 100).toFixed(0)}%，建议适当分散或减仓约 ${fmtCash(trim)}`,
    })
  }

  return list
})
</script>
