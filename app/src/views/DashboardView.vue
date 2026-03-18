<template>
  <header>
    <div class="container">
      <h1>🚜 FS25 Live Dashboard</h1>
      <span class="subtitle">{{ saveTitle }}</span>
      <span v-if="version" class="version-tag">v{{ version }}</span>
      <span style="flex:1"></span>
      <div class="theme-btns">
        <button :class="['theme-btn', { active: theme === 'light' }]" @click="setTheme('light')" :title="t('ui.theme.light')">{{ t('ui.theme.light') }}</button>
        <button :class="['theme-btn', { active: theme === 'dark' }]" @click="setTheme('dark')" :title="t('ui.theme.dark')">{{ t('ui.theme.dark') }}</button>
        <button :class="['theme-btn', { active: theme === 'system' }]" @click="setTheme('system')" :title="t('ui.theme.system')">{{ t('ui.theme.system') }}</button>
      </div>
      <button class="btn btn-secondary" style="font-size:13px; padding:6px 14px;" @click="toggleLocale">{{ t('ui.lang') }}</button>
      <RouterLink to="/" class="btn btn-secondary" style="font-size:13px; padding:6px 14px;">{{ t('ui.backButton') }}</RouterLink>
    </div>
  </header>

  <div class="refresh-bar">
    <div class="container">
      <span>{{ t('ui.dashboard.lastRefresh') }}: <span>{{ lastRefresh || '—' }}</span></span>
      <span v-if="localUrl" style="color:var(--text-dim); display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
        <a :href="localUrl" target="_blank" style="color:var(--accent2); font-family:monospace; font-size:12px;">📱 {{ localUrl }}</a>
        <button @click="copyAddress" style="background:none; border:none; cursor:pointer; color:var(--text-dim); font-size:12px; padding:0; white-space:nowrap;">
          {{ copied ? t('ui.dashboard.copied') : t('ui.dashboard.copy') }}
        </button>
      </span>
      <span class="refresh-status">
        <template v-if="refreshStatus">{{ t('ui.dashboard.' + refreshStatus) }}</template>
        <template v-else-if="secondsLeft > 0">⏱️ {{ t('ui.dashboard.refreshIn') }} {{ secondsLeft }}s</template>
      </span>
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
          {{ t('ui.tabs.' + tab.id) }}
        </button>
      </div>

      <div v-show="activeTab === 'overview'">
        <OverviewTab :data="overviewData" :loading="overviewLoading" :error="overviewError"
          :weatherData="weatherData" :weatherLoading="weatherLoading" :weatherError="weatherError" />
      </div>
      <div v-show="activeTab === 'fields'">
        <FieldsTab :data="fieldsData" :loading="fieldsLoading" :error="fieldsError" />
      </div>
      <div v-show="activeTab === 'vehicles'">
        <VehiclesTab :data="vehiclesData" :loading="vehiclesLoading" :error="vehiclesError" />
      </div>
      <div v-show="activeTab === 'prices'">
        <PricesTab :data="pricesData" :loading="pricesLoading" :error="pricesError" />
      </div>
      <div v-show="activeTab === 'storage'">
        <StorageTab :data="storageData" :loading="storageLoading" :error="storageError" :pricesData="pricesData" />
      </div>
      <div v-show="activeTab === 'precision'">
        <PrecisionTab :data="precisionData" :loading="precisionLoading" :error="precisionError" />
      </div>
      <div v-show="activeTab === 'animals'">
        <AnimalsTab :data="animalsData" :loading="animalsLoading" :error="animalsError" />
      </div>
      <div v-show="activeTab === 'production'">
        <ProductionTab :data="productionData" :loading="productionLoading" :error="productionError" />
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getConfig, getSummary, getFields, getVehicles, getWeather, getEconomy, getStorage, getLocalAddress, getPrecisionFarming, getAnimals, getProduction } from '../api.js'
import { useI18n } from '../i18n/index.js'
import { useTheme } from '../theme.js'
import { usePersist } from '../useUIState.js'
import OverviewTab from '../components/OverviewTab.vue'
import FieldsTab from '../components/FieldsTab.vue'
import VehiclesTab from '../components/VehiclesTab.vue'
import PricesTab from '../components/PricesTab.vue'
import StorageTab from '../components/StorageTab.vue'
import PrecisionTab from '../components/PrecisionTab.vue'
import AnimalsTab from '../components/AnimalsTab.vue'
import ProductionTab from '../components/ProductionTab.vue'

const { t, locale, setLocale } = useI18n()
function toggleLocale() { setLocale(locale.value === 'pl' ? 'en' : 'pl') }
const { theme, setTheme } = useTheme()

