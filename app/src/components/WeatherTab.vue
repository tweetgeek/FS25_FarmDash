<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> Ładowanie pogody...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div class="weather-card">
        <div class="weather-icon">{{ data.currentWeatherIcon || '🌤️' }}</div>
        <div class="weather-info">
          <div class="weather-type">{{ weatherName(data.currentWeather) }}</div>
          <div class="weather-details">
            Dzień {{ data.currentDay || '—' }} • Godzina {{ data.dayTime || '—' }}
            <template v-if="data.wetness > 0"> • Wilgotność gruntu: {{ data.wetness }}%</template>
            <template v-if="data.snowHeight > 0"> • Śnieg: {{ data.snowHeight }}m</template>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>📅 Prognoza pogody</h2>
        <div class="forecast-list">
          <div
            v-for="day in forecastDays"
            :key="day.day"
            class="forecast-item"
            :style="day.day === data.currentDay ? 'border:1px solid var(--accent)' : ''"
          >
            <span class="forecast-icon">{{ day.icon }}</span>
            <div class="forecast-day">Dzień {{ day.day }}</div>
            <div class="forecast-type">{{ weatherName(day.dominant) }}</div>
            <div style="font-size:10px; color:var(--text-dim)">{{ day.season }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const WEATHER_NAMES = {
  SUN: 'Słonecznie', CLOUDY: 'Zachmurzenie', RAIN: 'Deszcz',
  HAIL: 'Grad', SNOW: 'Śnieg', THUNDERSTORM: 'Burza', FOG: 'Mgła',
}

function weatherName(type) {
  return WEATHER_NAMES[type] || type || '—'
}

const forecastDays = computed(() => {
  const forecast = props.data?.forecast || []
  const byDay = {}
  forecast.forEach(f => {
    if (!byDay[f.day]) byDay[f.day] = []
    byDay[f.day].push(f)
  })
  return Object.keys(byDay)
    .map(Number)
    .sort((a, b) => a - b)
    .slice(0, 14)
    .map(day => {
      const entries = byDay[day]
      const counts = {}
      entries.forEach(e => { counts[e.typeName] = (counts[e.typeName] || 0) + e.durationSec })
      const dominant = Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0]
      const icon = entries.find(e => e.typeName === dominant)?.icon || '🌤️'
      return { day, dominant, icon, season: entries[0]?.seasonPl || '' }
    })
})
</script>
