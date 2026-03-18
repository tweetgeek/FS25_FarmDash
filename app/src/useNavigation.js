import { ref, watch } from 'vue'

function _load(key, def) {
  const v = localStorage.getItem(key)
  return v !== null ? JSON.parse(v) : def
}

// Module-level singletons — shared across all components
export const activeTab     = ref(_load('fd_activeTab',       'overview'))
export const pricesSearch  = ref(_load('fd_pricesSearch',    ''))
export const pricesCategory = ref(_load('fd_pricesCategory', null))

watch(activeTab,      v => localStorage.setItem('fd_activeTab',       JSON.stringify(v)))
watch(pricesSearch,   v => localStorage.setItem('fd_pricesSearch',    JSON.stringify(v)))
watch(pricesCategory, v => localStorage.setItem('fd_pricesCategory',  JSON.stringify(v)))

/**
 * Navigate to the Prices tab and pre-filter by product name.
 * Clears the category filter so the product is always visible.
 */
export function goToPrices(name) {
  pricesSearch.value  = name
  pricesCategory.value = null
  activeTab.value     = 'prices'
}
