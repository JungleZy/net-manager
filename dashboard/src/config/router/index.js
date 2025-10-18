import { key } from 'localforage'
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
        key: '1-1',
        path: '/home',
        name: 'Home',
        component: () => import('../../views/home/Home.vue')
      },
      {
        key: '1-2',
        path: '/network',
        name: 'Network',
        component: () => import('../../views/network/Network.vue')
      },
      {
        key: '1-3',
        path: '/devices',
        name: 'Devices',
        component: () => import('../../views/devices/Devices.vue')
      },
      {
        key: '1-4',
        path: '/topology',
        name: 'Topology',
        component: () => import('../../views/topology/Topology.vue')
      },
      {
        key: '1-5',
        path: '/test',
        name: 'Test',
        component: () => import('../../views/test/Demo.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
})

export default router