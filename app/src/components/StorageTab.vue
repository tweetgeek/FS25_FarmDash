<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.storage.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div v-if="data.items.length === 0" class="alert alert-info">
        {{ t('ui.storage.empty') }}
      </div>

      <!-- Summary card (only when priced crops exist) -->
      <div v-if="totalCurrentValue > 0" class="card summary-card">
        <h2>{{ t('ui.storage.valueTitle') }}</h2>
        <div class="summary-grid">
          <div class="summary-item">
            <div class="summary-label">{{ t('ui.storage.valueNow') }}</div>
            <div class="summary-value">{{ formatMoney(totalCurrentValue, locale) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">{{ t('ui.storage.valueMax') }}</div>
            <div class="summary-value accent2">{{ formatMoney(totalMaxValue, locale) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">{{ t('ui.storage.potentialGain') }}</div>
            <div class="summary-value gain">
              +{{ formatMoney(totalMaxValue - totalCurrentValue, locale) }}
              <span class="gain-pct">(+{{ gainPct }}%)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Crops with pricing table -->
      <div v-if="pricedItems.length > 0" class="card" style="padding:0; overflow-x:auto">
        <div style="padding:16px 20px 12px; border-bottom:1px solid var(--border)">
          <h2 style="margin-bottom:0">{{ t('ui.storage.cropsTitle') }}</h2>
        </div>
        <table class="fields-table">
          <thead>
            <tr>
              <th>{{ t('ui.storage.colItem') }}</th>
              <th>{{ t('ui.storage.colAmount') }}</th>
              <th style="color:var(--text)">{{ t('ui.storage.colPriceNow') }}</th>
              <th style="color:var(--accent)">{{ t('ui.storage.colValueNow') }}</th>
              <th style="color:var(--text-dim)">{{ t('ui.storage.colPriceMax') }}</th>
              <th style="color:var(--accent2)">{{ t('ui.storage.colValueMax') }}</th>
              <th>{{ t('ui.storage.colGain') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in pricedItems" :key="row.item.type">
              <td>
                <strong
                  class="crop-link"
                  :title="t('ui.fields.seePrices')"
                  @click="goToPrices(tItem(row.item.type))"
                >{{ row.item.emoji }} {{ tItem(row.item.type) }}</strong>
              </td>
              <td>{{ formatAmount(row.item.level) }}</td>
              <td>{{ formatPrice(row.price.currentPrice, locale) }}</td>
              <td style="color:var(--accent); font-weight:600">{{ formatMoney(row.currentValue, locale) }}</td>
              <td style="color:var(--text-dim)">
                {{ formatPrice(row.price.maxPrice, locale) }}
                <small>({{ row.price.maxPeriodLabel }})</small>
              </td>
              <td style="color:var(--accent2); font-weight:600">{{ formatMoney(row.maxValue, locale) }}</td>
              <td>
                <span v-if="row.gain > 0" class="gain-badge">+{{ formatMoney(row.gain, locale) }}</span>
                <span v-else style="color:var(--text-dim)">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Other categories (cards) -->
      <template v-for="(group, catKey) in otherGroups" :key="catKey">
        <div class="card">
          <h2>{{ t('categories.' + catKey + '.emoji') }} {{ t('categories.' + catKey + '.label') }}</h2>
          <div class="storage-grid">
            <div v-for="item in group" :key="item.type" class="storage-item">
              <div class="storage-header">
                <span class="storage-emoji">{{ item.emoji }}</span>
                <span class="storage-name">{{ tItem(item.type) }}</span>
                <span class="storage-amount">{{ formatAmount(item.level) }}</span>
              </div>
              <div class="progress-bar" style="height:6px; margin-top:6px">
                <div
                  class="progress-fill"
                  :class="barClass(catKey)"
                  :style="{ width: barWidth(item.level, group) + '%' }"
                ></div>
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
import { formatMoney, formatPrice } from '../utils.js'
import { useI18n } from '../i18n/index.js'
import { goToPrices } from '../useNavigation.js'

const { t, tItem, locale } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
  pricesData: Object,
})

const CATEGORY_ORDER = ['feed', 'products', 'supplies', 'manure', 'other']

// Build a price lookup map keyed by fill type
const priceMap = computed(() => {
  const map = {}
  if (!props.pricesData?.items) return map
  const periods = props.pricesData.periods || []
  for (const crop of props.pricesData.items) {
    map[crop.type] = {
      currentPrice: crop.currentPrice,
      maxPrice: crop.maxPrice,
      maxPeriodLabel: periods[crop.maxPeriodIdx] ? t('periods.' + periods[crop.maxPeriodIdx]) : '',
    }
  }
  return map
})

// Items with a known market price, with value calculations
const pricedItems = computed(() => {
  if (!props.data?.items) return []
  return props.data.items
    .filter(item => item.category === 'crops' && priceMap.value[item.type])
    .map(item => {
      const price = priceMap.value[item.type]
      const tons = item.level / 1000
      const currentValue = Math.round(tons * price.currentPrice)
      const maxValue = Math.round(tons * price.maxPrice)
      return { item, price, currentValue, maxValue, gain: maxValue - currentValue }
    })
    .sort((a, b) => b.gain - a.gain)
})

// Non-crops groups for card display
const otherGroups = computed(() => {
  if (!props.data?.items) return {}
  const groups = {}
  for (const item of props.data.items) {
    if (item.category === 'crops') continue
    const cat = item.category || 'other'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(item)
  }
  const result = {}
  for (const key of CATEGORY_ORDER) {
    if (groups[key]?.length) result[key] = groups[key]
  }
  return result
})

const totalCurrentValue = computed(() =>
  pricedItems.value.reduce((s, r) => s + r.currentValue, 0)
)
const totalMaxValue = computed(() =>
  pricedItems.value.reduce((s, r) => s + r.maxValue, 0)
)
const gainPct = computed(() => {
  if (!totalCurrentValue.value) return 0
  return Math.round(((totalMaxValue.value - totalCurrentValue.value) / totalCurrentValue.value) * 100)
})

function formatAmount(level) {
  if (level >= 1000) return (level / 1000).toFixed(1) + ' t'
  return Math.round(level) + ' L'
}

function barWidth(level, group) {
  const max = Math.max(...group.map(i => i.level))
  return max > 0 ? Math.round((level / max) * 100) : 0
}

function barClass(catKey) {
  if (catKey === 'feed') return 'progress-dirt'
  if (catKey === 'manure') return 'progress-damage'
  return 'progress-fuel'
}
</script>

<style scoped>
.summary-card { margin-bottom: 16px; }

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.summary-item {
  background: var(--surface2);
  border-radius: var(--radius);
  padding: 14px 16px;
}

.summary-label {
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}

.summary-value.accent2 { color: var(--accent2); }

.summary-value.gain { color: var(--accent); }

.gain-pct {
  font-size: 13px;
  font-weight: 500;
  margin-left: 4px;
}

.gain-badge {
  display: inline-block;
  background: var(--badge-good-bg);
  color: var(--accent);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
}

.storage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.storage-item {
  background: var(--surface2);
  border-radius: var(--radius);
  padding: 12px 14px;
}

.storage-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.storage-emoji { font-size: 18px; }

.storage-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
}

.storage-amount {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent);
  white-space: nowrap;
}

@media (max-width: 700px) {
  .summary-grid { grid-template-columns: 1fr; }
}

.crop-link {
  cursor: pointer;
  border-bottom: 1px dashed var(--text-dim);
  transition: color 0.15s, border-color 0.15s;
}
.crop-link:hover {
  color: var(--accent);
  border-color: var(--accent);
}
</style>
