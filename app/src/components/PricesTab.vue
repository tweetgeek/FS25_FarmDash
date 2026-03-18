<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> Ładowanie cen...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <!-- Current period info -->
      <div class="alert alert-info" style="margin-bottom:16px">
        📅 Aktualny okres: <strong>{{ data.currentPeriodLabel }}</strong>
      </div>

      <!-- Crop selector + chart -->
      <div class="card">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px">
          <h2 style="margin-bottom:0">📈 Wykres cen sezonowych</h2>
          <select v-model="selectedCrop" class="crop-select">
            <option v-for="c in data.crops" :key="c.type" :value="c.type">
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
              <th>Surowiec</th>
              <th>Aktualnie</th>
              <th>Następny okres</th>
              <th>Min</th>
              <th>Max (kiedy)</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in data.crops"
              :key="c.type"
              :style="c.type === selectedCrop ? 'background:var(--surface2)' : ''"
              style="cursor:pointer"
              @click="selectedCrop = c.type"
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
const selectedCrop = ref(null)
let chartInstance = null

const currentCropData = computed(() => {
  if (!props.data || !selectedCrop.value) return null
  return props.data.crops.find(c => c.type === selectedCrop.value)
})

function priceClass(c) {
  const ratio = c.currentPrice / c.maxPrice
  if (ratio >= 0.85) return 'price-high'
  if (ratio <= 0.55) return 'price-low'
  return ''
}

function buildChart() {
  if (!chartCanvas.value || !currentCropData.value || !props.data) return

  const crop = currentCropData.value
  const labels = props.data.periodLabels
  const currentIdx = props.data.currentPeriodIdx

  const colors = crop.prices.map((_, i) =>
    i === currentIdx ? '#4caf50' : 'rgba(76, 175, 80, 0.3)'
  )
  const borderColors = crop.prices.map((_, i) =>
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
        label: `${crop.emoji} ${crop.name} (PLN/t)`,
        data: crop.prices,
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
            afterLabel: (ctx) => ctx.dataIndex === currentIdx ? '← aktualny' : '',
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
  if (props.data?.crops?.length) {
    selectedCrop.value = props.data.crops[0].type
    nextTick(buildChart)
  }
})

watch(() => props.data, (val) => {
  if (val?.crops?.length && !selectedCrop.value) {
    selectedCrop.value = val.crops[0].type
  }
  nextTick(buildChart)
})

watch(selectedCrop, () => nextTick(buildChart))

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
</style>
