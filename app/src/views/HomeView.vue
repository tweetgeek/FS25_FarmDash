<template>
  <header>
    <div class="container">
      <h1>🚜 FS25 Live Dashboard</h1>
      <span class="subtitle">Farming Simulator 25 — Panel monitorowania</span>
    </div>
  </header>

  <main class="page-content">
    <div class="container">

      <div class="card">
        <h2>⚙️ Konfiguracja</h2>
        <div v-if="alert" :class="['alert', 'alert-' + alert.type]">{{ alert.message }}</div>

        <div class="form-group">
          <label>Ścieżka do katalogu z zapisami FS25</label>
          <input
            type="text"
            v-model="fs25Path"
            placeholder="np. C:\Users\Użytkownik\Documents\My Games\FarmingSimulator2025\savegame"
          />
          <div style="margin-top:4px; font-size:12px; color:var(--text-dim)">
            Wklej ścieżkę do katalogu zawierającego foldery savegame1, savegame2...
          </div>
        </div>

        <div class="form-group">
          <label>Interwał odświeżania (sekundy)</label>
          <input
            type="number"
            v-model.number="refreshInterval"
            min="5"
            max="300"
            style="width:120px"
          />
        </div>

        <button class="btn" :disabled="saving" @click="onSaveConfig">
          {{ saving ? 'Zapisywanie...' : 'Zapisz konfigurację' }}
        </button>
      </div>

      <div v-if="savesVisible" class="card">
        <h2>💾 Wybierz zapis gry</h2>
        <div v-if="savesAlert" :class="['alert', 'alert-' + savesAlert.type]">{{ savesAlert.message }}</div>
        <div v-if="savesLoading" class="loading">
          <span class="spinner"></span> Ładowanie zapisów...
        </div>
        <div v-else-if="saves.length === 0 && !savesAlert" class="alert alert-info">
          Nie znaleziono żadnych zapisów gry w podanej ścieżce.
        </div>
        <div v-else class="saves-grid">
          <div
            v-for="save in saves"
            :key="save.id"
            class="save-card"
            @click="openDashboard(save.id)"
          >
            <div class="save-name">{{ save.savegameName || save.name }}</div>
            <div class="save-map">🗺️ {{ save.mapTitle || '—' }}</div>
            <div class="save-meta">
              <span class="save-money">💰 {{ save.money ? formatMoney(save.money) : '—' }}</span>
              <span>📅 {{ save.saveDate || '—' }}</span>
              <span>🗂️ {{ save.id }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getConfig, saveConfig, getSaves } from '../api.js'
import { formatMoney } from '../utils.js'

const router = useRouter()

const fs25Path = ref('')
const refreshInterval = ref(30)
const saving = ref(false)
const alert = ref(null)
const savesVisible = ref(false)
const savesLoading = ref(false)
const savesAlert = ref(null)
const saves = ref([])

onMounted(async () => {
  try {
    const config = await getConfig()
    if (config.fs25_path) fs25Path.value = config.fs25_path
    if (config.refresh_interval) refreshInterval.value = config.refresh_interval
    if (config.fs25_path) await loadSaves()
  } catch (e) {
    alert.value = { type: 'error', message: 'Błąd wczytywania konfiguracji: ' + e.message }
  }
})

async function onSaveConfig() {
  if (!fs25Path.value.trim()) {
    alert.value = { type: 'error', message: 'Podaj ścieżkę do katalogu z zapisami FS25.' }
    return
  }
  saving.value = true
  alert.value = null
  try {
    await saveConfig({ fs25_path: fs25Path.value.trim(), refresh_interval: refreshInterval.value || 30 })
    alert.value = { type: 'success', message: 'Konfiguracja zapisana pomyślnie.' }
    await loadSaves()
  } catch (e) {
    alert.value = { type: 'error', message: 'Błąd zapisu: ' + e.message }
  } finally {
    saving.value = false
  }
}

async function loadSaves() {
  savesVisible.value = true
  savesLoading.value = true
  savesAlert.value = null
  saves.value = []
  try {
    const data = await getSaves()
    saves.value = data.saves || []
  } catch (e) {
    savesAlert.value = { type: 'error', message: 'Błąd ładowania zapisów: ' + e.message }
  } finally {
    savesLoading.value = false
  }
}

function openDashboard(saveId) {
  router.push('/dashboard?save=' + encodeURIComponent(saveId))
}
</script>
