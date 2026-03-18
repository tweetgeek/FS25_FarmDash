<template>
  <header>
    <div class="container">
      <h1>🚜 FS25 Live Dashboard</h1>
      <span class="subtitle">{{ saveTitle }}</span>
      <span style="flex:1"></span>
      <RouterLink to="/" class="btn btn-secondary" style="font-size:13px; padding:6px 14px;">← Wróć</RouterLink>
    </div>
  </header>

  <div class="refresh-bar">
    <div class="container">
      <span>Ostatnie odświeżenie: <span>{{ lastRefresh || '—' }}</span></span>
      <span class="refresh-status">{{ refreshStatus }}</span>
    </div>
  </div>

  <main class="page-content">
    <div class="container">

      <div class="tabs">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-show="activeTab === 'overview'">
        <OverviewTab :data="overviewData" :loading="overviewLoading" :error="overviewError" />
      </div>
      <div v-show="activeTab === 'fields'">
        <FieldsTab :data="fieldsData" :loading="fieldsLoading" :error="fieldsError" />
      </div>
      <div v-show="activeTab === 'vehicles'">
        <VehiclesTab :data="vehiclesData" :loading="vehiclesLoading" :error="vehiclesError" />
      </div>
      <div v-show="activeTab === 'weather'">
        <WeatherTab :data="weatherData" :loading="weatherLoading" :error="weatherError" />
      </div>
      <div v-show="activeTab === 'prices'">
        <PricesTab :data="pricesData" :loading="pricesLoading" :error="pricesError" />
      </div>
      <div v-show="activeTab === 'storage'">
        <StorageTab :data="storageData" :loading="storageLoading" :error="storageError" :pricesData="pricesData" />
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getConfig, getSummary, getFields, getVehicles, getWeather, getEconomy, getStorage } from '../api.js'
import OverviewTab from '../components/OverviewTab.vue'
import FieldsTab from '../components/FieldsTab.vue'
import VehiclesTab from '../components/VehiclesTab.vue'
import WeatherTab from '../components/WeatherTab.vue'
import PricesTab from '../components/PricesTab.vue'
import StorageTab from '../components/StorageTab.vue'

const TABS = [
  { id: 'overview', label: '📊 Przegląd' },
  { id: 'fields', label: '🌾 Pola' },
  { id: 'vehicles', label: '🚜 Pojazdy' },
  { id: 'weather', label: '🌤️ Pogoda' },
  { id: 'prices', label: '💰 Ceny skupu' },
  { id: 'storage', label: '🏪 Magazyn' },
]

const route = useRoute()
const saveId = route.query.save

const activeTab = ref('overview')
const refreshInterval = ref(30)
const lastRefresh = ref(null)
const refreshStatus = ref('⏳ Ładowanie danych...')
let timer = null

const overviewData = ref(null)
const overviewLoading = ref(true)
const overviewError = ref(null)

const fieldsData = ref(null)
const fieldsLoading = ref(true)
const fieldsError = ref(null)

const vehiclesData = ref(null)
const vehiclesLoading = ref(true)
const vehiclesError = ref(null)

const weatherData = ref(null)
const weatherLoading = ref(true)
const weatherError = ref(null)

const pricesData = ref(null)
const pricesLoading = ref(true)
const pricesError = ref(null)

const storageData = ref(null)
const storageLoading = ref(true)
const storageError = ref(null)

const saveTitle = computed(() => {
  const career = overviewData.value?.career
  if (!career) return 'Ładowanie...'
  return `${career.savegameName || saveId} | ${career.mapTitle || '—'}`
})

onMounted(async () => {
  if (!saveId) return

  try {
    const config = await getConfig()
    refreshInterval.value = config.refresh_interval || 30
  } catch {}

  await Promise.all([loadOverview(), loadFields(), loadVehicles(), loadWeather(), loadPrices(), loadStorage()])
  setRefreshOk()
  scheduleRefresh()
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
})

async function loadOverview() {
  overviewLoading.value = true
  overviewError.value = null
  try {
    overviewData.value = await getSummary(saveId)
  } catch (e) {
    overviewError.value = 'Błąd ładowania przeglądu: ' + e.message
  } finally {
    overviewLoading.value = false
  }
}

async function loadFields() {
  fieldsLoading.value = true
  fieldsError.value = null
  try {
    fieldsData.value = await getFields(saveId)
  } catch (e) {
    fieldsError.value = 'Błąd ładowania pól: ' + e.message
  } finally {
    fieldsLoading.value = false
  }
}

async function loadVehicles() {
  vehiclesLoading.value = true
  vehiclesError.value = null
  try {
    vehiclesData.value = await getVehicles(saveId)
  } catch (e) {
    vehiclesError.value = 'Błąd ładowania pojazdów: ' + e.message
  } finally {
    vehiclesLoading.value = false
  }
}

async function loadWeather() {
  weatherLoading.value = true
  weatherError.value = null
  try {
    weatherData.value = await getWeather(saveId)
  } catch (e) {
    weatherError.value = 'Błąd ładowania pogody: ' + e.message
  } finally {
    weatherLoading.value = false
  }
}

async function loadPrices() {
  pricesLoading.value = true
  pricesError.value = null
  try {
    pricesData.value = await getEconomy(saveId)
  } catch (e) {
    pricesError.value = 'Błąd ładowania cen: ' + e.message
  } finally {
    pricesLoading.value = false
  }
}

async function loadStorage() {
  storageLoading.value = true
  storageError.value = null
  try {
    storageData.value = await getStorage(saveId)
  } catch (e) {
    storageError.value = 'Błąd ładowania magazynu: ' + e.message
  } finally {
    storageLoading.value = false
  }
}

async function loadTab(tab) {
  switch (tab) {
    case 'overview': await loadOverview(); break
    case 'fields': await loadFields(); break
    case 'vehicles': await loadVehicles(); break
    case 'weather': await loadWeather(); break
    case 'prices': await loadPrices(); break
    case 'storage': await loadStorage(); break
  }
}

function setRefreshOk() {
  lastRefresh.value = new Date().toLocaleTimeString('pl-PL')
  refreshStatus.value = `⏱️ Odświeżenie za ${refreshInterval.value}s`
}

function scheduleRefresh() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(async () => {
    refreshStatus.value = '🔄 Odświeżanie...'
    await loadTab(activeTab.value)
    if (activeTab.value !== 'overview') loadOverview()
    setRefreshOk()
    scheduleRefresh()
  }, refreshInterval.value * 1000)
}
</script>
