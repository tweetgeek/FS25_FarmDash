<template>
  <div class="card animal-card">

    <div class="animal-card-header">
      <span class="animal-type-icon">{{ typeIcon(pen.mainType) }}</span>
      <div>
        <div class="animal-card-title">{{ typeLabel(pen.mainType) }}</div>
        <div v-if="pen.buildingName" class="animal-card-subtitle">{{ pen.buildingName }}</div>
      </div>
      <span class="animal-count">{{ pen.totalAnimals }} {{ t('ui.animals.count') }}</span>
    </div>

    <div class="animal-groups">
      <div v-for="g in pen.animalGroups" :key="g.subType" class="animal-group-row">
        <span class="animal-subtype">{{ formatSubType(g.subType) }}</span>
        <span class="animal-group-count">{{ g.count }} {{ t('ui.animals.count') }}</span>
        <span class="animal-age">~{{ Math.round(g.avgAgeMonths) }}m</span>
      </div>
    </div>

    <div class="animal-stats-row">
      <div v-if="pen.avgHealth > 0" class="animal-stat">
        <div class="animal-stat-label">{{ t('ui.animals.avgHealth') }}</div>
        <div class="progress-bar" style="width:80px; margin-top:4px">
          <div class="progress-fill" :class="healthClass(pen.avgHealth)" :style="{ width: pen.avgHealth + '%' }"></div>
        </div>
        <div class="animal-stat-val">{{ pen.avgHealth }}%</div>
      </div>
      <div v-if="pen.productionFactor > 0" class="animal-stat">
        <div class="animal-stat-label">{{ t('ui.animals.production') }}</div>
        <div class="animal-stat-val" :class="pen.productionFactor >= 80 ? 'text-good' : 'text-warn'">
          {{ pen.productionFactor }}%
        </div>
      </div>
    </div>

    <div v-if="pen.food.length" class="animal-section">
      <div class="animal-section-label">{{ t('ui.animals.food') }}</div>
      <div class="animal-fill-list">
        <span v-for="f in pen.food" :key="f.type" class="animal-fill-item">
          {{ tItem(f.type) }} {{ formatLiters(f.liters) }}
        </span>
      </div>
    </div>

    <div v-if="pen.products.length" class="animal-section">
      <div class="animal-section-label">{{ t('ui.animals.products') }}</div>
      <div class="animal-fill-list">
        <span v-for="p in pen.products" :key="p.type" class="animal-fill-item text-good">
          {{ tItem(p.type) }} {{ formatLiters(p.liters) }}
        </span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useI18n } from '../i18n/index.js'

const { t, tItem } = useI18n()

defineProps({ pen: Object })

const TYPE_ICONS = {
  sheep: '🐑', cow: '🐄', chicken: '🐔', pig: '🐷',
  horse: '🐴', goat: '🐐', donkey: '🫏', bee: '🐝',
  deer: '🦌', rabbit: '🐇', ostrich: '🦤',
}

function typeIcon(type) { return TYPE_ICONS[type] || '🐾' }
function typeLabel(type) { return t('ui.animals.types.' + type, type) }

function formatSubType(subType) {
  return subType.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase())
}

function healthClass(pct) {
  if (pct >= 70) return 'progress-fuel'
  if (pct >= 35) return 'progress-dirt'
  return 'progress-damage'
}

function formatLiters(liters) {
  if (liters >= 1000) return (liters / 1000).toFixed(1) + ' t'
  return Math.round(liters) + ' L'
}
</script>

<style scoped>
.animal-card {
  padding: 16px;
  margin-bottom: 0;
}

.animal-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.animal-type-icon { font-size: 28px; line-height: 1; }

.animal-card-title { font-weight: 700; font-size: 15px; }

.animal-card-subtitle {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 1px;
}

.animal-count {
  margin-left: auto;
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
}

.animal-groups {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.animal-group-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.animal-subtype { flex: 1; color: var(--text-dim); }
.animal-group-count { font-weight: 600; }
.animal-age { color: var(--text-dim); font-size: 11px; min-width: 28px; text-align: right; }

.animal-stats-row { display: flex; gap: 20px; margin-bottom: 10px; }

.animal-stat { display: flex; flex-direction: column; gap: 2px; }

.animal-stat-label {
  font-size: 10px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.animal-stat-val { font-size: 13px; font-weight: 600; margin-top: 2px; }

.animal-section { margin-top: 8px; }

.animal-section-label {
  font-size: 10px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.animal-fill-list { display: flex; flex-wrap: wrap; gap: 4px; }

.animal-fill-item {
  background: var(--surface2);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
}

.text-good { color: var(--accent); }
.text-warn { color: var(--warn); }
</style>
