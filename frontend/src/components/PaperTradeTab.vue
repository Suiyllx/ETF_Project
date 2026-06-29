<template>
  <div>
    <div v-if="loading" class="py-24 text-center text-label-2">加载中…</div>
    <div v-else-if="err" class="py-10 text-center text-sys-red">{{ err }}</div>
    <template v-else>

      <!-- 顶部操作栏 -->
      <div class="flex items-center justify-between mb-5">
        <div>
          <h2 class="font-bold text-label-1 text-base">
            模拟盘追踪
            <span class="text-xs font-normal text-label-2 ml-2">
              入场价 = T+1 开盘，出场价 = T+{{ paper.trades?.[0]?.forward ?? 5 }}+1 开盘
            </span>
          </h2>
          <p v-if="paper.updated_at" class="text-xs text-label-2 mt-0.5">
            上次更新：{{ paper.updated_at }}
          </p>
        </div>
        <BaseButton v-if="store.isAdmin" variant="primary" :disabled="refreshing" @click="refreshPaper">
          <Loader2 v-if="refreshing" :size="14" class="animate-spin" />
          <RefreshCw v-else :size="14" />
          {{ refreshing ? '计算中…' : '重新计算' }}
        </BaseButton>
      </div>

      <!-- 汇总卡片 -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="已结束交易" :value="ps.total ?? 0" />
        <StatCard label="整体胜率" :value="(ps.win_rate_pct ?? 0) + '%'" :accent="winRateAccent"
                  :delta="(ps.wins ?? 0) + '胜 ' + (ps.losses ?? 0) + '败'" trend="neutral" />
        <StatCard label="近30条胜率" :value="(ps.recent30_win_rate_pct ?? 0) + '%'" accent="blue"
                  :delta="'样本 ' + (ps.recent30_total ?? 0) + ' 笔'" trend="neutral" />
        <StatCard label="平均收益" :value="((ps.avg_ret_pct >= 0 ? '+' : '') + (ps.avg_ret_pct ?? 0)) + '%'"
                  :accent="avgRetAccent"
                  :delta="'最优 +' + (ps.best_ret_pct ?? 0) + '% / 最差 ' + (ps.worst_ret_pct ?? 0) + '%'" trend="neutral" />
      </div>

      <!-- 逐笔明细 -->
      <BaseCard class="overflow-hidden">
        <div class="flex items-center gap-3 px-5 py-4 border-b border-hairline">
          <span class="font-semibold text-label-1">逐笔明细</span>
          <div class="ml-auto">
            <SegmentControl v-model="filter" :options="FILTERS" />
          </div>
        </div>

        <div v-if="!filteredTrades.length" class="text-center py-14 text-label-2">
          <ClipboardList :size="36" class="mx-auto mb-3 opacity-50" />
          <p>暂无记录</p>
        </div>

        <table v-else class="w-full text-sm">
          <thead class="bg-surface-2">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-label-2">信号日</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-label-2">标的</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">做多概率</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">入场价</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">出场价</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">收益</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-label-2">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in filteredTrades" :key="t.signal_date + t.code"
                class="border-t border-hairline transition-colors hover:bg-surface-2">
              <td class="px-4 py-3 text-xs text-label-2">{{ t.signal_date }}</td>
              <td class="px-4 py-3">
                <div class="font-semibold text-label-1">{{ t.name }}</div>
                <div class="text-xs text-label-2">{{ t.code }}</div>
              </td>
              <td class="px-4 py-3 text-right">
                <span class="text-xs font-bold text-sys-green">
                  {{ (t.prob_up * 100).toFixed(1) }}%
                </span>
              </td>
              <td class="px-4 py-3 text-right text-label-2 text-xs">
                <div class="text-label-1">{{ t.entry_price ? '¥' + t.entry_price : '—' }}</div>
                <div>{{ t.entry_date ?? '' }}</div>
              </td>
              <td class="px-4 py-3 text-right text-label-2 text-xs">
                <div class="text-label-1">{{ t.exit_price ? '¥' + t.exit_price : '—' }}</div>
                <div>{{ t.exit_date ?? '' }}</div>
              </td>
              <td class="px-4 py-3 text-right font-bold text-sm">
                <span v-if="t.ret !== null" :class="t.ret >= 0 ? 'text-sys-green' : 'text-sys-red'">
                  {{ t.ret >= 0 ? '+' : '' }}{{ (t.ret * 100).toFixed(2) }}%
                </span>
                <span v-else class="text-label-3">—</span>
              </td>
              <td class="px-4 py-3 text-center">
                <Badge :tone="STATUS_TONE[t.status] || 'gray'" :label="STATUS_LABEL[t.status]" />
              </td>
            </tr>
          </tbody>
        </table>
      </BaseCard>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'
import { store } from '../store.js'
import BaseCard       from './base/BaseCard.vue'
import BaseButton     from './base/BaseButton.vue'
import SegmentControl from './base/SegmentControl.vue'
import StatCard       from './base/StatCard.vue'
import Badge          from './base/Badge.vue'
import { RefreshCw, ClipboardList, Loader2 } from '@lucide/vue'

const FILTERS = [
  { key: 'all',     label: '全部' },
  { key: 'closed',  label: '已结束' },
  { key: 'open',    label: '持仓中' },
  { key: 'pending', label: '待入场' },
]
const STATUS_LABEL = { closed: '已结束', open: '持仓中', pending: '待入场' }
const STATUS_TONE  = { closed: 'green', open: 'blue', pending: 'gray' }

const paper     = ref({ summary: {}, trades: [], updated_at: null })
const loading   = ref(false)
const err       = ref('')
const refreshing = ref(false)
const filter    = ref('all')

const ps = computed(() => paper.value.summary ?? {})
const winRateAccent = computed(() => {
  const r = ps.value.win_rate_pct ?? 0
  if (r >= 60) return 'green'
  if (r >= 50) return 'orange'
  return 'red'
})
const avgRetAccent = computed(() => (ps.value.avg_ret_pct ?? 0) >= 0 ? 'green' : 'red')
const filteredTrades = computed(() => {
  const all = paper.value.trades ?? []
  return filter.value === 'all' ? all : all.filter(t => t.status === filter.value)
})

async function loadPaper() {
  loading.value = true; err.value = ''
  try { paper.value = await api('GET', '/api/paper-trades') }
  catch (e) { err.value = e.message }
  finally { loading.value = false }
}

async function refreshPaper() {
  refreshing.value = true
  try { paper.value = await api('POST', '/api/paper-trades/refresh', {}) }
  catch (e) { err.value = e.message }
  finally { refreshing.value = false }
}

onMounted(loadPaper)
</script>
