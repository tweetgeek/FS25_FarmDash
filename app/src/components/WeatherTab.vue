<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.weather.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div class="card">
        <h2>{{ t('ui.weather.forecast') }}</h2>
        <div class="forecast-list">
          <div
            v-for="day in forecastDays"
            :key="day.day"
            class="forecast-item"
            :class="{ 'forecast-current': day.isCurrent }"
          >
            <span class="forecast-icon">{{ day.icon }}</span>
            <div class="forecast-month">{{ day.monthLabel }}</div>
            <div class="forecast-type">{{ t('weather.' + day.typeName) }}</div>
            <div v-if="day.tempHigh != null" class="forecast-temps">
              <span class="temp-high">{{ day.tempHigh }}°</span>
              <span class="temp-low">{{ day.tempLow }}°</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'

const { t } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const forecastDays = computed(() => {
  const forecast = props.data?.forecast || []
  const currentDay = props.data?.currentDay
  return forecast.slice(0, 14).map(f => ({
    day: f.day,
    typeName: f.typeName,
    icon: f.icon,
    monthLabel: f.periodKey ? t('periods.' + f.periodKey) : '',
    isCurrent: f.day === currentDay,
    tempHigh: f.tempHigh ?? null,
    tempLow:  f.tempLow  ?? null,
  }))
})
</script>
