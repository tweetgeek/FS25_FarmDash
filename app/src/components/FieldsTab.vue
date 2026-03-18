<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> Ładowanie pól...</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div class="fields-summary">
        <div class="field-badge"><span class="dot dot-ready"></span> Gotowe do zbioru: <strong>{{ summary.ready || 0 }}</strong></div>
        <div class="field-badge"><span class="dot dot-growing"></span> W trakcie wzrostu: <strong>{{ summary.growing || 0 }}</strong></div>
        <div class="field-badge"><span class="dot dot-empty"></span> Puste/przygotowane: <strong>{{ summary.empty || 0 }}</strong></div>
        <div class="field-badge">📊 Łącznie: <strong>{{ summary.total || 0 }}</strong></div>
        <div v-if="summary.ready > 0" class="field-badge" style="color:var(--ready)">
          ✅ Pola do zbioru: {{ (summary.readyIds || []).join(', ') }}
        </div>
      </div>

      <div class="card" style="padding:0; overflow:hidden">
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
            <tr v-for="f in fields" :key="f.id">
              <td><strong>{{ f.id }}</strong></td>
              <td>{{ f.fruitEmoji }} {{ f.fruitType }}</td>
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
import { computed } from 'vue'

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const fields = computed(() => props.data?.fields || [])
const summary = computed(() => props.data?.summary || {})

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
