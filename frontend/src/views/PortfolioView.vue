<template>
  <div class="flex h-full overflow-hidden">

    <!-- ── Left sidebar ──────────────────────────────────── -->
    <aside class="w-56 flex-shrink-0 flex flex-col bg-surface-1 border-r border-hairline">
      <div class="px-4 py-4 flex items-center justify-between flex-shrink-0 border-b border-hairline">
        <span class="text-xs font-semibold tracking-widest uppercase text-label-3">账户</span>
        <button v-if="store.isAdmin"
                class="flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg font-medium transition bg-sys-blueDim text-sys-blue hover:opacity-80"
                @click="openAddUser"><Plus :size="13" /> 新增</button>
      </div>

      <div class="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
        <p v-if="!store.users.length" class="text-center py-8 text-sm text-label-3">暂无用户</p>
        <div v-for="u in store.users" :key="u.id"
             class="flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all"
             :class="selId === u.id ? 'bg-sys-blueDim' : 'hover:bg-surface-2'"
             @click="selectUser(u.id)">
          <div class="w-8 h-8 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
               :style="{ background: avatarColor(u.name) }">
            {{ u.name[0]?.toUpperCase() }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-sm font-medium truncate text-label-1">{{ u.name }}</div>
            <div class="text-xs truncate text-label-2">
              {{ u.email ? u.email.split('@')[0] + '@…' : '未设置邮箱' }}
            </div>
          </div>
          <div class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="u.active ? 'bg-sys-green' : 'bg-label-3'"></div>
        </div>
      </div>
    </aside>

    <!-- ── Main area ──────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto">

      <div v-if="!selId" class="flex flex-col items-center justify-center h-full gap-3 text-label-2">
        <ArrowLeft :size="40" class="opacity-50" />
        <p class="text-lg font-semibold text-label-1">从左侧选择账户</p>
        <p v-if="store.isAdmin" class="text-sm">或点击「+ 新增」创建用户</p>
      </div>

      <template v-else-if="selUser && pf">
        <!-- User header banner -->
        <BaseCard tag="div" class="m-6 mb-0 px-6 py-5 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-2xl font-bold"
                 :style="{ background: avatarColor(selUser.name) }">
              {{ selUser.name[0]?.toUpperCase() }}
            </div>
            <div>
              <div class="flex items-center gap-2 mb-0.5">
                <h2 class="text-xl font-bold text-label-1">{{ selUser.name }}</h2>
                <Badge v-if="selUser.role === 'admin'" tone="orange" label="管理员" />
              </div>
              <p class="text-sm text-label-2">{{ selUser.email || '未设置邮箱' }}</p>
            </div>
          </div>
          <div v-if="store.isAdmin" class="flex gap-2">
            <BaseButton v-if="selId !== store.currentUser?.id" variant="ghost" size="sm" @click="resetPassword(selUser.id)">
              重置密码
            </BaseButton>
            <BaseButton variant="red" size="sm" @click="deleteUser(selUser.id)">删除账户</BaseButton>
          </div>
        </BaseCard>

        <!-- Metric cards -->
        <div class="grid grid-cols-5 gap-3 px-6 pt-5">
          <StatCard label="总资产" :value="fmtCash(totalAssets)" accent="blue" />
          <div class="relative">
            <StatCard label="可用现金" :value="fmtCash(pf.cash)" accent="green" />
            <button class="absolute top-3 right-3 text-xs px-2.5 py-1 rounded-lg font-semibold transition bg-surface-3 text-label-1 hover:bg-sys-blueDim hover:text-sys-blue"
                    @click="showDepositModal = true">+ 入金</button>
          </div>
          <StatCard label="持仓市值" :value="fmtCash(totalMarketValue)"
                    :delta="pricesLoading ? '行情加载中…' : '按实时价估算'" trend="neutral" />
          <StatCard label="总浮盈" :value="pricesLoading ? '…' : fmtProfit(totalProfit)" :accent="profitAccent" />
          <StatCard label="持仓品种" :value="(pf.positions?.length ?? 0) + ' 只'" />
        </div>

        <!-- Today signal banner -->
        <div class="px-6 pt-3">
          <TodaySignalBanner
            :signals="todaySignals"
            :positions="pf?.positions ?? []"
            @buy-signal="onBuySignal"
          />
        </div>

        <!-- Tab bar + content -->
        <div class="px-6 pt-5 pb-6">
          <div class="mb-5">
            <SegmentControl v-model="tab" :options="TABS" />
          </div>

          <!-- 持仓明细 -->
          <PositionTab v-if="tab === 'positions'"
                       :pf="pf" :sel-id="selId" :today-signals="todaySignals"
                       :market-prices="marketPrices" :prices-loading="pricesLoading"
                       :sell-sigs="sellSigs"
                       @refresh="reloadPortfolio" />

          <!-- 交易记录 -->
          <TransactionTab v-else-if="tab === 'transactions'"
                          :transactions="transactions" :pf="pf"
                          :sel-id="selId" :today-signals="todaySignals"
                          :prefill="pendingSignal"
                          @refresh="reloadAll" />

          <!-- 账号设置 -->
          <div v-else-if="tab === 'settings'" class="grid grid-cols-2 gap-4">
            <BaseCard class="p-5">
              <h3 class="font-semibold text-label-1 text-sm mb-4 pb-3 border-b border-hairline">基本信息</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-medium text-label-2 mb-1.5">姓名</label>
                  <input v-model="cfg.name" type="text" class="input" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-label-2 mb-1.5">邮箱（信号推送）</label>
                  <input v-model="cfg.email" type="email" class="input" />
                </div>
                <label class="flex items-center gap-2.5 text-sm text-label-2 cursor-pointer select-none">
                  <input v-model="cfg.active" type="checkbox" class="w-4 h-4 rounded accent-sys-blue" />
                  接收每日推送邮件
                </label>
              </div>
            </BaseCard>

            <BaseCard class="p-5">
              <h3 class="font-semibold text-label-1 text-sm mb-4 pb-3 border-b border-hairline">风控参数</h3>
              <div class="space-y-5">
                <div>
                  <div class="flex justify-between items-center mb-2">
                    <label class="text-xs font-medium text-label-2">单只最大仓位</label>
                    <span class="text-sm font-bold text-sys-blue">{{ fmtPct(cfg.max_position_pct) }}</span>
                  </div>
                  <input v-model.number="cfg.max_position_pct" type="range"
                         min="0.05" max="0.5" step="0.05"
                         class="w-full h-1.5 rounded-full cursor-pointer accent-sys-blue" />
                  <div class="flex justify-between text-xs text-label-3 mt-1"><span>5%</span><span>50%</span></div>
                </div>
                <div>
                  <div class="flex justify-between items-center mb-2">
                    <label class="text-xs font-medium text-label-2">板块最大仓位</label>
                    <span class="text-sm font-bold text-sys-blue">{{ fmtPct(cfg.max_sector_pct) }}</span>
                  </div>
                  <input v-model.number="cfg.max_sector_pct" type="range"
                         min="0.1" max="0.8" step="0.05"
                         class="w-full h-1.5 rounded-full cursor-pointer accent-sys-blue" />
                  <div class="flex justify-between text-xs text-label-3 mt-1"><span>10%</span><span>80%</span></div>
                </div>
              </div>
            </BaseCard>

            <div class="col-span-2 flex justify-end">
              <BaseButton variant="primary" @click="saveSettings">保存设置</BaseButton>
            </div>

            <BaseCard v-if="selId === store.currentUser?.id" class="col-span-2 p-5">
              <h3 class="font-semibold text-label-1 text-sm mb-4 pb-3 border-b border-hairline">修改密码</h3>
              <div class="grid grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-medium text-label-2 mb-1.5">当前密码</label>
                  <input v-model="pwForm.old" type="password" class="input" autocomplete="current-password" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-label-2 mb-1.5">新密码</label>
                  <input v-model="pwForm.new1" type="password" class="input" autocomplete="new-password" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-label-2 mb-1.5">确认新密码</label>
                  <input v-model="pwForm.new2" type="password" class="input" autocomplete="new-password" />
                </div>
              </div>
              <div class="flex items-center justify-between mt-4">
                <span v-if="pwMsg" class="text-sm" :class="pwMsg.ok ? 'text-sys-green' : 'text-sys-red'">{{ pwMsg.text }}</span>
                <span v-else class="text-xs text-label-3">密码至少 4 位</span>
                <BaseButton variant="primary" size="sm" @click="changePassword">修改密码</BaseButton>
              </div>
            </BaseCard>
          </div>

        </div>
      </template>
    </div>

    <!-- ── Modals ─────────────────────────────────────────── -->

    <!-- Add User -->
    <Teleport to="body">
      <div v-if="showUserModal" class="modal-overlay">
        <BaseCard class="modal-box" @click.stop>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-label-1">新增用户</h3>
            <button class="close-btn" @click="showUserModal = false"><X :size="16" /></button>
          </div>
          <div class="space-y-3">
            <div><label class="field-label">姓名 *</label>
              <input v-model="newUser.name" type="text" placeholder="例：张三" class="input" /></div>
            <div><label class="field-label">邮箱 *</label>
              <input v-model="newUser.email" type="email" placeholder="例：user@163.com" class="input" /></div>
            <div><label class="field-label">初始现金（元）</label>
              <input v-model.number="newUser.cash" type="number" class="input" /></div>
            <label class="flex items-center gap-2 text-sm text-label-2 cursor-pointer">
              <input v-model="newUser.active" type="checkbox" class="accent-sys-blue" /> 立即启用
            </label>
            <p class="text-xs text-label-3">初始密码 = 用户名（登录后请通知用户修改）</p>
          </div>
          <div class="flex gap-2 mt-5">
            <BaseButton variant="ghost" class="flex-1" @click="showUserModal = false">取消</BaseButton>
            <BaseButton variant="primary" class="flex-1" @click="submitAddUser">创建账户</BaseButton>
          </div>
        </BaseCard>
      </div>
    </Teleport>

    <!-- Deposit -->
    <Teleport to="body">
      <div v-if="showDepositModal" class="modal-overlay">
        <BaseCard class="modal-box" style="width:340px" @click.stop>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-label-1">增加可用资金</h3>
            <button class="close-btn" @click="showDepositModal = false"><X :size="16" /></button>
          </div>
          <div class="space-y-3">
            <div><label class="field-label">当前余额</label>
              <div class="input text-label-2">{{ fmtCash(pf?.cash ?? 0) }}</div></div>
            <div><label class="field-label">入金金额（元）*</label>
              <input v-model.number="depositAmt" type="number" min="1" step="1000"
                     placeholder="例：50000" class="input" /></div>
            <div v-if="depositAmt > 0" class="flex items-center justify-between text-sm px-1">
              <span class="text-label-2">入金后余额</span>
              <span class="font-bold text-sys-green">
                {{ fmtCash((pf?.cash ?? 0) + Number(depositAmt)) }}
              </span>
            </div>
          </div>
          <div class="flex gap-2 mt-5">
            <BaseButton variant="ghost" class="flex-1" @click="showDepositModal = false">取消</BaseButton>
            <BaseButton variant="green" class="flex-1" @click="submitDeposit">确认入金</BaseButton>
          </div>
        </BaseCard>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { store } from '../store.js'
import { api, fmtCash, fmtPct, todayStr } from '../api.js'
import PositionTab        from '../components/PositionTab.vue'
import TransactionTab     from '../components/TransactionTab.vue'
import TodaySignalBanner  from '../components/TodaySignalBanner.vue'
import BaseCard        from '../components/base/BaseCard.vue'
import BaseButton      from '../components/base/BaseButton.vue'
import Badge           from '../components/base/Badge.vue'
import StatCard        from '../components/base/StatCard.vue'
import SegmentControl  from '../components/base/SegmentControl.vue'
import { Plus, ArrowLeft, X } from '@lucide/vue'

const TABS = [
  { key: 'positions',    label: '持仓明细' },
  { key: 'transactions', label: '交易记录' },
  { key: 'settings',     label: '账号设置' },
]

const AVATAR_COLORS = ['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#06b6d4','#f43f5e','#84cc16']
function avatarColor(name) {
  return AVATAR_COLORS[(name?.charCodeAt(0) ?? 0) % AVATAR_COLORS.length]
}

// ── State ─────────────────────────────────────────────────────
const selId        = ref(null)
const tab          = ref('positions')
const pendingSignal = ref(null)
const pf          = ref(null)
const transactions = ref([])
const todaySignals = ref([])

const showUserModal    = ref(false)
const showDepositModal = ref(false)
const depositAmt       = ref('')
const marketPrices     = ref({})
const pricesLoading    = ref(false)
const sellSigs         = ref({})   // { [code]: trigger }

const cfg     = reactive({ name: '', email: '', cash: 0, max_position_pct: 0.3, max_sector_pct: 0.5, active: true })
const newUser = reactive({ name: '', email: '', cash: 100000, active: true })
const pwForm  = reactive({ old: '', new1: '', new2: '' })
const pwMsg   = ref(null)

// ── Computed ──────────────────────────────────────────────────
const selUser = computed(() => store.users.find(u => u.id === selId.value))
const totalCost = computed(() =>
  (pf.value?.positions ?? []).reduce((s, p) => s + p.shares * p.cost_price, 0)
)
const totalMarketValue = computed(() =>
  (pf.value?.positions ?? []).reduce((s, p) => {
    const price = marketPrices.value[p.code] ?? p.cost_price
    return s + p.shares * price
  }, 0)
)
const totalProfit = computed(() =>
  (pf.value?.positions ?? []).reduce((s, p) => {
    const price = marketPrices.value[p.code]
    return price != null ? s + p.shares * (price - p.cost_price) : s
  }, 0)
)
const totalAssets = computed(() => (pf.value?.cash ?? 0) + totalMarketValue.value)
const profitAccent = computed(() => {
  if (pricesLoading.value || !Object.keys(marketPrices.value).length) return ''
  return totalProfit.value >= 0 ? 'green' : 'red'
})

function fmtProfit(v) {
  const abs = Math.abs(Math.round(v || 0))
  return (v >= 0 ? '+¥' : '-¥') + abs.toLocaleString('zh-CN')
}

watch(selUser, u => {
  if (!u) return
  cfg.name = u.name; cfg.email = u.email ?? ''; cfg.active = u.active
  Object.assign(pwForm, { old: '', new1: '', new2: '' }); pwMsg.value = null
})
watch(pf, p => {
  if (!p) return
  cfg.cash = p.cash; cfg.max_position_pct = p.max_position_pct; cfg.max_sector_pct = p.max_sector_pct
})

// ── Data loading ──────────────────────────────────────────────
async function loadSellSignals() {
  try {
    const data = await api('GET', '/api/sell-signals')
    const map = {}
    for (const s of data.signals ?? []) map[s.code] = s.trigger
    sellSigs.value = map
  } catch { sellSigs.value = {} }
}

async function loadMarketPrices() {
  const positions = pf.value?.positions ?? []
  if (!positions.length) { marketPrices.value = {}; return }
  pricesLoading.value = true
  const results = await Promise.allSettled(
    positions.map(p => api('GET', `/api/realtime-price/${p.code}`))
  )
  const map = {}
  results.forEach((r, i) => {
    if (r.status === 'fulfilled' && r.value?.price) {
      map[positions[i].code] = r.value.price
    }
  })
  marketPrices.value  = map
  pricesLoading.value = false
}

async function selectUser(id) {
  selId.value = id; tab.value = 'positions'
  transactions.value = []; pf.value = null; marketPrices.value = {}; sellSigs.value = {}
  try {
    [pf.value, transactions.value] = await Promise.all([
      api('GET', `/api/portfolio/${id}`),
      api('GET', `/api/transactions/${id}`),
    ])
    await Promise.all([loadMarketPrices(), loadSellSignals()])
  } catch (e) { store.status = '加载失败: ' + e.message }
}

async function reloadPortfolio() {
  if (!selId.value) return
  try {
    pf.value = await api('GET', `/api/portfolio/${selId.value}`)
    await Promise.all([loadMarketPrices(), loadSellSignals()])
  } catch {}
}

async function reloadAll() {
  if (!selId.value) return
  try {
    [pf.value, transactions.value] = await Promise.all([
      api('GET', `/api/portfolio/${selId.value}`),
      api('GET', `/api/transactions/${selId.value}`),
    ])
    await Promise.all([loadMarketPrices(), loadSellSignals()])
  } catch {}
}

onMounted(async () => {
  if (store.currentUser && !store.isAdmin) await selectUser(store.currentUser.id)
  try {
    const d = await api('GET', '/api/signals')
    todaySignals.value = (d.signals ?? []).slice(0, 8)
  } catch {}
})

// ── User management ───────────────────────────────────────────
function openAddUser() {
  Object.assign(newUser, { name: '', email: '', cash: 100000, active: true })
  showUserModal.value = true
}

async function submitAddUser() {
  if (!newUser.name || !newUser.email) { alert('姓名和邮箱不能为空'); return }
  try {
    store.status = '创建中…'
    const u = await api('POST', '/api/users', { ...newUser })
    showUserModal.value = false
    await store.refreshUsers()
    store.status = '账户已创建 ✓'
    await selectUser(u.id)
  } catch (e) { store.status = '创建失败: ' + e.message }
}

async function deleteUser(id) {
  const u = store.users.find(u => u.id === id)
  if (!confirm(`确认删除用户「${u.name}」及其所有持仓和交易记录？此操作不可撤销。`)) return
  try {
    await api('DELETE', `/api/users/${id}`)
    selId.value = null; pf.value = null
    await store.refreshUsers()
    store.status = '已删除 ✓'
  } catch (e) { store.status = '删除失败: ' + e.message }
}

async function resetPassword(id) {
  const pw = prompt('为该用户设置新密码（留空则重置为用户名）:')
  if (pw === null) return
  try {
    await api('POST', `/api/users/${id}/reset-password`, { password: pw.trim() || id })
    store.status = '密码已重置 ✓'
  } catch (e) { store.status = '重置失败: ' + e.message }
}

// ── Settings ──────────────────────────────────────────────────
async function saveSettings() {
  try {
    store.status = '保存中…'
    await api('PUT', `/api/users/${selId.value}`, { name: cfg.name, email: cfg.email, active: cfg.active })
    pf.value = await api('PUT', `/api/portfolio/${selId.value}`, {
      cash: cfg.cash, max_position_pct: cfg.max_position_pct, max_sector_pct: cfg.max_sector_pct,
    })
    await store.refreshUsers()
    store.status = '已保存 ✓'
  } catch (e) { store.status = '保存失败: ' + e.message }
}

async function changePassword() {
  pwMsg.value = null
  if (pwForm.new1 !== pwForm.new2) { pwMsg.value = { ok: false, text: '两次新密码不一致' }; return }
  if (pwForm.new1.length < 4)      { pwMsg.value = { ok: false, text: '新密码至少 4 位' };   return }
  try {
    await api('POST', '/api/auth/change-password', { old_password: pwForm.old, new_password: pwForm.new1 })
    Object.assign(pwForm, { old: '', new1: '', new2: '' })
    pwMsg.value = { ok: true, text: '密码已修改 ✓' }
  } catch (e) { pwMsg.value = { ok: false, text: e.message } }
}

// ── Signal banner → transaction prefill ──────────────────────
function onBuySignal(sig) {
  tab.value = 'transactions'
  pendingSignal.value = sig
  setTimeout(() => { pendingSignal.value = null }, 0)
}

// ── Deposit ───────────────────────────────────────────────────
async function submitDeposit() {
  const amt = Number(depositAmt.value)
  if (!amt || amt <= 0) { alert('请输入有效金额'); return }
  try {
    store.status = '入金中…'
    pf.value = await api('PUT', `/api/portfolio/${selId.value}`, { cash: (pf.value?.cash ?? 0) + amt })
    cfg.cash = pf.value.cash
    depositAmt.value = ''
    showDepositModal.value = false
    store.status = '入金成功 ✓'
  } catch (e) { store.status = '入金失败: ' + e.message }
}
</script>

<style scoped>
.input {
  @apply w-full rounded-xl px-3.5 py-2.5 text-sm bg-surface-2 text-label-1 border border-transparent
         focus:outline-none focus:ring-2 focus:ring-sys-blue focus:border-transparent transition;
}
.field-label  { @apply block text-xs font-medium text-label-2 mb-1.5; }
.close-btn    { @apply w-8 h-8 flex items-center justify-center rounded-lg text-label-2 hover:text-label-1 hover:bg-surface-2 transition-all; }
.modal-overlay { @apply fixed inset-0 flex items-center justify-center z-50; background: rgba(0,0,0,.55); backdrop-filter: blur(4px); }
.modal-box    { @apply w-96 p-6; }
</style>
