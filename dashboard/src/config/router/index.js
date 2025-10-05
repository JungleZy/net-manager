import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    key: '1',
    path: '/',
    name: 'Index',
    component: () => import('../../views/Index.vue'),
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: () => import('../../views/home/Home.vue')
      },
      {
        path: '/devices',
        name: 'Devices',
        component: () => import('../../views/devices/Devices.vue')
      },
      {
        path: '/topology',
        name: 'Topology',
        component: () => import('../../views/topology/Topology.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
})

export default router