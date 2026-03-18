import { ref } from 'vue'
import pl from './pl.js'
import en from './en.js'

const LOCALES = { pl, en }
const locale = ref(localStorage.getItem('farmdash_locale') || 'pl')

export function useI18n() {
  function t(key, fallback) {
    const parts = key.split('.')
    let obj = LOCALES[locale.value]
    for (const part of parts) {
      if (obj == null || typeof obj !== 'object') return fallback ?? key
      obj = obj[part]
    }
    if (typeof obj === 'string') return obj
    return fallback ?? key
  }

  // Translate an item/fill type with auto-formatted fallback for unknown keys
  function tItem(type) {
    if (!type) return '—'
    const key = `items.${type}`
    const result = t(key)
    if (result === key) {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    return result
  }

  // Translate a fruit/crop type (fields tab)
  function tFruit(type) {
    if (!type) return '—'
    const key = `fruits.${type}`
    const result = t(key)
    if (result === key) {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    return result
  }

  function setLocale(lang) {
    if (LOCALES[lang]) {
      locale.value = lang
      localStorage.setItem('farmdash_locale', lang)
    }
  }

  return { t, tItem, tFruit, locale, setLocale, localeKeys: Object.keys(LOCALES) }
}
