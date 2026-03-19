<template>
  <div v-if="data" class="weather-widget">
    <span class="ww-icon">{{ data.currentWeatherIcon || '🌤️' }}</span>
    <span class="ww-label">{{ t('weather.' + (data.currentWeather || 'SUN')) }}</span>
    <span v-if="data.temperature != null" class="ww-temp">{{ data.temperature }}°C</span>
    <span class="ww-sep">·</span>
    <span class="ww-month">{{ currentMonthLabel }}</span>
    <span v-if="data.windSpeed != null" class="ww-sep">·</span>
    <span v-if="data.windSpeed != null" class="ww-wind">💨 {{ data.windSpeed }} km/h</span>
    <span v-if="data.wetness > 0" class="ww-sep">·</span>
    <span v-if="data.wetness > 0" class="ww-detail">💧 {{ data.wetness }}%</span>
    <span v-if="data.snowHeight > 0" class="ww-sep">·</span>
    <span v-if="data.snowHeight > 0" class="ww-detail">❄️ {{ data.snowHeight }}m</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'

const { t } = useI18n()

const props = defineProps({
  data: Object,
})

const currentMonthLabel = computed(() => {
  const key = props.data?.currentPeriodKey
  return key ? t('periods.' + key) : '—'
})
</script>

<style scoped>
.weather-widget {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 13px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.ww-icon { font-size: 18px; line-height: 1; }
.ww-label { font-weight: 600; }
.ww-temp { color: var(--accent); font-weight: 700; font-size: 14px; }
.ww-month { color: var(--text-dim); }
.ww-wind { color: var(--text-dim); }
.ww-detail { color: var(--text-dim); }
.ww-sep { color: var(--border); user-select: none; }
</style>
