<template>
  <div style="position:relative; height:240px">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Filler } from 'chart.js'
import { useI18n } from '../i18n/index.js'
import { formatPrice } from '../utils.js'

Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Filler)

const { t, tItem } = useI18n()

const props = defineProps({
  item: Object,          // selected price item: { type, emoji, prices }
  periodLabels: Array,   // translated period label strings
  currentIdx: Number,    // index of the current in-game period
  locale: String,
})

const chartCanvas = ref(null)
let chartInstance = null

function buildChart() {
  if (!chartCanvas.value || !props.item) return

  const { item, periodLabels, currentIdx } = props

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels: periodLabels,
      datasets: [{
        label: `${item.emoji} ${tItem(item.type)} (PLN/t)`,
        data: item.prices,
        borderColor: '#4caf50',
        backgroundColor: 'rgba(76, 175, 80, 0.08)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: item.prices.map((_, i) => i === currentIdx ? '#fff' : '#4caf50'),
        pointBorderColor:     item.prices.map((_, i) => i === currentIdx ? '#81c784' : '#4caf50'),
        pointBorderWidth:     item.prices.map((_, i) => i === currentIdx ? 2 : 1),
        pointRadius:          item.prices.map((_, i) => i === currentIdx ? 6 : 3),
        pointHoverRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label:      ctx => formatPrice(ctx.parsed.y, props.locale),
            afterLabel: ctx => ctx.dataIndex === currentIdx ? t('ui.prices.currentMarker') : '',
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#9ea7b3', font: { size: 10 } },
          grid:  { color: 'rgba(53, 59, 72, 0.5)' },
        },
        y: {
          ticks: { color: '#9ea7b3', callback: v => formatPrice(v, props.locale) },
          grid:  { color: 'rgba(53, 59, 72, 0.5)' },
        },
      },
    },
  })
}

onMounted(buildChart)
watch(() => props.item, buildChart)
watch(() => props.periodLabels, buildChart)
watch(() => props.locale, buildChart)

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>
