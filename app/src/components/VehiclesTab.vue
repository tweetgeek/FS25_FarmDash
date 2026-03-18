<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.vehicles.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div style="margin-bottom:12px; color:var(--text-dim); font-size:13px">
        {{ t('ui.vehicles.total') }}: {{ vehicles.length }}
      </div>
      <div class="vehicles-grid">
        <div v-for="v in vehicles" :key="v.filename" class="vehicle-card">
          <div class="vehicle-name" :title="v.filename">{{ v.name }}</div>
          <div class="vehicle-stats">
            <div>
              <div style="color:var(--text-dim)">{{ t('ui.vehicles.wear') }}</div>
              <div class="vehicle-stat-val" :style="{ color: dmgColor(v.damage) }">{{ v.damage }}%</div>
              <div class="progress-bar">
                <div class="progress-fill progress-damage" :style="{ width: v.damage + '%' }"></div>
              </div>
            </div>
            <div>
              <div style="color:var(--text-dim)">{{ t('ui.vehicles.dirt') }}</div>
              <div class="vehicle-stat-val">{{ v.dirt }}%</div>
              <div class="progress-bar">
                <div class="progress-fill progress-dirt" :style="{ width: v.dirt + '%' }"></div>
              </div>
            </div>
            <div>
              <div style="color:var(--text-dim)">{{ t('ui.vehicles.workTime') }}</div>
              <div class="vehicle-stat-val">{{ v.operatingTime }}h</div>
            </div>
            <div>
              <div style="color:var(--text-dim)">{{ t('ui.vehicles.age') }}</div>
              <div class="vehicle-stat-val">{{ v.age }}m</div>
            </div>
          </div>
          <template v-for="u in fuelUnits(v)" :key="u.type">
            <div style="font-size:11px; color:var(--text-dim); margin-top:4px">
              ⛽ {{ tItem(u.type) }}: {{ Math.round(u.level) }}L
              <div class="progress-bar">
                <div class="progress-fill progress-fuel" :style="{ width: fuelPct(u) + '%' }"></div>
              </div>
            </div>
          </template>
          <template v-for="u in cargoUnits(v)" :key="u.type">
            <div v-if="u.level > 0" style="font-size:11px; color:var(--text-dim); margin-top:2px">
              📦 {{ tItem(u.type) }}: {{ Math.round(u.level) }}
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'

const { t, tItem } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const FUEL_TYPES = ['DIESEL', 'PETROL', 'ELECTRICCHARGE', 'METHANE']

const vehicles = computed(() => props.data?.vehicles || [])

function dmgColor(damage) {
  if (damage > 50) return 'var(--danger)'
  if (damage > 20) return 'var(--warn)'
  return 'var(--accent)'
}

function fuelUnits(v) {
  return (v.fillUnits || []).filter(u => FUEL_TYPES.includes(u.type))
}

function cargoUnits(v) {
  return (v.fillUnits || []).filter(u => !FUEL_TYPES.includes(u.type) && u.type !== 'UNKNOWN')
}

function fuelPct(u) {
  return Math.min(100, Math.round(u.level / 100))
}
</script>
