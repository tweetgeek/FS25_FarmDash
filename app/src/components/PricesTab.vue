<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> Ładowanie cen...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div class="alert alert-info" style="margin-bottom:16px">
        📅 Aktualny okres: <strong>{{ data.currentPeriodLabel }}</strong>
        &nbsp;·&nbsp; {{ filteredItems.length }} pozycji
      </div>

      <!-- Category filter -->
      <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:16px;">
        <button
          :class="['tab-btn', { active: activeCategory === null }]"
          style="font-size:12px; padding:5px 12px;"
          @click="setCategory(null)"
        >
          🌍 Wszystkie ({{ data.items.length }})
        </button>
        <button
          v-for="[key, [label, emoji]] in presentCategories"
          :key="key"
          :class="['tab-btn', { active: activeCategory === key }]"
          style="font-size:12px; padding:5px 12px;"
          @click="setCategory(key)"
        >
          {{ emoji }} {{ label }} ({{ countByCategory(key) }})
        </button>
      </div>

      <!-- Chart -->
      <div class="card">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px">
          <h2 style="margin-bottom:0">📈 Wykres cen sezonowych</h2>
          <select v-model="selectedItem" class="crop-select">
            <option v-for="c in filteredItems" :key="c.type" :value="c.type">
              {{ c.emoji }} {{ c.name }}
            </option>
          </select>
        </div>
        <div style="position:relative; height:240px">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>

      <!-- Prices table -->
      <div class="card" style="padding:0; overflow:hidden">
        <table class="fields-table">
          <thead>
            <tr>
              <th class="sortable" @click="toggleSort('name')">Produkt {{ sortIcon('name') }}</th>
              <th class="sortable" @click="toggleSort('currentPrice')">Aktualnie {{ sortIcon('currentPrice') }}</th>
              <th class="sortable" @click="toggleSort('nextPrice')">Następny okres {{ sortIcon('nextPrice') }}</th>
              <th class="sortable" @click="toggleSort('minPrice')">Min {{ sortIcon('minPrice') }}</th>
              <th class="sortable" @click="toggleSort('maxPrice')">Max (kiedy) {{ sortIcon('maxPrice') }}</th>
              <th>Trend</th>
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
              <td><strong>{{ c.emoji }} {{ c.name }}</strong></td>
              <td>
                <span :class="priceClass(c)">{{ c.currentPrice }} PLN/t</span>
              </td>
              <td style="color:var(--text-dim)">{{ c.nextPrice }} PLN/t</td>
              <td style="color:var(--text-dim)">{{ c.minPrice }}</td>
              <td>
                <span style="color:var(--accent)">{{ c.maxPrice }}</span>
                <small style="color:var(--text-dim)"> ({{ data.periodLabels[c.maxPeriodIdx] }})</small>
              </td>
              <td>
                <span v-if="c.trend === 'up'" style="color:var(--accent)">▲ Rośnie</span>
                <span v-else-if="c.trend === 'down'" style="color:var(--danger)">▼ Spada</span>
                <span v-else style="color:var(--text-dim)">— Stabilna</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip } from 'chart.js'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip)

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const chartCanvas = ref(null)
const selectedItem = ref(null)
const activeCategory = ref(null)
let chartInstance = null

const allItems = computed(() => props.data?.items || [])

const presentCategories = computed(() => {
  if (!props.data?.categories) return []
  const present = new Set(allItems.value.map(i => i.category))
  return Object.entries(props.data.categories).filter(([key]) => present.has(key))
})

function countByCategory(key) {
  return allItems.value.filter(i => i.category === key).length
}

const sortCol = ref('currentPrice')
const sortDir = ref(-1) // -1 = desc, 1 = asc

const SORT_KEYS = {
  name:         i => i.name.toLowerCase(),
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
  const base = activeCategory.value
    ? allItems.value.filter(i => i.category === activeCategory.value)
    : allItems.value
  const keyFn = SORT_KEYS[sortCol.value] ?? SORT_KEYS.currentPrice
  return [...base].sort((a, b) => {
    const av = keyFn(a), bv = keyFn(b)
    return av < bv ? -sortDir.value : av > bv ? sortDir.value : 0
  })
})

function setCategory(key) {
  activeCategory.value = key
  if (filteredItems.value.length > 0) {
    selectedItem.value = filteredItems.value[0].type
  }
  nextTick(buildChart)
}

const currentItemData = computed(() => {
  if (!props.data || !selectedItem.value) return null
  return allItems.value.find(c => c.type === selectedItem.value)
})

function priceClass(c) {
  const ratio = c.currentPrice / c.maxPrice
  if (ratio >= 0.85) return 'price-high'
  if (ratio <= 0.55) return 'price-low'
  return ''
}

function buildChart() {
  if (!chartCanvas.value || !currentItemData.value || !props.data) return

  const item = currentItemData.value
  const labels = props.data.periodLabels
  const currentIdx = props.data.currentPeriodIdx

  const colors = item.prices.map((_, i) =>
    i === currentIdx ? '#4caf50' : 'rgba(76, 175, 80, 0.3)'
  )
  const borderColors = item.prices.map((_, i) =>
    i === currentIdx ? '#81c784' : 'rgba(76, 175, 80, 0.6)'
  )

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: `${item.emoji} ${item.name} (PLN/t)`,
        data: item.prices,
        backgroundColor: colors,
        borderColor: borderColors,
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.parsed.y} PLN/t`,
            afterLabel: ctx => ctx.dataIndex === currentIdx ? '← aktualny' : '',
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#9ea7b3', font: { size: 10 } },
          grid: { color: 'rgba(53, 59, 72, 0.5)' },
        },
        y: {
          ticks: { color: '#9ea7b3', callback: v => v + ' PLN' },
          grid: { color: 'rgba(53, 59, 72, 0.5)' },
        },
      },
    },
  })
}

onMounted(() => {
  if (allItems.value.length) {
    selectedItem.value = allItems.value[0].type
    nextTick(buildChart)
  }
})

watch(() => props.data, (val) => {
  if (val?.items?.length && !selectedItem.value) {
    selectedItem.value = val.items[0].type
  }
  nextTick(buildChart)
})

watch(selectedItem, () => nextTick(buildChart))

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
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
</style>
