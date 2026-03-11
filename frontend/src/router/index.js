import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import AdminDash from '../components/AdminDash.vue'
import DoctorDash from '../components/DoctorDash.vue'
import PatientDash from '../components/PatientDash.vue'

const routes = [
  { path: '/', component: Login, meta: { guestOnly: true } },
  { path: '/admin', component: AdminDash, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/doctor', component: DoctorDash, meta: { requiresAuth: true, role: 'doctor' } },
  { path: '/patient', component: PatientDash, meta: { requiresAuth: true, role: 'patient' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const stored = localStorage.getItem('user')
  const user = stored ? JSON.parse(stored) : null

  if (to.meta.requiresAuth) {
    if (!user) return next('/')
    if (to.meta.role && user.role !== to.meta.role) return next('/')
  }
  if (to.meta.guestOnly && user) {
    if (user.role === 'admin') return next('/admin')
    if (user.role === 'doctor') return next('/doctor')
    return next('/patient')
  }
  next()
})

export default router
