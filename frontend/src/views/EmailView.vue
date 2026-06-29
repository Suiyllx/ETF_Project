<template>
  <div class="p-6">
    <h2 class="text-xl font-bold text-label-1 mb-5 flex items-center gap-2">
      <Mail :size="20" class="text-label-2" /> 邮件发送记录
    </h2>

    <div v-if="loading" class="text-center text-label-2 py-20">加载中…</div>

    <template v-else>
      <div v-if="logs.length" class="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="总发送" :value="logs.length" />
        <StatCard label="成功" :value="successCount" accent="green" />
        <StatCard label="失败" :value="failCount" accent="red" />
      </div>

      <div v-if="!logs.length" class="text-center py-24 text-label-2">
        <Inbox :size="44" class="mx-auto opacity-50" />
        <p class="mt-3 text-lg text-label-1">暂无邮件记录</p>
        <p class="text-sm mt-1">发送邮件后会自动记录在这里</p>
      </div>

      <BaseCard v-else class="overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-surface-2 text-xs text-label-2">
            <tr>
              <th class="px-4 py-3 text-left">时间</th>
              <th class="px-4 py-3 text-left">收件人</th>
              <th class="px-4 py-3 text-left">主题</th>
              <th class="px-4 py-3 text-center">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(log, i) in logs" :key="i"
              class="border-t border-hairline hover:bg-surface-2"
            >
              <td class="px-4 py-3 text-label-2 text-xs whitespace-nowrap">{{ log.timestamp }}</td>
              <td class="px-4 py-3 text-label-1">{{ log.to }}</td>
              <td class="px-4 py-3 text-label-1 max-w-sm truncate">{{ log.subject }}</td>
              <td class="px-4 py-3 text-center">
                <Badge v-if="log.success" tone="green" label="✓ 成功" />
                <Badge v-else tone="red" label="✗ 失败" :title="log.error ?? ''" />
              </td>
            </tr>
          </tbody>
        </table>
      </BaseCard>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api.js'
import BaseCard from '../components/base/BaseCard.vue'
import StatCard from '../components/base/StatCard.vue'
import Badge    from '../components/base/Badge.vue'
import { Mail, Inbox } from '@lucide/vue'

const logs    = ref([])
const loading = ref(true)

const successCount = computed(() => logs.value.filter(l => l.success).length)
const failCount    = computed(() => logs.value.filter(l => !l.success).length)

onMounted(async () => {
  try { logs.value = await api('GET', '/api/email-log') }
  catch {}
  finally { loading.value = false }
})
</script>
