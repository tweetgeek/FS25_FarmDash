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
        <button class="theme-btn" :title="isFullscreen ? t('ui.dashboard.exitFullscreen') : t('ui.dashboard.enterFullscreen')" @click="toggleFullscreen">{{ isFullscreen ? '⊡' : '⛶' }}</button>
        <button v-if="wakeLockSupported" :class="['theme-btn', { active: wakeLockActive }]" :title="wakeLockEnabled ? t('ui.dashboard.wakeLockOff') : t('ui.dashboard.wakeLockOn')" @click="toggleWakeLock">{{ wakeLockEnabled ? '☀️' : '💤' }}</button>
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
        <button
          class="refresh-btn"
          :disabled="!!refreshStatus"
          :title="t('ui.dashboard.refreshNow')"
          @click="manualRefresh"
        >⟳</button>
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
        <OverviewTab :data="effectiveOverviewData" :loading="overviewLoading" :error="overviewError"
          :weatherData="weatherData" :weatherLoading="weatherLoading" :weatherError="weatherError" />
      </div>
      <div v-show="activeTab === 'fields'">
        <FieldsTab :data="effectiveFieldsData" :loading="fieldsLoading" :error="fieldsError" />
      </div>
      <div v-show="activeTab === 'vehicles'">
        <VehiclesTab :data="effectiveVehiclesData" :loading="vehiclesLoading" :error="vehiclesError" />
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
import { getConfig, getSummary, getFields, getVehicles, getWeather, getEconomy, getStorage, getLocalAddress, getPrecisionFarming, getAnimals, getProduction, getModLive } from '../api.js'
import { useI18n } from '../i18n/index.js'
import { useTheme } from '../theme.js'
import { usePersist } from '../useUIState.js'
import { activeTab } from '../useNavigation.js'
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

// Fullscreen
const isFullscreen = ref(false)
function toggleFullscreen() {
  if (!document.fullscreenElement) { document.documentElement.requestFullscreen().catch(() => {}) }
  else { document.exitFullscreen().catch(() => {}) }
}
function onFullscreenChange() { isFullscreen.value = !!document.fullscreenElement }

// Wake Lock
const wakeLockSupported = 'wakeLock' in navigator
const wakeLockEnabled = ref(false)
const wakeLockActive = ref(false)
let wakeLockSentinel = null
async function acquireWakeLock() {
  try {
    wakeLockSentinel = await navigator.wakeLock.request('screen')
    wakeLockActive.value = true
    wakeLockSentinel.addEventListener('release', () => { wakeLockActive.value = false; wakeLockSentinel = null })
  } catch { wakeLockActive.value = false }
}
async function toggleWakeLock() {
  wakeLockEnabled.value = !wakeLockEnabled.value
  if (wakeLockEnabled.value) { await acquireWakeLock() }
  else { if (wakeLockSentinel) { await wakeLockSentinel.release(); wakeLockSentinel = null }; wakeLockActive.value = false }
}
async function onVisibilityChange() {
  if (document.visibilityState === 'visible' && wakeLockEnabled.value && !wakeLockSentinel) { await acquireWakeLock() }
}

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

// activeTab is imported from useNavigation.js (shared singleton)
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

const modLiveData = ref(null)

// Merge mod live data (more real-time) on top of XML-parsed data where applicable
const effectiveOverviewData = computed(() => {
  const base = overviewData.value
  if (!base || !modLiveData.value?.updatedAt) return base
  const mod = modLiveData.value
  return {
    ...base,
    environment: mod.environment ? { ...base.environment, dayTime: mod.environment.dayTime ?? base.environment?.dayTime, currentDay: mod.environment.currentDay ?? base.environment?.currentDay } : base.environment,
    farm: mod.farm ? { ...base.farm, money: mod.farm.money ?? base.farm?.money, loan: mod.farm.loan ?? base.farm?.loan } : base.farm,
  }
})

const effectiveVehiclesData = computed(() => {
  const base = vehiclesData.value
  if (!base || !modLiveData.value?.vehicles?.length) return base
  const modByFilename = {}
  for (const mv of modLiveData.value.vehicles) { if (mv.filename) modByFilename[mv.filename] = mv }
  return {
    ...base,
    vehicles: (base.vehicles || []).map(v => {
      const mv = modByFilename[v.filename]
      if (!mv) return v
      return { ...v, name: mv.name || v.name, typeName: mv.typeName || v.typeName, damage: mv.damage ?? v.damage, dirt: mv.dirt ?? v.dirt, operatingTime: mv.operatingHours ?? v.operatingTime, fuelPct: mv.fuelPct }
    }),
  }
})

const effectiveFieldsData = computed(() => {
  const base = fieldsData.value
  if (!base || !modLiveData.value?.fields?.length) return base
  const modById = {}
  for (const mf of modLiveData.value.fields) { modById[mf.id] = mf }
  return {
    ...base,
    fields: (base.fields || []).map(f => {
      const mf = modById[f.id]
      if (!mf || mf.fruitType === 'NONE') return f
      return { ...f, fruitType: mf.fruitType }
    }),
  }
})

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

  document.addEventListener('fullscreenchange', onFullscreenChange)
  document.addEventListener('visibilitychange', onVisibilityChange)

  getLocalAddress().then(r => { localUrl.value = r.url }).catch(() => {})

  await Promise.all([loadOverview(), loadFields(), loadVehicles(), loadWeather(), loadPrices(), loadStorage(), loadPrecision(), loadAnimals(), loadProduction(), loadModLive()])
  setRefreshOk()
  scheduleRefresh()
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
  if (countdown) clearInterval(countdown)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  document.removeEventListener('visibilitychange', onVisibilityChange)
  if (wakeLockSentinel) wakeLockSentinel.release()
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

async function loadModLive() {
  try { modLiveData.value = await getModLive() } catch { /* mod not available */ }
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

async function manualRefresh() {
  if (refreshStatus.value) return
  if (timer) clearTimeout(timer)
  if (countdown) { clearInterval(countdown); countdown = null }
  refreshStatus.value = 'refreshing'
  await loadTab(activeTab.value)
  if (activeTab.value !== 'overview') { loadOverview(); loadWeather() }
  loadModLive()
  setRefreshOk()
  scheduleRefresh()
}

function scheduleRefresh() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(async () => {
    if (countdown) { clearInterval(countdown); countdown = null }
    refreshStatus.value = 'refreshing'
    await loadTab(activeTab.value)
    if (activeTab.value !== 'overview') { loadOverview(); loadWeather() }
    loadModLive()
    setRefreshOk()
    scheduleRefresh()
  }, refreshInterval.value * 1000)
}
</script>