const TABS = [
  { id: 'overview' },
  { id: 'fields' },
  { id: 'vehicles' },
  { id: 'prices' },
  { id: 'storage' },
  { id: 'precision' },
  { id: 'animals' },
  { id: 'production' },
]

const route = useRoute()
const saveId = route.query.save

const activeTab = usePersist('fd_activeTab', 'overview')
const refreshInterval = ref(30)
const version = ref(null)
const lastRefresh = ref(null)
const refreshStatus = ref('loading')
const localUrl = ref(null)
const copied = ref(false)
let timer = null
let countdown = null
const secondsLeft = ref(0)

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

const precisionData = ref(null)
const precisionLoading = ref(true)
const precisionError = ref(null)

const animalsData = ref(null)
const animalsLoading = ref(true)
const animalsError = ref(null)

const productionData = ref(null)
const productionLoading = ref(true)
const productionError = ref(null)

const saveTitle = computed(() => {
  const career = overviewData.value?.career
  if (!career) return t('ui.dashboard.loadingTitle')
  return `${career.savegameName || saveId} | ${career.mapTitle || '—'}`
})

onMounted(async () => {
  if (!saveId) return

  try {
    const config = await getConfig()
    refreshInterval.value = config.refresh_interval || 30
    if (config.version) version.value = config.version
  } catch {}

  getLocalAddress().then(r => { localUrl.value = r.url }).catch(() => {})

  await Promise.all([loadOverview(), loadFields(), loadVehicles(), loadWeather(), loadPrices(), loadStorage(), loadPrecision(), loadAnimals(), loadProduction()])
  setRefreshOk()
  scheduleRefresh()
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
  if (countdown) clearInterval(countdown)
})

async function copyAddress() {
  if (!localUrl.value) return
  try {
    await navigator.clipboard.writeText(localUrl.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {}
}

async function loadOverview() {
  overviewLoading.value = true
  overviewError.value = null
  try {
    overviewData.value = await getSummary(saveId)
  } catch (e) {
    overviewError.value = t('ui.dashboard.errorOverview') + ': ' + e.message
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
    fieldsError.value = t('ui.dashboard.errorFields') + ': ' + e.message
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
    vehiclesError.value = t('ui.dashboard.errorVehicles') + ': ' + e.message
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
    weatherError.value = t('ui.dashboard.errorWeather') + ': ' + e.message
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
    pricesError.value = t('ui.dashboard.errorPrices') + ': ' + e.message
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
    storageError.value = t('ui.dashboard.errorStorage') + ': ' + e.message
  } finally {
    storageLoading.value = false
  }
}

async function loadPrecision() {
  precisionLoading.value = true
  precisionError.value = null
  try {
    precisionData.value = await getPrecisionFarming(saveId)
  } catch (e) {
    precisionError.value = t('ui.dashboard.errorPrecision') + ': ' + e.message
  } finally {
    precisionLoading.value = false
  }
}

async function loadAnimals() {
  animalsLoading.value = true
  animalsError.value = null
  try {
    animalsData.value = await getAnimals(saveId)
  } catch (e) {
    animalsError.value = t('ui.dashboard.errorAnimals') + ': ' + e.message
  } finally {
    animalsLoading.value = false
  }
}

async function loadTab(tab) {
  switch (tab) {
    case 'overview':   await Promise.all([loadOverview(), loadWeather()]); break
    case 'fields':     await loadFields(); break
    case 'vehicles':   await loadVehicles(); break
    case 'prices':     await loadPrices(); break
    case 'storage':    await loadStorage(); break
    case 'precision':  await loadPrecision(); break
    case 'animals':    await loadAnimals(); break
    case 'production': await loadProduction(); break
  }
}

async function loadProduction() {
  productionLoading.value = true
  productionError.value = null
  try {
    productionData.value = await getProduction(saveId)
  } catch (e) {
    productionError.value = t('ui.dashboard.errorProduction') + ': ' + e.message
  } finally {
    productionLoading.value = false
  }
}

function setRefreshOk() {
  lastRefresh.value = new Date().toLocaleTimeString('pl-PL')
  secondsLeft.value = refreshInterval.value
  refreshStatus.value = ''
  if (countdown) clearInterval(countdown)
  countdown = setInterval(() => {
    secondsLeft.value--
    if (secondsLeft.value <= 0) {
      clearInterval(countdown)
      countdown = null
    }
  }, 1000)
}

function scheduleRefresh() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(async () => {
    if (countdown) { clearInterval(countdown); countdown = null }
    refreshStatus.value = 'refreshing'
    await loadTab(activeTab.value)
    if (activeTab.value !== 'overview') { loadOverview(); loadWeather() }
    setRefreshOk()
    scheduleRefresh()
  }, refreshInterval.value * 1000)
}
</script>
