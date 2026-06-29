<template>
  <div class="flex flex-col h-full overflow-hidden">

    <!-- Top bar: Tab + 历史/帮助 入口 -->
    <div class="flex-shrink-0 flex items-center gap-3 px-6 pt-5 pb-4">
      <SegmentControl v-model="tab" :options="TOP_TABS" />
      <div class="ml-auto flex items-center gap-2">
        <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-surface-2 text-label-2 hover:bg-surface-3 hover:text-label-1 transition"
                @click="historyOpen = true">
          <History :size="15" /> 历史信号
        </button>
        <button class="w-8 h-8 rounded-lg flex items-center justify-center bg-surface-2 text-label-2 hover:bg-surface-3 hover:text-label-1 transition"
                aria-label="算法说明" @click="helpOpen = true">
          <CircleHelp :size="16" />
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-6 pb-6">

      <!-- 信号：卖出提醒（紧急事项）在上，今日买入信号（浏览发现）在下 -->
      <div v-if="tab === 'signals'" class="space-y-8">
        <SellSignalTab />
        <div>
          <h2 class="font-bold text-label-1 text-base mb-4 flex items-center gap-2">
            <Radar :size="17" class="text-label-2" /> 今日买入信号
          </h2>
          <TodaySignalTab ref="todayTabRef" @open-trade="openTradeModal" />
        </div>
      </div>

      <!-- 模拟盘胜率 -->
      <PaperTradeTab v-else-if="tab === 'paper'" />

    </div>
  </div>

  <!-- 历史档案 · 右侧滑出抽屉 -->
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="historyOpen" class="drawer-overlay" @click.self="historyOpen = false">
        <div class="drawer-panel">
          <div class="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-hairline">
            <h3 class="font-bold text-label-1 text-base flex items-center gap-2">
              <History :size="17" class="text-label-2" /> 历史档案
            </h3>
            <button class="w-8 h-8 flex items-center justify-center rounded-lg text-label-2 hover:text-label-1 hover:bg-surface-2 transition-all"
                    @click="historyOpen = false"><X :size="16" /></button>
          </div>
          <div class="flex-1 overflow-hidden flex gap-5 p-6 min-h-0">
            <div class="w-36 flex-shrink-0 overflow-y-auto">
              <div class="text-xs font-semibold text-label-2 mb-2 uppercase tracking-wide">历史记录</div>
              <div v-if="loadingDates" class="text-xs text-label-2">加载中…</div>
              <div v-else-if="!histDates.length" class="text-xs text-label-2">暂无历史数据</div>
              <div v-else class="space-y-1">
                <div v-for="d in histDates" :key="d"
                     class="px-3 py-2 rounded-xl text-sm cursor-pointer transition-all"
                     :class="selectedDate === d
                       ? 'bg-sys-blueDim text-sys-blue font-semibold'
                       : 'text-label-2 hover:bg-surface-2 hover:text-label-1'"
                     @click="loadHistDate(d)">
                  {{ d.slice(5) }}
                  <span v-if="d === todayDateStr" class="ml-1 text-xs text-sys-blue">今</span>
                </div>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto min-h-0">
              <div v-if="!selectedDate" class="py-20 text-center text-label-2">
                <ArrowLeft :size="28" class="mx-auto mb-3 opacity-50" />
                <p>从左侧选择日期查看历史推荐</p>
              </div>
              <div v-else-if="loadingHist" class="py-20 text-center text-label-2">加载中…</div>
              <div v-else-if="errHist" class="py-10 text-center text-sys-red">{{ errHist }}</div>
              <template v-else>
                <div class="flex items-center gap-3 mb-4">
                  <h3 class="font-bold text-label-1">{{ selectedDate }} 的推荐</h3>
                  <Badge tone="blue" :label="histSignals.length + ' 只'" />
                  <span class="text-xs text-label-2">生成于 {{ histMeta.generated_at?.slice(11,16) }}</span>
                </div>
                <div v-if="!histSignals.length" class="text-center py-16 text-label-2">该日无信号</div>
                <div v-else class="space-y-4">
                  <SignalCard v-for="s in histSignals" :key="s.code" :signal="s" :historical="true" />
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- 算法说明 · 弹窗 -->
  <Teleport to="body">
    <div v-if="helpOpen" class="modal-overlay" @click.self="helpOpen = false">
      <BaseCard class="help-box" @click.stop>
        <div class="flex items-center justify-between mb-4 flex-shrink-0">
          <h3 class="text-base font-bold text-label-1 flex items-center gap-2">
            <BookOpen :size="17" class="text-label-2" /> 算法说明
          </h3>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-label-2 hover:text-label-1 hover:bg-surface-2 transition-all"
                  @click="helpOpen = false"><X :size="16" /></button>
        </div>
        <div class="flex-1 overflow-y-auto pr-1">
          <AlgoExplainer />
        </div>
      </BaseCard>
    </div>
  </Teleport>

  <!-- 快速交易 Modal -->
  <Teleport to="body">
    <div v-if="showTradeModal" class="modal-overlay" @click.self="showTradeModal = false">
      <BaseCard class="modal-box" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-bold text-label-1 flex items-center gap-2">
            <component :is="tradeMode === 'buy' ? TrendingUp : FolderPlus" :size="17" class="text-label-2" />
            {{ tradeMode === 'buy' ? '买入记录' : '加入持仓' }}
          </h3>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-label-2 hover:text-label-1 hover:bg-surface-2 transition-all"
                  @click="showTradeModal = false"><X :size="16" /></button>
        </div>

        <!-- ETF 信息 -->
        <div class="flex items-center gap-3 p-3 rounded-xl mb-4 bg-sys-greenDim">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold text-white bg-sys-green">
            {{ tradeSignal?.code?.slice(-2) }}
          </div>
          <div>
            <div class="font-semibold text-label-1 text-sm">{{ tradeSignal?.name }}</div>
            <div class="text-xs text-label-2">{{ tradeSignal?.code }} · 昨收 ¥{{ tradeSignal?.close?.toFixed(3) }}</div>
          </div>
          <div class="ml-auto text-right">
            <div class="text-sm font-bold text-sys-green">{{ ((tradeSignal?.prob_up ?? 0) * 100).toFixed(1) }}%</div>
            <div class="text-xs text-label-2">做多概率</div>
          </div>
        </div>

        <!-- 买入记录 -->
        <div v-if="tradeMode === 'buy'" class="space-y-3">
          <div class="flex gap-2">
            <button v-for="opt in [{v:'buy',label:'▲ 买入'},{v:'sell',label:'▼ 卖出'}]" :key="opt.v"
                    class="flex-1 py-2 rounded-xl text-sm font-semibold border transition"
                    :class="tradeForm.action === opt.v
                      ? (opt.v === 'buy' ? 'bg-sys-green text-white border-sys-green' : 'bg-sys-red text-white border-sys-red')
                      : 'bg-surface-1 text-label-2 border-hairline'"
                    @click="tradeForm.action = opt.v">{{ opt.label }}</button>
          </div>
          <div>
            <label class="field-label">交易日期</label>
            <input v-model="tradeForm.date" type="date" class="input" />
          </div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="field-label">数量（股）*</label>
              <input v-model.number="tradeForm.shares" type="number" placeholder="例：1000" class="input" />
            </div>
            <div class="flex-1">
              <label class="field-label">
                成交价（元）*
                <span v-if="tradePriceLoading" class="ml-1 text-sys-blue font-normal text-xs">拉取中…</span>
                <span v-else-if="tradePriceSource === 'realtime'" class="ml-1 font-normal text-xs text-sys-green">● 实时价</span>
                <span v-else-if="tradePriceSource === 'local_close'" class="ml-1 font-normal text-xs text-label-2">昨收价</span>
              </label>
              <input v-model.number="tradeForm.price" type="number" step="0.001" class="input" />
            </div>
          </div>
          <div class="flex justify-between items-center text-sm px-1 py-1 rounded-lg bg-surface-2">
            <span class="text-label-2 text-xs">金额合计</span>
            <span class="font-bold text-label-1">
              {{ tradeForm.shares > 0 && tradeForm.price > 0
                  ? '¥' + (tradeForm.shares * tradeForm.price).toLocaleString('zh-CN') : '—' }}
            </span>
          </div>
          <div>
            <label class="field-label">备注（可选）</label>
            <input v-model="tradeForm.note" type="text" placeholder="例：按信号买入" class="input" />
          </div>
        </div>

        <!-- 加入持仓 -->
        <div v-else class="space-y-3">
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="field-label">股数 *</label>
              <input v-model.number="tradeForm.shares" type="number" placeholder="例：1000" class="input" />
            </div>
            <div class="flex-1">
              <label class="field-label">
                成本价（元）*
                <span v-if="tradePriceLoading" class="ml-1 text-sys-blue font-normal text-xs">拉取中…</span>
                <span v-else-if="tradePriceSource === 'realtime'" class="ml-1 font-normal text-xs text-sys-green">● 实时价</span>
                <span v-else-if="tradePriceSource === 'local_close'" class="ml-1 font-normal text-xs text-label-2">昨收价</span>
              </label>
              <input v-model.number="tradeForm.price" type="number" step="0.001" class="input" />
            </div>
          </div>
          <div>
            <label class="field-label">买入日期</label>
            <input v-model="tradeForm.date" type="date" class="input" />
          </div>
        </div>

        <div v-if="tradeMsgErr" class="mt-2 text-xs text-sys-red">{{ tradeMsgErr }}</div>

        <div class="flex gap-2 mt-5">
          <BaseButton variant="ghost" class="flex-1" @click="showTradeModal = false">取消</BaseButton>
          <BaseButton variant="green" class="flex-1" :disabled="tradeSaving" @click="submitTrade">
            {{ tradeSaving ? '保存中…' : (tradeMode === 'buy' ? '确认记录' : '加入持仓') }}
          </BaseButton>
        </div>
      </BaseCard>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api, todayStr, fetchRealtimePrice } from '../api.js'
