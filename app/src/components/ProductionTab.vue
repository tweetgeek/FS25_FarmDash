<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.production.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div v-if="!data.facilities?.length" class="alert alert-info">
        {{ t('ui.production.empty') }}
      </div>

      <template v-else>
        <div class="stats-grid" style="margin-bottom:20px">
          <StatCard :label="t('ui.production.totalFacilities')">{{ data.totalFacilities }}</StatCard>
          <StatCard :label="t('ui.production.activeProductions')" :value-style="{ color: 'var(--accent)' }">
            {{ data.totalActiveProductions }}
          </StatCard>
          <StatCard v-for="(count, cat) in data.summary" :key="cat" :label="catLabel(cat)">
            {{ count }}
          </StatCard>
        </div>

        <div v-for="group in groupedFacilities" :key="group.category">
          <h2 style="font-size:14px; font-weight:600; color:var(--accent2); margin:0 0 10px;">
            {{ catLabel(group.category) }}
          </h2>
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
import StatCard from './StatCard.vue'
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
  return t('ui.production.categories.' + cat, CAT_ICONS[cat] + ' ' + cat)
}

const groupedFacilities = computed(() => {
  const facilities = props.data?.facilities || []
  const groups = {}
  for (const f of facilities) {
    if (!groups[f.category]) groups[f.category] = []
    groups[f.category].push(f)
  }
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
</style>
