<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.overview.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div class="stats-grid">
        <StatCard :label="t('ui.overview.cash')">{{ formatMoney(money, locale) }}</StatCard>
        <StatCard :label="t('ui.overview.loan')" :value-style="{ color: loan > 0 ? 'var(--danger)' : 'var(--text-dim)' }">
          {{ formatMoney(loan, locale) }}
        </StatCard>
        <StatCard :label="t('ui.overview.playTime')">{{ playTimeH }}h</StatCard>
        <StatCard :label="t('ui.overview.cultivated')">{{ round1(stats.workedHectares || 0) }} ha</StatCard>
        <StatCard :label="t('ui.overview.harvested')">{{ round1(stats.threshedHectares || 0) }} ha</StatCard>
        <StatCard :label="t('ui.overview.gameTime')">{{ env.dayTime || '—' }}</StatCard>
        <StatCard :label="(env.currentWeatherIcon || '🌤️') + ' ' + t('ui.overview.weatherLabel')">
          {{ env.currentDay != null ? t('ui.overview.day') + ' ' + env.currentDay : '—' }}
        </StatCard>
      </div>

      <WeatherTab :data="weatherData" :loading="weatherLoading" :error="weatherError" />

      <div class="summary-cols">
        <div class="card">
          <h2>{{ t('ui.overview.farmInfo') }}</h2>
          <table style="width:100%; font-size:13px; border-collapse:collapse">
            <tr v-for="row in farmRows" :key="row.label">
              <td style="padding:5px 8px; color:var(--text-dim); width:50%">{{ row.label }}</td>
              <td style="padding:5px 8px; font-weight:500">{{ row.value }}</td>
            </tr>
          </table>
        </div>
        <div class="card">
          <h2>{{ t('ui.overview.finances') }}</h2>
          <div v-if="financeRows.length > 0">
            <table class="finance-table" style="width:100%">
              <tr v-for="row in financeRows" :key="row.label">
                <td style="padding:5px 8px; color:var(--text-dim)">{{ row.label }}</td>
                <td style="padding:5px 8px; text-align:right" :class="row.val >= 0 ? 'finance-positive' : 'finance-negative'">
                  {{ formatMoney(row.val, locale) }}
                </td>
              </tr>
            </table>
          </div>
          <div v-else style="color:var(--text-dim); font-size:13px">{{ t('ui.overview.noFinances') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatMoney, round1 } from '../utils.js'
import { useI18n } from '../i18n/index.js'
import WeatherTab from './WeatherTab.vue'
import StatCard from './StatCard.vue'

const { t, locale } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
  weatherData: Object,
  weatherLoading: Boolean,
  weatherError: String,
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
  const gm = t('growthModes.' + String(c.growthMode))
  const fu = t('fuelUsage.' + String(c.fuelUsage))
  return [
    { label: t('ui.overview.farmName'),  value: f.name || c.savegameName || '—' },
    { label: t('ui.overview.map'),       value: c.mapTitle || '—' },
    { label: t('ui.overview.saveDate'),  value: c.saveDateFormatted || c.saveDate || '—' },
    { label: t('ui.overview.difficulty'),value: c.economicDifficulty || '—' },
    { label: t('ui.overview.growthMode'),value: gm === 'growthModes.' + String(c.growthMode) ? String(c.growthMode || '—') : gm },
    { label: t('ui.overview.timeScale'), value: c.timeScale ? `${c.timeScale}x` : '—' },
    { label: t('ui.overview.fuelUsage'), value: fu === 'fuelUsage.' + String(c.fuelUsage) ? String(c.fuelUsage || '—') : fu },
    { label: t('ui.overview.weeds'),     value: c.weedsEnabled ? t('ui.overview.weedsOn') : t('ui.overview.weedsOff') },
    { label: t('ui.overview.lime'),      value: c.limeRequired ? t('ui.overview.limeRequired') : t('ui.overview.limeNotRequired') },
  ]
})

const FINANCE_KEYS = [
  ['soldVehicles',      'soldVehicles'],
  ['newVehiclesCost',   'newVehiclesCost'],
  ['harvestIncome',     'harvestIncome'],
  ['missionIncome',     'missionIncome'],
  ['wagePayment',       'wagePayment'],
  ['purchaseFertilizer','purchaseFertilizer'],
  ['purchaseSeeds',     'purchaseSeeds'],
  ['purchaseFuel',      'purchaseFuel'],
]

const financeRows = computed(() => {
  const finances = farm.value.finances || []
  const latest = finances[finances.length - 1]
  if (!latest) return []
  return FINANCE_KEYS
    .filter(([key]) => latest[key] != null && latest[key] !== 0)
    .map(([key, msgKey]) => ({ label: t(`ui.overview.finance.${msgKey}`), val: latest[key] }))
})
</script>
