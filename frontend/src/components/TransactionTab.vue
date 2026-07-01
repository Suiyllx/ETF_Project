<template>
  <BaseCard class="overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4 border-b border-hairline">
      <div class="flex items-center gap-2">
        <span class="font-semibold text-label-1">交易记录</span>
        <Badge tone="blue" :label="transactions.length + ' 笔'" />
      </div>
      <BaseButton variant="primary" size="sm" @click="openAdd">
        <Plus :size="14" /> 新增交易
      </BaseButton>
    </div>

    <table class="w-full text-sm">
      <thead class="bg-surface-2">
        <tr>
          <th class="px-5 py-3 text-left text-xs font-semibold text-label-2">日期</th>
          <th class="px-5 py-3 text-left text-xs font-semibold text-label-2">方向</th>
          <th class="px-5 py-3 text-left text-xs font-semibold text-label-2">标的</th>
          <th class="px-5 py-3 text-right text-xs font-semibold text-label-2">数量</th>
          <th class="px-5 py-3 text-right text-xs font-semibold text-label-2">成交价</th>
          <th class="px-5 py-3 text-right text-xs font-semibold text-label-2">金额</th>
          <th class="px-5 py-3 text-right text-xs font-semibold text-label-2">实现盈亏</th>
          <th class="px-5 py-3 text-left text-xs font-semibold text-label-2">备注</th>
          <th class="px-5 py-3"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!transactions.length">
          <td colspan="9" class="text-center py-14 text-label-2">
            <ClipboardList :size="36" class="mx-auto mb-3 opacity-50" />
            <p class="font-medium text-label-1">暂无交易记录</p>
            <p class="text-xs mt-1">点击「新增交易」添加</p>
          </td>
        </tr>
        <tr v-for="tx in transactions" :key="tx.id" class="border-t border-hairline transition-colors hover:bg-surface-2">
          <td class="px-5 py-3.5">
            <Badge tone="gray" :label="tx.date" />
          </td>
          <td class="px-5 py-3.5">
            <Badge :tone="tx.action === 'buy' ? 'green' : 'red'" :label="tx.action === 'buy' ? '▲ 买入' : '▼ 卖出'" />
          </td>
          <td class="px-5 py-3.5">
            <div class="font-semibold text-label-1">{{ tx.etf_code }}</div>
            <div class="text-xs text-label-2">{{ tx.etf_name }}</div>
          </td>
          <td class="px-5 py-3.5 text-right text-label-1">{{ tx.shares.toLocaleString() }}</td>
          <td class="px-5 py-3.5 text-right text-label-2">¥{{ tx.price.toFixed(3) }}</td>
          <td class="px-5 py-3.5 text-right font-semibold" :class="tx.action === 'sell' ? 'text-sys-green' : 'text-label-1'">
            {{ tx.action === 'sell' ? '+' : '' }}{{ fmtCash(tx.amount) }}
          </td>
          <td class="px-5 py-3.5 text-right font-semibold"
              :class="tx.action === 'sell' && tx.realized_pnl != null ? (tx.realized_pnl >= 0 ? 'text-sys-green' : 'text-sys-red') : 'text-label-3'">
            {{ tx.action === 'sell' && tx.realized_pnl != null ? (tx.realized_pnl >= 0 ? '+' : '') + fmtCash(tx.realized_pnl) : '—' }}
          </td>
          <td class="px-5 py-3.5 text-xs text-label-2 max-w-32 truncate">{{ tx.note || '—' }}</td>
          <td class="px-5 py-3.5 text-right">
            <button class="text-xs font-medium text-sys-red" @click="deleteTx(tx)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </BaseCard>

  <!-- 新增交易 Modal -->
  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay">
      <BaseCard class="modal-box" style="width:420px" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-bold text-label-1">新增交易记录</h3>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-label-2 hover:text-label-1 hover:bg-surface-2 transition-all"
                  @click="showModal = false"><X :size="16" /></button>
        </div>

        <div class="space-y-3">
          <!-- 方向 -->
          <div>
            <label class="field-label">交易方向</label>
            <div class="flex gap-2">
              <button v-for="opt in [{v:'buy',label:'▲ 买入'},{v:'sell',label:'▼ 卖出'}]" :key="opt.v"
                      class="flex-1 py-2 rounded-xl text-sm font-semibold border transition"
                      :class="form.action === opt.v
                        ? (opt.v === 'buy' ? 'bg-sys-green text-white border-sys-green' : 'bg-sys-red text-white border-sys-red')
                        : 'bg-surface-1 text-label-2 border-hairline'"
                      @click="form.action = opt.v">{{ opt.label }}</button>
            </div>
          </div>

          <!-- 标的快捷 -->
          <div>
            <label class="field-label">ETF 标的 *</label>
            <div v-if="pf?.positions?.length || todaySignals.length" class="mb-2">
              <div v-if="pf?.positions?.length" class="mb-1.5">
                <span class="text-xs text-label-2 mr-1.5">持仓中：</span>
                <button v-for="p in pf.positions" :key="p.code"
                        class="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full mr-1 mb-1 transition"
                        :class="form.etf_code === p.code ? 'bg-sys-blue text-white' : 'bg-sys-blueDim text-sys-blue'"
                        @click="quickPick(p.code, p.name)">
                  {{ p.name }}
                </button>
              </div>
              <div v-if="todaySignals.length">
                <span class="text-xs text-label-2 mr-1.5">今日推荐：</span>
                <button v-for="s in todaySignals" :key="s.code"
                        class="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full mr-1 mb-1 transition"
                        :class="form.etf_code === s.code ? 'bg-sys-green text-white' : 'bg-sys-greenDim text-sys-green'"
                        @click="quickPick(s.code, s.name)">
                  {{ s.name }}
                  <span class="opacity-70">{{ (s.prob_up * 100).toFixed(0) }}%</span>
                </button>
              </div>
            </div>
            <EtfSearch v-model="form.etf_code" v-model:name="form.etf_name"
                       placeholder="输入代码或名称搜索" />
          </div>

          <!-- 日期 / 数量 / 价格 -->
          <div>
            <label class="field-label">交易日期</label>
            <input v-model="form.date" type="date" class="input" />
          </div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="field-label">数量（股）*</label>
              <input v-model.number="form.shares" type="number" placeholder="例：1000" class="input" />
            </div>
            <div class="flex-1">
              <label class="field-label">
                成交价（元）*
                <span v-if="priceLoading" class="ml-1 text-sys-blue font-normal text-xs">拉取中…</span>
                <span v-else-if="priceSource === 'realtime'" class="ml-1 font-normal text-xs text-sys-green">● 实时价</span>
                <span v-else-if="priceSource === 'local_close'" class="ml-1 font-normal text-xs text-label-2">昨收价</span>
              </label>
              <input v-model.number="form.price" type="number" step="0.001" placeholder="例：4.250" class="input" />
            </div>
          </div>

          <!-- 金额合计 -->
          <div class="flex justify-between items-center text-sm px-1 py-1 rounded-lg bg-surface-2">
            <span class="text-label-2 text-xs">金额合计</span>
            <span class="font-bold"
                  :class="txAmount === '—' ? 'text-label-3' : (form.action === 'sell' ? 'text-sys-green' : 'text-label-1')">
              {{ txAmount === '—' ? '—' : (form.action === 'sell' ? '+' : '') + '¥' + Number(txAmount).toLocaleString('zh-CN') }}
            </span>
          </div>

          <div>
            <label class="field-label">备注（可选）</label>
            <input v-model="form.note" type="text" placeholder="例：按信号买入" class="input" />
          </div>
        </div>

        <div class="flex gap-2 mt-5">
          <BaseButton variant="ghost" class="flex-1" @click="showModal = false">取消</BaseButton>
          <BaseButton :variant="form.action === 'sell' ? 'red' : 'primary'" class="flex-1" @click="submit">
            确认{{ form.action === 'buy' ? '买入' : '卖出' }}
          </BaseButton>
        </div>
      </BaseCard>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { api, fmtCash, todayStr, fetchRealtimePrice } from '../api.js'
