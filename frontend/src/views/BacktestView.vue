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

    <h2 class="text-xl font-bold text-label-1 mb-5 mt-10 flex items-center gap-2">
      <Target :size="20" class="text-label-2" /> 信号回测（真实推送结果验证）
    </h2>

    <div v-if="sbLoading" class="text-center text-label-2 py-20">加载中…</div>

    <div v-else-if="!sb || !sb.overall" class="text-center py-24 text-label-2">
      <Target :size="44" class="mx-auto opacity-50" />
      <p class="mt-3 text-lg text-label-1">暂无可回测的信号</p>
      <p class="text-sm mt-1">历史信号的 forward 期还未走完，等待更多交易日后再查看</p>
    </div>

    <template v-else>
      <BaseCard class="mb-4 p-5">
        <div class="flex items-center gap-8">
          <div>
            <p class="text-xs text-label-2 mb-1">已验证信号数</p>
            <p class="text-2xl font-bold text-label-1">{{ sb.valid_signals }} / {{ sb.total_signals }}</p>
          </div>
          <div>
            <p class="text-xs text-label-2 mb-1">整体胜率</p>
            <p class="text-2xl font-bold" :class="sb.overall.hit_rate >= 0.5 ? 'text-sys-green' : 'text-sys-red'">
              {{ pct(sb.overall.hit_rate) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-label-2 mb-1">平均收益</p>
            <p class="text-2xl font-bold" :class="sb.overall.mean_ret >= 0 ? 'text-sys-green' : 'text-sys-red'">
              {{ pct(sb.overall.mean_ret) }}
            </p>
          </div>
        </div>
        <p v-if="!sb.reliable" class="text-xs text-sys-orange mt-4">
          样本数 {{ sb.valid_signals }} 低于 {{ sb.min_samples }}，分组统计仅供参考，不建议据此调整过滤规则。
        </p>
      </BaseCard>

      <BaseCard v-if="Object.keys(sb.groups).length" class="overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-surface-2 text-xs text-label-2">
            <tr>
              <th class="px-4 py-3 text-left">指标</th>
              <th class="px-4 py-3 text-left">分组</th>
              <th class="px-4 py-3 text-right">样本数</th>
              <th class="px-4 py-3 text-right">平均收益</th>
              <th class="px-4 py-3 text-right">胜率</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(g, metric) in sb.groups" :key="metric">
              <tr v-for="(label, key) in { positive: `${metric} >= 0`, negative: `${metric} < 0` }"
                  :key="metric + key" class="border-t border-hairline hover:bg-surface-2">
                <td class="px-4 py-3 font-semibold text-label-1">{{ key === 'positive' ? metric : '' }}</td>
                <td class="px-4 py-3 text-label-2">{{ label }}</td>
                <td class="px-4 py-3 text-right text-label-2">{{ g[key]?.count ?? '—' }}</td>
                <td class="px-4 py-3 text-right font-medium"
                    :class="(g[key]?.mean_ret ?? 0) >= 0 ? 'text-sys-green' : 'text-sys-red'">
                  {{ g[key] ? pct(g[key].mean_ret) : '—' }}
                </td>
                <td class="px-4 py-3 text-right text-label-1">{{ g[key] ? pct(g[key].hit_rate) : '—' }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </BaseCard>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'
import BaseCard from '../components/base/BaseCard.vue'
import { FlaskConical, Target } from '@lucide/vue'

const results = ref([])
const loading = ref(true)
const sb = ref(null)
const sbLoading = ref(true)

const pct = v => v != null ? ((v * 100).toFixed(2) + '%') : '—'

onMounted(async () => {
  try { results.value = await api('GET', '/api/backtest') }
  catch {}
  finally { loading.value = false }

  try { sb.value = await api('GET', '/api/signal-backtest') }
  catch {}
  finally { sbLoading.value = false }
})
</script>