import { store } from '../store.js'
import {
  Radar, History, BookOpen, CircleHelp, ArrowLeft, X, TrendingUp, FolderPlus,
} from '@lucide/vue'
import SignalCard      from '../components/SignalCard.vue'
import AlgoExplainer   from '../components/AlgoExplainer.vue'
import TodaySignalTab  from '../components/TodaySignalTab.vue'
import SellSignalTab   from '../components/SellSignalTab.vue'
import PaperTradeTab   from '../components/PaperTradeTab.vue'
import SegmentControl  from '../components/base/SegmentControl.vue'
import BaseCard        from '../components/base/BaseCard.vue'
import BaseButton      from '../components/base/BaseButton.vue'
import Badge           from '../components/base/Badge.vue'

// 信号布局重构（2026-06-26）：5 个 Tab 精简为 2 个；买入/卖出合并为一个 Tab（卖出在上，
// 因为是已有持仓的紧急事项；买入在下，因为是浏览发现）；历史档案改为右侧抽屉，
// 算法说明改为帮助弹窗——两者都不再常驻占用 Tab 位置。
const TOP_TABS = [
  { key: 'signals', label: '信号' },
  { key: 'paper',   label: '模拟盘胜率' },
]
const tab = ref('signals')
const todayTabRef  = ref(null)
const todayDateStr = new Date().toISOString().slice(0, 10)

