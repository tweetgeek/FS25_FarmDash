<template>
  <div class="card prod-card">

    <!-- Header -->
    <div class="prod-header">
      <span class="prod-cat-icon">{{ catIcon(facility.category) }}</span>
      <span class="prod-name">{{ facility.name }}</span>
      <span :class="['prod-status-badge', statusClass]">{{ statusLabel }}</span>
    </div>

    <!-- Production lines -->
    <div class="prod-section">
      <div class="prod-section-label">{{ t('ui.production.productions') }}</div>
      <div class="prod-lines">
        <div
          v-for="pr in facility.productions"
          :key="pr.id"
          :class="['prod-line', pr.enabled ? 'prod-line-on' : 'prod-line-off']"
        >
          <span class="prod-line-dot">{{ pr.enabled ? '●' : '○' }}</span>
          <span class="prod-line-name">{{ tProc(pr.id, pr.label) }}</span>
        </div>
      </div>
    </div>

    <!-- Storage -->
    <div v-if="facility.storage?.length" class="prod-section">
      <div class="prod-section-label">{{ t('ui.production.inventory') }}</div>
      <div class="prod-storage-list">
        <div v-for="node in facility.storage" :key="node.type" class="prod-storage-row">
          <span class="prod-storage-icon">{{ fillEmoji(node.type) }}</span>
          <span class="prod-storage-name">{{ tItem(node.type) || node.type }}</span>
          <span class="prod-storage-qty">{{ formatQty(node.level) }}</span>
        </div>
      </div>
    </div>

    <!-- Costs to claim -->
    <div v-if="facility.productionCostsToClaim > 0" class="prod-costs">
      <span>{{ t('ui.production.costsToClaim') }}:</span>
      <span class="prod-costs-value">{{ formatMoney(facility.productionCostsToClaim, locale) }}</span>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'
import { formatMoney } from '../utils.js'

const { t, tItem, locale } = useI18n()

const props = defineProps({ facility: Object })

const CAT_ICONS = {
  greenhouse: '🌿', bakery: '🥐', flourmill: '⚙️', sawmill: '🪵',
  spinnery: '🧶', biogas: '♻️', dairy: '🧀', oilmill: '🫒',
  winery: '🍷', brewery: '🍺', fishfarm: '🐟', slaughterhouse: '🥩',
  quarry: '⛏️', factory: '🏭', other: '🏗️',
}

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
  FERTILIZER: '🧪', MANURE: '💩', LIQUIDMANURE: '💧', METHANE: '⚡',
  CANOLA_OIL: '🫙', SUNFLOWER_OIL: '🫙', OLIVE_OIL: '🫙',
  WINE: '🍷', BEER: '🍺', GRAPEJUICE: '🍇',
  CEMENT: '🧱', STONE: '🪨', COAL: '⬛', ROPE: '🪢',
  BOARDS: '🪵', PLANKS: '🪵', WOODBEAM: '🪵',
}

function catIcon(cat) { return CAT_ICONS[cat] || '🏗️' }
function fillEmoji(type) { return FILL_EMOJIS[type] || '📦' }

function tProc(id, fallback) {
  // 1. Explicit process translation (makeFlour, makeBread, growTomato…)
  const procKey = 'ui.production.processes.' + id
  const procVal = t(procKey)
  if (procVal !== procKey) return procVal

  // 2. Try as fill-type name: "tomato" → "TOMATO"
  const upper = id.toUpperCase()
  const direct = tItem(upper)
  if (direct !== upper) return direct

  // 3. camelCase → UPPER_SNAKE: "springOnion" → "SPRING_ONION"
  const snake = id.replace(/([a-z])([A-Z])/g, '$1_$2').toUpperCase()
  const snakeVal = tItem(snake)
  if (snakeVal !== snake) return snakeVal

  // 4. Raw label fallback
  return fallback
}

function formatQty(level) {
  if (level >= 1000) return (level / 1000).toFixed(1) + ' t'
  return Math.round(level) + ' L'
}

const statusClass = computed(() => {
  const { enabledCount, totalCount } = props.facility
  if (enabledCount === 0) return 'status-off'
  if (enabledCount < totalCount) return 'status-partial'
  return 'status-on'
})

const statusLabel = computed(() => {
  const { enabledCount, totalCount } = props.facility
  if (enabledCount === 0) return t('ui.production.statusOff')
  if (enabledCount < totalCount) return t('ui.production.statusPartial')
  return t('ui.production.statusActive')
})
</script>

<style scoped>
.prod-card {
  padding: 14px 16px;
}

/* Header */
.prod-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.prod-cat-icon { font-size: 20px; flex-shrink: 0; }

.prod-name {
  flex: 1;
  font-weight: 700;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.prod-status-badge {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  border-radius: 10px;
  padding: 2px 9px;
}
.status-on      { background: var(--badge-good-bg); color: var(--accent); }
.status-partial { background: var(--badge-warn-bg); color: var(--warn); }
.status-off     { background: var(--surface2); color: var(--text-dim); }

/* Sections */
.prod-section { margin-bottom: 10px; }

.prod-section-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
  margin-bottom: 5px;
}

/* Production lines */
.prod-lines { display: flex; flex-direction: column; gap: 3px; }

.prod-line {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  padding: 2px 0;
}

.prod-line-dot { font-size: 8px; flex-shrink: 0; }

.prod-line-on  .prod-line-dot { color: var(--accent); }
.prod-line-off .prod-line-dot { color: var(--text-dim); }

.prod-line-on  .prod-line-name { color: var(--text); }
.prod-line-off .prod-line-name { color: var(--text-dim); text-decoration: line-through; }

/* Storage */
.prod-storage-list { display: flex; flex-direction: column; gap: 4px; }

.prod-storage-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  background: var(--surface2);
  border-radius: 6px;
  padding: 4px 8px;
}

.prod-storage-icon { font-size: 14px; flex-shrink: 0; }
.prod-storage-name { flex: 1; color: var(--text-dim); }
.prod-storage-qty  { font-weight: 700; color: var(--accent2); font-size: 13px; }

/* Costs */
.prod-costs {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-dim);
}
.prod-costs-value { font-weight: 600; color: var(--accent); }
</style>
