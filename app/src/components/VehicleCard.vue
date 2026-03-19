<template>
  <div class="vehicle-card">
    <div class="vehicle-name" :title="vehicle.filename">{{ vehicle.name }}</div>
    <div class="vehicle-stats">
      <div>
        <div style="color:var(--text-dim)">{{ t('ui.vehicles.wear') }}</div>
        <div class="vehicle-stat-val" :style="{ color: dmgColor(vehicle.damage) }">{{ vehicle.damage }}%</div>
        <div class="progress-bar">
          <div class="progress-fill progress-damage" :style="{ width: vehicle.damage + '%' }"></div>
        </div>
      </div>
      <div>
        <div style="color:var(--text-dim)">{{ t('ui.vehicles.dirt') }}</div>
        <div class="vehicle-stat-val">{{ vehicle.dirt }}%</div>
        <div class="progress-bar">
          <div class="progress-fill progress-dirt" :style="{ width: vehicle.dirt + '%' }"></div>
        </div>
      </div>
      <div>
        <div style="color:var(--text-dim)">{{ t('ui.vehicles.workTime') }}</div>
        <div class="vehicle-stat-val">{{ vehicle.operatingTime }}h</div>
      </div>
      <div>
        <div style="color:var(--text-dim)">{{ t('ui.vehicles.age') }}</div>
        <div class="vehicle-stat-val">{{ vehicle.age }}m</div>
      </div>
    </div>
    <template v-for="u in fuelUnits" :key="u.type">
      <div style="font-size:11px; color:var(--text-dim); margin-top:4px">
        ⛽ {{ tItem(u.type) }}: {{ Math.round(u.level) }}L
        <div class="progress-bar">
          <div class="progress-fill progress-fuel" :style="{ width: fuelPct(u) + '%' }"></div>
        </div>
      </div>
    </template>
    <template v-for="u in cargoUnits" :key="u.type">
      <div v-if="u.level > 0" style="font-size:11px; color:var(--text-dim); margin-top:2px">
        📦 {{ tItem(u.type) }}: {{ Math.round(u.level) }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'

const { t, tItem } = useI18n()

const props = defineProps({ vehicle: Object })

const FUEL_TYPES = ['DIESEL', 'PETROL', 'ELECTRICCHARGE', 'METHANE']

const fuelUnits = computed(() =>
  (props.vehicle.fillUnits || []).filter(u => FUEL_TYPES.includes(u.type))
)

const cargoUnits = computed(() =>
  (props.vehicle.fillUnits || []).filter(u => !FUEL_TYPES.includes(u.type) && u.type !== 'UNKNOWN')
)

function dmgColor(damage) {
  if (damage > 50) return 'var(--danger)'
  if (damage > 20) return 'var(--warn)'
  return 'var(--accent)'
}

function fuelPct(u) {
  return Math.min(100, Math.round(u.level / 100))
}
</script>
