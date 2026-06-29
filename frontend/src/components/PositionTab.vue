<template>
  <BaseCard class="overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4 border-b border-hairline">
      <div class="flex items-center gap-2">
        <span class="font-semibold text-label-1">持仓明细</span>
        <Badge tone="blue" :label="(pf.positions?.length ?? 0) + ' 只'" />
      </div>
      <BaseButton variant="primary" size="sm" @click="openAdd">
        <Upload :size="14" /> 导入初始持仓
      </BaseButton>
    </div>

    <table class="w-full text-sm">
      <thead class="bg-surface-2">
        <tr>
          <th class="px-4 py-3 text-left text-xs font-semibold text-label-2">标的</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">股数</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">成本价</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">成本市值</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">现价</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">现值</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">浮盈</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">浮盈%</th>
          <th class="px-4 py-3 text-center text-xs font-semibold text-label-2">买入日期</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-label-2">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!pf.positions?.length">
          <td colspan="10" class="text-center py-14 text-label-2">
            <Inbox :size="36" class="mx-auto mb-3 opacity-50" />
            <p class="font-medium text-label-1">暂无持仓</p>
            <p class="text-xs mt-1">点击「导入初始持仓」添加使用平台前的已有持仓</p>
          </td>
        </tr>
        <template v-for="p in pf.positions" :key="p.code">
        <tr class="border-t border-hairline transition-colors hover:bg-surface-2">
          <td class="px-4 py-4">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold bg-sys-blueDim text-sys-blue">
                {{ p.code.slice(-2) }}
              </div>
              <div>
                <div class="flex items-center gap-1.5 font-semibold text-label-1">
                  {{ p.name }}
                  <Badge v-if="sellSigs[p.code]" :type="sellSigs[p.code]" />
                </div>
                <div class="text-xs text-label-2">{{ p.code }}</div>
              </div>
            </div>
          </td>
          <td class="px-4 py-4 text-right text-label-1 font-medium">{{ p.shares.toLocaleString() }}</td>
          <td class="px-4 py-4 text-right text-label-1">¥{{ p.cost_price.toFixed(3) }}</td>
          <td class="px-4 py-4 text-right font-semibold text-label-1">
            {{ fmtCash(p.shares * p.cost_price) }}
          </td>
          <td class="px-4 py-4 text-right">
            <span v-if="pricesLoading" class="text-xs text-label-3">…</span>
            <span v-else-if="marketPrices[p.code]" class="text-label-1">
              ¥{{ marketPrices[p.code].toFixed(3) }}
            </span>
            <span v-else class="text-xs text-label-3">--</span>
          </td>
          <td class="px-4 py-4 text-right font-semibold text-label-1">
            <span v-if="marketPrices[p.code]">{{ fmtCash(p.shares * marketPrices[p.code]) }}</span>
            <span v-else class="text-xs text-label-3">--</span>
          </td>
          <td class="px-4 py-4 text-right font-semibold">
            <template v-if="marketPrices[p.code]">
              <span :class="profitToneClass(p.shares * (marketPrices[p.code] - p.cost_price))">
                {{ fmtProfit(p.shares * (marketPrices[p.code] - p.cost_price)) }}
              </span>
            </template>
            <span v-else class="text-xs text-label-3">--</span>
          </td>
          <td class="px-4 py-4 text-right font-semibold">
            <template v-if="marketPrices[p.code]">
              <span :class="profitToneClass(marketPrices[p.code] - p.cost_price)">
                {{ fmtPct2((marketPrices[p.code] - p.cost_price) / p.cost_price * 100) }}
              </span>
            </template>
            <span v-else class="text-xs text-label-3">--</span>
          </td>
          <td class="px-4 py-4 text-center">
            <Badge tone="gray" :label="p.buy_date" />
          </td>
          <td class="px-4 py-4 text-right">
            <div class="flex items-center justify-end gap-2">
              <button class="text-xs font-semibold px-2 py-1 rounded-lg transition"
                      :class="activeQuick?.code===p.code&&activeQuick.action==='buy'
                        ? 'bg-sys-green text-white' : 'bg-sys-greenDim text-sys-green'"
                      @click="openQuick(p.code,'buy')">+加仓</button>
              <button class="text-xs font-semibold px-2 py-1 rounded-lg transition"
                      :class="activeQuick?.code===p.code&&activeQuick.action==='sell'
                        ? 'bg-sys-red text-white' : 'bg-sys-redDim text-sys-red'"
                      @click="openQuick(p.code,'sell')">-减持</button>
              <span class="text-label-3 select-none text-xs">|</span>
              <button class="text-xs font-medium text-sys-blue" @click="openEdit(p.code)">编辑</button>
              <button class="text-xs font-medium text-label-2" @click="deletePos(p.code)">删除</button>
            </div>
          </td>
        </tr>
        <tr v-if="activeQuick?.code === p.code" :class="activeQuick.action === 'buy' ? 'bg-sys-greenDim' : 'bg-sys-redDim'">
          <td colspan="10" class="px-6 py-3">
            <div class="flex items-center gap-4 flex-wrap">
              <span class="text-sm font-semibold flex-shrink-0"
                    :class="activeQuick.action==='buy' ? 'text-sys-green' : 'text-sys-red'">
                {{ activeQuick.action==='buy' ? '+ 加仓' : '- 减持' }} · {{ p.name }}
              </span>
              <div class="flex items-center gap-1.5">
                <label class="text-xs text-label-2 flex-shrink-0">股数</label>
                <input v-model.number="quickForm.shares" type="number" min="100" step="100"
                       class="rounded-lg px-2.5 py-1.5 text-sm w-28 bg-surface-1 text-label-1 border border-hairline focus:outline-none focus:ring-2 focus:ring-sys-blue"
                       placeholder="100 股" @keyup.enter="submitQuick(p)" />
              </div>
              <div class="flex items-center gap-1.5">
                <label class="text-xs text-label-2 flex-shrink-0">价格（元）</label>
                <input v-model.number="quickForm.price" type="number" step="0.001"
                       class="rounded-lg px-2.5 py-1.5 text-sm w-24 bg-surface-1 text-label-1 border border-hairline focus:outline-none focus:ring-2 focus:ring-sys-blue"
                       placeholder="0.000" @keyup.enter="submitQuick(p)" />
              </div>
              <div v-if="quickQuota > 0" class="text-xs text-label-2 flex-shrink-0">
                {{ activeQuick.action==='buy' ? '扣款' : '到账' }}
                <span class="font-semibold text-label-1">{{ fmtCash(quickQuota) }}</span>
                <span class="mx-1.5 text-label-3">·</span>
                现金将变为
                <span :class="activeQuick.action==='buy' && pf.cash-quickQuota<0 ? 'text-sys-red font-semibold' : 'text-label-1'">
                  {{ fmtCash(activeQuick.action==='buy' ? pf.cash-quickQuota : pf.cash+quickQuota) }}
                </span>
              </div>
              <div class="ml-auto flex items-center gap-2 flex-shrink-0">
                <BaseButton :variant="activeQuick.action==='buy' ? 'green' : 'red'" size="sm" @click="submitQuick(p)">
                  确认
                </BaseButton>
                <BaseButton variant="ghost" size="sm" @click="activeQuick = null">取消</BaseButton>
              </div>
            </div>
          </td>
        </tr>
        </template>
      </tbody>
    </table>
  </BaseCard>

  <!-- 导入/编辑持仓 Modal -->
  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay">
      <BaseCard class="modal-box" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-bold text-label-1">{{ modalTitle }}</h3>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-label-2 hover:text-label-1 hover:bg-surface-2 transition-all"
                  @click="showModal = false"><X :size="16" /></button>
        </div>

        <div v-if="editCode === null"
             class="flex items-start gap-2 text-xs text-sys-blue bg-sys-blueDim rounded-lg px-3 py-2 mb-3">
          <Info :size="14" class="mt-0.5 flex-shrink-0" />
          <span>仅用于导入使用平台前的已有持仓，<strong>不扣减现金余额</strong>。日常交易请使用「新增交易」按钮。</span>
        </div>

        <div class="space-y-3">
          <div>
            <label class="field-label">ETF 代码 *</label>
            <div v-if="editCode === null && todaySignals.length" class="mb-2">
              <span class="text-xs text-label-2 mr-1.5">今日推荐：</span>
              <button v-for="s in todaySignals" :key="s.code"
                      class="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full mr-1 mb-1 transition"
                      :class="form.code === s.code ? 'bg-sys-green text-white' : 'bg-sys-greenDim text-sys-green'"
                      @click="form.code = s.code; form.name = s.name">
                {{ s.name }}
                <span class="opacity-70">{{ (s.prob_up * 100).toFixed(0) }}%</span>
              </button>
            </div>
            <EtfSearch v-model="form.code" v-model:name="form.name"
                       :readonly="editCode !== null"
                       placeholder="输入代码或名称搜索，例：沪深300" />
          </div>
          <div>
            <label class="field-label">名称</label>
            <input v-model="form.name" type="text" readonly class="input text-label-2" />
          </div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="field-label">股数 *</label>
              <input v-model.number="form.shares" type="number" placeholder="例：1000" class="input" />
            </div>
            <div class="flex-1">
              <label class="field-label">成本价（元）*</label>
              <input v-model.number="form.cost_price" type="number" step="0.001"
                     placeholder="例：3.250" class="input" />
            </div>
          </div>
          <div>
            <label class="field-label">买入日期</label>
            <input v-model="form.buy_date" type="date" class="input" />
          </div>
        </div>

        <div class="flex gap-2 mt-5">
          <BaseButton variant="ghost" class="flex-1" @click="showModal = false">取消</BaseButton>
          <BaseButton variant="primary" class="flex-1" @click="submit">保存</BaseButton>
        </div>
      </BaseCard>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { api, fmtCash, todayStr } from '../api.js'
