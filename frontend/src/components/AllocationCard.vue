<template>
  <BaseCard v-if="positions.length" class="p-4">
    <div class="flex items-center justify-between mb-3">
      <span class="font-semibold text-label-1 text-sm">持仓分布</span>
      <span class="text-[11px] text-label-3">按现值估算</span>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <!-- ── 板块饼图 ── -->
      <div class="flex items-center gap-3">
        <div class="relative w-20 h-20 flex-shrink-0">
          <canvas ref="pieCanvas"></canvas>
        </div>
        <div class="flex-1 min-w-0 space-y-1">
          <div v-for="s in sectorRows" :key="s.category"
               class="flex items-center gap-1.5 text-xs">
            <span class="w-2 h-2 rounded-full flex-shrink-0" :style="{ background: s.color }"></span>
            <span class="text-label-1 truncate">{{ s.category }}</span>
            <span class="ml-auto font-semibold flex-shrink-0" :class="s.overLimit ? 'text-sys-red' : 'text-label-1'">
              {{ s.pct.toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- ── 持仓权重 ── -->
      <div class="space-y-2">
        <div v-for="p in weightRows" :key="p.code" class="flex items-center gap-2">
          <span class="text-xs text-label-1 w-14 flex-shrink-0 truncate">{{ p.name }}</span>
          <div class="flex-1 h-1.5 rounded-full bg-surface-2 overflow-hidden">
            <div class="h-full rounded-full transition-all"
                 :class="p.overLimit ? 'bg-sys-red' : 'bg-sys-blue'"
                 :style="{ width: Math.min(p.pct, 100) + '%' }"></div>
          </div>
          <span class="text-xs font-semibold w-10 text-right flex-shrink-0" :class="p.overLimit ? 'text-sys-red' : 'text-label-2'">
            {{ p.pct.toFixed(1) }}%
          </span>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import BaseCard from './base/BaseCard.vue'
import { useAllocation } from '../composables/useAllocation.js'

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

const pieCanvas = ref(null)
let pieChart = null

function drawPie() {
  if (!pieCanvas.value) return
  const rows = sectorRows.value
  if (pieChart) { pieChart.destroy(); pieChart = null }
  pieChart = new Chart(pieCanvas.value, {
    type: 'doughnut',
    data: {
      labels: rows.map(r => r.category),
      datasets: [{
        data: rows.map(r => r.value),
        backgroundColor: rows.map(r => r.color),
        borderColor: 'transparent',
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '68%',
      animation: { duration: 250 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15,23,42,0.92)', titleColor: '#94a3b8', bodyColor: '#e2e8f0',
          callbacks: { label: item => ` ${item.label}：${(item.raw / (props.totalAssets || 1) * 100).toFixed(1)}%` },
        },
      },
    },
  })
}

watch(() => [props.positions, props.marketPrices, props.totalAssets], () => nextTick(drawPie), { deep: true })
onMounted(() => nextTick(drawPie))
onBeforeUnmount(() => { if (pieChart) pieChart.destroy() })
</script>