const historyOpen = ref(false)
const helpOpen     = ref(false)

// ── 历史档案 ──────────────────────────────────────────────────
const histDates    = ref([])
const loadingDates = ref(false)
const selectedDate = ref('')
const histMeta     = ref({})
const histSignals  = ref([])
const loadingHist  = ref(false)
const errHist      = ref('')

async function loadHistDate(date) {
  selectedDate.value = date
  loadingHist.value  = true
  errHist.value      = ''
  histSignals.value  = []
  try {
    const d = await api('GET', `/api/signal-history/${date}`)
    histMeta.value    = d
    histSignals.value = d.signals ?? []
  } catch (e) { errHist.value = e.message }
  finally { loadingHist.value = false }
}

onMounted(async () => {
  loadingDates.value = true
  try { histDates.value = await api('GET', '/api/signal-history') }
  catch {} finally { loadingDates.value = false }
})

// ── 快速交易 Modal ─────────────────────────────────────────────
const showTradeModal    = ref(false)
const tradeMode         = ref('buy')
const tradeSignal       = ref(null)
const tradeSaving       = ref(false)
const tradeMsgErr       = ref('')
const tradePriceLoading = ref(false)
const tradePriceSource  = ref('')
const tradeForm = reactive({ date: todayStr(), action: 'buy', shares: '', price: '', note: '' })