import { store } from '../store.js'
import EtfSearch from './EtfSearch.vue'
import BaseCard   from './base/BaseCard.vue'
import BaseButton from './base/BaseButton.vue'
import Badge      from './base/Badge.vue'
import { Upload, Inbox, Info, X } from '@lucide/vue'

const props = defineProps({
  pf:            { type: Object,  required: true },
  selId:         { type: String,  required: true },
  todaySignals:  { type: Array,   default: () => [] },
  marketPrices:  { type: Object,  default: () => ({}) },
  pricesLoading: { type: Boolean, default: false },
  sellSigs:      { type: Object,  default: () => ({}) },
})
const emit = defineEmits(['refresh'])

const activeQuick = ref(null)       // { code, action: 'buy'|'sell' }
const quickForm   = reactive({ shares: '', price: '' })
const quickQuota  = computed(() =>
  (!quickForm.shares || !quickForm.price) ? 0
  : Math.round(Number(quickForm.shares) * Number(quickForm.price) * 100) / 100
)

function openQuick(code, action) {
  if (activeQuick.value?.code === code && activeQuick.value?.action === action) {
    activeQuick.value = null; return
  }
  activeQuick.value = { code, action }
  quickForm.shares  = ''
  const pos = props.pf.positions.find(p => p.code === code)
  quickForm.price   = String(props.marketPrices[code] ?? pos?.cost_price ?? '')
}

