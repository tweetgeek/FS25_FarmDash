<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.precision.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div v-if="!data.available" class="alert alert-info">
        🌱 {{ t('ui.precision.notAvailable') }}
      </div>

      <template v-else>
        <!-- Summary -->
        <div class="card pf-summary">
          <h2>{{ t('ui.precision.summaryTitle') }}</h2>
          <div class="pf-summary-grid">
            <div class="pf-stat">
              <div class="pf-stat-label">🏠 {{ t('ui.precision.ownedFields') }}</div>
              <div class="pf-stat-value">{{ summary.ownedFieldCount }}</div>
            </div>
            <div class="pf-stat">
              <div class="pf-stat-label">🧪 {{ t('ui.precision.fieldsSampled') }}</div>
              <div class="pf-stat-value">
                {{ summary.fieldsWithSample }} / {{ summary.ownedFieldCount }}
              </div>
            </div>
            <div v-if="summary.totalYield > 0" class="pf-stat">
              <div class="pf-stat-label">🌾 {{ t('ui.precision.totalYield') }}</div>
              <div class="pf-stat-value">{{ formatAmount(summary.totalYield) }}</div>
            </div>
            <div v-if="summary.totalRevenue > 0" class="pf-stat">
              <div class="pf-stat-label">💰 {{ t('ui.precision.totalRevenue') }}</div>
              <div class="pf-stat-value accent">{{ formatMoney(summary.totalRevenue) }}</div>
            </div>
            <div v-if="summary.totalOperatingCosts > 0" class="pf-stat">
              <div class="pf-stat-label">⚙️ {{ t('ui.precision.totalCosts') }}</div>
              <div class="pf-stat-value danger">{{ formatMoney(summary.totalOperatingCosts) }}</div>
            </div>
          </div>
        </div>

        <!-- Filter -->
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

        <!-- Table -->
        <div class="card" style="padding:0; overflow-x:auto">
          <div style="padding:12px 16px 10px; border-bottom:1px solid var(--border)">
            <h2 style="margin-bottom:0">{{ t('ui.precision.tableTitle') }}</h2>
          </div>
          <table class="fields-table pf-table">
            <thead>
              <tr>
                <th>{{ t('ui.precision.colField') }}</th>
                <th>{{ t('ui.precision.colSoilSample') }}</th>
                <th>{{ t('ui.precision.colNitrogen') }}</th>
                <th>{{ t('ui.precision.colPH') }}</th>
                <th>{{ t('ui.precision.colTillage') }}</th>
                <th>{{ t('ui.precision.colHerbicide') }}</th>
                <th>{{ t('ui.precision.colYield') }}</th>
                <th>{{ t('ui.precision.colRevenue') }}</th>
                <th>{{ t('ui.precision.colCosts') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in visibleFields" :key="f.id">
                <td>
                  <strong>{{ f.id }}</strong>
                  <span v-if="f.owned" style="margin-left:4px; font-size:11px;" title="Twoje pole">🏠</span>
                  <span v-if="f.harvested" style="margin-left:4px; font-size:11px;" title="Zebrane">✅</span>
                </td>

                <!-- Soil sample -->
                <td>
                  <template v-if="f.soilSample < 0">
                    <span class="pf-badge pf-badge-dim">{{ t('ui.precision.noSample') }}</span>
                  </template>
                  <template v-else>
                    <div style="display:flex; align-items:center; gap:6px">
                      <div class="progress-bar" style="width:50px">
                        <div class="progress-fill progress-fuel" :style="{ width: (f.soilSample * 100) + '%' }"></div>
                      </div>
                      <span style="font-size:12px">{{ Math.round(f.soilSample * 100) }}%</span>
                    </div>
                  </template>
                </td>

                <!-- Nitrogen -->
                <td>
                  <template v-if="f.nitrogen">
                    <span :class="['pf-badge', nClass(f.nitrogen.perHa)]">
                      {{ nLabel(f.nitrogen.perHa) }}
                    </span>
                    <div style="font-size:11px; color:var(--text-dim); margin-top:2px">
                      {{ f.nitrogen.perHa != null ? (f.nitrogen.perHa > 0 ? '+' : '') + (f.nitrogen.perHa * 100).toFixed(1) : '—' }}
                    </div>
                  </template>
                  <span v-else class="pf-badge pf-badge-dim">{{ t('ui.precision.noData') }}</span>
                </td>

                <!-- pH -->
                <td>
                  <template v-if="f.ph">
                    <span :class="['pf-badge', phClass(f.ph.perHa)]">
                      {{ phLabel(f.ph.perHa) }}
                    </span>
                    <div style="font-size:11px; color:var(--text-dim); margin-top:2px">
                      {{ f.ph.perHa != null ? (f.ph.perHa > 0 ? '+' : '') + (f.ph.perHa * 100).toFixed(2) : '—' }}
                    </div>
                  </template>
                  <span v-else class="pf-badge pf-badge-dim">{{ t('ui.precision.noData') }}</span>
                </td>

                <!-- Tillage -->
                <td style="font-size:12px">
                  <template v-if="f.tillage">
                    <div v-if="f.tillage.directPct > 0" style="color:var(--accent)">
                      🌱 {{ t('ui.precision.tillageDirect') }} {{ f.tillage.directPct }}%
                    </div>
                    <div v-if="f.tillage.flatPct > 0" style="color:var(--text)">
                      🚜 {{ t('ui.precision.tillageFlat') }} {{ f.tillage.flatPct }}%
                    </div>
                    <div v-if="f.tillage.deepPct > 0" style="color:var(--text-dim)">
                      ⛏️ {{ t('ui.precision.tillageDeep') }} {{ f.tillage.deepPct }}%
                    </div>
                    <div v-if="f.tillage.nonePct > 0" style="color:var(--danger)">
                      ❌ {{ t('ui.precision.tillageNone') }} {{ f.tillage.nonePct }}%
                    </div>
                  </template>
                  <span v-else style="color:var(--text-dim)">{{ t('ui.precision.noData') }}</span>
                </td>

                <!-- Herbicide -->
                <td style="font-size:12px">
                  <template v-if="f.herbicide">
                    <div v-if="f.herbicide.spotSpray > 0" style="color:var(--accent)">
                      🎯 {{ t('ui.precision.herbSpot') }}
                    </div>
                    <div v-else-if="f.herbicide.fullSpray > 0" style="color:var(--warn)">
                      🌿 {{ t('ui.precision.herbFull') }}
                    </div>
                    <div v-else-if="f.herbicide.mechanical > 0" style="color:var(--text)">
                      ⚙️ {{ t('ui.precision.herbMech') }}
                    </div>
                    <span v-else style="color:var(--text-dim)">{{ t('ui.precision.noData') }}</span>
                  </template>
                  <span v-else style="color:var(--text-dim)">{{ t('ui.precision.noData') }}</span>
                </td>

                <!-- Yield -->
                <td>
                  <span v-if="f.totalStats?.yield > 0" style="color:var(--accent); font-weight:600">
                    {{ formatAmount(f.totalStats.yield) }}
                  </span>
                  <span v-else style="color:var(--text-dim)">—</span>
                </td>

                <!-- Revenue -->
                <td>
                  <span v-if="f.totalStats?.yieldBestPrice > 0" style="color:var(--accent2); font-weight:600">
                    {{ formatMoney(f.totalStats.yieldBestPrice) }}
                  </span>
                  <span v-else style="color:var(--text-dim)">—</span>
                </td>

                <!-- Costs -->
                <td>
                  <span v-if="totalCosts(f) > 0" style="color:var(--danger)">
                    {{ formatMoney(totalCosts(f)) }}
                  </span>
                  <span v-else style="color:var(--text-dim)">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { formatMoney } from '../utils.js'
import { useI18n } from '../i18n/index.js'
import { usePersist } from '../useUIState.js'

const { t } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const summary = computed(() => props.data?.summary || {})
const fields  = computed(() => props.data?.fields  || [])

const ownedFields = computed(() => fields.value.filter(f => f.owned))

const FILTERS = [
  { value: 'owned', label: () => t('ui.precision.filterOwned'), count: () => ownedFields.value.length },
  { value: 'all',   label: () => t('ui.precision.filterAll'),   count: () => fields.value.length },
]

const filter = usePersist('fd_precisionFilter', 'owned')
watch(() => props.data, (val) => {
  if (val && ownedFields.value.length === 0) filter.value = 'all'
}, { immediate: true })

const visibleFields = computed(() =>
  filter.value === 'owned' ? ownedFields.value : fields.value
)

// ── Nitrogen scoring ────────────────────────────────────────────────────────
// perHa < 0 = deficit, ~0 = optimal, > 0 = excess
function nClass(perHa) {
  if (perHa == null) return 'pf-badge-dim'
  if (Math.abs(perHa) < 0.01) return 'pf-badge-good'
  if (perHa < 0) return 'pf-badge-warn'
  return 'pf-badge-bad'  // over-fertilised
}
function nLabel(perHa) {
  if (perHa == null) return t('ui.precision.noData')
  if (Math.abs(perHa) < 0.01) return t('ui.precision.nBalanceGood')
  if (perHa < 0) return t('ui.precision.nBalanceLow')
  return t('ui.precision.nBalanceHigh')
}

// ── pH scoring ──────────────────────────────────────────────────────────────
function phClass(perHa) {
  if (perHa == null) return 'pf-badge-dim'
  if (Math.abs(perHa) < 0.003) return 'pf-badge-good'
  return 'pf-badge-warn'
}
function phLabel(perHa) {
  if (perHa == null) return t('ui.precision.noData')
  if (Math.abs(perHa) < 0.003) return t('ui.precision.phBalanceGood')
  return t('ui.precision.phBalanceLow')
}

function totalCosts(f) {
  const tc = f.totalStats
  if (!tc) return 0
  return (tc.vehicleCosts || 0) + (tc.helperCosts || 0)
}

function formatAmount(liters) {
  if (!liters) return '—'
  if (liters >= 1000) return (liters / 1000).toFixed(1) + ' t'
  return Math.round(liters) + ' L'
}
</script>

<style scoped>
.pf-summary-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 4px;
}

.pf-stat {
  background: var(--surface2);
  border-radius: var(--radius);
  padding: 10px 14px;
  min-width: 120px;
}

.pf-stat-label {
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.pf-stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}
.pf-stat-value.accent  { color: var(--accent); }
.pf-stat-value.danger  { color: var(--danger); }

/* Badges */
.pf-badge {
  display: inline-block;
  border-radius: 4px;
  padding: 2px 7px;
  font-size: 11px;
  font-weight: 600;
}
.pf-badge-good { background: var(--badge-good-bg); color: var(--accent); }
.pf-badge-warn { background: var(--badge-warn-bg); color: var(--warn); }
.pf-badge-bad  { background: var(--badge-bad-bg); color: var(--danger); }
.pf-badge-dim  { background: var(--surface2); color: var(--text-dim); }

.pf-table td { vertical-align: middle; }
</style>
