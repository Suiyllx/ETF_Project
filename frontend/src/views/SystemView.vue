<template>
  <div class="p-6">
    <h2 class="text-xl font-bold text-label-1 mb-5 flex items-center gap-2">
      <Settings :size="20" class="text-label-2" /> 系统状态
    </h2>

    <!-- 信号生成触发器 -->
    <BaseCard class="mb-5 p-5">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <Rocket :size="16" class="text-label-2" />
            <span class="font-semibold text-label-1">手动触发信号生成</span>
            <Badge :tone="JOB_TONE[job.status] ?? 'gray'" :label="JOB_LABEL[job.status] ?? '空闲'" />
          </div>
          <div class="text-xs text-label-2">
            <template v-if="job.status === 'running'">
              开始于 {{ job.started_at }} — {{ job.log?.[job.log.length-1] ?? '处理中…' }}
            </template>
            <template v-else-if="job.status === 'done'">
              完成于 {{ job.finished_at }}，生成 {{ job.signal_count }} 个做多信号
            </template>
            <template v-else-if="job.status === 'error'">
              失败：{{ job.error }}
            </template>
            <template v-else>更新所有 ETF 行情并重新生成今日信号</template>
          </div>
        </div>
        <BaseButton variant="primary" :disabled="job.status === 'running'" @click="runSignals">
          {{ job.status === 'running' ? '生成中…' : '立即触发' }}
        </BaseButton>
      </div>
    </BaseCard>

    <div v-if="loading" class="text-center text-label-2 py-20">加载中…</div>
    <div v-else-if="!status" class="text-center text-sys-red py-10">状态加载失败</div>

    <div v-else class="grid grid-cols-2 gap-4">
      <BaseCard v-for="c in cards" :key="c.key" class="p-5">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2">
              <component :is="c.icon" :size="16" class="text-label-2" />
              <span class="font-semibold text-label-1">{{ c.label }}</span>
            </div>
            <div class="text-xs text-label-2 mt-1">{{ c.desc }}</div>
          </div>
          <Badge :tone="status[c.key]?.exists ? 'green' : 'orange'"
                 :label="status[c.key]?.exists ? '正常' : '缺失'" class="flex-shrink-0" />
        </div>
        <div class="mt-3 text-xs" :class="status[c.key]?.exists ? 'text-label-2' : 'text-sys-orange'">
          {{ status[c.key]?.last_modified
              ? '最后更新：' + status[c.key].last_modified
              : '文件不存在，功能可能受限' }}
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'
import BaseCard   from '../components/base/BaseCard.vue'
import BaseButton from '../components/base/BaseButton.vue'
import Badge      from '../components/base/Badge.vue'
import { Settings, Rocket, Radar, Target, Users, Mail, Bot } from '@lucide/vue'

const status  = ref(null)
const loading = ref(true)

const cards = [
  { label: '今日信号候选池', key: 'signals',    desc: '每日收盘后由 generator.py 生成', icon: Radar },
  { label: '动态阈值校准',   key: 'thresholds', desc: '由 calibrator.py 维护',          icon: Target },
  { label: '用户注册表',     key: 'users',      desc: 'portfolios/users.json',           icon: Users },
  { label: '邮件发送日志',   key: 'email_log',  desc: 'logs/email_log.jsonl',            icon: Mail },
  { label: '模型文件',       key: 'models',     desc: 'quant/models/',                    icon: Bot },
]

// ── Signal trigger ────────────────────────────────────────────
const job = ref({ status: 'idle', signal_count: 0, started_at: null, finished_at: null, log: [], error: null })
let _pollTimer = null

const JOB_LABEL = { idle: '空闲', running: '运行中', done: '完成', error: '失败' }
const JOB_TONE  = { idle: 'gray', running: 'blue', done: 'green', error: 'red' }

async function runSignals() {
  try {
    await api('POST', '/api/run-signals', {})
    job.value.status = 'running'
    _startPolling()
  } catch (e) {
    alert('触发失败：' + e.message)
  }
}

function _startPolling() {
  if (_pollTimer) clearInterval(_pollTimer)
  _pollTimer = setInterval(async () => {
    try {
      const s = await api('GET', '/api/run-signals/status')
      job.value = s
      if (s.status !== 'running') {
        clearInterval(_pollTimer)
        _pollTimer = null
        // 刷新系统状态卡片
        status.value = await api('GET', '/api/system-status')
      }
    } catch {}
  }, 2000)
}

onMounted(async () => {
  try { status.value = await api('GET', '/api/system-status') }
  catch {}
  finally { loading.value = false }

  // 同步触发器状态
  try {
    const s = await api('GET', '/api/run-signals/status')
    job.value = s
    if (s.status === 'running') _startPolling()
  } catch {}
})
</script>
