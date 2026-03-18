<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.production.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div v-if="!data.facilities?.length" class="alert alert-info">
        {{ t('ui.production.empty') }}
      </div>

      <template v-else>
        <!-- Summary -->
        <div class="stats-grid" style="margin-bottom:20px">
          <div class="stat-item">
            <div class="stat-value">{{ data.totalFacilities }}</div>
            <div class="stat-label">{{ t('ui.production.totalFacilities') }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-value" style="color:var(--accent)">{{ data.totalActiveProductions }}</div>
            <div class="stat-label">{{ t('ui.production.activeProductions') }}</div>
          </div>
          <div v-for="(count, cat) in data.summary" :key="cat" class="stat-item">
            <div class="stat-value">{{ count }}</div>
            <div class="stat-label">{{ catLabel(cat) }}</div>
          </div>
        </div>

        <!-- Category groups -->
        <div v-for="group in groupedFacilities" :key="group.category">
          <h2 style="font-size:14px; font-weight:600; color:var(--accent2); margin:0 0 10px;">
            {{ catLabel(group.category) }}
          </h2>
          <div class="production-grid">
            <div v-for="(f, i) in group.facilities" :key="i" class="card production-card">

              <div class="production-header">
                <span class="production-icon">{{ catIcon(f.category) }}</span>
                <span class="production-name">{{ f.name }}</span>
                <span class="production-counts">
                  <span class="prod-badge prod-on">{{ f.enabledCount }}</span>
                  <span v-if="f.totalCount - f.enabledCount > 0" class="prod-badge prod-off">
                    {{ f.totalCount - f.enabledCount }}
                  </span>
                </span>
              </div>

              <div class="production-list">
                <span
                  v-for="pr in f.productions"
                  :key="pr.id"
                  :class="['prod-chip', pr.enabled ? 'prod-chip-on' : 'prod-chip-off']"
                  :title="pr.enabled ? t('ui.production.enabled') : t('ui.production.disabled')"
                >
                  {{ tItem(pr.id) !== pr.id ? tItem(pr.id) : pr.label }}
                </span>
              </div>

            </div>
          </div>
        </div>
      </template>
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

const CAT_ICONS = {
  greenhouse: '🌿', bakery: '🥐', flourmill: '⚙️', sawmill: '🪵',
  spinnery: '🧶', biogas: '♻️', dairy: '🧀', oilmill: '🫒',
  winery: '🍷', brewery: '🍺', fishfarm: '🐟', slaughterhouse: '🥩',
  quarry: '⛏️', factory: '🏭', other: '🏗️',
}

function catLabel(cat) {
  return t('ui.production.categories.' + cat, CAT_ICONS[cat] + ' ' + cat)
}

function catIcon(cat) {
  return CAT_ICONS[cat] || '🏗️'
}

const groupedFacilities = computed(() => {
  const facilities = props.data?.facilities || []
  const groups = {}
  for (const f of facilities) {
    if (!groups[f.category]) groups[f.category] = []
    groups[f.category].push(f)
  }
  // Sort: greenhouse first, then alphabetically
  const catOrder = ['greenhouse', 'dairy', 'bakery', 'flourmill', 'oilmill',
    'winery', 'brewery', 'spinnery', 'sawmill', 'biogas',
    'fishfarm', 'slaughterhouse', 'quarry', 'factory', 'other']
  return catOrder
    .filter(cat => groups[cat])
    .map(cat => ({ category: cat, facilities: groups[cat] }))
})
</script>

<style scoped>
.production-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.production-card {
  padding: 14px;
  margin-bottom: 0;
}

.production-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.production-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.production-name {
  font-weight: 600;
  font-size: 14px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.production-counts {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.prod-badge {
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 700;
}
.prod-on  { background: var(--badge-good-bg); color: var(--accent); }
.prod-off { background: var(--surface2); color: var(--text-dim); }

.production-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.prod-chip {
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
}
.prod-chip-on  { background: var(--badge-good-bg); color: var(--accent); }
.prod-chip-off { background: var(--surface2); color: var(--text-dim); text-decoration: line-through; }
</style>
