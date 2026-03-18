<template>
  <RouterView />

  <Transition name="offline-fade">
    <div v-if="!serverOnline" class="offline-overlay">
      <div class="offline-card">
        <div class="offline-icon">🔌</div>
        <h2 class="offline-title">{{ t('ui.offline.title') }}</h2>
        <p class="offline-subtitle">{{ t('ui.offline.subtitle') }}</p>
        <div class="offline-retrying">
          <span class="spinner"></span>
          {{ t('ui.offline.retrying') }}
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { serverOnline } from './useServerStatus.js'
import { useI18n } from './i18n/index.js'

const { t } = useI18n()
</script>

<style scoped>
.offline-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.offline-card {
  background: var(--surface);
  border: 1px solid var(--table-border);
  border-radius: 12px;
  padding: 40px 48px;
  text-align: center;
  max-width: 420px;
  width: 90%;
}

.offline-icon {
  font-size: 48px;
  margin-bottom: 16px;
  line-height: 1;
}

.offline-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 8px;
}

.offline-subtitle {
  font-size: 13px;
  color: var(--text-dim);
  margin: 0 0 24px;
}

.offline-retrying {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-dim);
}

.offline-fade-enter-active,
.offline-fade-leave-active {
  transition: opacity 0.3s ease;
}
.offline-fade-enter-from,
.offline-fade-leave-to {
  opacity: 0;
}
</style>
