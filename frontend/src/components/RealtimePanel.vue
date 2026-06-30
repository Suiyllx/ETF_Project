<template>
  <BaseCard class="overflow-hidden">

    <!-- ── Header ─────────────────────────────────────────────── -->
    <div class="flex items-center justify-between px-5 py-3 border-b border-hairline">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-label-1">盘中实时数据</span>
        <span v-if="snap" class="text-xs text-label-3">
          {{ snap.update_time ? snap.update_time.slice(11, 19) : '' }}
          {{ snap.cache_age_s != null ? `· ${snap.cache_age_s}s 前` : '' }}
        </span>
        <span v-if="snap?.cache_age_s > 120"
              class="text-xs text-sys-orange bg-sys-orangeDim px-2 py-0.5 rounded-full">
          数据可能过期
        </span>
      </div>
      <button class="flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg font-medium transition
                     bg-surface-2 text-label-2 hover:text-label-1 disabled:opacity-40"
              :disabled="loading"
              @click="load">
        <RefreshCw :size="12" :class="loading ? 'animate-spin' : ''" />
        刷新
      </button>
    </div>

    <!-- ── Loading ────────────────────────────────────────────── -->
    <div v-if="loading && !snap" class="flex items-center justify-center gap-2 py-10 text-label-2 text-sm">
      <Loader2 :size="20" class="animate-spin" />
      <span>拉取实时数据中（首次约 15 秒）…</span>
    </div>

    <!-- ── Error ──────────────────────────────────────────────── -->
    <div v-else-if="error" class="px-5 py-4 text-xs text-sys-red">{{ error }}</div>

    <!-- ── Metrics grid ───────────────────────────────────────── -->
    <div v-else-if="snap" class="p-4 space-y-3">

      <div class="grid grid-cols-3 gap-3">

        <!-- 1. IOPV & 折溢价 -->
        <div class="rounded-xl bg-surface-2 p-3">
          <div class="text-xs text-label-3 mb-1">IOPV 折溢价</div>
          <div class="text-base font-bold" :class="premiumColor">
            {{ premiumLabel }}
          </div>
          <div class="text-xs mt-1 leading-snug" :class="premiumColor">{{ premiumInterp }}</div>
        </div>

        <!-- 2. 委比 -->
        <div class="rounded-xl bg-surface-2 p-3">
          <div class="text-xs text-label-3 mb-1">委比</div>
          <div class="text-base font-bold" :class="weibiColor">
            {{ snap.wei_bi != null ? (snap.wei_bi > 0 ? '+' : '') + snap.wei_bi + '%' : '—' }}
          </div>
          <div class="text-xs mt-1 leading-snug" :class="weibiColor">{{ weibiInterp }}</div>
        </div>

        <!-- 3. 量比 -->
        <div class="rounded-xl bg-surface-2 p-3">
          <div class="text-xs text-label-3 mb-1">量比</div>
          <div class="text-base font-bold" :class="volRatioColor">
            {{ snap.vol_ratio != null ? snap.vol_ratio + 'x' : '—' }}
          </div>
          <div class="text-xs mt-1 leading-snug" :class="volRatioColor">{{ volRatioInterp }}</div>
        </div>

        <!-- 4. 主力净流入 -->
        <div class="rounded-xl bg-surface-2 p-3">
          <div class="text-xs text-label-3 mb-1">主力净流入</div>
          <div class="text-base font-bold" :class="mainFlowColor">
            {{ fmtFlow(snap.main_net_inflow) }}
          </div>
          <div class="text-xs mt-1 leading-snug" :class="mainFlowColor">
            净占比 {{ snap.main_net_pct != null ? (snap.main_net_pct > 0 ? '+' : '') + snap.main_net_pct + '%' : '—' }}
            · {{ mainFlowInterp }}
          </div>
        </div>

        <!-- 5. 外盘 / 内盘 -->
        <div class="rounded-xl bg-surface-2 p-3">
          <div class="text-xs text-label-3 mb-1">外盘 / 内盘</div>
          <div class="text-base font-bold" :class="outerInnerColor">
            {{ snap.outer_inner != null ? snap.outer_inner : '—' }}
          </div>
          <div class="text-xs mt-1 leading-snug" :class="outerInnerColor">{{ outerInnerInterp }}</div>
        </div>

        <!-- 6. 换手率 -->
        <div class="rounded-xl bg-surface-2 p-3">
          <div class="text-xs text-label-3 mb-1">换手率</div>
          <div class="text-base font-bold text-label-1">
            {{ snap.turnover != null ? snap.turnover + '%' : '—' }}
          </div>
          <div class="text-xs mt-1 leading-snug text-label-2">
            {{ turnoverInterp }}
          </div>
        </div>

      </div>

      <!-- ── Guide toggle ── -->
      <button class="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl text-xs
                     font-medium text-label-2 bg-surface-2 hover:text-label-1 transition"
              @click="showGuide = !showGuide">
        <BookOpen :size="13" />
        {{ showGuide ? '收起指标解读' : '展开指标解读 — 各指标含义及买卖参考' }}
        <ChevronDown :size="13" :class="showGuide ? 'rotate-180' : ''" class="transition-transform" />
      </button>

      <!-- ── Guide panel ── -->
      <div v-show="showGuide" class="space-y-3">

        <!-- IOPV & 折溢价 -->
        <div class="rounded-xl border border-hairline p-4">
          <div class="font-semibold text-sm text-label-1 mb-2 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-sys-blue inline-block"></span>
            IOPV 实时估值 &amp; 折溢价率
          </div>
          <p class="text-xs text-label-2 leading-relaxed mb-3">
            IOPV（基金参考净值）是根据 ETF 持仓的成分股实时价格，每隔约 15 秒估算一次的理论净值。
            <strong class="text-label-1">折溢价率 = (IOPV − 市价) ÷ 市价 × 100%</strong>。
            由于套利机制，大多数时候这个差距很小，主要在市场异常波动或流动性差时才会拉大。
          </p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="rounded-lg bg-sys-greenDim p-2.5">
              <div class="font-semibold text-sys-green mb-1">买入参考</div>
              <p class="text-label-2 leading-snug">折价率 &gt; +0.5%（市价低于净值）：
                ETF 价格低于其持仓实际价值，短期具备安全边际，可视为相对低估。</p>
            </div>
            <div class="rounded-lg bg-sys-redDim p-2.5">
              <div class="font-semibold text-sys-red mb-1">卖出 / 谨慎参考</div>
              <p class="text-label-2 leading-snug">溢价率 &gt; +0.5%（市价高于净值，即折价率 &lt; −0.5%）：
                买入价格已高于理论净值，套利资金会卖出压低价格，存在回归风险。</p>
            </div>
          </div>
        </div>

        <!-- 委比 -->
        <div class="rounded-xl border border-hairline p-4">
          <div class="font-semibold text-sm text-label-1 mb-2 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-sys-purple inline-block"></span>
            委比
          </div>
          <p class="text-xs text-label-2 leading-relaxed mb-3">
            委比 = （买单挂单量 − 卖单挂单量）÷（买单 + 卖单）× 100%，反映<strong class="text-label-1">当前市场的买卖意愿对比</strong>。
            正值代表买盘挂单更多，负值代表卖盘挂单更多。注意这是"未成交"挂单，投机性强，可随时撤单。
          </p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="rounded-lg bg-sys-greenDim p-2.5">
              <div class="font-semibold text-sys-green mb-1">买入参考</div>
              <p class="text-label-2 leading-snug">委比 &gt; +30%：买盘意愿远强于卖盘，短期价格偏多。
                结合量比放大效果更佳。</p>
            </div>
            <div class="rounded-lg bg-sys-redDim p-2.5">
              <div class="font-semibold text-sys-red mb-1">卖出参考</div>
              <p class="text-label-2 leading-snug">委比 &lt; −30%：卖盘意愿强烈，短期压力大。
                警惕主力砸盘前拉高委比的"虚晃"操作。</p>
            </div>
          </div>
        </div>

        <!-- 主力净流入 -->
        <div class="rounded-xl border border-hairline p-4">
          <div class="font-semibold text-sm text-label-1 mb-2 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-sys-orange inline-block"></span>
            主力净流入
          </div>
          <p class="text-xs text-label-2 leading-relaxed mb-3">
            主力净流入 = 大单买入额 − 大单卖出额（单笔成交金额 &gt; 20 万元视为大单）。
            <strong class="text-label-1">净占比</strong>是净流入金额占总成交额的比例，消除了市值大小的影响，更适合跨品种比较。
          </p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="rounded-lg bg-sys-greenDim p-2.5">
              <div class="font-semibold text-sys-green mb-1">买入参考</div>
              <p class="text-label-2 leading-snug">净占比持续 &gt; +3%：机构资金在积极布局，趋势向好。
                净占比 &gt; +8% 且价格同步上涨为量价配合信号。</p>
            </div>
            <div class="rounded-lg bg-sys-redDim p-2.5">
              <div class="font-semibold text-sys-red mb-1">卖出参考</div>
              <p class="text-label-2 leading-snug">净占比 &lt; −3%：大资金持续流出，主力在减仓。
                若同时伴随价格下跌，卖出信号更强。</p>
            </div>
          </div>
        </div>

        <!-- 外盘/内盘 -->
        <div class="rounded-xl border border-hairline p-4">
          <div class="font-semibold text-sm text-label-1 mb-2 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-sys-green inline-block"></span>
            外盘 / 内盘
          </div>
          <p class="text-xs text-label-2 leading-relaxed mb-3">
            <strong class="text-label-1">外盘</strong>（主动买入）= 成交价在卖一及以上的成交量，代表买方主动"追涨"。
            <strong class="text-label-1">内盘</strong>（主动卖出）= 成交价在买一及以下，代表卖方主动"杀跌"。
            外盘/内盘比值 &gt; 1 说明买方更主动；&lt; 1 说明卖方更主动。与委比不同，外内盘统计的是<strong class="text-label-1">已成交</strong>订单，更真实。
          </p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="rounded-lg bg-sys-greenDim p-2.5">
              <div class="font-semibold text-sys-green mb-1">买入参考</div>
              <p class="text-label-2 leading-snug">外/内 &gt; 1.5：买方主动成交远多于卖方，
                市场在"抢筹"，短期偏多，可考虑跟进。</p>
            </div>
            <div class="rounded-lg bg-sys-redDim p-2.5">
              <div class="font-semibold text-sys-red mb-1">卖出参考</div>
              <p class="text-label-2 leading-snug">外/内 &lt; 0.67：卖方主动抛售占主导，
                市场在"出货"，短期偏空，持仓者需警惕。</p>
            </div>
          </div>
        </div>

        <!-- 综合提示 -->
        <div class="rounded-xl bg-sys-orangeDim px-4 py-3 flex items-start gap-2 text-xs text-sys-orange">
          <Lightbulb :size="14" class="flex-shrink-0 mt-0.5" />
          <span class="leading-relaxed">
            <strong>综合判断：</strong>
            单一指标容易被主力操纵或产生误判，建议观察多指标共振。
            理想买入：委比正值 + 主力持续净流入 + 外盘 &gt; 内盘 + 折价/正常溢价，三者以上同向时胜率更高。
            盘中数据反映当日情绪，结合模型信号（基于历史日线趋势）一起判断效果最佳。
          </span>
        </div>

      </div>
    </div>

  </BaseCard>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { api } from '../api.js'