import { store } from '../store.js'
import EtfSearch  from './EtfSearch.vue'
import BaseCard   from './base/BaseCard.vue'
import BaseButton from './base/BaseButton.vue'
import Badge      from './base/Badge.vue'
import { Plus, ClipboardList, X } from '@lucide/vue'

const props = defineProps({
  transactions: { type: Array, required: true },
  pf:           { type: Object, required: true },
  selId:        { type: String, required: true },
  todaySignals: { type: Array, default: () => [] },
  prefill:      { type: Object, default: null },
})
const emit = defineEmits(['refresh'])

const showModal   = ref(false)
const priceLoading = ref(false)
const priceSource  = ref('')
const form = reactive({
  date: todayStr(), action: 'buy',
  etf_code: '', etf_name: '', shares: '', price: '', note: '',
})

// 来自信号简报的预填：切换到交易 Tab 时自动打开弹窗并填好 ETF
watch(() => props.prefill, (sig) => {
  if (!sig) return
  Object.assign(form, {
    date: todayStr(), action: 'buy',
    etf_code: sig.code, etf_name: sig.name,
    shares: '', price: '', note: '按信号建仓',
  })
  priceSource.value = ''
  showModal.value = true
}, { immediate: true })

const txAmount = computed(() => {
  const s = Number(form.shares), p = Number(form.price)
  return (!isNaN(s) && !isNaN(p) && s > 0 && p > 0) ? (s * p).toFixed(2) : '—'
})

// 自动拉实时价
watch(() => form.etf_code, async (code) => {
  if (!code || !showModal.value) return
  priceSource.value  = ''
  priceLoading.value = true
  const rt = await fetchRealtimePrice(code)
  priceLoading.value = false
  if (rt?.price) { form.price = rt.price; priceSource.value = rt.source }
})

async function quickPick(code, name) {
  form.etf_code = code
  form.etf_name = name || store.etfList[code] || code
}

function openAdd() {
  Object.assign(form, {
    date: todayStr(), action: 'buy',
    etf_code: '', etf_name: '', shares: '', price: '', note: '',
  })
  priceSource.value = ''
  showModal.value   = true
}

async function submit() {
  if (!form.etf_code || !form.shares || !form.price) {
    alert('请填写 ETF、数量和成交价'); return
  }
  try {
    store.status = '保存中…'
    await api('POST', `/api/transactions/${props.selId}`, {
      date:     form.date,
      action:   form.action,
      etf_code: form.etf_code.trim(),
      etf_name: form.etf_name || store.etfList[form.etf_code] || form.etf_code,
      shares:   Number(form.shares),
      price:    Number(form.price),
      note:     form.note,
    })
    showModal.value = false
    store.status = form.action === 'buy' ? '买入已记录 ✓' : '卖出已记录 ✓'
    emit('refresh')
  } catch (e) { store.status = '保存失败: ' + e.message }
}

async function deleteTx(tx) {
  if (!confirm('确认删除这笔交易记录？')) return
  try {
    await api('DELETE', `/api/transactions/${props.selId}/${tx.id}`)
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
.modal-box { @apply p-6; }
</style>
