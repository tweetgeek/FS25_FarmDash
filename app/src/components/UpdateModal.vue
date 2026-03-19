<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <span>🔄 {{ t('ui.update.title') }}</span>
        <button class="modal-close" @click="$emit('close')" :disabled="busy">✕</button>
      </div>

      <div class="modal-body">
        <div class="update-versions">
          <span class="ver-current">v{{ info.current }}</span>
          <span class="ver-arrow">→</span>
          <span class="ver-new">v{{ info.latest }}</span>
        </div>

        <div v-if="info.changelog?.length" class="update-changelog">
          <div class="changelog-title">{{ t('ui.update.changelog') }}</div>
          <ul>
            <li v-for="(line, i) in info.changelog" :key="i">{{ line }}</li>
          </ul>
        </div>

        <!-- idle / error -->
        <template v-if="phase === 'idle'">
          <div v-if="devMode" class="alert alert-info" style="font-size:13px;">
            {{ t('ui.update.devOnly') }}
          </div>
          <div v-if="errorMsg" class="alert alert-error" style="font-size:13px;">{{ errorMsg }}</div>
        </template>

        <!-- downloading -->
        <template v-else-if="phase === 'downloading'">
          <div class="update-progress-label">{{ t('ui.update.downloading') }} {{ progress }}%</div>
          <div class="update-progress-bar">
            <div class="update-progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
        </template>

        <!-- launching / done -->
        <template v-else-if="phase === 'launching' || phase === 'done'">
          <div class="alert alert-success" style="font-size:13px;">{{ t('ui.update.restarting') }}</div>
        </template>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')" :disabled="busy">
          {{ t('ui.update.cancel') }}
        </button>
        <button
          class="btn"
          @click="startUpdate"
          :disabled="busy || devMode || phase === 'launching' || phase === 'done'"
        >
          <span v-if="busy" class="spinner" style="width:14px;height:14px;margin-right:6px;"></span>
          {{ phase === 'idle' ? t('ui.update.installBtn') : t('ui.update.installing') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { applyUpdate, getUpdateStatus } from '../api.js'
import { useI18n } from '../i18n/index.js'

const props = defineProps({
  info: { type: Object, required: true },
})
const emit = defineEmits(['close'])

const { t } = useI18n()

const phase    = ref('idle')   // idle | downloading | launching | done | error
const progress = ref(0)
const errorMsg = ref('')
const devMode  = ref(false)

const busy = computed(() => phase.value === 'downloading' || phase.value === 'launching')

let pollTimer = null

async function startUpdate() {
  errorMsg.value = ''
  phase.value = 'downloading'
  progress.value = 0

  try {
    await applyUpdate(props.info.download_url)
  } catch (e) {
    if (e.message?.includes('exe')) {
      devMode.value = true
    } else {
      errorMsg.value = e.message
    }
    phase.value = 'idle'
    return
  }

  // Poll status
  pollTimer = setInterval(async () => {
    try {
      const s = await getUpdateStatus()
      progress.value = s.progress ?? progress.value
      if (s.status === 'launching' || s.status === 'done') {
        phase.value = s.status
        clearInterval(pollTimer)
      } else if (s.status === 'error') {
        errorMsg.value = s.error || 'Nieznany błąd'
        phase.value = 'idle'
        clearInterval(pollTimer)
      } else if (s.status === 'downloading') {
        phase.value = 'downloading'
      }
    } catch {}
  }, 800)
}

onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  width: min(480px, 95vw);
  display: flex; flex-direction: column;
  box-shadow: 0 8px 32px rgba(0,0,0,.4);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  font-weight: 600; font-size: 15px;
  border-bottom: 1px solid var(--card-border);
}
.modal-close {
  background: none; border: none; cursor: pointer;
  color: var(--text-dim); font-size: 16px; padding: 2px 6px;
  border-radius: 4px;
}
.modal-close:hover { background: var(--hover-bg); }
.modal-body  { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.modal-footer {
  padding: 14px 20px;
  border-top: 1px solid var(--card-border);
  display: flex; justify-content: flex-end; gap: 10px;
}

.update-versions {
  display: flex; align-items: center; gap: 10px;
  font-size: 20px; font-weight: 700;
}
.ver-current { color: var(--text-dim); }
.ver-arrow   { color: var(--text-dim); }
.ver-new     { color: var(--accent); }

.update-changelog { font-size: 13px; }
.changelog-title  { font-weight: 600; margin-bottom: 6px; color: var(--text-dim); }
.update-changelog ul { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px; }

.update-progress-label { font-size: 13px; color: var(--text-dim); }
.update-progress-bar {
  height: 8px; border-radius: 4px;
  background: var(--table-border, #333);
  overflow: hidden;
}
.update-progress-fill {
  height: 100%; border-radius: 4px;
  background: var(--accent);
  transition: width .3s ease;
}
</style>
