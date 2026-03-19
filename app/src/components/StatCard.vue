<template>
  <div class="stat-item">
    <div class="stat-value" :style="valueStyle"><slot /></div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  valueStyle: [String, Object],
})
</script>
