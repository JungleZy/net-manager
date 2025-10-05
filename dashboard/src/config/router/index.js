import { createRouter, createWebHistory } from 'vue-router'
const routes = [
  {
    key: '1',
    path: '/',
    name: 'Index',
    component: () => import('../../views/Index.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
})

export default router