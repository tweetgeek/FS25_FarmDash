<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.production.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div v-if="!data.facilities?.length" class="alert alert-info">
        {{ t('ui.production.empty') }}
      </div>

      <template v-else>

        <!-- Summary bar -->
        <div class="prod-summary-bar">
          <div class="prod-summary-item">
            <span class="prod-summary-val">{{ data.totalFacilities }}</span>
            <span class="prod-summary-label">{{ t('ui.production.totalFacilities') }}</span>
          </div>
          <div class="prod-summary-sep"></div>
          <div class="prod-summary-item">
            <span class="prod-summary-val" style="color:var(--accent)">{{ activeCount }}</span>
            <span class="prod-summary-label">{{ t('ui.production.statusActive') }}</span>
          </div>
          <div v-if="partialCount > 0" class="prod-summary-item">
            <span class="prod-summary-val" style="color:var(--warn)">{{ partialCount }}</span>
            <span class="prod-summary-label">{{ t('ui.production.statusPartial') }}</span>
          </div>
          <div v-if="offCount > 0" class="prod-summary-item">
            <span class="prod-summary-val" style="color:var(--text-dim)">{{ offCount }}</span>
            <span class="prod-summary-label">{{ t('ui.production.statusOff') }}</span>
          </div>
          <div class="prod-summary-sep"></div>
          <div class="prod-summary-item">
            <span class="prod-summary-val" style="color:var(--accent)">{{ data.totalActiveProductions }}</span>
            <span class="prod-summary-label">{{ t('ui.production.activeProductions') }}</span>
          </div>
        </div>

        <!-- Facilities grouped by category -->
        <div v-for="group in groupedFacilities" :key="group.category" class="prod-group">
          <div class="prod-group-header">
            {{ catLabel(group.category) }}
          </div>
          <div class="production-grid">
            <ProductionCard v-for="(f, i) in group.facilities" :key="i" :facility="f" />
          </div>
        </div>

      </template>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'
import ProductionCard from './ProductionCard.vue'

const { t } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const CAT_ICONS = {
  greenhouse: '🌿', bakery: '🥐', flourmill: '⚙️', sawmill: '🪵',
  spinnery: '🧶', biogas: '♻️', dairy: '🧀', oilmill: '🫒',
  winery: '🍷', brewery: '🍺', fishfarm: '🐟', slaughterhouse: '🥩',
  quarry: '⛏️', factory: '🏭', other: '🏗️',
}

function catLabel(cat) {
  return t('ui.production.categories.' + cat, (CAT_ICONS[cat] || '') + ' ' + cat)
}

const CAT_ORDER = [
  'greenhouse', 'dairy', 'bakery', 'flourmill', 'oilmill',
  'winery', 'brewery', 'spinnery', 'sawmill', 'biogas',
  'fishfarm', 'slaughterhouse', 'quarry', 'factory', 'other',
]

const groupedFacilities = computed(() => {
  const facilities = props.data?.facilities || []
  const groups = {}
  for (const f of facilities) {
    if (!groups[f.category]) groups[f.category] = []
    groups[f.category].push(f)
  }
  return CAT_ORDER
    .filter(cat => groups[cat])
    .map(cat => ({ category: cat, facilities: groups[cat] }))
})

const activeCount = computed(() =>
  (props.data?.facilities || []).filter(f => f.enabledCount === f.totalCount).length
)
const partialCount = computed(() =>
  (props.data?.facilities || []).filter(f => f.enabledCount > 0 && f.enabledCount < f.totalCount).length
)
const offCount = computed(() =>
  (props.data?.facilities || []).filter(f => f.enabledCount === 0).length
)
</script>

<style scoped>
.prod-summary-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.prod-summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.prod-summary-val {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.prod-summary-label {
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.prod-summary-sep {
  width: 1px;
  height: 32px;
  background: var(--border);
  flex-shrink: 0;
}

.prod-group-header {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent2);
  margin: 0 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.prod-group { margin-bottom: 24px; }

.production-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
</style>