async function submitQuick(pos) {
  if (!quickForm.shares || !quickForm.price) { alert('请填写股数和价格'); return }
  const { code, action } = activeQuick.value
  if (action === 'sell' && Number(quickForm.shares) > pos.shares) {
    alert(`最多可减持 ${pos.shares.toLocaleString()} 股`); return
  }
  try {
    store.status = action === 'buy' ? '加仓中…' : '减持中…'
    await api('POST', `/api/transactions/${props.selId}`, {
      action,
      etf_code: pos.code,
      etf_name: pos.name,
      shares:   Number(quickForm.shares),
      price:    Number(quickForm.price),
      date:     todayStr(),
      note:     action === 'buy' ? '快速加仓' : '快速减持',
    })
    activeQuick.value = null
    store.status = action === 'buy' ? '加仓成功 ✓' : '减持成功 ✓'
    emit('refresh')
  } catch (e) {
    store.status = (action === 'buy' ? '加仓' : '减持') + '失败: ' + e.message
  }
}

function profitToneClass(v) {
  return v > 0 ? 'text-sys-green' : v < 0 ? 'text-sys-red' : 'text-label-3'
}
function fmtProfit(v) {
  const abs = Math.abs(Math.round(v || 0))
  return (v >= 0 ? '+¥' : '-¥') + abs.toLocaleString('zh-CN')
}
function fmtPct2(v) {
  return (v >= 0 ? '+' : '') + (v || 0).toFixed(2) + '%'
}

const showModal  = ref(false)
const editCode   = ref(null)
const modalTitle = ref('导入初始持仓')
const form = reactive({ code: '', name: '', shares: '', cost_price: '', buy_date: todayStr() })

function openAdd() {
  editCode.value   = null
  modalTitle.value = '导入初始持仓'
  Object.assign(form, { code: '', name: '', shares: '', cost_price: '', buy_date: todayStr() })
  showModal.value  = true
}

function openEdit(code) {
  const pos = props.pf?.positions?.find(p => p.code === code)
  if (!pos) return
  editCode.value   = code
  modalTitle.value = '编辑持仓'
  Object.assign(form, {
    code: pos.code, name: pos.name,
    shares: pos.shares, cost_price: pos.cost_price, buy_date: pos.buy_date,
  })
  showModal.value = true
}

async function submit() {
  const code = form.code.trim()
  const name = form.name || store.etfList[code] || code
  if (!code || isNaN(form.shares) || isNaN(form.cost_price)) {
    alert('请填写代码、股数和成本价'); return
  }
  try {
    store.status = '保存中…'
    await api('POST', `/api/portfolio/${props.selId}/positions`, {
      code, name,
      shares:     Number(form.shares),
      cost_price: Number(form.cost_price),
      buy_date:   form.buy_date,
    })
    showModal.value = false
    store.status = '已保存 ✓'
    emit('refresh')
  } catch (e) { store.status = '保存失败: ' + e.message }
}

async function deletePos(code) {
  if (!confirm(`确认删除持仓 ${code}？`)) return
  try {
    await api('DELETE', `/api/portfolio/${props.selId}/positions/${code}`)
    store.status = '已删除 ✓'
    emit('refresh')
  } catch (e) { store.status = '删除失败: ' + e.message }
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
</style>
