<template>
  <BaseCard tag="div" class="overflow-hidden transition-all">
    <!-- Card header -->
    <div class="flex items-center justify-between px-5 py-4 border-b border-hairline">
      <div class="flex items-center gap-3">
        <!-- ETF tile -->
        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold" :class="tileToneClass">
          {{ s.code.slice(-2) }}
        </div>
        <div>
          <div class="font-bold text-label-1 text-base">{{ s.name }}</div>
          <div class="text-xs text-label-2">{{ s.code }}</div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <!-- Advice badge -->
        <Badge :type="s.advice" />
        <!-- Probability -->
        <div class="text-right">
          <div class="text-2xl font-bold" :class="probToneClass">{{ (s.prob_up * 100).toFixed(1) }}%</div>
          <div class="text-xs text-label-2">做多置信度</div>
        </div>
      </div>
    </div>

    <!-- Card body -->
    <div class="px-5 py-4">
      <!-- Probability bars -->
      <div class="flex gap-4 mb-4 items-stretch">
        <div class="flex-1">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-label-2">做多</span>
            <span class="font-bold text-sys-green">{{ pct(s.prob_up) }}</span>
          </div>
          <div class="h-2 rounded-full bg-surface-3">
            <div class="h-2 rounded-full transition-all bg-sys-green" :style="{width: pct(s.prob_up)}"></div>
          </div>
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-label-2">震荡</span>
            <span class="font-medium text-label-2">{{ pct(s.prob_flat) }}</span>
          </div>
          <div class="h-2 rounded-full bg-surface-3">
            <div class="h-2 rounded-full transition-all bg-label-3" :style="{width: pct(s.prob_flat)}"></div>
          </div>
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-label-2">做空</span>
            <span class="font-medium text-sys-red">{{ pct(s.prob_down) }}</span>
          </div>
          <div class="h-2 rounded-full bg-surface-3">
            <div class="h-2 rounded-full transition-all bg-sys-red" :style="{width: pct(s.prob_down)}"></div>
          </div>
        </div>
        <!-- Price info -->
        <div class="border-l border-hairline pl-4 flex flex-col justify-center text-right flex-shrink-0">
          <div class="font-bold text-label-1">¥{{ s.close?.toFixed(3) ?? '—' }}</div>
          <div class="text-xs font-medium mt-0.5" :class="(s.pct_chg ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'">
            {{ (s.pct_chg ?? 0) >= 0 ? '▲' : '▼' }}{{ Math.abs(s.pct_chg ?? 0).toFixed(2) }}%
          </div>
          <div class="text-xs text-label-3 mt-0.5">{{ s.date }} 收盘</div>
        </div>
      </div>

      <!-- Indicator tags -->
      <div v-if="s.indicator_tags?.length" class="flex flex-wrap gap-1.5 mb-4">
        <span v-for="tag in s.indicator_tags" :key="tag"
              class="text-xs px-2.5 py-1 rounded-full font-medium" :class="tagToneClass(tag)">
          {{ tag }}
        </span>
      </div>

      <!-- Advice reason -->
      <div class="rounded-xl px-4 py-3 text-sm leading-relaxed" :class="reasonBgClass"
           :style="`border-left:3px solid ${reasonBorderColor}`">
        <div class="text-xs font-semibold mb-1 flex items-center gap-1.5" :style="`color:${reasonBorderColor}`">
          <Briefcase :size="13" /> {{ historical ? '当日建议' : '当前建议' }}：{{ ADV_LABEL[s.advice] || s.advice }}
        </div>
        <div class="text-label-1">{{ s.advice_reason }}</div>
      </div>

      <!-- Holding info (if any) -->
      <div v-if="s.holding" class="mt-3 flex items-center gap-4 text-xs text-label-2 border-t border-hairline pt-3">
        <span>成本价 <span class="font-bold text-label-1">¥{{ s.cost_price?.toFixed(3) }}</span></span>
        <span>浮盈亏
          <span class="font-bold" :class="(s.unrealized_pct ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'">
            {{ ((s.unrealized_pct ?? 0) * 100).toFixed(1) }}%
          </span>
        </span>
        <span v-if="s.pos_weight">仓位占比 <span class="font-bold text-label-1">{{ (s.pos_weight * 100).toFixed(1) }}%</span></span>
        <span v-if="s.sector" class="text-label-3">板块：{{ s.sector }}</span>
      </div>

      <!-- Quick trade actions -->
      <div v-if="!historical" class="mt-3 flex items-center gap-2 border-t border-hairline pt-3">
        <BaseButton variant="green" size="sm" class="flex-1" @click.stop="$emit('trade', { ...s, action: 'buy' })">
          <TrendingUp :size="14" /> 买入记录
        </BaseButton>
        <BaseButton variant="ghost" size="sm" class="flex-1" @click.stop="$emit('trade', { ...s, action: 'position' })">
          <FolderPlus :size="14" /> 加入持仓
        </BaseButton>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard   from './base/BaseCard.vue'
