<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden app-bg">

    <div class="relative w-full max-w-sm mx-4">
      <!-- Logo + title -->
      <div class="text-center mb-7">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 bg-sys-blue text-white">
          <ChartNoAxesCombined :size="30" />
        </div>
        <h1 class="text-2xl font-bold text-label-1 tracking-tight">ETF 量化管理</h1>
        <p class="text-sm mt-1 text-label-2">内部交易系统 · 请登录</p>
      </div>

      <!-- Login card -->
      <BaseCard class="overflow-hidden">
        <div class="px-7 py-7">
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-semibold mb-1.5 text-label-2" style="letter-spacing:.06em;text-transform:uppercase">用户名</label>
              <input v-model="form.username" type="text" placeholder="输入用户名"
                     class="input w-full"
                     @keydown.enter="submit"
                     autocomplete="username" />
            </div>
            <div>
              <label class="block text-xs font-semibold mb-1.5 text-label-2" style="letter-spacing:.06em;text-transform:uppercase">密码</label>
              <input v-model="form.password" type="password" placeholder="输入密码"
                     class="input w-full"
                     @keydown.enter="submit"
                     autocomplete="current-password" />
            </div>

            <!-- Error -->
            <div v-if="error" class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-sm bg-sys-redDim text-sys-red">
              <TriangleAlert :size="15" class="flex-shrink-0" /> {{ error }}
            </div>

            <!-- Submit button -->
            <BaseButton variant="primary" class="w-full mt-1" :disabled="loading" @click="submit">
              <Loader2 v-if="loading" :size="15" class="animate-spin" />
              {{ loading ? '登录中…' : '登 录' }}
            </BaseButton>
          </div>
        </div>

        <div class="px-7 py-3 text-center text-xs bg-surface-2 border-t border-hairline text-label-3">
          © ETF 量化系统 · 仅供内部使用
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { store } from '../store.js'
import BaseCard   from '../components/base/BaseCard.vue'
import BaseButton from '../components/base/BaseButton.vue'
import { ChartNoAxesCombined, TriangleAlert, Loader2 } from '@lucide/vue'

const form    = reactive({ username: '', password: '' })
const error   = ref('')
const loading = ref(false)

async function submit() {
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value   = ''
  try {
    await store.login(form.username, form.password)
  } catch (e) {
    error.value = e.message || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.input {
  @apply rounded-xl px-4 py-2.5 text-sm bg-surface-2 text-label-1 border border-transparent
         focus:outline-none focus:ring-2 focus:ring-sys-blue focus:border-transparent transition;
}
</style>
