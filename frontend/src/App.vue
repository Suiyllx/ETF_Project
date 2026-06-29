<template>
  <!-- Login page -->
  <LoginView v-if="!store.isLoggedIn" />

  <!-- Main app -->
  <template v-else>

    <!-- ── Header ───────────────────────────────────────── -->
    <header class="flex-shrink-0 flex items-center justify-between px-5 backdrop-blur-2xl backdrop-saturate-150 border-b border-hairline"
            style="height:52px;background:var(--nav-bg)">
      <!-- Logo -->
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-xl flex items-center justify-center text-white bg-sys-blue">
          <ChartNoAxesCombined :size="18" />
        </div>
        <div>
          <h1 class="font-bold text-sm leading-tight tracking-wide text-label-1">ETF 量化管理</h1>
          <p class="text-xs leading-none text-label-2">持仓 · 信号 · 回测</p>
        </div>
      </div>

      <!-- Right: status + theme + user -->
      <div class="flex items-center gap-3">
        <!-- Status pill -->
        <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium" :class="statusClasses">
          <span class="w-1.5 h-1.5 rounded-full" :class="statusDotClasses"></span>
          {{ store.status }}
        </div>

        <!-- Theme toggle -->
        <button class="w-7 h-7 rounded-lg flex items-center justify-center bg-surface-2 hover:bg-surface-3 text-label-2 transition"
                :aria-label="store.darkMode ? '切换到浅色模式' : '切换到深色模式'"
                @click="store.toggleDarkMode()">
          <Moon v-if="store.darkMode" :size="14" />
          <Sun v-else :size="14" />
        </button>

        <!-- Divider -->
        <div class="h-4 w-px bg-hairline"></div>

        <!-- User -->
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold"
               :style="{background: avatarColor(store.currentUser?.name)}">
            {{ store.currentUser?.name?.[0]?.toUpperCase() }}
          </div>
          <span class="text-sm font-medium text-label-1">{{ store.currentUser?.name }}</span>
          <Badge v-if="store.isAdmin" tone="orange" label="管理员" />
          <button class="text-xs px-2.5 py-1 rounded-lg font-medium transition ml-1 bg-surface-2 text-label-2 hover:bg-surface-3 hover:text-label-1"
                  @click="logout">退出</button>
        </div>
      </div>
    </header>

    <!-- ── Body ─────────────────────────────────────────── -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Sidebar nav -->
      <nav class="flex-shrink-0 flex flex-col py-3 px-2 bg-surface-1 border-r border-hairline" style="width:180px">

        <!-- Nav items -->
        <div class="space-y-0.5">
          <div v-for="item in visibleNav" :key="item.key"
               class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm cursor-pointer transition-all select-none"
               :class="page === item.key
                 ? 'bg-sys-blueDim text-sys-blue font-semibold'
                 : 'text-label-2 hover:bg-surface-2 hover:text-label-1'"
               @click="page = item.key">
            <component :is="item.icon" :size="17" class="flex-shrink-0" />
            <span>{{ item.label }}</span>
          </div>
        </div>

        <!-- Spacer -->
        <div class="flex-1"></div>

        <!-- Admin section label -->
        <div v-if="store.isAdmin" class="px-3 mb-2">
          <div class="text-xs font-semibold tracking-widest uppercase text-label-3">管理</div>
        </div>

        <!-- Bottom: date -->
        <div class="px-3 py-3 text-xs text-label-3 border-t border-hairline">
          {{ dateStr }}
        </div>
      </nav>

      <!-- Main content -->
      <main class="flex-1 overflow-hidden flex flex-col app-bg">
        <PortfolioView v-if="page === 'portfolio'" class="flex-1 min-h-0" />
        <EtfView v-else-if="page === 'market'" class="flex-1 min-h-0" />
        <div v-else class="flex-1 overflow-y-auto">
          <SignalView   v-if="page === 'signals'" />
          <ModelView    v-if="page === 'model'  && store.isAdmin" />
          <BacktestView v-if="page === 'backtest' && store.isAdmin" />
          <EmailView    v-if="page === 'emails'   && store.isAdmin" />
          <SystemView   v-if="page === 'system'   && store.isAdmin" />
        </div>
      </main>

    </div>
  </template>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { store } from './store.js'
import {
  ChartNoAxesCombined, Wallet, Radar, LineChart, SlidersHorizontal,
  FlaskConical, Mail, Settings, Moon, Sun,
} from '@lucide/vue'
import Badge          from './components/base/Badge.vue'
import LoginView     from './views/LoginView.vue'
import PortfolioView from './views/PortfolioView.vue'
import SignalView    from './views/SignalView.vue'
import EtfView       from './views/EtfView.vue'
import BacktestView  from './views/BacktestView.vue'
import EmailView     from './views/EmailView.vue'
import SystemView    from './views/SystemView.vue'
import ModelView     from './views/ModelView.vue'

const page = ref('portfolio')

const allNav = [
  { key: 'portfolio', icon: Wallet,            label: '持仓管理', adminOnly: false },
  { key: 'signals',   icon: Radar,             label: '信号看板', adminOnly: false },
  { key: 'market',    icon: LineChart,         label: 'ETF 行情', adminOnly: false },
  { key: 'model',     icon: SlidersHorizontal, label: '模型调参', adminOnly: true  },
  { key: 'backtest',  icon: FlaskConical,      label: '回测结果', adminOnly: true  },
  { key: 'emails',    icon: Mail,              label: '邮件记录', adminOnly: true  },
  { key: 'system',    icon: Settings,          label: '系统状态', adminOnly: true  },
]

const visibleNav = computed(() =>
  allNav.filter(item => !item.adminOnly || store.isAdmin)
)

const dateStr = new Date().toLocaleDateString('zh-CN', {
  month: 'long', day: 'numeric', weekday: 'short',
})

// Avatar color（纯装饰用，与主题色板无关，保留多色区分用户）
const AVATAR_COLORS = ['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#06b6d4','#f43f5e','#84cc16']
function avatarColor(name) {
  return AVATAR_COLORS[(name?.charCodeAt(0) ?? 0) % AVATAR_COLORS.length]
}

// Status pill appearance
const STATUS_TONE_CLASSES = {
  green:  'bg-sys-greenDim text-sys-green',
  red:    'bg-sys-redDim text-sys-red',
  orange: 'bg-sys-orangeDim text-sys-orange',
  gray:   'bg-surface-2 text-label-2',
}
const statusTone = computed(() => {
  const s = store.status
  if (s === '就绪' || s.includes('✓')) return 'green'
  if (s === '未登录') return 'gray'
  if (s.includes('失败') || s.includes('错误')) return 'red'
  return 'orange'
})
const statusClasses    = computed(() => STATUS_TONE_CLASSES[statusTone.value])
const STATUS_DOT_CLASSES = {
  green: 'bg-sys-green', red: 'bg-sys-red', orange: 'bg-sys-orange', gray: 'bg-label-3',
}
const statusDotClasses = computed(() => STATUS_DOT_CLASSES[statusTone.value])

async function logout() {
  await store.logout()
  page.value = 'portfolio'
}

onMounted(() => {
  store.init().catch(() => {})
  window.addEventListener('session:expired', () => {
    store.currentUser = null
    page.value = 'portfolio'
  })
})
</script>
