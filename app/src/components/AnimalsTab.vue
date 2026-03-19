<template>
  <div>
    <div v-if="loading" class="loading"><span class="spinner"></span> {{ t('ui.animals.loading') }}</div>
    <div v-else-if="error" class="alert alert-error">{{ error }}</div>
    <div v-else-if="data">

      <div v-if="!data.pens?.length" class="alert alert-info">
        {{ t('ui.animals.empty') }}
      </div>

      <template v-else>
        <div class="stats-grid" style="margin-bottom:20px">
          <StatCard
            v-for="(count, type) in data.summary"
            :key="type"
            :label="t('ui.animals.types.' + type, type)"
          >{{ count }}</StatCard>
        </div>

        <div class="animals-grid">
          <AnimalCard v-for="(pen, i) in data.pens" :key="i" :pen="pen" />
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { useI18n } from '../i18n/index.js'
import StatCard from './StatCard.vue'
import AnimalCard from './AnimalCard.vue'

const { t } = useI18n()

defineProps({
  data: Object,
  loading: Boolean,
  error: String,
})
</script>

<style scoped>
.animals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
</style>