import BaseCard from './base/BaseCard.vue'
import { RefreshCw, Loader2, BookOpen, ChevronDown, Lightbulb } from '@lucide/vue'

const props = defineProps({
  code: { type: String, required: true },
})

const snap      = ref(null)
const loading   = ref(false)
const error     = ref('')
const showGuide = ref(false)
let   timer     = null

async function load() {
  loading.value = true
  error.value   = ''
  try {
    snap.value = await api('GET', `/api/realtime-snapshot/${props.code}`)
  } catch (e) {
    error.value = e.message ?? '加载失败'
  } finally {
    loading.value = false
  }
}

function startTimer() {
  stopTimer()
  load()
  timer = setInterval(load, 30_000)
}
function stopTimer() {
  if (timer) { clearInterval(timer); timer = null }
}

watch(() => props.code, (c) => { if (c) startTimer() }, { immediate: true })
onBeforeUnmount(stopTimer)

// ── Interpretations ───────────────────────────────────────────

function fmtFlow(v) {
  if (v == null) return '—'
  const abs = Math.abs(v)
  const sign = v >= 0 ? '+' : '-'
  if (abs >= 1e8) return sign + (abs / 1e8).toFixed(2) + ' 亿'
  if (abs >= 1e4) return sign + (abs / 1e4).toFixed(0) + ' 万'
  return sign + abs.toFixed(0)
}

