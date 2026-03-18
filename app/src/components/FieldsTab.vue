<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> Ładowanie pól...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div class="fields-summary">
        <div class="field-badge"><span class="dot dot-ready"></span> Gotowe do zbioru: <strong>{{ summary.ready || 0 }}</strong></div>
        <div class="field-badge"><span class="dot dot-growing"></span> W trakcie wzrostu: <strong>{{ summary.growing || 0 }}</strong></div>
        <div class="field-badge"><span class="dot dot-empty"></span> Puste/przygotowane: <strong>{{ summary.empty || 0 }}</strong></div>
        <div class="field-badge">🏠 Moje pola: <strong>{{ summary.owned || 0 }}</strong> / {{ summary.total || 0 }}</div>
        <div v-if="ownedReadyIds.length" class="field-badge" style="color:var(--ready)">
          ✅ Moje gotowe do zbioru: {{ ownedReadyIds.join(', ') }}
        </div>
      </div>

      <div style="display:flex; gap:6px; margin-bottom:12px;">
        <button
          v-for="f in FILTERS"
          :key="f.value"
          :class="['tab-btn', { active: filter === f.value }]"
          style="font-size:13px; padding:6px 14px;"
          @click="filter = f.value"
        >
          {{ f.label }} ({{ f.count() }})
        </button>
      </div>

      <div class="card" style="padding:0; overflow-x:auto">
        <table class="fields-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Uprawa</th>
              <th>Status</th>
              <th>Wzrost</th>
              <th>Chwasty</th>
              <th>Oprysk</th>
              <th>Wapno</th>
              <th>Podłoże</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in visibleFields" :key="f.id">
              <td>
                <strong>{{ f.id }}</strong>
                <span v-if="f.owned" style="margin-left:4px; font-size:11px;" title="Twoje pole">🏠</span>
              </td>
              <td>{{ f.fruitEmoji }} {{ f.fruitName }}</td>
              <td>
                <span :class="['status-badge', 'status-' + f.status]">
                  {{ statusLabel(f.status) }}
                </span>
              </td>
              <td>
                <div style="display:flex; align-items:center; gap:6px">
                  <span>{{ f.growthState }}/9</span>
                  <div class="progress-bar" style="width:50px">
                    <div class="progress-fill progress-fuel" :style="{ width: growthPct(f) + '%' }"></div>
                  </div>
                </div>
              </td>
              <td>
                <div style="display:flex; align-items:center; gap:6px">
                  <span>{{ f.weedState }}/9</span>
                  <div class="weed-bar">
                    <div class="weed-fill" :style="{ width: weedPct(f) + '%' }"></div>
                  </div>
                </div>
              </td>
              <td>
                {{ f.sprayLevel }}/3
                <small v-if="f.sprayType !== 'NONE'" style="color:var(--text-dim)"> {{ f.sprayType }}</small>
              </td>
              <td>{{ f.limeLevel }}/3</td>
              <td style="font-size:12px; color:var(--text-dim)">{{ f.groundType }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const fields = computed(() => props.data?.fields || [])
const summary = computed(() => props.data?.summary || {})
const ownedReadyIds = computed(() => summary.value?.ownedReadyIds || [])

const ownedFields = computed(() => fields.value.filter(f => f.owned))
const otherFields = computed(() => fields.value.filter(f => !f.owned))

const FILTERS = [
  { value: 'owned', label: '🏠 Moje pola', count: () => ownedFields.value.length },
  { value: 'all',   label: '🌍 Wszystkie',  count: () => fields.value.length },
  { value: 'other', label: '👥 Pozostałe',  count: () => otherFields.value.length },
]

// Default to "owned" when data loads if there are any owned fields
const filter = ref('owned')
watch(() => props.data, (val) => {
  if (val && ownedFields.value.length === 0) filter.value = 'all'
}, { immediate: true })

const visibleFields = computed(() => {
  if (filter.value === 'owned') return ownedFields.value
  if (filter.value === 'other') return otherFields.value
  return fields.value
})

function statusLabel(status) {
  return { ready: 'Gotowe', growing: 'Rośnie', empty: 'Puste' }[status] || status
}

function growthPct(f) {
  return Math.round((f.growthState / 9) * 100)
}

function weedPct(f) {
  return Math.round((f.weedState / 9) * 100)
}
</script>
