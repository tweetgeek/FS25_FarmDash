<template>
  <div class="card production-card">

    <div class="production-header">
      <span class="production-icon">{{ catIcon(facility.category) }}</span>
      <span class="production-name">{{ facility.name }}</span>
      <span class="production-counts">
        <span class="prod-badge prod-on">{{ facility.enabledCount }}</span>
        <span v-if="facility.totalCount - facility.enabledCount > 0" class="prod-badge prod-off">
          {{ facility.totalCount - facility.enabledCount }}
        </span>
      </span>
    </div>

    <div class="production-list">
      <span
        v-for="pr in facility.productions"
        :key="pr.id"
        :class="['prod-chip', pr.enabled ? 'prod-chip-on' : 'prod-chip-off']"
        :title="pr.enabled ? t('ui.production.enabled') : t('ui.production.disabled')"
      >
        {{ tItem(pr.id) !== pr.id ? tItem(pr.id) : pr.label }}
      </span>
    </div>

    <div v-if="facility.storage?.length" class="prod-storage">
      <div class="prod-storage-label">{{ t('ui.production.inventory') }}</div>
      <div class="prod-storage-items">
        <span v-for="node in facility.storage" :key="node.type" class="prod-storage-item">
          {{ fillEmoji(node.type) }} {{ tItem(node.type) || node.type }}
          <span class="prod-storage-qty">{{ formatQty(node.level) }}</span>
        </span>
      </div>
    </div>

    <div v-if="facility.productionCostsToClaim > 0" class="prod-costs">
      {{ t('ui.production.costsToClaim') }}:
      <span class="prod-costs-value">{{ facility.productionCostsToClaim.toFixed(2) }} $</span>
    </div>

  </div>
</template>

<script setup>
import { useI18n } from '../i18n/index.js'

const { t, tItem } = useI18n()

defineProps({ facility: Object })

const FILL_EMOJIS = {
  WATER: '💧', WHEAT: '🌾', BARLEY: '🌾', OAT: '🌾', MAIZE: '🌽',
  CANOLA: '🟡', SUNFLOWER: '🌻', SOYBEAN: '🫘', POTATO: '🥔',
  SUGARBEET: '🟤', SUGARCANE: '🍬', BEETROOT: '🟣', CARROT: '🥕',
  PARSNIP: '🥕', ONION: '🧅', LETTUCE: '🥬', TOMATO: '🍅',
  STRAWBERRY: '🍓', GARLIC: '🧄', NAPACABBAGE: '🥬', CHILLI: '🌶️',
  SPRING_ONION: '🌿', GRAPE: '🍇', OLIVE: '🫒', PEA: '🟢',
  GREENBEAN: '🫛', SPINACH: '🌿', RICE: '🌾', MILK: '🥛',
  EGG: '🥚', WOOL: '🐑', HONEY: '🍯', FLOUR: '🌾', BREAD: '🍞',
  BUTTER: '🧈', CHEESE: '🧀', SUGAR: '🍬', SILAGE: '🟫',
  WOOD: '🪵', WOODCHIPS: '♻️', STRAW: '🟨', SEEDS: '🌱',
  FERTILIZER: '🧪', MANURE: '💩', LIQUIDMANURE: '💧',
}

const CAT_ICONS = {
  greenhouse: '🌿', bakery: '🥐', flourmill: '⚙️', sawmill: '🪵',
  spinnery: '🧶', biogas: '♻️', dairy: '🧀', oilmill: '🫒',
  winery: '🍷', brewery: '🍺', fishfarm: '🐟', slaughterhouse: '🥩',
  quarry: '⛏️', factory: '🏭', other: '🏗️',
}

function catIcon(cat) { return CAT_ICONS[cat] || '🏗️' }
function fillEmoji(type) { return FILL_EMOJIS[type] || '📦' }

function formatQty(level) {
  if (level >= 1000) return (level / 1000).toFixed(1) + 't'
  return level.toFixed(0) + ' l'
}
</script>

<style scoped>
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

.production-icon { font-size: 20px; line-height: 1; flex-shrink: 0; }

.production-name {
  font-weight: 600;
  font-size: 14px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.production-counts { display: flex; gap: 4px; flex-shrink: 0; }

.prod-badge { border-radius: 10px; padding: 1px 7px; font-size: 11px; font-weight: 700; }
.prod-on  { background: var(--badge-good-bg); color: var(--accent); }
.prod-off { background: var(--surface2); color: var(--text-dim); }

.production-list { display: flex; flex-wrap: wrap; gap: 4px; }

.prod-chip { border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 500; }
.prod-chip-on  { background: var(--badge-good-bg); color: var(--accent); }
.prod-chip-off { background: var(--surface2); color: var(--text-dim); text-decoration: line-through; }

.prod-storage {
  margin-top: 10px;
  border-top: 1px solid var(--table-border);
  padding-top: 8px;
}

.prod-storage-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-dim);
  margin-bottom: 5px;
}

.prod-storage-items { display: flex; flex-wrap: wrap; gap: 4px; }

.prod-storage-item {
  font-size: 11px;
  color: var(--text);
  background: var(--surface2);
  border-radius: 4px;
  padding: 2px 6px;
  display: flex;
  align-items: center;
  gap: 3px;
}

.prod-storage-qty { color: var(--accent2); font-weight: 600; }

.prod-costs { margin-top: 7px; font-size: 11px; color: var(--text-dim); }
.prod-costs-value { color: var(--accent); font-weight: 600; }
</style>
