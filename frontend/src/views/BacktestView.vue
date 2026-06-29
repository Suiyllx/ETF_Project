<template>
  <div class="p-6">
    <h2 class="text-xl font-bold text-label-1 mb-5 flex items-center gap-2">
      <FlaskConical :size="20" class="text-label-2" /> 回测结果
    </h2>

    <div v-if="loading" class="text-center text-label-2 py-20">加载中…</div>

    <div v-else-if="!results.length" class="text-center py-24 text-label-2">
      <FlaskConical :size="44" class="mx-auto opacity-50" />
      <p class="mt-3 text-lg text-label-1">暂无回测结果</p>
      <p class="text-sm mt-1">
        运行
        <code class="bg-surface-2 px-1.5 py-0.5 rounded text-label-2">
          python -m quant.backtest.backtester
        </code>
        生成结果
      </p>
    </div>

    <BaseCard v-else class="overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-surface-2 text-xs text-label-2">
          <tr>
            <th class="px-4 py-3 text-left">代码</th>
            <th class="px-4 py-3 text-right">总收益</th>
            <th class="px-4 py-3 text-right">年化收益</th>
            <th class="px-4 py-3 text-right">胜率</th>
            <th class="px-4 py-3 text-right">最大回撤</th>
            <th class="px-4 py-3 text-right">交易次数</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in results" :key="r.code ?? r.etf_code"
            class="border-t border-hairline hover:bg-surface-2"
          >
            <td class="px-4 py-3 font-semibold text-label-1">{{ r.code ?? r.etf_code ?? '—' }}</td>
            <td
              class="px-4 py-3 text-right font-medium"
              :class="(r.total_return ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'"
            >{{ pct(r.total_return) }}</td>
            <td
              class="px-4 py-3 text-right font-medium"
              :class="(r.annual_return ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'"
            >{{ pct(r.annual_return) }}</td>
            <td class="px-4 py-3 text-right text-label-1">{{ pct(r.win_rate) }}</td>
            <td class="px-4 py-3 text-right text-sys-red">{{ pct(r.max_drawdown) }}</td>
            <td class="px-4 py-3 text-right text-label-2">{{ r.trade_count ?? r.n_trades ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'
import BaseCard from '../components/base/BaseCard.vue'
import { FlaskConical } from '@lucide/vue'

const results = ref([])
const loading = ref(true)

const pct = v => v != null ? ((v * 100).toFixed(2) + '%') : '—'

onMounted(async () => {
  try { results.value = await api('GET', '/api/backtest') }
  catch {}
  finally { loading.value = false }
})
</script>
