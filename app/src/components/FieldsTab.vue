<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.fields.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div class="fields-summary">
        <div class="field-badge"><span class="dot dot-ready"></span> {{ t('ui.fields.ready') }}: <strong>{{ summary.ready || 0 }}</strong></div>
        <div class="field-badge"><span class="dot dot-growing"></span> {{ t('ui.fields.growing') }}: <strong>{{ summary.growing || 0 }}</strong></div>
        <div class="field-badge"><span class="dot dot-empty"></span> {{ t('ui.fields.empty') }}: <strong>{{ summary.empty || 0 }}</strong></div>
        <div class="field-badge">🏠 {{ t('ui.fields.myCount') }}: <strong>{{ summary.owned || 0 }}</strong> / {{ summary.total || 0 }}</div>
        <div v-if="ownedReadyIds.length" class="field-badge" style="color:var(--ready)">
          {{ t('ui.fields.ownedReady') }}: {{ ownedReadyIds.join(', ') }}
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
          {{ f.label() }} ({{ f.count() }})
        </button>
      </div>

      <div class="card" style="padding:0; overflow-x:auto">
        <table class="fields-table">
          <thead>
            <tr>
              <th>#</th>
              <th>{{ t('ui.fields.colCrop') }}</th>
              <th>{{ t('ui.fields.colStatus') }}</th>
              <th>{{ t('ui.fields.colGrowth') }}</th>
              <th>{{ t('ui.fields.colWeeds') }}</th>
              <th>{{ t('ui.fields.colSpray') }}</th>
              <th>{{ t('ui.fields.colLime') }}</th>
              <th>{{ t('ui.fields.colSoil') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in visibleFields" :key="f.id">
              <td>
                <strong>{{ f.id }}</strong>
                <span v-if="f.owned" style="margin-left:4px; font-size:11px;" title="Twoje pole">🏠</span>
              </td>
              <td>{{ f.fruitEmoji }} {{ tFruit(f.fruitType) }}</td>
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
import { useI18n } from '../i18n/index.js'
import { usePersist } from '../useUIState.js'

const { t, tFruit } = useI18n()

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
  { value: 'owned', label: () => t('ui.fields.filterOwned'), count: () => ownedFields.value.length },
  { value: 'all',   label: () => t('ui.fields.filterAll'),   count: () => fields.value.length },
  { value: 'other', label: () => t('ui.fields.filterOther'), count: () => otherFields.value.length },
]

const filter = usePersist('fd_fieldsFilter', 'owned')
watch(() => props.data, (val) => {
  if (val && ownedFields.value.length === 0) filter.value = 'all'
}, { immediate: true })

const visibleFields = computed(() => {
  if (filter.value === 'owned') return ownedFields.value
  if (filter.value === 'other') return otherFields.value
  return fields.value
})

function statusLabel(status) {
  return {
    ready: t('ui.fields.statusReady'),
    growing: t('ui.fields.statusGrowing'),
    empty: t('ui.fields.statusEmpty'),
  }[status] || status
}

function growthPct(f) {
  return Math.round((f.growthState / 9) * 100)
}

function weedPct(f) {
  return Math.round((f.weedState / 9) * 100)
}
</script>
