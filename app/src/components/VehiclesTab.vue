<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.vehicles.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">
      <div style="margin-bottom:12px; color:var(--text-dim); font-size:13px">
        {{ t('ui.vehicles.total') }}: {{ vehicles.length }}
      </div>
      <div class="vehicles-grid">
        <VehicleCard v-for="v in vehicles" :key="v.filename" :vehicle="v" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n/index.js'
import VehicleCard from './VehicleCard.vue'

const { t } = useI18n()

const props = defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})

const vehicles = computed(() => props.data?.vehicles || [])
</script>
