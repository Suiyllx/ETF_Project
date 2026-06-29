<template>
  <div>
    <!-- 管理员操作栏 -->
    <div v-if="store.isAdmin" class="flex gap-2 mb-5">
      <BaseButton variant="red" :disabled="runningSellGen" @click="runSellGenerator">
        <Loader2 v-if="runningSellGen" :size="14" class="animate-spin" />
        <Zap v-else :size="14" />
        {{ runningSellGen ? '生成中…' : '重新生成卖出信号' }}
      </BaseButton>
      <BaseButton variant="primary" :disabled="runningMonitor" @click="runPriceMonitor">
        <Loader2 v-if="runningMonitor" :size="14" class="animate-spin" />
        <Radio v-else :size="14" />
        {{ runningMonitor ? '监控中…' : '立即盘中监控' }}
      </BaseButton>
    </div>

    <!-- 收盘卖出建议 -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <h2 class="font-bold text-label-1 text-base flex items-center gap-2">
          <ClipboardList :size="17" class="text-label-2" /> 收盘卖出建议
        </h2>
        <Badge v-if="sellSignals.trade_date" tone="red" :label="sellSignals.trade_date" />
        <Badge tone="gray" :label="(sellSignals.signals?.length ?? 0) + ' 条'" />
        <span v-if="sellSignals.generated_at" class="text-xs text-label-2 ml-auto">
          生成于 {{ sellSignals.generated_at?.slice(11, 16) }}
        </span>
      </div>

      <div v-if="loadingSell" class="py-10 text-center text-label-2">加载中…</div>
      <div v-else-if="errSell" class="py-6 text-center text-sys-red text-sm">{{ errSell }}</div>
      <BaseCard v-else-if="!sellSignals.signals?.length" class="text-center py-14">
        <CircleCheck :size="36" class="mx-auto mb-3 text-sys-green opacity-80" />
        <p class="text-label-1 font-semibold">暂无卖出建议</p>
        <p class="text-xs text-label-2 mt-1">所有持仓均未触及止损/止盈/模型看空阈值</p>
      </BaseCard>
      <div v-else class="space-y-3">
        <BaseCard v-for="sig in sellSignals.signals" :key="sig.code + sig.user_id" class="p-4"
                  :style="TRIGGER_BORDER[sig.trigger] ?? 'border-left:3px solid var(--label-3)'">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0 bg-sys-redDim text-sys-red">
              {{ sig.code?.slice(-2) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-semibold text-label-1 text-sm">{{ sig.name }}</span>
                <span class="text-xs text-label-2">{{ sig.code }}</span>
                <Badge v-if="sig.user_name" tone="blue" :label="sig.user_name" />
                <Badge :type="sig.trigger" />
              </div>
              <p class="text-xs text-label-2 mt-1.5 leading-relaxed">{{ sig.trigger_reason }}</p>
              <div class="flex gap-4 mt-2">
                <div class="text-xs">
                  <span class="text-label-2">成本价 </span>
                  <span class="font-medium text-label-1">¥{{ sig.cost_price?.toFixed(3) ?? '—' }}</span>
                </div>
                <div class="text-xs">
                  <span class="text-label-2">参考价 </span>
                  <span class="font-medium text-label-1">¥{{ sig.current_price?.toFixed(3) ?? '—' }}</span>
                </div>
                <div class="text-xs font-bold" :class="(sig.unrealized_pct ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'">
                  {{ (sig.unrealized_pct ?? 0) >= 0 ? '+' : '' }}{{ ((sig.unrealized_pct ?? 0) * 100).toFixed(2) }}%
                </div>
                <div v-if="sig.tech_warnings?.length" class="text-xs text-sys-orange flex items-center gap-1">
                  <TriangleAlert :size="13" /> {{ sig.tech_warnings.join(' · ') }}
                </div>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>

    <!-- 盘中价格告警 -->
    <div>
      <div class="flex items-center gap-3 mb-4">
        <h2 class="font-bold text-label-1 text-base flex items-center gap-2">
          <Bell :size="17" class="text-label-2" /> 盘中价格告警
        </h2>
        <Badge :tone="activeAlerts.length ? 'red' : 'gray'" :label="activeAlerts.length + ' 条未读'" />
        <BaseButton v-if="activeAlerts.length > 1" variant="ghost" size="sm" class="ml-auto"
                    :disabled="dismissingAll" @click="dismissAllAlerts">
          {{ dismissingAll ? '处理中…' : '全部标记已读' }}
        </BaseButton>
      </div>

      <div v-if="loadingAlerts" class="py-10 text-center text-label-2">加载中…</div>
      <BaseCard v-else-if="!activeAlerts.length" class="text-center py-14">
        <BellOff :size="36" class="mx-auto mb-3 text-label-2 opacity-60" />
        <p class="text-label-1 font-semibold">暂无盘中告警</p>
        <p class="text-xs text-label-2 mt-1">价格监控每 30 分钟运行一次，盘中触发后此处显示</p>
      </BaseCard>
      <div v-else class="space-y-3">
        <BaseCard v-for="alert in activeAlerts" :key="alert.id" class="p-4"
                  :style="TRIGGER_BORDER[alert.trigger] ?? 'border-left:3px solid var(--label-3)'">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0 bg-sys-orangeDim text-sys-orange">
              {{ alert.code?.slice(-2) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-semibold text-label-1 text-sm">{{ alert.name }}</span>
                <span class="text-xs text-label-2">{{ alert.code }}</span>
                <Badge v-if="alert.user_name" tone="blue" :label="alert.user_name" />
                <Badge :type="alert.trigger" />
                <span class="text-xs text-label-2 ml-auto">{{ alert.timestamp?.slice(11, 16) }}</span>
              </div>
              <p class="text-xs text-label-2 mt-1.5 leading-relaxed">{{ alert.trigger_reason }}</p>
              <div class="flex items-center gap-4 mt-2">
                <div class="text-xs">
                  <span class="text-label-2">成本价 </span>
                  <span class="font-medium text-label-1">¥{{ alert.cost_price?.toFixed(3) ?? '—' }}</span>
                </div>
                <div class="text-xs">
                  <span class="text-label-2">实时价 </span>
                  <span class="font-medium text-label-1">¥{{ alert.current_price?.toFixed(3) ?? '—' }}</span>
                </div>
                <div class="text-xs font-bold" :class="(alert.unrealized_pct ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'">
                  {{ (alert.unrealized_pct ?? 0) >= 0 ? '+' : '' }}{{ ((alert.unrealized_pct ?? 0) * 100).toFixed(2) }}%
                </div>
                <div class="text-xs text-label-2">
                  {{ alert.shares?.toLocaleString() }} 股
                  · {{ alert.unrealized_pnl >= 0 ? '+' : '' }}¥{{ alert.unrealized_pnl?.toFixed(0) }}
                </div>
                <BaseButton variant="ghost" size="sm" class="ml-auto"
                            :disabled="dismissingId === alert.id" @click="dismissAlert(alert.id)">
                  {{ dismissingId === alert.id ? '…' : '已读' }}
                </BaseButton>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'
import { store } from '../store.js'
import BaseCard   from './base/BaseCard.vue'
import BaseButton from './base/BaseButton.vue'
import Badge      from './base/Badge.vue'
import {
  Zap, Radio, ClipboardList, CircleCheck, Bell, BellOff, TriangleAlert, Loader2,
} from '@lucide/vue'

const TRIGGER_BORDER = {
  STOP_LOSS:   'border-left:3px solid var(--sys-red)',
  TAKE_PROFIT: 'border-left:3px solid var(--sys-orange)',
  MODEL_SELL:  'border-left:3px solid var(--sys-blue)',
}

// ── 卖出信号 ──────────────────────────────────────────────────
const sellSignals    = ref({ signals: [], count: 0, trade_date: '', generated_at: '' })
const loadingSell    = ref(false)
const errSell        = ref('')
const runningSellGen = ref(false)

async function loadSellSignals() {
  loadingSell.value = true; errSell.value = ''
  try { sellSignals.value = await api('GET', '/api/sell-signals') }
  catch (e) { errSell.value = e.message }
  finally { loadingSell.value = false }
}

async function runSellGenerator() {
  runningSellGen.value = true
  try {
    await api('POST', '/api/sell-signals/run', {})
    await loadSellSignals()
    store.status = '卖出信号已重新生成 ✓'
  } catch (e) { store.status = '生成失败: ' + e.message }
  finally { runningSellGen.value = false }
}

// ── 价格告警 ──────────────────────────────────────────────────
const sellAlerts    = ref({ alerts: [], count: 0 })
const loadingAlerts = ref(false)
const dismissingId  = ref('')
const dismissingAll = ref(false)
const runningMonitor = ref(false)

const activeAlerts = computed(() => (sellAlerts.value.alerts ?? []).filter(a => !a.dismissed))

async function loadAlerts() {
  loadingAlerts.value = true
  try { sellAlerts.value = await api('GET', '/api/alerts') }
  catch {} finally { loadingAlerts.value = false }
}

async function dismissAlert(id) {
  dismissingId.value = id
  try {
    await api('POST', `/api/alerts/${id}/dismiss`, {})
    const a = (sellAlerts.value.alerts ?? []).find(x => x.id === id)
    if (a) a.dismissed = true
  } catch (e) { store.status = '操作失败: ' + e.message }
  finally { dismissingId.value = '' }
}

async function dismissAllAlerts() {
  dismissingAll.value = true
  try {
    await api('POST', '/api/alerts/dismiss-all', {});
    (sellAlerts.value.alerts ?? []).forEach(a => { a.dismissed = true })
  } catch (e) { store.status = '操作失败: ' + e.message }
  finally { dismissingAll.value = false }
}

async function runPriceMonitor() {
  runningMonitor.value = true
  try {
    await api('POST', '/api/alerts/run', {})
    await loadAlerts()
    store.status = '盘中监控已执行 ✓'
  } catch (e) { store.status = '执行失败: ' + e.message }
  finally { runningMonitor.value = false }
}

onMounted(() => { loadSellSignals(); loadAlerts() })
</script>