// 折溢价：premium_rt 正=折价 负=溢价
const premiumLabel = computed(() => {
  const v = snap.value?.premium_rt
  if (v == null) return '—'
  if (v > 0) return `折价 ${v.toFixed(2)}%`
  if (v < 0) return `溢价 ${Math.abs(v).toFixed(2)}%`
  return '平价'
})
const premiumColor = computed(() => {
  const v = snap.value?.premium_rt
  if (v == null) return 'text-label-3'
  if (v > 0.5) return 'text-sys-green'
  if (v < -0.5) return 'text-sys-red'
  return 'text-label-2'
})
const premiumInterp = computed(() => {
  const v = snap.value?.premium_rt
  if (v == null) return ''
  if (v > 0.5) return '市价低于净值，折价买入窗口'
  if (v > 0) return '轻微折价，正常范围'
  if (v > -0.5) return '轻微溢价，正常范围'
  return '市价高于净值，存在回归压力'
})

// 委比
const weibiColor = computed(() => {
  const v = snap.value?.wei_bi
  if (v == null) return 'text-label-3'
  if (v > 10) return 'text-sys-green'
  if (v < -10) return 'text-sys-red'
  return 'text-label-2'
})
const weibiInterp = computed(() => {
  const v = snap.value?.wei_bi
  if (v == null) return ''
  if (v > 30) return '买盘积极压倒卖盘，偏多'
  if (v > 10) return '买盘略占优'
  if (v < -30) return '卖盘明显占优，偏空'
  if (v < -10) return '卖盘略占优'
  return '多空均衡'
})

