import { createRouter, createWebHistory } from 'vue-router'

import TicketsList from '@/Pages/TicketsList.vue'
const TicketNew = () => import('@/pages/TicketNew.vue')
const TicketDetail = () => import('@/pages/TicketDetail.vue')
const Dashboard = () => import('@/Pages/Dashboard.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/tickets' },
    { path: '/dashboard', name: 'dashboard', component: Dashboard },
    { path: '/tickets', name: 'tickets', component: TicketsList },
    { path: '/tickets/new', name: 'ticket-new', component: TicketNew },
    { path: '/tickets/:id', name: 'ticket-detail', component: TicketDetail, props: true },
  ],
})

export default router
