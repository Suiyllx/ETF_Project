<template>
  <BaseCard class="p-5">
    <div class="flex items-center justify-between mb-1">
      <span class="font-semibold text-label-1">收益曲线</span>
      <span class="text-xs text-label-3">收盘后自动快照，按各曲线首个数据点归一为 0%</span>
    </div>

    <div v-if="!dates.length" class="text-center py-16 text-label-2">
      <TrendingUp :size="36" class="mx-auto mb-3 opacity-50" />
      <p class="font-medium text-label-1">暂无历史数据</p>
      <p class="text-xs mt-1">每个交易日收盘后任务运行后将开始积累每日快照</p>
    </div>

    <template v-else>
      <div class="flex flex-wrap gap-1.5 mb-4">
        <button v-for="s in legendItems" :key="s.key"
                class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium transition"
                :class="s.active ? 'text-white' : 'bg-surface-2 text-label-3'"
                :style="s.active ? { background: s.color } : {}"
                @click="toggle(s.key)">
          <span class="w-1.5 h-1.5 rounded-full" :style="{ background: s.active ? '#fff' : s.color }"></span>
          {{ s.label }}
        </button>
      </div>
      <div class="relative h-72">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </template>
  </BaseCard>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { api } from '../api.js'
import BaseCard from './base/BaseCard.vue'
import { TrendingUp } from '@lucide/vue'

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#f43f5e', '#84cc16']
const BENCHMARK_COLOR = '#94a3b8'

const dates     = ref([])
const benchmark = ref([])
const series    = ref({})   // { user_id: [values...] }
const names     = ref({})   // { user_id: name }
const active    = reactive({})   // { [user_id|'benchmark']: bool }

const chartCanvas = ref(null)
let chart = null

async function load() {
  try {
    const d = await api('GET', '/api/asset-history')
    dates.value     = d.dates ?? []
    benchmark.value = d.benchmark ?? []
    series.value    = d.series ?? {}
    names.value     = d.names ?? {}
    for (const uid of Object.keys(names.value)) {
      if (!(uid in active)) active[uid] = true
    }
    if (!('benchmark' in active)) active.benchmark = true
  } catch { dates.value = []; series.value = {}; names.value = {}; benchmark.value = [] }
}

const legendItems = computed(() => {
  const ids = Object.keys(names.value)
  const items = ids.map((uid, i) => ({
    key: uid, label: names.value[uid], color: COLORS[i % COLORS.length], active: active[uid] !== false,
  }))
  items.push({ key: 'benchmark', label: '沪深300', color: BENCHMARK_COLOR, active: active.benchmark !== false })
  return items
})

function toggle(key) {
  active[key] = active[key] === false
  nextTick(drawChart)
}

// 归一化：以该曲线第一个非空值为基准，转换为累计收益率（%）
function normalize(values) {
  const base = values.find(v => v != null)
  if (base == null || base === 0) return values.map(() => null)
  return values.map(v => (v == null ? null : (v / base - 1) * 100))
}

function drawChart() {
  if (!chartCanvas.value || !dates.value.length) return
  if (chart) { chart.destroy(); chart = null }

  const datasets = []
  const ids = Object.keys(names.value)
  ids.forEach((uid, i) => {
    if (active[uid] === false) return
    datasets.push({
      label: names.value[uid],
      data: normalize(series.value[uid] ?? []),
      borderColor: COLORS[i % COLORS.length], backgroundColor: 'transparent',
      borderWidth: 2, pointRadius: 0, tension: 0.15, spanGaps: true,
    })
  })
  if (active.benchmark !== false && benchmark.value.length) {
    datasets.push({
      label: '沪深300', data: normalize(benchmark.value),
      borderColor: BENCHMARK_COLOR, borderDash: [4, 3], backgroundColor: 'transparent',
      borderWidth: 1.5, pointRadius: 0, tension: 0.15, spanGaps: true,
    })
  }

  chart = new Chart(chartCanvas.value, {
    type: 'line',
    data: { labels: dates.value, datasets },
    options: {
      responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15,23,42,0.92)', titleColor: '#94a3b8',
          bodyColor: '#e2e8f0', borderColor: 'rgba(59,130,246,0.3)', borderWidth: 1, padding: 10,
          callbacks: {
            label: item => item.raw == null ? null : ` ${item.dataset.label}：${item.raw >= 0 ? '+' : ''}${item.raw.toFixed(2)}%`,
          },
        },
      },
      scales: {
        x: { ticks: { maxTicksLimit: 8, font: { size: 11 }, color: '#94a3b8' }, grid: { color: 'rgba(226,232,240,0.15)' } },
        y: { ticks: { font: { size: 11 }, color: '#94a3b8', callback: v => v.toFixed(1) + '%' }, grid: { color: 'rgba(226,232,240,0.15)' } },
      },
    },
  })
}

watch(() => [dates.value, series.value, benchmark.value, JSON.stringify(active)], () => nextTick(drawChart), { deep: true })
onMounted(async () => { await load(); nextTick(drawChart) })
onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>