// 量比
const volRatioColor = computed(() => {
  const v = snap.value?.vol_ratio
  if (v == null) return 'text-label-3'
  if (v > 2) return 'text-sys-orange'
  if (v > 1.2) return 'text-sys-green'
  if (v < 0.5) return 'text-label-3'
  return 'text-label-1'
})
const volRatioInterp = computed(() => {
  const v = snap.value?.vol_ratio
  if (v == null) return ''
  if (v > 3) return '异常放量，当前走势可能加速'
  if (v > 2) return '放量明显，信号可信度更高'
  if (v > 1.2) return '成交略活跃'
  if (v < 0.5) return '成交萎缩，市场观望'
  return '成交正常'
})

// 主力净流入
const mainFlowColor = computed(() => {
  const v = snap.value?.main_net_pct
  if (v == null) return 'text-label-3'
  if (v > 2) return 'text-sys-green'
  if (v < -2) return 'text-sys-red'
  return 'text-label-2'
})
const mainFlowInterp = computed(() => {
  const v = snap.value?.main_net_pct
  if (v == null) return ''
  if (v > 8) return '大资金强势流入'
  if (v > 3) return '机构积极买入'
  if (v > 0) return '主力小幅流入'
  if (v > -3) return '主力小幅流出'
  if (v > -8) return '机构在减仓'
  return '大资金持续流出'
})

// 外/内盘
const outerInnerColor = computed(() => {
  const v = snap.value?.outer_inner
  if (v == null) return 'text-label-3'
  if (v > 1.3) return 'text-sys-green'
  if (v < 0.77) return 'text-sys-red'
  return 'text-label-2'
})
const outerInnerInterp = computed(() => {
  const v = snap.value?.outer_inner
  if (v == null) return ''
  if (v > 1.5) return '买方主动追涨，偏多'
  if (v > 1.1) return '买方略占主动'
  if (v < 0.67) return '卖方主动杀跌，偏空'
  if (v < 0.9) return '卖方略占主动'
  return '买卖力量相当'
})

// 换手率
const turnoverInterp = computed(() => {
  const v = snap.value?.turnover
  if (v == null) return ''
  if (v > 5) return '换手活跃，资金流动性强'
  if (v > 2) return '正常换手'
  return '换手偏低，市场参与度不足'
})
</script>