async function openTradeModal(sig) {
  tradeSignal.value      = sig
  tradeMode.value        = sig.action === 'position' ? 'position' : 'buy'
  tradeMsgErr.value      = ''
  tradeSaving.value      = false
  tradePriceSource.value = ''
  Object.assign(tradeForm, {
    date:   todayStr(),
    action: 'buy',
    shares: '',
    price:  sig.close ?? '',
    note:   `按信号买入 ${sig.date}`,
  })
  showTradeModal.value = true

  tradePriceLoading.value = true
  const rt = await fetchRealtimePrice(sig.code)
  tradePriceLoading.value = false
  if (rt?.price) { tradeForm.price = rt.price; tradePriceSource.value = rt.source }
}

async function submitTrade() {
  const uid = store.currentUser?.id
  if (!uid)                                  { tradeMsgErr.value = '未登录'; return }
  if (!tradeForm.shares || !tradeForm.price) { tradeMsgErr.value = '请填写数量和价格'; return }
  tradeSaving.value = true
  tradeMsgErr.value = ''
  try {
    if (tradeMode.value === 'buy') {
      await api('POST', `/api/transactions/${uid}`, {
        date:     tradeForm.date,
        action:   tradeForm.action,
        etf_code: tradeSignal.value.code,
        etf_name: tradeSignal.value.name,
        shares:   Number(tradeForm.shares),
        price:    Number(tradeForm.price),
        note:     tradeForm.note,
      })
    } else {
      await api('POST', `/api/portfolio/${uid}/positions`, {
        code:       tradeSignal.value.code,
        name:       tradeSignal.value.name,
        shares:     Number(tradeForm.shares),
        cost_price: Number(tradeForm.price),
        buy_date:   tradeForm.date,
      })
    }
    showTradeModal.value = false
    store.status = `已记录 ${tradeSignal.value.name} ✓`
  } catch (e) { tradeMsgErr.value = e.message }
  finally { tradeSaving.value = false }
}
</script>

<style scoped>
.input {
  @apply w-full rounded-xl px-3.5 py-2.5 text-sm bg-surface-2 text-label-1 border border-transparent
         focus:outline-none focus:ring-2 focus:ring-sys-blue focus:border-transparent transition;
}
.field-label { @apply block text-xs font-medium text-label-2 mb-1.5; }

.modal-overlay {
  @apply fixed inset-0 flex items-center justify-center z-50;
  background: rgba(0,0,0,.55);
  backdrop-filter: blur(4px);
}
.modal-box { @apply w-96 p-6; }
.help-box  { @apply w-full p-6 flex flex-col; max-width: 760px; max-height: 80vh; }

.drawer-overlay {
  @apply fixed inset-0 flex justify-end z-50;
  background: rgba(0,0,0,.5);
  backdrop-filter: blur(2px);
}
.drawer-panel {
  @apply h-full flex flex-col bg-surface-1 border-l border-hairline;
  width: 680px;
  max-width: 92vw;
}
.drawer-enter-active, .drawer-leave-active { transition: opacity .2s ease; }
.drawer-enter-from, .drawer-leave-to { opacity: 0; }
.drawer-enter-active .drawer-panel, .drawer-leave-active .drawer-panel { transition: transform .25s ease; }
.drawer-enter-from .drawer-panel, .drawer-leave-to .drawer-panel { transform: translateX(100%); }
</style>
