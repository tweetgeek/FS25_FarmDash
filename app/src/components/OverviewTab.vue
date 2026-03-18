<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> Ładowanie danych...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ formatMoney(money) }}</div>
          <div class="stat-label">💰 Gotówka</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" :style="{ color: loan > 0 ? 'var(--danger)' : 'var(--text-dim)' }">{{ formatMoney(loan) }}</div>
          <div class="stat-label">🏦 Pożyczka</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ playTimeH }}h</div>
          <div class="stat-label">⏱️ Czas gry</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ round1(stats.workedHectares || 0) }} ha</div>
          <div class="stat-label">🌾 Uprawiane</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ round1(stats.threshedHectares || 0) }} ha</div>
          <div class="stat-label">🚜 Zebrane</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ env.dayTime || '—' }}</div>
          <div class="stat-label">🕐 Czas w grze</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ env.currentDay != null ? 'Dzień ' + env.currentDay : '—' }}</div>
          <div class="stat-label">{{ env.currentWeatherIcon || '🌤️' }} Pogoda</div>
        </div>
      </div>

      <div class="summary-cols">
        <div class="card">
          <h2>🏡 Informacje o farmie</h2>
          <table style="width:100%; font-size:13px; border-collapse:collapse">
            <tr v-for="row in farmRows" :key="row.label">
              <td style="padding:5px 8px; color:var(--text-dim); width:50%">{{ row.label }}</td>
              <td style="padding:5px 8px; font-weight:500">{{ row.value }}</td>
            </tr>
          </table>
        </div>
        <div class="card">
          <h2>💹 Finanse</h2>
          <div v-if="financeRows.length > 0">
            <table class="finance-table" style="width:100%">
              <tr v-for="row in financeRows" :key="row.label">
                <td style="padding:5px 8px; color:var(--text-dim)">{{ row.label }}</td>
                <td style="padding:5px 8px; text-align:right" :class="row.val >= 0 ? 'finance-positive' : 'finance-negative'">
                  {{ formatMoney(row.val) }}
                </td>
              </tr>
            </table>
          </div>
          <div v-else style="color:var(--text-dim); font-size:13px">Brak danych finansowych</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatMoney, round1, growthModeLabel, fuelLabel } from '../utils.js'

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const career = computed(() => props.data?.career || {})
const farm = computed(() => props.data?.farm || {})
const env = computed(() => props.data?.environment || {})
const stats = computed(() => farm.value.statistics || {})
const money = computed(() => farm.value.money || career.value.money || 0)
const loan = computed(() => farm.value.loan || 0)
const playTimeH = computed(() => {
  const pt = stats.value.playTime || career.value.playTime || 0
  return Math.round(pt / 60)
})

const farmRows = computed(() => {
  const c = career.value
  const f = farm.value
  return [
    { label: 'Nazwa farmy', value: f.name || c.savegameName || '—' },
    { label: 'Mapa', value: c.mapTitle || '—' },
    { label: 'Data zapisu', value: c.saveDateFormatted || c.saveDate || '—' },
    { label: 'Trudność', value: c.economicDifficulty || '—' },
    { label: 'Tryb wzrostu', value: growthModeLabel(c.growthMode) },
    { label: 'Prędkość czasu', value: c.timeScale ? `${c.timeScale}x` : '—' },
    { label: 'Paliwo', value: fuelLabel(c.fuelUsage) },
    { label: 'Chwasty', value: c.weedsEnabled ? '✅ Włączone' : '❌ Wyłączone' },
    { label: 'Wapno', value: c.limeRequired ? '✅ Wymagane' : '❌ Nie wymagane' },
  ]
})

const FINANCE_KEYS = [
  ['soldVehicles', '🚜 Sprzedane pojazdy'],
  ['newVehiclesCost', '🏷️ Zakup pojazdów'],
  ['harvestIncome', '🌾 Dochód ze żniw'],
  ['missionIncome', '📋 Dochód z misji'],
  ['wagePayment', '👷 Wynagrodzenia'],
  ['purchaseFertilizer', '🧪 Nawozy'],
  ['purchaseSeeds', '🌱 Nasiona'],
  ['purchaseFuel', '⛽ Paliwo'],
]

const financeRows = computed(() => {
  const finances = farm.value.finances || []
  const latest = finances[finances.length - 1]
  if (!latest) return []
  return FINANCE_KEYS
    .filter(([key]) => latest[key] != null && latest[key] !== 0)
    .map(([key, label]) => ({ label, val: latest[key] }))
})
</script>
