import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import DashboardView from './views/DashboardView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/dashboard', component: DashboardView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