import BaseButton from './base/BaseButton.vue'
import Badge      from './base/Badge.vue'
import { Briefcase, TrendingUp, FolderPlus } from '@lucide/vue'

const props = defineProps({
  signal:     { type: Object, required: true },
  historical: { type: Boolean, default: false },
})
defineEmits(['trade'])
const s = computed(() => props.signal)

const ADV_LABEL = { OPEN: '建议开仓', ADD: '建议加仓', HOLD: '维持持有', REDUCE: '建议减仓', SKIP: '暂时跳过' }

// ETF 代码方块 / 概率数字 颜色（淡色调，呼应 Badge 的 dim 风格，不用大块纯色）
const TONE_TILE_CLASS = {
  OPEN:   'bg-sys-greenDim text-sys-green',
  ADD:    'bg-sys-blueDim text-sys-blue',
  HOLD:   'bg-sys-orangeDim text-sys-orange',
  REDUCE: 'bg-sys-redDim text-sys-red',
  SKIP:   'bg-surface-2 text-label-2',
}
const tileToneClass = computed(() => TONE_TILE_CLASS[s.value.advice] || TONE_TILE_CLASS.SKIP)

const TONE_TEXT_CLASS = {
  OPEN: 'text-sys-green', ADD: 'text-sys-blue', HOLD: 'text-sys-orange',
  REDUCE: 'text-sys-red', SKIP: 'text-label-1',
}
const probToneClass = computed(() => TONE_TEXT_CLASS[s.value.advice] || TONE_TEXT_CLASS.SKIP)

// Reason box
const REASON_CLASS = {
  OPEN:   { bg: 'bg-sys-greenDim',  border: 'var(--sys-green)'  },
  ADD:    { bg: 'bg-sys-blueDim',   border: 'var(--sys-blue)'   },
  HOLD:   { bg: 'bg-sys-orangeDim', border: 'var(--sys-orange)' },
  REDUCE: { bg: 'bg-sys-redDim',    border: 'var(--sys-red)'    },
  SKIP:   { bg: 'bg-surface-2',     border: 'var(--label-3)'    },
}
const reasonBgClass     = computed(() => (REASON_CLASS[s.value.advice] || REASON_CLASS.SKIP).bg)
const reasonBorderColor = computed(() => (REASON_CLASS[s.value.advice] || REASON_CLASS.SKIP).border)

function pct(v) { return ((v ?? 0) * 100).toFixed(1) + '%' }

// Tag color by content keywords
function tagToneClass(tag) {
  if (tag.includes('超卖') || tag.includes('偏低') || tag.includes('多头') || tag.includes('翻正') || tag.includes('放量'))
    return 'bg-sys-greenDim text-sys-green'
  if (tag.includes('超买') || tag.includes('偏高') || tag.includes('追高') || tag.includes('为负') || tag.includes('缩量'))
    return 'bg-sys-redDim text-sys-red'
  return 'bg-surface-2 text-label-2'
}
</script>
