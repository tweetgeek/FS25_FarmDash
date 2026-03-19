<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.prices.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div class="alert alert-info" style="margin-bottom:16px">
        {{ t('ui.prices.currentPeriod') }}: <strong>{{ currentPeriodLabel }}</strong>
        &nbsp;·&nbsp; {{ filteredItems.length }} {{ t('ui.prices.items') }}
      </div>

      <!-- Category filter -->
      <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px;">
        <button
          :class="['tab-btn', { active: activeCategory === null }]"
          style="font-size:12px; padding:5px 12px;"
          @click="setCategory(null)"
        >
          {{ t('ui.prices.all') }} ({{ allItems.length }})
        </button>
        <button
          v-for="key in presentCategories"
          :key="key"
          :class="['tab-btn', { active: activeCategory === key }]"
          style="font-size:12px; padding:5px 12px;"
          @click="setCategory(key)"
        >
          {{ t('categories.' + key + '.emoji') }} {{ t('categories.' + key + '.label') }} ({{ countByCategory(key) }})
        </button>
      </div>

      <!-- Search filter -->
      <div class="search-bar" style="margin-bottom:16px;">
        <span class="search-icon">🔍</span>
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          class="search-input"
          :placeholder="t('ui.prices.searchPlaceholder')"
        />
        <button v-if="searchQuery" class="search-clear" @click="clearSearch" :title="t('ui.prices.clearSearch')">×</button>
      </div>

      <!-- Chart -->
      <div class="card">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px">
          <h2 style="margin-bottom:0">{{ t('ui.prices.chart') }}</h2>
          <select v-model="selectedItem" class="crop-select">
            <option v-for="c in filteredItems" :key="c.type" :value="c.type">
              {{ c.emoji }} {{ tItem(c.type) }}
            </option>
          </select>
        </div>
        <PriceChart
          :item="currentItemData"
          :period-labels="periodLabels"
          :current-idx="data?.currentPeriodIdx ?? 0"
          :locale="locale"
        />
      </div>

      <!-- Prices table -->
      <div class="card" style="padding:0; overflow-x:auto">
        <table class="fields-table">
          <thead>
            <tr>
              <th class="sortable" @click="toggleSort('name')">{{ t('ui.prices.colProduct') }} {{ sortIcon('name') }}</th>
              <th class="sortable" @click="toggleSort('currentPrice')">{{ t('ui.prices.colCurrent') }} {{ sortIcon('currentPrice') }}</th>
              <th class="sortable" @click="toggleSort('nextPrice')">{{ t('ui.prices.colNext') }} {{ sortIcon('nextPrice') }}</th>
              <th class="sortable" @click="toggleSort('minPrice')">{{ t('ui.prices.colMin') }} {{ sortIcon('minPrice') }}</th>
              <th class="sortable" @click="toggleSort('maxPrice')">{{ t('ui.prices.colMax') }} {{ sortIcon('maxPrice') }}</th>
              <th>{{ t('ui.prices.colTrend') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in filteredItems"
              :key="c.type"
              :style="c.type === selectedItem ? 'background:var(--surface2)' : ''"
              style="cursor:pointer"
              @click="selectedItem = c.type"
            >
              <td><strong>{{ c.emoji }} {{ tItem(c.type) }}</strong></td>
              <td>
                <span :class="priceClass(c)">{{ formatPrice(c.currentPrice, locale) }}</span>
              </td>
              <td style="color:var(--text-dim)">{{ formatPrice(c.nextPrice, locale) }}</td>
              <td style="color:var(--text-dim)">{{ formatPrice(c.minPrice, locale) }}</td>
              <td>
                <span style="color:var(--accent)">{{ formatPrice(c.maxPrice, locale) }}</span>
                <small style="color:var(--text-dim)"> ({{ periodLabels[c.maxPeriodIdx] }})</small>
              </td>
              <td>
                <span v-if="c.trend === 'up'" style="color:var(--accent)">{{ t('ui.prices.trendUp') }}</span>
                <span v-else-if="c.trend === 'down'" style="color:var(--danger)">{{ t('ui.prices.trendDown') }}</span>
                <span v-else style="color:var(--text-dim)">{{ t('ui.prices.trendFlat') }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useI18n } from '../i18n/index.js'
import { usePersist } from '../useUIState.js'
import { formatPrice } from '../utils.js'
import { pricesSearch, pricesCategory } from '../useNavigation.js'
import PriceChart from './PriceChart.vue'

const { t, tItem, locale } = useI18n()

const CATEGORY_ORDER = [
  'crops', 'processed', 'dairy', 'animals', 'fish',
  'forestry', 'bales', 'byproducts', 'inputs', 'construction', 'other',
]

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const searchInput = ref(null)
const selectedItem = ref(null)
const activeCategory = pricesCategory   // shared singleton from useNavigation
const searchQuery    = pricesSearch     // shared singleton from useNavigation

const allItems = computed(() => props.data?.items || [])

const periodLabels = computed(() =>
  (props.data?.periods || []).map(p => t('periods.' + p))
)

const currentPeriodLabel = computed(() => {
  const periods = props.data?.periods || []
  const idx = props.data?.currentPeriodIdx ?? 0
  return periods[idx] ? t('periods.' + periods[idx]) : '—'
})

const presentCategories = computed(() => {
  const present = new Set(allItems.value.map(i => i.category))
  return CATEGORY_ORDER.filter(key => present.has(key))
})

function countByCategory(key) {
  return allItems.value.filter(i => i.category === key).length
}

const sortCol = usePersist('fd_pricesSortCol', 'currentPrice')
const sortDir = usePersist('fd_pricesSortDir', -1)

const SORT_KEYS = {
  name:         i => tItem(i.type).toLowerCase(),
  currentPrice: i => i.currentPrice,
  nextPrice:    i => i.nextPrice,
  minPrice:     i => i.minPrice,
  maxPrice:     i => i.maxPrice,
}

function toggleSort(col) {
  if (sortCol.value === col) {
    sortDir.value *= -1
  } else {
    sortCol.value = col
    sortDir.value = col === 'name' ? 1 : -1
  }
}

function sortIcon(col) {
  if (sortCol.value !== col) return '↕'
  return sortDir.value === 1 ? '↑' : '↓'
}

const filteredItems = computed(() => {
  let base = activeCategory.value
    ? allItems.value.filter(i => i.category === activeCategory.value)
    : allItems.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    base = base.filter(i => tItem(i.type).toLowerCase().includes(q))
  }
  const keyFn = SORT_KEYS[sortCol.value] ?? SORT_KEYS.currentPrice
  return [...base].sort((a, b) => {
    const av = keyFn(a), bv = keyFn(b)
    return av < bv ? -sortDir.value : av > bv ? sortDir.value : 0
  })
})

function clearSearch() {
  searchQuery.value = ''
  searchInput.value?.focus()
}

function setCategory(key) {
  activeCategory.value = key
  if (filteredItems.value.length > 0) {
    selectedItem.value = filteredItems.value[0].type
  }
}

const currentItemData = computed(() =>
  allItems.value.find(c => c.type === selectedItem.value) ?? null
)

function priceClass(c) {
  const ratio = c.currentPrice / c.maxPrice
  if (ratio >= 0.85) return 'price-high'
  if (ratio <= 0.55) return 'price-low'
  return ''
}

onMounted(() => {
  if (allItems.value.length) selectedItem.value = allItems.value[0].type
})

watch(() => props.data, (val) => {
  if (val?.items?.length && !selectedItem.value) selectedItem.value = val.items[0].type
})

watch(searchQuery, () => {
  if (filteredItems.value.length > 0 && !filteredItems.value.find(i => i.type === selectedItem.value)) {
    selectedItem.value = filteredItems.value[0].type
  }
})
</script>

<style scoped>
.crop-select {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  padding: 6px 10px;
  font-size: 13px;
  outline: none;
  cursor: pointer;
}
.crop-select:focus { border-color: var(--accent); }

.price-high { color: var(--accent); font-weight: 600; }
.price-low { color: var(--danger); }

.sortable {
  cursor: pointer;
  user-select: none;
}
.sortable:hover { color: var(--text); }

.search-bar {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0 10px;
  max-width: 340px;
  transition: border-color 0.15s;
}
.search-bar:focus-within { border-color: var(--accent); }

.search-icon {
  font-size: 14px;
  opacity: 0.5;
  pointer-events: none;
  margin-right: 6px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 13px;
  padding: 7px 0;
  min-width: 0;
}
.search-input::placeholder { color: var(--text-dim); }

.search-clear {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  padding: 0 0 0 6px;
  flex-shrink: 0;
  transition: color 0.15s;
}
.search-clear:hover { color: var(--text); }
</style>
