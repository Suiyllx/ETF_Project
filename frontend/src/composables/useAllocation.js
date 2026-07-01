import { computed } from 'vue'

// code → 主题色（与分类体系一一对应，供饼图/图例复用）
export const CATEGORY_COLORS = {
  '宽基': '#3b82f6', '海外': '#06b6d4', '金融': '#f59e0b', '医疗': '#ec4899',
  '科技': '#8b5cf6', '能源': '#84cc16', '消费': '#f43f5e', '周期': '#14b8a6',
  '地产': '#eab308', '债券': '#6366f1', '商品': '#a855f7', '其他': '#94a3b8',
}

/**
 * 持仓权重 & 板块占比的共享计算逻辑（AllocationCard / AllocationAdviceCard 共用）。
 * @param {import('vue').Ref|ComputedRef} positions
 * @param {import('vue').Ref|ComputedRef} totalAssets
 * @param {import('vue').Ref|ComputedRef} marketPrices
 * @param {import('vue').Ref|ComputedRef} categories
 * @param {import('vue').Ref|ComputedRef} maxPositionPct
 * @param {import('vue').Ref|ComputedRef} maxSectorPct
 */
export function useAllocation({ positions, totalAssets, marketPrices, categories, maxPositionPct, maxSectorPct }) {
  function marketValue(p) {
    const price = marketPrices.value[p.code] ?? p.cost_price
    return p.shares * price
  }

  const weightRows = computed(() => {
    const total = totalAssets.value || 1
    return [...positions.value]
      .map(p => {
        const value = marketValue(p)
        const pct = value / total * 100
        return { code: p.code, name: p.name, value, pct, overLimit: pct / 100 > maxPositionPct.value }
      })
      .sort((a, b) => b.pct - a.pct)
  })

  const sectorRows = computed(() => {
    const total = totalAssets.value || 1
    const bySector = {}
    for (const p of positions.value) {
      const cat = categories.value[p.code] || '其他'
      bySector[cat] = (bySector[cat] || 0) + marketValue(p)
    }
    return Object.entries(bySector)
      .map(([category, value]) => {
        const pct = value / total * 100
        return {
          category, value, pct,
          color: CATEGORY_COLORS[category] || CATEGORY_COLORS['其他'],
          overLimit: pct / 100 > maxSectorPct.value,
        }
      })
      .sort((a, b) => b.pct - a.pct)
  })

  return { weightRows, sectorRows }
}
