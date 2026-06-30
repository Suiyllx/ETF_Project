<template>
  <BaseCard v-if="signals.length" class="overflow-hidden">
    <!-- Header -->
    <div
      class="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
      :class="collapsed ? '' : 'border-b border-hairline'"
      @click="collapsed = !collapsed"
    >
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-label-1">今日信号简报</span>
        <Badge tone="blue" :label="signals.length + ' 个'" />
        <span v-if="heldCount" class="text-xs text-label-3">· 已持 {{ heldCount }} 只</span>
      </div>
      <ChevronDown
        :size="16"
        class="text-label-3 transition-transform duration-200"
        :class="collapsed ? '' : 'rotate-180'"
      />
    </div>

    <!-- Signal cards row -->
    <div v-show="!collapsed" class="flex gap-3 px-4 pt-3 pb-3 overflow-x-auto">
      <div
        v-for="sig in signals"
        :key="sig.code"
        class="flex-shrink-0 w-44 rounded-xl border border-hairline bg-surface-2 p-3 flex flex-col gap-2"
      >
        <!-- Name + code -->
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold bg-sys-blueDim text-sys-blue flex-shrink-0">
            {{ sig.code.slice(-2) }}
          </div>
          <div class="min-w-0">
            <div class="text-xs font-semibold text-label-1 truncate">{{ sig.name }}</div>
            <div class="text-[11px] text-label-3">{{ sig.code }}</div>
          </div>
        </div>

        <!-- Prob + price/pct -->
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-sys-green bg-sys-greenDim px-2 py-0.5 rounded-full">
            {{ (sig.prob_up * 100).toFixed(0) }}%↑
          </span>
          <div class="text-right leading-tight">
            <div class="text-xs font-medium text-label-1">¥{{ sig.close.toFixed(3) }}</div>
            <div class="text-[11px]" :class="sig.pct_chg >= 0 ? 'text-sys-green' : 'text-sys-red'">
              {{ sig.pct_chg >= 0 ? '+' : '' }}{{ sig.pct_chg.toFixed(2) }}%
            </div>
          </div>
        </div>

        <!-- Action button -->
        <button
          class="w-full text-xs font-semibold py-1.5 rounded-lg transition"
          :class="heldCodes.has(sig.code)
            ? 'bg-sys-greenDim text-sys-green hover:bg-sys-green hover:text-white'
            : 'bg-sys-blue text-white hover:opacity-80'"
          @click="$emit('buy-signal', sig)"
        >
          {{ heldCodes.has(sig.code) ? '+ 加仓' : '+ 建仓' }}
        </button>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseCard from './base/BaseCard.vue'
import Badge    from './base/Badge.vue'
import { ChevronDown } from '@lucide/vue'

const props = defineProps({
  signals:   { type: Array, default: () => [] },
  positions: { type: Array, default: () => [] },
})

defineEmits(['buy-signal'])

const collapsed = ref(false)

const heldCodes = computed(() => new Set(props.positions.map(p => p.code)))
const heldCount = computed(() => props.signals.filter(s => heldCodes.value.has(s.code)).length)
</script>
